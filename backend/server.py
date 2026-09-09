from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import random
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'hypeblock2026')

app = FastAPI(title="HYPEBLOCK API")
api_router = APIRouter(prefix="/api")

# ---------------------------------------------------------------------------
# Collection generation
# ---------------------------------------------------------------------------
IMG = {
    "green_beanie": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/de2465864aefac69c38f99e0c8719e2c190ef17a3f67c4052e2afd8cfee6866e.jpeg",
    "green_vr": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/9e0a66744be295415aa6405906e62b17c158e914ecac15719294c850415975c7.jpeg",
    "green_stoned": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/4cbcd58bfba0340398d83766663b321392f8c91a78c9b2ad6addde7236b12262.jpeg",
    "green_cyclops_cigar": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/c0383b50853ac1d0128ecde8dc93d0df7ae6688c94e00ccce9931406e179830b.jpeg",
    "female_green_crown": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/80d124b96fec73e24fac3e1b192188b6f1447334d92bc4eb9af420bfbbf5095c.jpeg",
    "blue_snapback": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/eba46a9c8b42de7aa35e707632c16c9bbeee67600e024647b6cd87f3accda2ee.jpeg",
    "blue_bucket": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/4779c283c1acf937ba259a421bc2e610ffd768023a2f76d512d1ce4ee868ba40.jpeg",
    "blue_chainonly": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/17a6e7e45c79e5721f653b676bd02b01412fd5d45ffca29cf85fa5905e2060a7.jpeg",
    "female_blue_vr": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/c6fba6e3262f7065e3faedbd84ba884662c1c62aceed702a3b8f8085839f9e34.jpeg",
    "purple_3dglasses": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/9a3dde413f050a445b47183db65f185872d944049d4766e057278b8f8a8e06dc.jpeg",
    "purple_cyclops": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/ac7110d4f63e2596b5b1412f02d0caee588a66fb1fdd5beac8a77c5dffd8513d.jpeg",
    "albino_durag": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/5fe48fd67e7758fde61b4834f97099484d02ebb901854eb66afb3406fb0dba2d.jpeg",
    "albino_devil": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/56b0a8cbaaa51c779020a90e99287128bf57d14e0af3716d58fa1dbd5786f415.jpeg",
    "zombie_horns": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/33416a50f597391530af4fbaa7f1eb4929202a1a972ddf8728f82ba367a18ad5.jpeg",
    "zombie_bomber": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/8dbe4bf1712316e93dfdc4c9bd0044341abba18cfa02c2b955fa66bfaba3f807.jpeg",
    "blue_laser_epic": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/d5c889cef616dc06679224636dd84a04bd4a755a24d68636395278ac448efbb2.jpeg",
    "purple_flame_epic": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/8d5c5cbef44f7f6fba7a052a741576f4a51a726a33a242bda4366050ac14885f.jpeg",
    "zombie_laser_epic": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/8649abd12c1f9cd3a93b658ac81826576854ca8b4f8c52b7b5214db824c63ff2.jpeg",
    "gold_crown_laser": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/1457c54c9767fd5fa4931d94ad1dab717471e6ff27432c366e32ad90d47e6e98.jpeg",
    "diamond_halo_flame": "https://static.prod-images.emergentagent.com/jobs/5805fef9-3e3d-44d7-9d0a-cc7916d51f1d/images/4c34eab44cdba05869cb9177ed7e1db6287a3c5845f62755902b80d3c6a1d4a8.jpeg",
}
FEMALE_IMAGES = {"female_green_crown", "female_blue_vr"}
SKIN_IMAGES = {
    "Classic Green": ["green_beanie", "green_vr", "green_stoned", "green_cyclops_cigar", "female_green_crown"],
    "Toxic Blue": ["blue_snapback", "blue_bucket", "blue_chainonly", "female_blue_vr"],
    "Purple Haze": ["purple_3dglasses", "purple_cyclops"],
    "Albino": ["albino_durag", "albino_devil"],
    "Zombie": ["zombie_horns", "zombie_bomber"],
}
EPIC_IMAGES = {
    "Toxic Blue": ["blue_laser_epic"],
    "Purple Haze": ["purple_flame_epic"],
    "Zombie": ["zombie_laser_epic"],
}

COMMON_SKINS = ["Classic Green", "Toxic Blue", "Purple Haze", "Albino", "Zombie"]
COMMON_EYES = ["Mischief", "3D Glasses", "Stoned", "VR Visor"]
STAR_EYES = ["Laser", "Flame"]
COMMON_HEADWEAR = ["Beanie", "Snapback", "Bucket Hat", "Durag", "None"]
STAR_HEADWEAR = ["Crown", "Flaming Halo"]
MOUTHS = ["Grin", "Gold Grillz", "Toothpick", "Tongue Out", "Cigar", "Bubblegum"]
OUTFITS = ["Hoodie", "Bomber", "Tie-dye Tee", "Puffer", "Tracksuit", "Chain-only"]
COMMON_BG = ["Neon Split", "Acid Green", "Hot Pink", "Deep Purple", "Graffiti Wall"]
COMMON_ACC = ["None", "Chain", "Earring"]
RARE_ACC = ["Diamond Chain", "Face Tattoo"]

ADJ = ["Neon", "Toxic", "Rowdy", "Grimey", "Feral", "Cyber", "Sludge", "Riot", "Vandal",
       "Static", "Hazard", "Reckless", "Savage", "Gutter", "Wired", "Rabid", "Glitch",
       "Blaze", "Venom", "Chrome", "Rogue", "Menace", "Vicious", "Frantic"]
NOUN = ["Biter", "Tagger", "Creep", "Goblin", "Menace", "Shredder", "Bandit", "Snitch",
        "Prowler", "Rascal", "Hooligan", "Scrapper", "Trickster", "Lurker", "Brawler",
        "Vandal", "Gremlin", "Wraith", "Punk", "Fiend"]


def _pick_image(skin, tier, gender, rng):
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


def _price(tier, rng):
    if tier == "Common":
        return round(rng.uniform(8, 15), 1)
    if tier == "Rare":
        return round(rng.uniform(20, 40), 1)
    if tier == "Epic":
        return round(rng.uniform(60, 120), 1)
    return round(rng.uniform(200, 350), 1)


def generate_collection():
    rng = random.Random(42)
    tiers = ["Common"] * 120 + ["Rare"] * 50 + ["Epic"] * 24 + ["Legendary"] * 6
    # keep legendary spread but deterministic: shuffle then sort back by id later
    order = list(range(200))
    rng.shuffle(order)
    tier_map = {}
    for slot, idx in enumerate(order):
        tier_map[idx] = tiers[slot]

    items = []
    for i in range(200):
        token_id = i + 1
        tier = tier_map[i]
        # gender ~ 28% female
        gender = "Female" if rng.random() < 0.28 else "Male"

        if tier == "Legendary":
            leg_i = sum(1 for j in range(i) if tier_map[j] == "Legendary")
            skin = "Gold" if leg_i % 2 == 0 else "Diamond"
            eyes = "Laser" if skin == "Gold" else "Flame"
            headwear = "Crown" if skin == "Gold" else "Flaming Halo"
            mouth = "Gold Grillz"
            outfit = rng.choice(["Bomber", "Puffer", "Chain-only"])
            background = "Legendary Glow"
            accessory = "Diamond Chain"
            gender = "Male"
        elif tier == "Epic":
            skin = rng.choice(COMMON_SKINS)
            # epic = one starred non-skin trait
            if rng.random() < 0.6:
                eyes = rng.choice(STAR_EYES)
                headwear = rng.choice(COMMON_HEADWEAR + ["Devil Horns"])
            else:
                eyes = rng.choice(COMMON_EYES + ["Cyclops"])
                headwear = rng.choice(STAR_HEADWEAR)
            mouth = rng.choice(MOUTHS)
            outfit = rng.choice(OUTFITS)
            background = rng.choice(COMMON_BG)
            accessory = rng.choice(RARE_ACC + ["Diamond Chain"])
        elif tier == "Rare":
            skin = rng.choice(COMMON_SKINS)
            eyes = rng.choice(COMMON_EYES + ["Cyclops"])
            headwear = rng.choice(COMMON_HEADWEAR + ["Devil Horns"])
            mouth = rng.choice(MOUTHS)
            outfit = rng.choice(OUTFITS)
            background = rng.choice(COMMON_BG)
            accessory = rng.choice(RARE_ACC + ["Chain"])
        else:  # Common
            skin = rng.choice(COMMON_SKINS)
            eyes = rng.choice(COMMON_EYES)
            headwear = rng.choice(COMMON_HEADWEAR)
            mouth = rng.choice(MOUTHS)
            outfit = rng.choice(OUTFITS)
            background = rng.choice(COMMON_BG)
            accessory = rng.choice(COMMON_ACC)

        traits = {
            "Gender": gender,
            "Skin": skin,
            "Eyes": eyes,
            "Headwear": headwear,
            "Mouth": mouth,
            "Outfit": outfit,
            "Background": background,
            "Accessory": accessory,
        }
        name = f"{rng.choice(ADJ)} {rng.choice(NOUN)}"
        image = _pick_image(skin, tier, gender, rng)
        items.append({
            "id": str(uuid.uuid4()),
            "token_id": token_id,
            "name": name,
            "title": f"HYPEBLOCK #{token_id:03d}",
            "description": "One of 200 Graffiti Gremlins from the HYPEBLOCK underground collective.",
            "image": image,
            "tier": tier,
            "traits": traits,
            "price_pol": _price(tier, rng),
        })

    # rarity score based on trait frequency
    scored_cats = ["Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory", "Gender"]
    counts = {c: {} for c in scored_cats}
    for it in items:
        for c in scored_cats:
            v = it["traits"][c]
            counts[c][v] = counts[c].get(v, 0) + 1
    for it in items:
        score = 0.0
        for c in scored_cats:
            v = it["traits"][c]
            score += 200.0 / counts[c][v]
        it["rarity_score"] = round(score, 2)

    ranked = sorted(items, key=lambda x: x["rarity_score"], reverse=True)
    for rank, it in enumerate(ranked, start=1):
        it["rank"] = rank
    items.sort(key=lambda x: x["token_id"])
    return items, counts


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class WaitlistCreate(BaseModel):
    email: EmailStr
    wallet: Optional[str] = None


class WaitlistEntry(BaseModel):
    id: str
    email: str
    wallet: Optional[str] = None
    created_at: str
    contacted: bool = False


# ---------------------------------------------------------------------------
# Startup seeding
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def seed_collection():
    existing = await db.nfts.count_documents({})
    if existing != 200:
        items, counts = generate_collection()
        await db.nfts.delete_many({})
        await db.nfts.insert_many([{**it} for it in items])
        await db.meta.replace_one({"_id": "trait_counts"}, {"_id": "trait_counts", "counts": counts}, upsert=True)
    logger.info("HYPEBLOCK collection ready (200 NFTs)")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@api_router.get("/")
async def root():
    return {"message": "HYPEBLOCK API online"}


@api_router.get("/stats")
async def stats():
    total = await db.nfts.count_documents({})
    tiers = {}
    for t in ["Common", "Rare", "Epic", "Legendary"]:
        tiers[t] = await db.nfts.count_documents({"tier": t})
    wl = await db.waitlist.count_documents({})
    return {
        "total_supply": total,
        "network": "Polygon",
        "standard": "ERC-721 (Single)",
        "tiers": tiers,
        "trait_categories": 8,
        "waitlist_count": wl,
        "creator_wallet": "0x0d7704E370b21DB2Ae66CF6b599b71B819E1BA9c",
    }


@api_router.get("/traits")
async def traits():
    doc = await db.meta.find_one({"_id": "trait_counts"})
    return {"total": 200, "counts": doc["counts"] if doc else {}}


@api_router.get("/nfts")
async def list_nfts(
    tier: Optional[str] = None,
    gender: Optional[str] = None,
    skin: Optional[str] = None,
    eyes: Optional[str] = None,
    headwear: Optional[str] = None,
    mouth: Optional[str] = None,
    outfit: Optional[str] = None,
    background: Optional[str] = None,
    accessory: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "rank_asc",
    page: int = 1,
    limit: int = 24,
):
    q = {}
    if tier:
        q["tier"] = tier
    for field, val in [("Gender", gender), ("Skin", skin), ("Eyes", eyes), ("Headwear", headwear),
                       ("Mouth", mouth), ("Outfit", outfit), ("Background", background), ("Accessory", accessory)]:
        if val:
            q[f"traits.{field}"] = val
    if search:
        s = search.strip()
        conds = [{"name": {"$regex": s, "$options": "i"}}, {"title": {"$regex": s, "$options": "i"}}]
        if s.lstrip("#").isdigit():
            conds.append({"token_id": int(s.lstrip("#"))})
        q["$or"] = conds

    sort_map = {
        "rank_asc": [("rank", 1)],
        "score_desc": [("rarity_score", -1)],
        "id_asc": [("token_id", 1)],
        "id_desc": [("token_id", -1)],
        "price_desc": [("price_pol", -1)],
        "price_asc": [("price_pol", 1)],
    }
    sort_spec = sort_map.get(sort, [("rank", 1)])
    total = await db.nfts.count_documents(q)
    limit = max(1, min(limit, 200))
    skip = (max(1, page) - 1) * limit
    cursor = db.nfts.find(q, {"_id": 0}).sort(sort_spec).skip(skip).limit(limit)
    items = await cursor.to_list(limit)
    return {"total": total, "page": page, "limit": limit, "items": items}


@api_router.get("/nfts/{token_id}")
async def get_nft(token_id: int):
    doc = await db.nfts.find_one({"token_id": token_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Gremlin not found")
    trait_doc = await db.meta.find_one({"_id": "trait_counts"})
    counts = trait_doc["counts"] if trait_doc else {}
    rarity = {}
    for cat, val in doc["traits"].items():
        c = counts.get(cat, {}).get(val)
        rarity[cat] = round(c / 200 * 100, 1) if c else None
    doc["trait_rarity_pct"] = rarity
    return doc


@api_router.post("/waitlist")
async def join_waitlist(payload: WaitlistCreate):
    email = payload.email.lower()
    existing = await db.waitlist.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email sudah terdaftar di waitlist.")
    entry = {
        "id": str(uuid.uuid4()),
        "email": email,
        "wallet": payload.wallet,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "contacted": False,
    }
    await db.waitlist.insert_one({**entry})
    count = await db.waitlist.count_documents({})
    return {"ok": True, "count": count}


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

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
