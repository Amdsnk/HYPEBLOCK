import json
from server import generate_collection

items, counts = generate_collection()
prompts = {str(it["token_id"]): it["prompt"] for it in items}
meta = {str(it["token_id"]): {"tier": it["tier"], "traits": it["traits"]} for it in items}
with open("prompts.json", "w") as f:
    json.dump(prompts, f, indent=0)
with open("token_meta.json", "w") as f:
    json.dump(meta, f)
print("wrote", len(prompts), "prompts")
