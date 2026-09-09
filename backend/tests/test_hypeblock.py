import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL") or open("/app/frontend/.env").read().split("REACT_APP_BACKEND_URL=")[1].split()[0]
BASE_URL = BASE_URL.rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_KEY = "hypeblock2026"


@pytest.fixture(scope="session")
def s():
    return requests.Session()


# -------- Stats --------
def test_stats(s):
    r = s.get(f"{API}/stats", timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["total_supply"] == 200
    assert d["tiers"] == {"Common": 120, "Rare": 50, "Epic": 24, "Legendary": 6}


# -------- NFTs listing / filters / search / sort --------
def test_list_default(s):
    r = s.get(f"{API}/nfts", timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["total"] == 200
    assert len(d["items"]) == 24
    # rank_asc default
    ranks = [it["rank"] for it in d["items"]]
    assert ranks == sorted(ranks)


def test_filter_legendary(s):
    r = s.get(f"{API}/nfts?tier=Legendary&limit=50", timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["total"] == 6
    assert len(d["items"]) == 6
    assert all(it["tier"] == "Legendary" for it in d["items"])


def test_filter_trait_skin_gold(s):
    # Gold skin exists only on Legendary
    r = s.get(f"{API}/nfts?skin=Gold&limit=50", timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["total"] >= 1
    assert all(it["traits"]["Skin"] == "Gold" for it in d["items"])


def test_search_by_hash(s):
    r = s.get(f"{API}/nfts?search=%237", timeout=15)
    assert r.status_code == 200
    d = r.json()
    ids = [it["token_id"] for it in d["items"]]
    assert 7 in ids


def test_search_by_name(s):
    # get token 1's name and search partial
    one = s.get(f"{API}/nfts/1").json()
    part = one["name"].split()[0]
    r = s.get(f"{API}/nfts?search={part}", timeout=15)
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_sort_id_asc(s):
    r = s.get(f"{API}/nfts?sort=id_asc&limit=10", timeout=15).json()
    ids = [it["token_id"] for it in r["items"]]
    assert ids == sorted(ids)
    assert ids[0] == 1


def test_sort_price_desc(s):
    r = s.get(f"{API}/nfts?sort=price_desc&limit=10", timeout=15).json()
    prices = [it["price_pol"] for it in r["items"]]
    assert prices == sorted(prices, reverse=True)


# -------- NFT detail --------
def test_get_nft_detail(s):
    r = s.get(f"{API}/nfts/7", timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["token_id"] == 7
    assert "traits" in d and len(d["traits"]) == 8
    assert "rarity_score" in d
    assert "rank" in d
    assert "trait_rarity_pct" in d
    assert all(isinstance(v, (int, float)) for v in d["trait_rarity_pct"].values())


def test_get_nft_invalid(s):
    r = s.get(f"{API}/nfts/9999", timeout=15)
    assert r.status_code == 404


# -------- Traits --------
def test_traits(s):
    r = s.get(f"{API}/traits", timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["total"] == 200
    for cat in ["Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory", "Gender"]:
        assert cat in d["counts"]


# -------- Waitlist --------
@pytest.fixture(scope="session")
def waitlist_email():
    return f"test_{uuid.uuid4().hex[:8]}@hypeblock.io"


def test_waitlist_join_new(s, waitlist_email):
    before = s.get(f"{API}/waitlist/count").json()["count"]
    r = s.post(f"{API}/waitlist", json={"email": waitlist_email, "wallet": "0xabc"})
    assert r.status_code == 200
    assert r.json()["ok"] is True
    after = s.get(f"{API}/waitlist/count").json()["count"]
    assert after == before + 1


def test_waitlist_duplicate(s, waitlist_email):
    r = s.post(f"{API}/waitlist", json={"email": waitlist_email})
    assert r.status_code == 409


# -------- Admin --------
def test_admin_wrong_key(s):
    r = s.get(f"{API}/admin/waitlist?key=wrong")
    assert r.status_code == 401


def test_admin_flow(s, waitlist_email):
    r = s.get(f"{API}/admin/waitlist?key={ADMIN_KEY}")
    assert r.status_code == 200
    entries = r.json()["entries"]
    entry = next((e for e in entries if e["email"] == waitlist_email), None)
    assert entry is not None
    eid = entry["id"]

    # mark contacted
    r2 = s.post(f"{API}/admin/waitlist/{eid}/contacted?key={ADMIN_KEY}")
    assert r2.status_code == 200
    r3 = s.get(f"{API}/admin/waitlist?key={ADMIN_KEY}").json()
    found = next(e for e in r3["entries"] if e["id"] == eid)
    assert found["contacted"] is True

    # delete
    r4 = s.delete(f"{API}/admin/waitlist/{eid}?key={ADMIN_KEY}")
    assert r4.status_code == 200
    r5 = s.get(f"{API}/admin/waitlist?key={ADMIN_KEY}").json()
    assert not any(e["id"] == eid for e in r5["entries"])
