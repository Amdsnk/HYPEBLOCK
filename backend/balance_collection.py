"""Balance Genesis using only tokens without an artwork file.

Existing rendered identities, token IDs, names, tiers and other traits stay fixed.
The explicit creator direction is 148 male and 148 female Genesis characters.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRAITS = ('Gender', 'Skin', 'Eyes', 'Headwear', 'Mouth', 'Outfit', 'Background', 'Accessory')
MALE_TARGETS = {'Common': 84, 'Rare': 37, 'Epic': 18, 'Legendary': 6, 'Mythic': 3}

def balance(items, artwork_ids):
    result = json.loads(json.dumps(items))
    signature = lambda item: tuple(item['traits'][key] for key in TRAITS)
    used = {signature(item) for item in result}
    changes = []
    for tier, target in MALE_TARGETS.items():
        needed = sum(item['tier'] == tier and item['traits']['Gender'] == 'Male' for item in result) - target
        if needed < 0:
            raise ValueError('Unexpected tier distribution; existing artwork must not be relabeled')
        candidates = [item for item in result if item['tier'] == tier and item['traits']['Gender'] == 'Male' and item['token_id'] not in artwork_ids]
        candidates.sort(key=lambda item: hashlib.sha256(f"hypeblock-balance:{item['token_id']}".encode()).hexdigest())
        for item in candidates:
            if not needed:
                break
            old = signature(item)
            female = ('Female',) + old[1:]
            if female in used:
                continue
            used.remove(old)
            used.add(female)
            item['traits']['Gender'] = 'Female'
            changes.append({'token_id': item['token_id'], 'name': item['name'], 'tier': tier, 'from': 'Male', 'to': 'Female', 'reason': 'Unrendered concept slot assigned to female character for equal Genesis quantities'})
            needed -= 1
        if needed:
            raise ValueError(f'Not enough unrendered unique slots in {tier}')
    counts = Counter(item['traits']['Gender'] for item in result)
    if counts != {'Male': 148, 'Female': 148}:
        raise ValueError(f'Unbalanced Genesis: {counts}')
    return result, changes

def main():
    path = ROOT / 'merged_collection.json'
    items = json.loads(path.read_text())
    artwork_ids = {int(path.stem) for path in (ROOT / 'generated').iterdir() if path.stem.isdigit() and path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')}
    balanced, changes = balance(items, artwork_ids)
    path.write_text(json.dumps(balanced, indent=1) + '\n')
    if changes:
        (ROOT / 'gender_balance.json').write_text(json.dumps({'total': 296, 'male': 148, 'female': 148, 'changed_unrendered_tokens': changes}, indent=2) + '\n')
    print(json.dumps({'Male': 148, 'Female': 148, 'changed': len(changes)}))

if __name__ == '__main__':
    main()
