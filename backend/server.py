from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import logging
import random
from pathlib import Path
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'hypeblock2026')
RELEASED_BATCHES = int(os.environ.get('RELEASED_BATCHES', '3'))
BATCH_SIZE = 20
LAUNCH_DATE = datetime(2026, 6, 16, tzinfo=timezone.utc)
COLLECTION_VERSION = "v5"

app = FastAPI(title="HYPEBLOCK API")
api_router = APIRouter(prefix="/api")

# ---------------------------------------------------------------------------
# Fallback image library (used until a per-token render exists)
# ---------------------------------------------------------------------------
BASE = "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/"
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
        return IMG["gold_crown_laser"]
    if skin == "Diamond":
        return IMG["diamond_halo_flame"]
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
    return IMG[rng.choice(pool)]


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
    rng = random.Random(77)
    # 200 total = 3 Mythic (1-of-1) + 5 Legendary + 24 Epic + 50 Rare + 118 Common
    tiers = ["Common"] * 118 + ["Rare"] * 50 + ["Epic"] * 24 + ["Legendary"] * 5 + ["Mythic"] * 3
    order = list(range(200))
    rng.shuffle(order)
    tier_map = {idx: tiers[slot] for slot, idx in enumerate(order)}

    items = []
    leg_count = 0
    mythic_count = 0
    for i in range(200):
        token_id = i + 1
        tier = tier_map[i]

        if tier == "Mythic":
            spec = MYTHIC_SPECS[mythic_count % len(MYTHIC_SPECS)]
            mythic_count += 1
            traits = {**spec["traits"], "1 of 1": spec["name"]}
            batch = (token_id - 1) // BATCH_SIZE + 1
            items.append({
                "id": str(uuid.uuid4()),
                "token_id": token_id,
                "name": spec["name"],
                "title": f"HYPEBLOCK #{token_id:03d}",
                "description": f"A 1-of-1 crown jewel of the HYPEBLOCK underground collective — the {spec['name']}. Sold via auction.",
                "image": spec["image"],
                "tier": tier,
                "traits": traits,
                "price_pol": 0,  # 0 == auction / 1-of-1
                "batch": batch,
                "prompt": build_prompt(spec["traits"], spec["name"], token_id),
            })
            continue

        gender = "Female" if rng.random() < 0.45 else "Male"

        if tier == "Legendary":
            skin = "Gold" if leg_count % 2 == 0 else "Diamond"
            leg_count += 1
            eyes = "Laser" if skin == "Gold" else "Flame"
            headwear = "Crown" if skin == "Gold" else "Flaming Halo"
            mouth = "Gold Grillz"
            outfit = rng.choice(["Bomber", "Puffer", "Chain-only"])
            background = "Legendary Glow"
            accessory = "Diamond Chain"
        elif tier == "Epic":
            skin = rng.choice(COMMON_SKINS)
            if rng.random() < 0.6:
                eyes = rng.choice(EYES_STAR)
                headwear = rng.choice(HEADWEAR_COMMON + HEADWEAR_EPIC_EXTRA)
            else:
                eyes = rng.choice(EYES_COMMON + EYES_RARE)
                headwear = rng.choice(HEADWEAR_STAR + HEADWEAR_EPIC_EXTRA)
            mouth = rng.choice(MOUTHS)
            outfit = rng.choice(OUTFITS)
            background = rng.choice(BG_COMMON)
            accessory = rng.choice(["Diamond Chain", "Face Tattoo"])
        elif tier == "Rare":
            skin = rng.choice(COMMON_SKINS)
            eyes = rng.choice(EYES_COMMON + EYES_RARE)
            headwear = rng.choice(HEADWEAR_COMMON + HEADWEAR_EPIC_EXTRA)
            mouth = rng.choice(MOUTHS)
            outfit = rng.choice(OUTFITS)
            background = rng.choice(BG_COMMON)
            accessory = rng.choice(ACC_RARE + ["Chain"])
        else:  # Common
            skin = rng.choice(COMMON_SKINS)
            eyes = rng.choice(EYES_COMMON)
            headwear = rng.choice(HEADWEAR_COMMON)
            mouth = rng.choice(MOUTHS)
            outfit = rng.choice(OUTFITS)
            background = rng.choice(BG_COMMON)
            accessory = rng.choice(ACC_COMMON)

        traits = {"Gender": gender, "Skin": skin, "Eyes": eyes, "Headwear": headwear,
                  "Mouth": mouth, "Outfit": outfit, "Background": background, "Accessory": accessory}
        batch = (token_id - 1) // BATCH_SIZE + 1
        gremlin_name = f"{rng.choice(ADJ)} {rng.choice(NOUN)}"
        items.append({
            "id": str(uuid.uuid4()),
            "token_id": token_id,
            "name": gremlin_name,
            "title": f"HYPEBLOCK #{token_id:03d}",
            "description": "One of 200 Graffiti Gremlins from the HYPEBLOCK underground collective.",
            "image": _fallback_image(skin, tier, gender, rng),
            "tier": tier,
            "traits": traits,
            "price_pol": _price(tier, rng),
            "batch": batch,
            "prompt": build_prompt(traits, gremlin_name, token_id),
        })

    scored = ["Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory", "Gender"]
    counts = {c: {} for c in scored}
    for it in items:
        for c in scored:
            v = it["traits"][c]
            counts[c][v] = counts[c].get(v, 0) + 1
    for it in items:
        it["rarity_score"] = round(sum(200.0 / counts[c][it["traits"][c]] for c in scored), 2)
    # The 1-of-1 Mythic is always the #1 rarest by design
    for it in items:
        if it["tier"] == "Mythic":
            it["rarity_score"] = round(max(x["rarity_score"] for x in items) + 100.0, 2)
    ranked = sorted(items, key=lambda x: x["rarity_score"], reverse=True)
    for rank, it in enumerate(ranked, start=1):
        it["rank"] = rank
    items.sort(key=lambda x: x["token_id"])

    # overlay per-token renders if available
    img_file = ROOT_DIR / "gremlin_images.json"
    if img_file.exists():
        mapping = json.loads(img_file.read_text())
        for it in items:
            url = mapping.get(str(it["token_id"]))
            if url:
                it["image"] = url
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
    # Released batches are already live (no countdown). Upcoming batches unlock weekly.
    if batch <= RELEASED_BATCHES:
        return None
    weeks = batch - RELEASED_BATCHES
    return (datetime.now(timezone.utc) + timedelta(days=7 * weeks - 4)).isoformat()


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
    if not meta or meta.get("version") != COLLECTION_VERSION or await db.nfts.count_documents({}) != 200:
        items, counts = generate_collection()
        await db.nfts.delete_many({})
        await db.nfts.insert_many([{**it} for it in items])
        await db.meta.replace_one({"_id": "trait_counts"}, {"_id": "trait_counts", "counts": counts}, upsert=True)
        await db.meta.replace_one({"_id": "collection"}, {"_id": "collection", "version": COLLECTION_VERSION}, upsert=True)
        logger.info("Reseeded HYPEBLOCK collection %s", COLLECTION_VERSION)
    logger.info("HYPEBLOCK collection ready (200 NFTs)")


def _released(batch):
    return batch <= RELEASED_BATCHES


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
        "released_count": await db.nfts.count_documents({"batch": {"$lte": RELEASED_BATCHES}}),
        "creator_wallet": "0x0d7704E370b21DB2Ae66CF6b599b71B819E1BA9c",
    }


@api_router.get("/batches")
async def batches():
    out = []
    total_batches = (200 + BATCH_SIZE - 1) // BATCH_SIZE
    for b in range(1, total_batches + 1):
        out.append({
            "batch": b,
            "released": _released(b),
            "size": BATCH_SIZE,
            "range": [(b - 1) * BATCH_SIZE + 1, min(b * BATCH_SIZE, 200)],
            "unlock_date": batch_unlock(b),
        })
    return {"batch_size": BATCH_SIZE, "released_batches": RELEASED_BATCHES, "batches": out}


@api_router.get("/traits")
async def traits():
    doc = await db.meta.find_one({"_id": "trait_counts"})
    return {"total": 200, "counts": doc["counts"] if doc else {}}


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
            score += 200.0 / cnt
            per[c] = round(cnt / 200 * 100, 1)
        else:
            per[c] = None
    score = round(score, 2)
    docs = await db.nfts.find({}, {"_id": 0, "rarity_score": 1}).to_list(1000)
    scores = [d["rarity_score"] for d in docs] or [0]
    rarer_than = sum(1 for s in scores if s < score)
    percentile = round(rarer_than / len(scores) * 100, 1)
    if percentile >= 98.5:
        tier = "Mythic"
    elif percentile >= 96:
        tier = "Legendary"
    elif percentile >= 84:
        tier = "Epic"
    elif percentile >= 59:
        tier = "Rare"
    else:
        tier = "Common"
    return {"score": score, "per_trait_pct": per, "percentile": percentile,
            "tier_guess": tier, "rank_estimate": max(1, len(scores) - rarer_than)}


def _decorate(doc):
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
        s = search.strip()
        conds = [{"name": {"$regex": s, "$options": "i"}}, {"title": {"$regex": s, "$options": "i"}}]
        if s.lstrip("#").isdigit():
            conds.append({"token_id": int(s.lstrip("#"))})
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
    doc["trait_rarity_pct"] = {cat: (round(counts.get(cat, {}).get(val, 0) / 200 * 100, 1) if counts.get(cat, {}).get(val) else None)
                               for cat, val in doc["traits"].items()}
    return _decorate(doc)


def _opensea_meta(doc):
    attrs = [{"trait_type": k, "value": v} for k, v in doc["traits"].items()]
    attrs.append({"trait_type": "Rarity", "value": doc["tier"]})
    attrs.append({"trait_type": "Rarity Rank", "value": doc["rank"]})
    return {
        "name": doc["title"],
        "description": doc["description"],
        "image": doc["image"],
        "external_url": f"https://hypeblock.xyz/gremlin/{doc['token_id']}",
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
    docs = await db.nfts.find({}, {"_id": 0}).sort("token_id", 1).to_list(200)
    payload = [_opensea_meta(d) for d in docs]
    return JSONResponse(content=payload, headers={"Content-Disposition": "attachment; filename=hypeblock-metadata.json"})


GENERATED_DIR = ROOT_DIR / "generated"


@api_router.get("/render/{token_id}")
async def render_image(token_id: int):
    for ext in ("png", "jpeg", "jpg", "webp"):
        p = GENERATED_DIR / f"{token_id}.{ext}"
        if p.exists():
            return FileResponse(str(p), media_type=f"image/{'jpeg' if ext in ('jpg','jpeg') else ext}")
    raise HTTPException(status_code=404, detail="Render not available yet")


@api_router.get("/render-status")
async def render_status():
    done = len(list(GENERATED_DIR.glob("*.png"))) if GENERATED_DIR.exists() else 0
    return {"generated": done, "total": 200}


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
    if key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")


@api_router.get("/admin/waitlist")
async def admin_waitlist(key: str = Query(...)):
    _check_admin(key)
    entries = await db.waitlist.find({}, {"_id": 0}).sort("created_at", -1).to_list(5000)
    return {"count": len(entries), "entries": entries}


@api_router.post("/admin/waitlist/{entry_id}/contacted")
async def admin_mark_contacted(entry_id: str, key: str = Query(...)):
    _check_admin(key)
    await db.waitlist.update_one({"id": entry_id}, {"$set": {"contacted": True}})
    return {"ok": True}


@api_router.delete("/admin/waitlist/{entry_id}")
async def admin_delete(entry_id: str, key: str = Query(...)):
    _check_admin(key)
    await db.waitlist.delete_one({"id": entry_id})
    return {"ok": True}


app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True,
                   allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
                   allow_methods=["*"], allow_headers=["*"])


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
