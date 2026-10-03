import io
import json
import zipfile
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from PIL import Image

from backend.artwork import ArtworkManager
from backend.server import _JsonDatabase


@pytest.fixture
def studio(tmp_path, monkeypatch):
    monkeypatch.setenv("HYPEBLOCK_ARTWORK_DIR", str(tmp_path / "art"))
    db = _JsonDatabase(tmp_path / "store.json")
    db.state["nfts"] = [{"token_id": i, "name": f"Character {i}", "tier": "Rare", "traits": {"Skin": "Blue"}} for i in (1, 2)]
    manager = ArtworkManager(db, tmp_path)
    app = FastAPI()
    def check(key):
        if key != "test-key":
            raise HTTPException(401)
    app.include_router(manager.router(check, lambda doc: {"name": doc["name"], "attributes": []}), prefix="/api")
    with TestClient(app) as client:
        yield client, manager, db


def image_bytes(color):
    output = io.BytesIO()
    Image.new("RGB", (256, 256), color).save(output, format="PNG")
    return output.getvalue()


HEADERS = {"X-Admin-Key": "test-key"}
CID = "Qm" + "a" * 44


def test_approval_gates_export_and_survives_restart(studio):
    client, manager, db = studio
    assert client.get("/api/admin/artwork").status_code == 401
    payload = {"token_ids": [1], "image_folder_cid": CID}
    assert client.post("/api/admin/release/export", json=payload, headers=HEADERS).status_code == 409
    uploaded = client.put("/api/admin/artwork/1", content=image_bytes("blue"), headers=HEADERS).json()
    assert uploaded["artwork_state"] == "candidate"
    review = {"sha256": uploaded["sha256"], "approved": True}
    assert client.post("/api/admin/artwork/1/review", json=review, headers=HEADERS).status_code == 422
    review.update(traits_match=True, original_artwork=True, art_direction_checked=True)
    assert client.post("/api/admin/artwork/1/review", json=review, headers=HEADERS).json()["artwork_state"] == "canonical"
    restarted = ArtworkManager(_JsonDatabase(db.path), manager.root)
    assert restarted.describe(db.state["nfts"][0])["artwork_state"] == "canonical"
    images = client.post("/api/admin/release/images", json={"token_ids": [1]}, headers=HEADERS)
    assert images.status_code == 200
    with zipfile.ZipFile(io.BytesIO(images.content)) as archive:
        assert archive.read("images/1.png") == image_bytes("blue")
    result = client.post("/api/admin/release/export", json=payload, headers=HEADERS)
    assert result.status_code == 200
    with zipfile.ZipFile(io.BytesIO(result.content)) as archive:
        meta = json.loads(archive.read("metadata/1.json"))
        assert meta["image"] == f"ipfs://{CID}/1.png"
        assert archive.read("images/1.png") == image_bytes("blue")
        assert json.loads(archive.read("manifest.json"))[0]["sha256"] == uploaded["sha256"]
    changed = client.put("/api/admin/artwork/1", content=image_bytes("green"), headers=HEADERS)
    assert changed.json()["artwork_state"] == "candidate"
    assert client.post("/api/admin/artwork/1/review", json=review, headers=HEADERS).status_code == 409
    assert client.post("/api/admin/release/export", json=payload, headers=HEADERS).status_code == 409


def test_duplicate_and_invalid_uploads_rejected(studio):
    client, _, _ = studio
    assert client.put("/api/admin/artwork/1", content=b"invalid", headers=HEADERS).status_code == 422
    assert client.put("/api/admin/artwork/999", content=image_bytes("blue"), headers=HEADERS).status_code == 404
    assert client.put("/api/admin/artwork/1", content=image_bytes("blue"), headers=HEADERS).status_code == 200
    assert client.put("/api/admin/artwork/2", content=image_bytes("blue"), headers=HEADERS).status_code == 409
    assert client.post("/api/admin/release/export", json={"token_ids": [1], "image_folder_cid": "https://wrong"}, headers=HEADERS).status_code == 422
