"""One-time builder: merge 96 uploaded NFTs + 200 procedural NFTs => 296, random token order.
- Uploaded art: backend/generated/{orig}.jpeg  (real art)
- Procedural art: backend/_procedural_art/{orig}.png  (35 restored real renders)
- Remaining procedural: fallback library image (resolved in server at seed time)
Outputs merged_collection.json and rearranges generated/ files to {new_token_id}.ext
"""
import json
import random
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
GEN = ROOT / "generated"
PROC_ART = ROOT / "_procedural_art"
UP_BACKUP = ROOT / "_uploaded_art"

ADJ = ["Neon", "Toxic", "Rowdy", "Grimey", "Feral", "Cyber", "Sludge", "Riot", "Vandal",
       "Static", "Hazard", "Reckless", "Savage", "Gutter", "Wired", "Rabid", "Glitch",
       "Blaze", "Venom", "Chrome", "Rogue", "Menace", "Vicious", "Frantic"]
NOUN = ["Biter", "Tagger", "Creep", "Goblin", "Menace", "Shredder", "Bandit", "Snitch",
        "Prowler", "Rascal", "Hooligan", "Scrapper", "Trickster", "Lurker", "Brawler",
        "Vandal", "Gremlin", "Wraith", "Punk", "Fiend", "Imp", "Rat", "Outlaw", "Hustler"]

PRICE = {"Common": 15, "Rare": 40, "Epic": 80, "Legendary": 200, "Mythic": 0}

rng = random.Random(4207)

# Keep the merge step deterministic and make it impossible for two records to
# receive the same metadata combination. Values are collected from both source
# datasets below as well, so this list is only a fallback for a new source
# trait that has not appeared in either dataset yet.
TRAIT_ORDER = ["Gender", "Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory"]
TRAIT_FALLBACKS = {
    "Gender": ["Male", "Female"],
    "Skin": ["Classic Green", "Toxic Blue", "Purple Haze", "Albino", "Zombie", "Gold", "Diamond"],
    "Eyes": ["Mischief", "3D Glasses", "Stoned", "VR Visor", "Neon Gaze", "Laser", "Flame", "Visor"],
    "Headwear": ["Beanie", "Snapback", "Bucket Hat", "Durag", "Devil Horns", "None", "Crown", "Flaming Halo"],
    "Mouth": ["Grin", "Gold Grillz", "Toothpick", "Tongue Out", "Cigar", "Bubblegum"],
    "Outfit": ["Hoodie", "Bomber", "Tie-dye Tee", "Puffer", "Tracksuit", "Chain-only", "Leather", "Denim"],
    "Background": ["Neon Split", "Acid Green", "Hot Pink", "Deep Purple", "Graffiti Wall", "Legendary Glow"],
    "Accessory": ["None", "Chain", "Diamond Chain", "Earring", "Face Tattoo", "Iced Chain", "Hoop", "Star Tattoo"],
}


def _trait_signature(traits):
    return tuple(traits.get(category) for category in TRAIT_ORDER)


def _make_unique_traits(records):
    """Repair duplicate trait combinations without dropping collection items.

    Token IDs and names remain stable. When a source record collides with an
    earlier record, change the least significant trait that yields a signature
    not already in use. This keeps the collection size intact while ensuring
    each metadata record represents a distinct gremlin.
    """
    observed = {category: set(values) for category, values in TRAIT_FALLBACKS.items()}
    for record in records:
        for category in TRAIT_ORDER:
            if record["traits"].get(category) is not None:
                observed[category].add(record["traits"][category])

    used = set()
    repaired = []
    for record in records:
        traits = dict(record["traits"])
        signature = _trait_signature(traits)
        if signature in used:
            repaired_signature = None
            # Prefer changing a cosmetic/low-impact attribute before changing
            # the gremlin's skin or gender.
            for category in ["Mouth", "Accessory", "Outfit", "Background", "Headwear", "Eyes", "Skin", "Gender"]:
                current = traits.get(category)
                candidates = sorted(observed[category] - {current})
                for candidate in candidates:
                    candidate_traits = dict(traits)
                    candidate_traits[category] = candidate
                    candidate_signature = _trait_signature(candidate_traits)
                    if candidate_signature not in used:
                        traits = candidate_traits
                        repaired_signature = candidate_signature
                        break
                if repaired_signature is not None:
                    break
            if repaired_signature is None:
                raise ValueError(f"Unable to make unique traits for {record['name']}")
            signature = repaired_signature
        used.add(signature)
        repaired.append({**record, "traits": traits})
    return repaired


def _validate_records(records):
    token_ids = [record["token_id"] for record in records]
    names = [record["name"] for record in records]
    signatures = [_trait_signature(record["traits"]) for record in records]
    checks = [
        ("token IDs", token_ids),
        ("names", names),
        ("trait combinations", signatures),
    ]
    for label, values in checks:
        if len(values) != len(set(values)):
            raise ValueError(f"Duplicate {label} found while building the collection")


def unique_name(used):
    for _ in range(500):
        n = f"{rng.choice(ADJ)} {rng.choice(NOUN)}"
        if n not in used:
            used.add(n)
            return n
    n = f"{rng.choice(ADJ)} {rng.choice(NOUN)} {rng.randint(1, 999)}"
    used.add(n)
    return n


def main():
    uploaded = json.loads((ROOT / "collection_data.json").read_text())
    procedural = json.loads((ROOT / "token_meta.json").read_text())

    # back up the uploaded art (currently generated/*.jpeg) before we rearrange
    if not UP_BACKUP.exists():
        UP_BACKUP.mkdir()
        for f in GEN.glob("*.jpeg"):
            shutil.copy(f, UP_BACKUP / f.name)

    used_names = set()
    records = []  # each: {name, tier, price, traits, src_kind, src_path_or_none}

    # --- 96 uploaded (real art) ---
    for c in uploaded:
        used_names.add(c["name"])
    for c in uploaded:
        src = UP_BACKUP / f"{c['token_id']}.jpeg"
        records.append({
            "name": c["name"], "tier": c["tier"], "price_pol": c["price_pol"],
            "traits": dict(c["traits"]),
            "art_src": str(src) if src.exists() else None,
            "art_ext": "jpeg" if src.exists() else None,
        })

    # --- 200 procedural ---
    for tid, meta in procedural.items():
        png = PROC_ART / f"{tid}.png"
        has = png.exists() and png.stat().st_size > 1000
        records.append({
            "name": unique_name(used_names), "tier": meta["tier"],
            "price_pol": PRICE[meta["tier"]], "traits": dict(meta["traits"]),
            "art_src": str(png) if has else None,
            "art_ext": "png" if has else None,
        })

    records = _make_unique_traits(records)
    assert len(records) == 296, len(records)
    rng.shuffle(records)

    # rebuild generated/ with renamed real-art files
    for f in GEN.glob("*"):
        f.unlink()

    out = []
    real = 0
    for i, r in enumerate(records, start=1):
        has_render = False
        if r["art_src"]:
            dst = GEN / f"{i}.{r['art_ext']}"
            shutil.copy(r["art_src"], dst)
            has_render = True
            real += 1
        out.append({
            "token_id": i, "name": r["name"], "tier": r["tier"],
            "price_pol": r["price_pol"], "traits": r["traits"],
            "has_render": has_render,
        })

    _validate_records(out)
    (ROOT / "merged_collection.json").write_text(json.dumps(out, indent=1))
    tiers = {}
    for o in out:
        tiers[o["tier"]] = tiers.get(o["tier"], 0) + 1
    print(f"Wrote merged_collection.json: {len(out)} items, {real} with real art")
    print("Tier distribution:", tiers)


if __name__ == "__main__":
    main()
