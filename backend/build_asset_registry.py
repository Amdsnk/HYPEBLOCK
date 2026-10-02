"""Build canonical artwork registry for HYPEBLOCK Genesis.

Creates backend/asset_registry.json from merged_collection.json + generated art.
The registry makes artwork state explicit and prevents placeholder renders from
being mistaken for mint-ready canonical assets.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
COLLECTION=ROOT/"merged_collection.json"
GENERATED=ROOT/"generated"
OUT=ROOT/"asset_registry.json"
EXTS=("png","jpg","jpeg","webp")

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def main():
    items=json.loads(COLLECTION.read_text(encoding="utf-8"))
    hashes={}
    registry=[]
    for item in items:
        tid=item["token_id"]
        matches=[]
        for ext in EXTS:
            p=GENERATED/f"{tid}.{ext}"
            if p.exists(): matches.append(p)
        if len(matches)>1:
            raise RuntimeError(f"Token {tid} has multiple artwork files: {matches}")
        if matches:
            p=matches[0]; sha=digest(p)
            if sha in hashes:
                raise RuntimeError(f"Exact duplicate artwork: token {tid} and {hashes[sha]}")
            hashes[sha]=tid
            state="candidate"
            artwork=f"generated/{p.name}"
        else:
            sha=None; state="placeholder"; artwork=None
        registry.append({
            "token_id":tid,
            "name":item["name"],
            "tier":item["tier"],
            "artwork_state":state,
            "artwork_path":artwork,
            "sha256":sha,
            "render_endpoint":f"/api/render/{tid}",
            "metadata_endpoint":f"/api/nfts/{tid}/metadata"
        })
    OUT.write_text(json.dumps(registry,indent=2),encoding="utf-8")
    canonical=sum(x["artwork_state"]=="canonical" for x in registry)
    print(f"Registry: {len(registry)} tokens; {canonical} canonical; {len(registry)-canonical} placeholders")

if __name__=="__main__": main()
