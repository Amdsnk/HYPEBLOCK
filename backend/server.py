from fastapi import FastAPI, APIRouter, HTTPException, Query, Header
from fastapi.responses import JSONResponse, FileResponse, Response, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
if __package__:
    from .artwork import ArtworkManager
else:
    from artwork import ArtworkManager
import base64
import secrets
import asyncio
import os
import json
import logging
import random
import io
import zipfile
import re
from html import escape
from pathlib import Path
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _nested_value(doc, path):
    value = doc
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _matches_query(doc, query):
    for key, expected in query.items():
        if key == "$or":
            if not any(_matches_query(doc, branch) for branch in expected):
                return False
            continue
        actual = _nested_value(doc, key)
        if isinstance(expected, dict):
            for operator, value in expected.items():
                if operator == "$regex":
                    flags = re.IGNORECASE if expected.get("$options") == "i" else 0
                    if actual is None or re.search(value, str(actual), flags) is None:
                        return False
                elif operator == "$options":
                    continue
                elif operator == "$lte" and (actual is None or actual > value):
                    return False
                elif operator == "$gt" and (actual is None or actual <= value):
                    return False
                elif operator == "$in" and actual not in value:
                    return False
        elif actual != expected:
            return False
    return True


def _project_doc(doc, projection):
    if not projection:
        return dict(doc)
    excluded = [key for key, value in projection.items() if not value]
    included = [key for key, value in projection.items() if value and key != "_id"]
    if included:
        result = {key: _nested_value(doc, key) for key in included if _nested_value(doc, key) is not None}
        if projection.get("_id", 1) and "_id" in doc:
            result["_id"] = doc["_id"]
        return result
    result = dict(doc)
    for key in excluded:
        result.pop(key, None)
    return result


class _MemoryCursor:
    def __init__(self, documents, projection=None):
        self.documents = [_project_doc(doc, projection) for doc in documents]

    def sort(self, ordering, direction=None):
        if direction is not None:
            ordering = [(ordering, direction)]
        for field, direction in reversed(ordering):
            self.documents.sort(
                key=lambda doc: (_nested_value(doc, field) is None, _nested_value(doc, field)),
                reverse=direction < 0,
            )
        return self

    def skip(self, count):
        self.documents = self.documents[count:]
        return self

    def limit(self, count):
        self.documents = self.documents[:count]
        return self

    async def to_list(self, length):
        return self.documents[:length]


class _MemoryCollection:
    def __init__(self):
        self.documents = []

    async def find_one(self, query, projection=None):
        for document in self.documents:
            if _matches_query(document, query):
                return _project_doc(document, projection)
        return None

    def find(self, query=None, projection=None):
        query = query or {}
        return _MemoryCursor(
            [document for document in self.documents if _matches_query(document, query)],
            projection,
        )

    async def count_documents(self, query):
        return sum(1 for document in self.documents if _matches_query(document, query))

    async def delete_many(self, query):
        self.documents = [document for document in self.documents if not _matches_query(document, query)]

    async def insert_many(self, documents):
        self.documents.extend(dict(document) for document in documents)

    async def insert_one(self, document):
        self.documents.append(dict(document))

    async def replace_one(self, query, replacement, upsert=False):
        for index, document in enumerate(self.documents):
            if _matches_query(document, query):
                self.documents[index] = dict(replacement)
                return
        if upsert:
            self.documents.append(dict(replacement))

    async def update_one(self, query, update):
        for document in self.documents:
            if _matches_query(document, query):
                for key, value in update.get("$set", {}).items():
                    document[key] = value
                return


class _JsonCollection:
    """Small async collection adapter backed by one atomic JSON file."""

    def __init__(self, database, name):
        self.database = database
        self.name = name

    @property
    def documents(self):
        return self.database.state[self.name]

    async def find_one(self, query, projection=None):
        for document in self.documents:
            if _matches_query(document, query):
                return _project_doc(document, projection)
        return None

    def find(self, query=None, projection=None):
        query = query or {}
        return _MemoryCursor(
            [document for document in self.documents if _matches_query(document, query)],
            projection,
        )

    async def count_documents(self, query):
        return sum(1 for document in self.documents if _matches_query(document, query))

    async def delete_many(self, query):
        async with self.database.lock:
            self.database.state[self.name] = [
                document for document in self.documents if not _matches_query(document, query)
            ]
            await self.database.save()

    async def insert_many(self, documents):
        async with self.database.lock:
            self.documents.extend(dict(document) for document in documents)
            await self.database.save()

    async def insert_one(self, document):
        async with self.database.lock:
            self.documents.append(dict(document))
            await self.database.save()

    async def replace_one(self, query, replacement, upsert=False):
        async with self.database.lock:
            for index, document in enumerate(self.documents):
                if _matches_query(document, query):
                    self.documents[index] = dict(replacement)
                    await self.database.save()
                    return
            if upsert:
                self.documents.append(dict(replacement))
                await self.database.save()

    async def update_one(self, query, update):
        async with self.database.lock:
            for document in self.documents:
                if _matches_query(document, query):
                    for key, value in update.get("$set", {}).items():
                        document[key] = value
                    await self.database.save()
                    return

    async def delete_one(self, query):
        async with self.database.lock:
            for index, document in enumerate(self.documents):
                if _matches_query(document, query):
                    del self.documents[index]
                    await self.database.save()
                    return


class _JsonDatabase:
    """Persistent replacement for MongoDB for traditional hosting."""

    def __init__(self, path):
        self.path = Path(path)
        self.lock = asyncio.Lock()
        self.state = {"meta": [], "nfts": [], "waitlist": []}
        self._load()
        self.meta = _JsonCollection(self, "meta")
        self.nfts = _JsonCollection(self, "nfts")
        self.waitlist = _JsonCollection(self, "waitlist")

    def _load(self):
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                for name in self.state:
                    if isinstance(raw.get(name), list):
                        self.state[name] = raw[name]
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Cannot read local data store {self.path}: {exc}") from exc

    async def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.path)

    async def close(self):
        async with self.lock:
            await self.save()


DATA_DIR = Path(os.environ.get("HYPEBLOCK_DATA_DIR", ROOT_DIR / "data"))
DATA_FILE = Path(os.environ.get("HYPEBLOCK_DATA_FILE", DATA_DIR / "store.json"))
db = _JsonDatabase(DATA_FILE)
artwork = ArtworkManager(db, ROOT_DIR)

ADMIN_KEY = os.environ.get('ADMIN_KEY', '')
RELEASED_BATCHES = int(os.environ.get('RELEASED_BATCHES', '3'))
BATCH_SIZE = 20
LAUNCH_DATE = datetime(2026, 6, 16, tzinfo=timezone.utc)
COLLECTION_VERSION = "v8"

try:
    COLLECTION_SIZE = len(json.loads((ROOT_DIR / "merged_collection.json").read_text()))
except Exception:
    COLLECTION_SIZE = 296

TRAIT_KEYS = ("Gender", "Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory")


def _trait_signature(traits):
    return tuple(traits.get(category) for category in TRAIT_KEYS)


def _validate_collection(raw):
    token_ids = [item.get("token_id") for item in raw]
    names = [item.get("name") for item in raw]
    signatures = [_trait_signature(item.get("traits", {})) for item in raw]
    for label, values in (("token IDs", token_ids), ("names", names), ("trait combinations", signatures)):
        if len(values) != len(set(values)):
            raise RuntimeError(f"Collection contains duplicate {label}; refusing to seed")
    return raw


def _public_base():
    try:
        fe = ROOT_DIR.parent / "frontend" / ".env"
        if fe.exists():
            for line in fe.read_text().splitlines():
                if line.startswith("REACT_APP_BACKEND_URL"):
                    return line.split("=", 1)[1].strip().rstrip("/")
    except Exception:
        pass
    return os.environ.get("APP_URL", "").rstrip("/")


PUBLIC_BASE = _public_base()


def _render_url(token_id):
    """Return a stable image URL for every token, including fallback renders."""
    base = PUBLIC_BASE or ""
    return f"{base}/api/render/{token_id}"

app = FastAPI(title="HYPEBLOCK API")
api_router = APIRouter(prefix="/api")

# ---------------------------------------------------------------------------
# Fallback image library (used until a per-token render exists)
# ---------------------------------------------------------------------------
BASE = "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/"
FALLBACK_ASSETS_DIR = ROOT_DIR / "fallback_assets"


def _fallback_asset_url(asset_key):
    """Use a same-host asset URL so renders work without third-party storage."""
    return f"/api/assets/{asset_key}.jpeg"


IMG = {
    "green_beanie": BASE + "de2465864aefac69c38f99e0c8719e2c190ef17a3f67c4052e2afd8cfee6866e.jpeg",
    "green_vr": BASE + "9e0a66744be295415aa6405906e62b17c158e914ecac15719294c850415975c7.jpeg",
    "green_stoned": BASE + "4cbcd58bfba0340398d83766663b321392f8c91a78c9b2ad6addde7236b12262.jpeg",
    "green_cyclops_cigar": BASE + "c0383b50853ac1d0128ecde8dc93d0df7ae6688c94e00ccce9931406e179830b.jpeg",
    "female_green_crown": BASE + "80d124b96fec73e24fac3e1b192188b6f1447334d92bc4eb9af420bfbbf5095c.jpeg",
    "blue_snapback": BASE + "eba46a9c8b42de7aa35e707632c16c9bbeee67600e024647b6cd87f3accda2ee.jpeg",
    "blue_bucket": BASE + "4779c283c1acf937ba259a421bc2e610ffd768023a2f76d512d1ce4ee868ba40.jpeg",
    "blue_chainonly": BASE + "17a6e7e45c79e5721f653b676bd02b01412fd5d45ffca29cf85fa5905e2060a7.jpeg",
    "female_blue_vr": BASE + "c6fba6e3262f7065e3faedbd84ba884662c1c62aceed702a3b8f8085839f9e34.jpeg",
    "purple_3dglasses": BASE + "9a3dde413f050a445b47183db65f185872d944049d4766e057278b8f8a8e06dc.jpeg",
    "purple_cyclops": BASE + "ac7110d4f63e2596b5b1412f02d0caee588a66fb1fdd5beac8a77c5dffd8513d.jpeg",
    "albino_durag": BASE + "5fe48fd67e7758fde61b4834f97099484d02ebb901854eb66afb3406fb0dba2d.jpeg",
    "albino_devil": BASE + "56b0a8cbaaa51c779020a90e99287128bf57d14e0af3716d58fa1dbd5786f415.jpeg",
    "zombie_horns": BASE + "33416a50f597391530af4fbaa7f1eb4929202a1a972ddf8728f82ba367a18ad5.jpeg",
    "zombie_bomber": BASE + "8dbe4bf1712316e93dfdc4c9bd0044341abba18cfa02c2b955fa66bfaba3f807.jpeg",
    "blue_laser_epic": BASE + "d5c889cef616dc06679224636dd84a04bd4a755a24d68636395278ac448efbb2.jpeg",
    "purple_flame_epic": BASE + "8d5c5cbef44f7f6fba7a052a741576f4a51a726a33a242bda4366050ac14885f.jpeg",
    "zombie_laser_epic": BASE + "8649abd12c1f9cd3a93b658ac81826576854ca8b4f8c52b7b5214db824c63ff2.jpeg",
    "gold_crown_laser": BASE + "1457c54c9767fd5fa4931d94ad1dab717471e6ff27432c366e32ad90d47e6e98.jpeg",
    "diamond_halo_flame": BASE + "4c34eab44cdba05869cb9177ed7e1db6287a3c5845f62755902b80d3c6a1d4a8.jpeg",
    # --- 5 original base-style renders supplied by the creator ---
    "att_female_green_buns": "https://customer-assets-m6fa6gv7.emergentagent.net/job_hypeblock-nft/artifacts/jlykm00u_image-1788909840905.jpeg",
    "att_zombie_devil_epic": "https://customer-assets-m6fa6gv7.emergentagent.net/job_hypeblock-nft/artifacts/8m9ykes4_image-1788909077929.jpeg",
    "att_blue_snapback": "https://customer-assets-m6fa6gv7.emergentagent.net/job_hypeblock-nft/artifacts/3li42p89_image-1788908924637.jpeg",
    "att_female_blue_neon": "https://customer-assets-m6fa6gv7.emergentagent.net/job_hypeblock-nft/artifacts/ts9wg36e_image-5%20%287%29.jpeg",
}
# The single crown-jewel 1-of-1 (Mythic) hero render
MYTHIC_IMAGE = "https://customer-assets-m6fa6gv7.emergentagent.net/job_hypeblock-nft/artifacts/6hfjziwu_image-5%20%288%29.jpeg"
FEMALE_IMAGES = {"female_green_crown", "female_blue_vr", "att_female_green_buns", "att_female_blue_neon"}
SKIN_IMAGES = {
    "Classic Green": ["green_beanie", "green_vr", "green_stoned", "green_cyclops_cigar", "female_green_crown", "att_female_green_buns"],
    "Toxic Blue": ["blue_snapback", "blue_bucket", "blue_chainonly", "female_blue_vr", "att_blue_snapback", "att_female_blue_neon"],
    "Purple Haze": ["purple_3dglasses", "purple_cyclops"],
    "Albino": ["albino_durag", "albino_devil"],
    "Zombie": ["zombie_horns", "zombie_bomber"],
}
EPIC_IMAGES = {"Toxic Blue": ["blue_laser_epic"], "Purple Haze": ["purple_flame_epic"],
               "Zombie": ["zombie_laser_epic", "att_zombie_devil_epic"]}

# The 3 crown-jewel 1-of-1 Mythics (each a unique founding character)
MYTHIC_SPECS = [
    {"name": "Genesis King", "image": MYTHIC_IMAGE,
     "traits": {"Gender": "Male", "Skin": "Toxic Blue", "Eyes": "Flame", "Headwear": "Crown",
                "Mouth": "Gold Grillz", "Outfit": "Chain-only", "Background": "Legendary Glow", "Accessory": "Diamond Chain"}},
    {"name": "Toxic Queen", "image": IMG["att_female_blue_neon"],
     "traits": {"Gender": "Female", "Skin": "Toxic Blue", "Eyes": "Laser", "Headwear": "Flaming Halo",
                "Mouth": "Bubblegum", "Outfit": "Leather", "Background": "Legendary Glow", "Accessory": "Diamond Chain"}},
    {"name": "Diamond Warlord", "image": IMG["att_zombie_devil_epic"],
     "traits": {"Gender": "Male", "Skin": "Diamond", "Eyes": "Flame", "Headwear": "Devil Horns",
                "Mouth": "Gold Grillz", "Outfit": "Leather", "Background": "Legendary Glow", "Accessory": "Diamond Chain"}},
]


def _fallback_image(skin, tier, gender, rng):
    if skin == "Gold":
        return _fallback_asset_url("gold_crown_laser")
    if skin == "Diamond":
        return _fallback_asset_url("diamond_halo_flame")
    pool = list(SKIN_IMAGES[skin])
    if tier == "Epic" and skin in EPIC_IMAGES:
        pool = EPIC_IMAGES[skin] * 2 + pool
    if gender == "Female":
        fem = [k for k in pool if k in FEMALE_IMAGES]
        if fem:
            pool = fem
    else:
        male = [k for k in pool if k not in FEMALE_IMAGES]
        if male:
            pool = male
    return _fallback_asset_url(rng.choice(pool))


# ---------------------------------------------------------------------------
# Original trait scheme (locked to the founding spec)
# ---------------------------------------------------------------------------
COMMON_SKINS = ["Classic Green", "Toxic Blue", "Purple Haze", "Albino", "Zombie"]

HEADWEAR_COMMON = ["Beanie", "Snapback", "Bucket Hat", "Durag", "None"]
HEADWEAR_STAR = ["Crown", "Flaming Halo"]
HEADWEAR_EPIC_EXTRA = ["Devil Horns"]

EYES_COMMON = ["Mischief", "3D Glasses", "Stoned", "VR Visor"]
EYES_RARE = ["Cyclops"]
EYES_STAR = ["Laser", "Flame"]

MOUTHS = ["Grin", "Gold Grillz", "Toothpick", "Tongue Out", "Cigar", "Bubblegum"]

OUTFITS = ["Hoodie", "Bomber", "Tie-dye Tee", "Puffer", "Tracksuit", "Chain-only"]

ACC_COMMON = ["None", "Chain", "Earring"]
ACC_RARE = ["Diamond Chain", "Face Tattoo"]

BG_COMMON = ["Neon Split", "Acid Green", "Hot Pink", "Deep Purple", "Graffiti Wall"]
BG_STAR = ["Legendary Glow"]

ADJ = ["Neon", "Toxic", "Rowdy", "Grimey", "Feral", "Cyber", "Sludge", "Riot", "Vandal",
       "Static", "Hazard", "Reckless", "Savage", "Gutter", "Wired", "Rabid", "Glitch",
       "Blaze", "Venom", "Chrome", "Rogue", "Menace", "Vicious", "Frantic"]
NOUN = ["Biter", "Tagger", "Creep", "Goblin", "Menace", "Shredder", "Bandit", "Snitch",
        "Prowler", "Rascal", "Hooligan", "Scrapper", "Trickster", "Lurker", "Brawler",
        "Vandal", "Gremlin", "Wraith", "Punk", "Fiend"]

# ---- prompt phrase maps ----
SKIN_D = {"Classic Green": "classic bright green skin", "Toxic Blue": "glowing toxic blue skin",
          "Purple Haze": "purple haze skin", "Albino": "pale albino white skin with pink eyes",
          "Zombie": "rotting grey-green zombie skin with stitches", "Gold": "shiny metallic gold skin",
          "Diamond": "sparkling crystal diamond skin"}
EYES_D = {"Mischief": "big mischievous eyes", "3D Glasses": "pixel 3D glasses", "Stoned": "droopy red stoned eyes",
          "VR Visor": "a futuristic VR visor", "Visor": "a sleek cyber visor over the eyes",
          "Cyclops": "a single large cyclops eye", "Laser": "glowing red laser-beam eyes", "Flame": "burning fire flame eyes"}
HEAD_D = {"None": "no hat", "Beanie": "a knit beanie", "Snapback": "a backwards snapback cap", "Bucket Hat": "a bucket hat",
          "Durag": "a durag", "Headphones": "big DJ headphones", "Neon-green Hair": "spiky neon-green hair",
          "Cyber Ponytail": "a high cyber ponytail", "Pink Mohawk": "a bright pink mohawk", "Space-buns": "space-bun hair",
          "Devil Horns": "red devil horns", "Crown": "a golden jewel crown", "Flaming Halo": "a floating flaming halo"}
MOUTH_D = {"Grin": "a sharp toothy grin", "Gold Grillz": "gold grillz teeth", "Toothpick": "a toothpick in mouth",
           "Tongue Out": "tongue sticking out", "Cigar": "a smoking cigar", "Bubblegum": "blowing a bubblegum bubble"}
OUT_D = {"Hoodie": "a streetwear hoodie", "Bomber": "a bomber jacket", "Tie-dye Tee": "a tie-dye tee",
         "Puffer": "a puffer jacket", "Tracksuit": "a tracksuit", "Chain-only": "bare chest with chains",
         "Leather": "a leather jacket", "Denim": "a denim jacket"}
ACC_D = {"None": "", "Chain": "a silver chain", "Diamond Chain": "a diamond chain", "Iced Chain": "an iced-out chain",
         "Hoop": "hoop earrings", "Earring": "an earring", "Face Tattoo": "a small face tattoo", "Star Tattoo": "a star face tattoo"}
BG_D = {"Neon Split": "a neon split pink-and-cyan", "Acid Green": "a solid acid-green", "Hot Pink": "a solid hot-pink",
        "Deep Purple": "a solid deep-purple", "Graffiti Wall": "a graffiti brick-wall", "Legendary Glow": "a radiant legendary golden-glow"}


POSES = ["facing forward, straight-on", "with a slight side glance", "with head tilted, cocky",
         "looking up with attitude", "three-quarter view, smirking", "chin down, menacing stare",
         "leaning slightly to one side", "shoulders squared, confident"]


def build_prompt(t, name=None, seed=0):
    g = "female" if t["Gender"] == "Female" else "male"
    fem = " with a feminine face, long eyelashes and glossy lips," if t["Gender"] == "Female" else " with a rugged masculine face,"
    acc = ACC_D.get(t["Accessory"], "")
    acc_clause = f" and {acc}" if acc else ""
    pose = POSES[seed % len(POSES)]
    tag = f' The graffiti tag "{name}" is sprayed in the background.' if name else ""
    return (
        f"Bold graffiti street-art NFT PFP illustration of an original cartoon GREMLIN mascot (NOT an ape), "
        f"front bust portrait, pointy ears, {pose}. A {g} gremlin{fem} with {SKIN_D[t['Skin']]}, {EYES_D[t['Eyes']]}, "
        f"{HEAD_D[t['Headwear']]}, {MOUTH_D[t['Mouth']]}. Wearing {OUT_D[t['Outfit']]}{acc_clause}. "
        f"Background: {BG_D[t['Background']]} background covered in neon graffiti tags.{tag} "
        f"Thick heavy black outline comic style, neon spray-paint drip texture, high-contrast vivid neon colors, "
        f"centered, edgy underground streetwear vibe. Unique variation #{seed:03d}."
    )


def generate_collection():
    data_file = ROOT_DIR / "merged_collection.json"
    raw = _validate_collection(json.loads(data_file.read_text()))
    N = len(raw)
    items = []
    for c in raw:
        tid = c["token_id"]
        tier = c["tier"]
        traits = dict(c["traits"])
        # Every token gets its own render URL. Tokens without an uploaded render
        # are served as deterministic composites by /api/render/{token_id};
        # returning the shared fallback URL here caused visible duplicate art.
        image = _render_url(tid)
        if tier == "Mythic":
            traits["1 of 1"] = c["name"]
            desc = f"A 1-of-1 crown jewel of the HYPEBLOCK underground collective — the {c['name']}. Sold via auction."
        else:
            desc = f"One of {N} original Graffiti Gremlins from the HYPEBLOCK underground collective."
        items.append({
            "id": str(uuid.uuid4()),
            "token_id": tid,
            "name": c["name"],
            "title": f"HYPEBLOCK #{tid:03d}",
            "description": desc,
            "image": image,
            "tier": tier,
            "traits": traits,
            "price_pol": c["price_pol"],
            "batch": (tid - 1) // BATCH_SIZE + 1,
            "prompt": build_prompt(c["traits"], c["name"], tid),
        })

    scored = ["Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory", "Gender"]
    counts = {c: {} for c in scored}
    for it in items:
        for c in scored:
            v = it["traits"][c]
            counts[c][v] = counts[c].get(v, 0) + 1
    for it in items:
        it["rarity_score"] = round(sum(100.0 / counts[c][it["traits"][c]] for c in scored), 2)
    # Mythics are always the rarest by design
    base_max = max(x["rarity_score"] for x in items)
    for it in items:
        if it["tier"] == "Mythic":
            it["rarity_score"] = round(base_max + 100.0 + it["token_id"] * 0.01, 2)
    ranked = sorted(items, key=lambda x: x["rarity_score"], reverse=True)
    for rank, it in enumerate(ranked, start=1):
        it["rank"] = rank
    items.sort(key=lambda x: x["token_id"])
    return items, counts


def _price(tier, rng):
    if tier == "Common":
        return round(rng.uniform(8, 15), 1)
    if tier == "Rare":
        return round(rng.uniform(20, 40), 1)
    if tier == "Epic":
        return round(rng.uniform(60, 120), 1)
    return round(rng.uniform(200, 350), 1)


def batch_unlock(batch):
    return None


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class WaitlistCreate(BaseModel):
    email: EmailStr
    wallet: Optional[str] = None


# ---------------------------------------------------------------------------
# Startup seed
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def seed_collection():
    meta = await db.meta.find_one({"_id": "collection"})
    if not meta or meta.get("version") != COLLECTION_VERSION or await db.nfts.count_documents({}) != COLLECTION_SIZE:
        items, counts = generate_collection()
        await db.nfts.delete_many({})
        await db.nfts.insert_many([{**it} for it in items])
        await db.meta.replace_one({"_id": "trait_counts"}, {"_id": "trait_counts", "counts": counts}, upsert=True)
        await db.meta.replace_one({"_id": "collection"}, {"_id": "collection", "version": COLLECTION_VERSION}, upsert=True)
        logger.info("Reseeded HYPEBLOCK collection %s", COLLECTION_VERSION)
    logger.info("HYPEBLOCK collection ready (%s NFTs)", COLLECTION_SIZE)


def _released(batch):
    return True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@api_router.get("/")
async def root():
    return {"message": "HYPEBLOCK API online"}


@api_router.get("/stats")
async def stats():
    total = await db.nfts.count_documents({})
    tiers = {t: await db.nfts.count_documents({"tier": t}) for t in ["Common", "Rare", "Epic", "Legendary", "Mythic"]}
    return {
        "total_supply": total,
        "network": "Polygon",
        "standard": "ERC-721 (Single)",
        "tiers": tiers,
        "trait_categories": 8,
        "waitlist_count": await db.waitlist.count_documents({}),
        "released_count": total,
        "creator_wallet": "0x0d7704E370b21DB2Ae66CF6b599b71B819E1BA9c",
    }


@api_router.get("/batches")
async def batches():
    out = []
    total_batches = (COLLECTION_SIZE + BATCH_SIZE - 1) // BATCH_SIZE
    for b in range(1, total_batches + 1):
        out.append({
            "batch": b,
            "released": _released(b),
            "size": BATCH_SIZE,
            "range": [(b - 1) * BATCH_SIZE + 1, min(b * BATCH_SIZE, COLLECTION_SIZE)],
            "unlock_date": batch_unlock(b),
        })
    return {"batch_size": BATCH_SIZE, "released_batches": RELEASED_BATCHES, "batches": out}


@api_router.get("/traits")
async def traits():
    doc = await db.meta.find_one({"_id": "trait_counts"})
    return {"total": COLLECTION_SIZE, "counts": doc["counts"] if doc else {}}


class TraitLabIn(BaseModel):
    traits: dict


@api_router.post("/trait-lab/estimate")
async def trait_lab_estimate(payload: TraitLabIn):
    scored = ["Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory", "Gender"]
    doc = await db.meta.find_one({"_id": "trait_counts"})
    counts = doc["counts"] if doc else {}
    score = 0.0
    per = {}
    for c in scored:
        v = payload.traits.get(c)
        cnt = counts.get(c, {}).get(v, 0) if v else 0
        if v and cnt:
            score += 100.0 / cnt
            per[c] = round(cnt / COLLECTION_SIZE * 100, 1)
        else:
            per[c] = None
    score = round(score, 2)
    docs = await db.nfts.find({}, {"_id": 0, "rarity_score": 1}).to_list(1000)
    scores = [d["rarity_score"] for d in docs] or [0]
    rarer_than = sum(1 for s in scores if s < score)
    percentile = round(rarer_than / len(scores) * 100, 1)
    if percentile >= 97:
        tier = "Mythic"
    elif percentile >= 90:
        tier = "Legendary"
    elif percentile >= 77:
        tier = "Epic"
    elif percentile >= 52:
        tier = "Rare"
    else:
        tier = "Common"
    return {"score": score, "per_trait_pct": per, "percentile": percentile,
            "tier_guess": tier, "rank_estimate": max(1, len(scores) - rarer_than)}


def _decorate(doc):
    state = artwork.describe(doc)
    doc["artwork_state"] = state["artwork_state"]
    doc["image"] = f"{PUBLIC_BASE}{state['image']}"
    doc["released"] = _released(doc.get("batch", 1))
    doc["unlock_date"] = batch_unlock(doc.get("batch", 1))
    return doc


@api_router.get("/nfts")
async def list_nfts(
    tier: Optional[str] = None, gender: Optional[str] = None, skin: Optional[str] = None,
    eyes: Optional[str] = None, headwear: Optional[str] = None, mouth: Optional[str] = None,
    outfit: Optional[str] = None, background: Optional[str] = None, accessory: Optional[str] = None,
    availability: Optional[str] = None, search: Optional[str] = None,
    sort: str = "rank_asc", page: int = 1, limit: int = 24,
):
    q = {}
    if tier:
        q["tier"] = tier
    for field, val in [("Gender", gender), ("Skin", skin), ("Eyes", eyes), ("Headwear", headwear),
                       ("Mouth", mouth), ("Outfit", outfit), ("Background", background), ("Accessory", accessory)]:
        if val:
            q[f"traits.{field}"] = val
    if availability == "released":
        q["batch"] = {"$lte": RELEASED_BATCHES}
    elif availability == "upcoming":
        q["batch"] = {"$gt": RELEASED_BATCHES}
    if search:
        raw_search = search.strip()
        s = re.escape(raw_search)
        conds = [{"name": {"$regex": s, "$options": "i"}}, {"title": {"$regex": s, "$options": "i"}}]
        if raw_search.lstrip("#").isdigit():
            conds.append({"token_id": int(raw_search.lstrip("#"))})
        q["$or"] = conds

    sort_map = {"rank_asc": [("rank", 1)], "score_desc": [("rarity_score", -1)], "id_asc": [("token_id", 1)],
                "id_desc": [("token_id", -1)], "price_desc": [("price_pol", -1)], "price_asc": [("price_pol", 1)]}
    total = await db.nfts.count_documents(q)
    limit = max(1, min(limit, 200))
    skip = (max(1, page) - 1) * limit
    items = await db.nfts.find(q, {"_id": 0, "prompt": 0}).sort(sort_map.get(sort, [("rank", 1)])).skip(skip).limit(limit).to_list(limit)
    for it in items:
        _decorate(it)
    return {"total": total, "page": page, "limit": limit, "items": items}


@api_router.get("/nfts/{token_id}")
async def get_nft(token_id: int):
    doc = await db.nfts.find_one({"token_id": token_id}, {"_id": 0, "prompt": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Gremlin not found")
    trait_doc = await db.meta.find_one({"_id": "trait_counts"})
    counts = trait_doc["counts"] if trait_doc else {}
    doc["trait_rarity_pct"] = {cat: (round(counts.get(cat, {}).get(val, 0) / COLLECTION_SIZE * 100, 1) if counts.get(cat, {}).get(val) else None)
                               for cat, val in doc["traits"].items()}
    return _decorate(doc)


def _opensea_meta(doc):
    doc = _decorate(dict(doc))
    attrs = [{"trait_type": k, "value": v} for k, v in doc["traits"].items()]
    attrs.append({"trait_type": "Rarity", "value": doc["tier"]})
    attrs.append({"trait_type": "Rarity Rank", "value": doc["rank"]})
    return {
        "name": doc["title"],
        "description": doc["description"],
        "image": doc["image"],
        "external_url": f"{PUBLIC_BASE}/gremlin/{doc['token_id']}",
        "attributes": attrs,
    }


@api_router.get("/nfts/{token_id}/metadata")
async def nft_metadata(token_id: int):
    doc = await db.nfts.find_one({"token_id": token_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Gremlin not found")
    return _opensea_meta(doc)


@api_router.get("/metadata/export")
async def metadata_export():
    docs = await db.nfts.find({}, {"_id": 0}).sort("token_id", 1).to_list(1000)
    payload = [_opensea_meta(d) for d in docs]
    return JSONResponse(content=payload, headers={"Content-Disposition": "attachment; filename=hypeblock-metadata.json"})


GENERATED_DIR = ROOT_DIR / "generated"


@api_router.get("/assets/{asset_name}")
async def local_asset(asset_name: str):
    """Serve checked-in/downloaded fallback art from this hosting account."""
    safe_name = Path(asset_name).name
    if safe_name != asset_name or not safe_name.endswith(".jpeg"):
        raise HTTPException(status_code=404, detail="Asset not found")
    asset = FALLBACK_ASSETS_DIR / safe_name
    if not asset.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(str(asset), media_type="image/jpeg",
                        headers={"Cache-Control": "public, max-age=31536000, immutable"})


def _fallback_svg(token_id, record):
    """Build a unique, cacheable SVG composite for tokens without uploaded art.

    The existing fallback library remains the visual base, while deterministic
    token-specific overlays, crops, colors, and marks make each image distinct.
    This avoids pretending that several NFTs share one image and does not
    require storing hundreds of generated binary files in the repository.
    """
    traits = record["traits"]
    seed = (token_id * 2654435761) & 0xFFFFFFFF
    hue = seed % 360
    accent = f"#{(seed >> 8) & 0xFFFFFF:06x}"
    accent_two = f"#{(seed >> 3) & 0xFFFFFF:06x}"
    rotation = (seed % 9) - 4
    crop_x = 500 + (seed % 31) - 15
    crop_y = 500 + ((seed >> 5) % 31) - 15
    base_image = _fallback_image(traits["Skin"], record["tier"], traits["Gender"], random.Random(token_id))
    base_path = FALLBACK_ASSETS_DIR / Path(base_image).name
    if base_path.is_file():
        base_image = "data:image/jpeg;base64," + base64.b64encode(base_path.read_bytes()).decode("ascii")
    safe_base = escape(base_image, quote=True)
    safe_name = escape(record["name"], quote=True)
    safe_skin = escape(traits["Skin"], quote=True)
    safe_tier = escape(record["tier"], quote=True)
    safe_token = f"{token_id:03d}"

    # These marks are intentionally derived from the token ID, so every SVG
    # remains stable between restarts while still being visually different.
    mark_a = 80 + (seed % 760)
    mark_b = 110 + ((seed >> 7) % 680)
    mark_c = 120 + ((seed >> 13) % 700)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
      width="1000" height="1000" viewBox="0 0 1000 1000" role="img"
      aria-label="HYPEBLOCK #{safe_token} {safe_name}">
      <defs>
        <linearGradient id="wash" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="{accent}" stop-opacity=".42"/>
          <stop offset="1" stop-color="{accent_two}" stop-opacity=".18"/>
        </linearGradient>
        <filter id="neon">
          <feColorMatrix type="hueRotate" values="{hue}"/>
          <feComponentTransfer>
            <feFuncA type="linear" slope="1.04"/>
          </feComponentTransfer>
        </filter>
        <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"
          patternTransform="rotate({rotation})">
          <path d="M 48 0 L 0 0 0 48" fill="none" stroke="{accent}" stroke-opacity=".2" stroke-width="2"/>
        </pattern>
      </defs>
      <rect width="1000" height="1000" fill="#10131f"/>
      <g transform="translate({500 - crop_x} {500 - crop_y}) rotate({rotation} 500 500) scale({1.02 + (seed % 4) / 100})">
        <image x="0" y="0" width="1000" height="1000" preserveAspectRatio="xMidYMid slice"
          href="{safe_base}" xlink:href="{safe_base}" filter="url(#neon)"/>
      </g>
      <rect width="1000" height="1000" fill="url(#wash)" style="mix-blend-mode:screen"/>
      <rect width="1000" height="1000" fill="url(#grid)"/>
      <path d="M 0 {mark_a} L 250 {mark_b} L 470 {mark_a - 24} L 760 {mark_c} L 1000 {mark_b}"
        fill="none" stroke="{accent}" stroke-width="12" stroke-linecap="round" opacity=".76"/>
      <path d="M {mark_b} 0 L {mark_c} 220 L {mark_a} 520 L {mark_c} 1000"
        fill="none" stroke="{accent_two}" stroke-width="5" stroke-linecap="round" opacity=".82"/>
      <circle cx="{mark_c}" cy="{mark_a}" r="{18 + seed % 28}" fill="{accent}" opacity=".82"/>
      <circle cx="{mark_a}" cy="{mark_c}" r="{10 + (seed >> 4) % 20}" fill="{accent_two}" opacity=".9"/>
      <rect x="34" y="34" width="932" height="932" fill="none" stroke="{accent}" stroke-width="5" opacity=".72"/>
      <text x="58" y="910" fill="white" font-family="monospace" font-size="22" letter-spacing="4"
        opacity=".9">HYPEBLOCK / {safe_token} / {safe_tier.upper()}</text>
      <text x="58" y="944" fill="{accent}" font-family="monospace" font-size="15"
        letter-spacing="2" opacity=".92">{safe_skin.upper()} // CONCEPT PREVIEW</text>
    </svg>"""


@api_router.get("/wallpapers")
async def wallpapers(limit: int = 12):
    docs = await db.nfts.find({"image": {"$regex": "/api/render/"}}, {"_id": 0, "prompt": 0}).sort("rank", 1).to_list(1000)
    limit = max(1, min(limit, 60))
    items = [_decorate(d) for d in docs[:limit]]
    return {"count": len(items), "items": items}


@api_router.get("/wallpapers/pack")
async def wallpapers_pack(limit: int = 12):
    docs = await db.nfts.find({"image": {"$regex": "/api/render/"}}, {"_id": 0}).sort("rank", 1).to_list(1000)
    docs = docs[:max(1, min(limit, 60))]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for d in docs:
            tid = d["token_id"]
            safe = "".join(ch if ch.isalnum() else "_" for ch in d["name"])
            added = False
            for ext in ("png", "jpeg", "jpg", "webp"):
                p = GENERATED_DIR / f"{tid}.{ext}"
                if p.exists():
                    z.write(str(p), arcname=f"HYPEBLOCK_{tid:03d}_{safe}.{ext}")
                    added = True
                    break
            if not added:
                record = next(
                    (item for item in json.loads((ROOT_DIR / "merged_collection.json").read_text())
                     if item["token_id"] == tid),
                    None,
                )
                if record:
                    z.writestr(
                        f"HYPEBLOCK_{tid:03d}_{safe}.svg",
                        _fallback_svg(tid, record),
                    )
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition": "attachment; filename=hypeblock-wallpaper-pack.zip"})


@api_router.get("/render/{token_id}")
async def render_image(token_id: int):
    p = artwork.path(token_id)
    if p:
        return FileResponse(p, headers={"Cache-Control": "no-cache"})
    record = next(
        (item for item in json.loads((ROOT_DIR / "merged_collection.json").read_text())
         if item["token_id"] == token_id),
        None,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Gremlin not found")
    return Response(
        content=_fallback_svg(token_id, record),
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


@api_router.get("/render-status")
async def render_status():
    done = len(list(GENERATED_DIR.glob("*.png"))) if GENERATED_DIR.exists() else 0
    return {"generated": COLLECTION_SIZE, "uploaded": done, "total": COLLECTION_SIZE}


@api_router.post("/waitlist")
async def join_waitlist(payload: WaitlistCreate):
    email = payload.email.lower()
    if await db.waitlist.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="This email is already on the waitlist.")
    entry = {"id": str(uuid.uuid4()), "email": email, "wallet": payload.wallet,
             "created_at": datetime.now(timezone.utc).isoformat(), "contacted": False}
    await db.waitlist.insert_one({**entry})
    return {"ok": True, "count": await db.waitlist.count_documents({})}


@api_router.get("/waitlist/count")
async def waitlist_count():
    return {"count": await db.waitlist.count_documents({})}


def _check_admin(key: str):
    if not ADMIN_KEY or not secrets.compare_digest(key, ADMIN_KEY):
        raise HTTPException(status_code=401, detail="Invalid admin key")


@api_router.get("/admin/waitlist")
async def admin_waitlist(x_admin_key: str = Header(default="")):
    _check_admin(x_admin_key)
    entries = await db.waitlist.find({}, {"_id": 0}).sort("created_at", -1).to_list(5000)
    return {"count": len(entries), "entries": entries}


@api_router.post("/admin/waitlist/{entry_id}/contacted")
async def admin_mark_contacted(entry_id: str, x_admin_key: str = Header(default="")):
    _check_admin(x_admin_key)
    await db.waitlist.update_one({"id": entry_id}, {"$set": {"contacted": True}})
    return {"ok": True}


@api_router.delete("/admin/waitlist/{entry_id}")
async def admin_delete(entry_id: str, x_admin_key: str = Header(default="")):
    _check_admin(x_admin_key)
    await db.waitlist.delete_one({"id": entry_id})
    return {"ok": True}


api_router.include_router(artwork.router(_check_admin, _opensea_meta))
app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True,
                   allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
                   allow_methods=["*"], allow_headers=["*"])


@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close()

# Serve the production React build on the same origin as the API.
FRONTEND_BUILD = ROOT_DIR.parent / "frontend" / "build"

@app.get("/healthz")
async def healthcheck():
    return {"ok": True, "collection_size": await db.nfts.count_documents({})}

if FRONTEND_BUILD.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=FRONTEND_BUILD / "static"), name="static")

    @app.get("/{path:path}")
    async def frontend_page(path: str):
        if path == "api" or path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        candidate = (FRONTEND_BUILD / path).resolve()
        if candidate.is_relative_to(FRONTEND_BUILD.resolve()) and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_BUILD / "index.html")
