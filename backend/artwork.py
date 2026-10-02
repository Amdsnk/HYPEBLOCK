"""Artwork review and immutable release export, stored on the host volume."""
import hashlib
import io
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field


class ArtworkReview(BaseModel):
    sha256: str
    approved: bool
    traits_match: bool = False
    original_artwork: bool = False


class ReleaseSelection(BaseModel):
    token_ids: list[int] = Field(min_length=1, max_length=296)


class ReleaseRequest(ReleaseSelection):
    image_folder_cid: str


class ArtworkManager:
    def __init__(self, db, root):
        self.db = db
        self.root = root
        report_path = root / "collection_audit.json"
        self.audit = json.loads(report_path.read_text()) if report_path.is_file() else {}
        self.uploads = Path(os.environ.get("HYPEBLOCK_ARTWORK_DIR", root / "data" / "artwork"))

    def overrides(self):
        return next((m.get("items", {}) for m in self.db.state["meta"] if m.get("_id") == "artwork_review"), {})

    def path(self, token_id):
        override = self.overrides().get(str(token_id), {})
        if override.get("filename"):
            name = override["filename"]
            if Path(name).name == name:
                p = self.uploads / name
                if p.is_file():
                    return p
        for ext in ("png", "jpg", "jpeg", "webp"):
            p = self.root / "generated" / f"{token_id}.{ext}"
            if p.is_file():
                return p
        return None

    def describe(self, doc):
        p = self.path(doc["token_id"])
        sha = hashlib.sha256(p.read_bytes()).hexdigest() if p else None
        review = self.overrides().get(str(doc["token_id"]), {})
        approved = bool(sha and review.get("approved_sha256") == sha)
        issues = [x["issue"] for x in self.audit.get("manual_flags", []) if x["token_id"] == doc["token_id"]]
        issues += [f"Similar composition to token(s) {pair['tokens']}; compare before approval." for pair in self.audit.get("similarity_flags", []) if doc["token_id"] in pair["tokens"]]
        return {"review_notes": issues, "token_id": doc["token_id"], "name": doc["name"], "tier": doc["tier"],
                "traits": doc["traits"], "artwork_state": "canonical" if approved else "candidate" if p else "placeholder",
                "sha256": sha, "approved_at": review.get("approved_at") if approved else None,
                "image": f"/api/render/{doc['token_id']}" + (f"?v={sha[:12]}" if sha else "?v=concept-2")}

    async def save(self, token_id, values):
        async with self.db.lock:
            review = next((m for m in self.db.state["meta"] if m.get("_id") == "artwork_review"), None)
            if review is None:
                review = {"_id": "artwork_review", "items": {}}
                self.db.state["meta"].append(review)
            review["items"][str(token_id)] = values
            await self.db.save()

    async def token(self, token_id):
        doc = await self.db.nfts.find_one({"token_id": token_id}, {"_id": 0})
        if not doc:
            raise HTTPException(404, "Token not found")
        return doc

    def router(self, check_admin, metadata):
        router = APIRouter()

        @router.get("/collection/readiness")
        async def readiness():
            docs = await self.db.nfts.find({}, {"_id": 0}).to_list(1000)
            items = [self.describe(doc) for doc in docs]
            counts = {state: sum(x["artwork_state"] == state for x in items) for state in ("canonical", "candidate", "placeholder")}
            return {"total": len(items), "artwork": counts, "artwork_ready": bool(items) and counts["canonical"] == len(items),
                    "mint_live": False, "note": "Artwork approval is separate from a deployed contract or marketplace listing."}

        @router.get("/admin/artwork")
        async def inventory(x_admin_key: str = Header(default="")):
            check_admin(x_admin_key)
            docs = await self.db.nfts.find({}, {"_id": 0}).sort("token_id", 1).to_list(1000)
            return {"items": [self.describe(d) for d in docs]}

        @router.put("/admin/artwork/{token_id}")
        async def upload(token_id: int, request: Request, x_admin_key: str = Header(default="")):
            check_admin(x_admin_key)
            doc = await self.token(token_id)
            data = bytearray()
            async for chunk in request.stream():
                data.extend(chunk)
                if len(data) > 8 * 1024 * 1024:
                    raise HTTPException(413, "Maximum artwork size is 8 MB")
            try:
                with Image.open(io.BytesIO(data)) as img:
                    fmt = img.format
                    if fmt not in ("PNG", "JPEG", "WEBP") or min(img.size) < 256 or max(img.size) > 8192:
                        raise HTTPException(422, "Use PNG, JPEG or WebP, 256–8192 pixels per side")
                    if getattr(img, "is_animated", False):
                        raise HTTPException(422, "Upload a still image")
                    img.verify()
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
                raise HTTPException(422, "Invalid image")
            sha = hashlib.sha256(data).hexdigest()
            docs = await self.db.nfts.find({}, {"_id": 0}).to_list(1000)
            for other in docs:
                if other["token_id"] != token_id and self.describe(other)["sha256"] == sha:
                    raise HTTPException(409, f"Exact duplicate artwork of token {other['token_id']}")
            ext = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}[fmt]
            name = f"{sha}.{ext}"
            self.uploads.mkdir(parents=True, exist_ok=True)
            path = self.uploads / name
            temp = path.with_suffix(".tmp")
            temp.write_bytes(data)
            temp.replace(path)
            await self.save(token_id, {"filename": name, "uploaded_at": datetime.now(timezone.utc).isoformat()})
            return self.describe(doc)

        @router.post("/admin/artwork/{token_id}/review")
        async def review(token_id: int, payload: ArtworkReview, x_admin_key: str = Header(default="")):
            check_admin(x_admin_key)
            doc = await self.token(token_id)
            current = self.describe(doc)
            if not current["sha256"] or current["sha256"] != payload.sha256:
                raise HTTPException(409, "Artwork changed or missing; refresh before reviewing")
            if payload.approved and not (payload.traits_match and payload.original_artwork):
                raise HTTPException(422, "Confirm original artwork and agreement with all traits")
            values = dict(self.overrides().get(str(token_id), {}))
            values.update(approved_sha256=payload.sha256 if payload.approved else None,
                          approved_at=datetime.now(timezone.utc).isoformat() if payload.approved else None)
            await self.save(token_id, values)
            return self.describe(doc)

        @router.post("/admin/release/export")
        async def export(payload: ReleaseRequest, x_admin_key: str = Header(default="")):
            check_admin(x_admin_key)
            cid = payload.image_folder_cid.strip()
            if not re.fullmatch(r"(?:Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-z2-7]{20,100})", cid):
                raise HTTPException(422, "Enter an IPFS folder CID, without ipfs:// or a URL")
            if len(set(payload.token_ids)) != len(payload.token_ids):
                raise HTTPException(422, "Duplicate token IDs")
            selected = []
            for token_id in sorted(payload.token_ids):
                doc = await self.token(token_id)
                item = self.describe(doc)
                if item["artwork_state"] != "canonical":
                    raise HTTPException(409, f"Token {token_id} still needs final artwork approval")
                selected.append((doc, item, self.path(token_id)))
            if len({item["sha256"] for _, item, _ in selected}) != len(selected):
                raise HTTPException(409, "Duplicate artwork in release")
            buf = io.BytesIO()
            manifest = []
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for doc, item, p in selected:
                    filename = f"{doc['token_id']}{p.suffix.lower()}"
                    meta = metadata(doc)
                    meta["image"] = f"ipfs://{cid}/{filename}"
                    z.write(p, f"images/{filename}")
                    z.writestr(f"metadata/{doc['token_id']}.json", json.dumps(meta, indent=2))
                    manifest.append({**item, "image": meta["image"], "metadata_sha256": hashlib.sha256(json.dumps(meta, indent=2).encode()).hexdigest()})
                z.writestr("manifest.json", json.dumps(manifest, indent=2))
                z.writestr("README.txt", "Upload the images folder to IPFS and verify its CID matches the CID used here. If it differs, export again with the actual CID. Then pin the metadata folder. This archive does not deploy a contract or mint NFTs.\n")
            buf.seek(0)
            return StreamingResponse(buf, media_type="application/zip", headers={"Content-Disposition": 'attachment; filename="hypeblock-release.zip"'})

        @router.post("/admin/release/images")
        async def release_images(payload: ReleaseSelection, x_admin_key: str = Header(default="")):
            check_admin(x_admin_key)
            if len(set(payload.token_ids)) != len(payload.token_ids):
                raise HTTPException(422, "Duplicate token IDs")
            selected = []
            for token_id in sorted(payload.token_ids):
                doc = await self.token(token_id)
                item = self.describe(doc)
                if item["artwork_state"] != "canonical":
                    raise HTTPException(409, f"Token {token_id} still needs final artwork approval")
                selected.append((item, self.path(token_id)))
            if len({item["sha256"] for item, _ in selected}) != len(selected):
                raise HTTPException(409, "Duplicate artwork in release")
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for item, p in selected:
                    z.write(p, f"images/{item['token_id']}{p.suffix.lower()}")
                z.writestr("manifest.json", json.dumps([item for item, _ in selected], indent=2))
            buf.seek(0)
            return StreamingResponse(buf, media_type="application/zip", headers={"Content-Disposition": 'attachment; filename="hypeblock-approved-images.zip"'})

        @router.get("/admin/artwork/{token_id}/download")
        async def download(token_id: int, x_admin_key: str = Header(default="")):
            check_admin(x_admin_key)
            await self.token(token_id)
            p = self.path(token_id)
            if not p:
                raise HTTPException(404, "No artwork file")
            return FileResponse(p, filename=f"{token_id}{p.suffix}")

        return router
