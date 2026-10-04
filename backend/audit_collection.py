"""HYPEBLOCK collection integrity audit.

Read-only utility: detects duplicate token identities, duplicate trait combinations,
multiple art files for a token, exact binary duplicates, and tokens still relying
on placeholder rendering.
"""
from __future__ import annotations
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
COLLECTION = ROOT / "merged_collection.json"
GENERATED = ROOT / "generated"
TRAITS = ("Gender", "Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory")
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def duplicates(values):
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def main() -> int:
    items = json.loads(COLLECTION.read_text(encoding="utf-8"))
    ids = [item.get("token_id") for item in items]
    names = [item.get("name") for item in items]
    signatures = [tuple(item.get("traits", {}).get(key) for key in TRAITS) for item in items]

    art = defaultdict(list)
    hashes = defaultdict(list)
    invalid_images = []
    if GENERATED.exists():
        for path in sorted(GENERATED.iterdir()):
            if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
                continue
            try:
                token_id = int(path.stem)
            except ValueError:
                continue
            art[token_id].append(path.name)
            hashes[sha256(path)].append(path.name)
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    if min(image.size) < 512:
                        raise ValueError("Image dimensions below 512 pixels")
            except Exception as exc:
                invalid_images.append({"file": path.name, "error": str(exc)})

    report = {
        "collection_size": len(items),
        "unique_token_ids": len(set(ids)),
        "unique_names": len(set(names)),
        "unique_trait_combinations": len(set(signatures)),
        "binary_art_tokens": len(art),
        "web_render_coverage": len(items),
        "duplicate_token_ids": duplicates(ids),
        "duplicate_names": duplicates(names),
        "duplicate_trait_combinations": len(signatures) - len(set(signatures)),
        "tokens_with_multiple_binary_files": {str(k): v for k, v in art.items() if len(v) > 1},
        "exact_duplicate_art_groups": [v for v in hashes.values() if len(v) > 1],
        "invalid_images": invalid_images,
        "missing_binary_token_ids": [token_id for token_id in ids if token_id not in art],
        "note": "Missing binary tokens are placeholders rendered by /api/render/{token_id}; replace them with canonical final artwork before minting."
    }
    print(json.dumps(report, indent=2))
    invalid = any((
        report["duplicate_token_ids"], report["duplicate_names"],
        report["duplicate_trait_combinations"], report["tokens_with_multiple_binary_files"],
        report["exact_duplicate_art_groups"], report["invalid_images"],
    ))
    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
