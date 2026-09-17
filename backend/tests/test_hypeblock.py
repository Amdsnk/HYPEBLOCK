import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL") or open("/app/frontend/.env").read().split("REACT_APP_BACKEND_URL=")[1].split()[0]
BASE_URL = BASE_URL.rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_KEY = "hypeblock2026"

TOTAL = 296
EXPECTED_TIERS = {"Common": 170, "Rare": 74, "Epic": 37, "Legendary": 12, "Mythic": 3}


@pytest.fixture(scope="session")
def s():
    return requests.Session()


# -------- Stats --------
def test_stats(s):
    r = s.get(f"{API}/stats", timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["total_supply"] == TOTAL
    assert d["tiers"] == EXPECTED_TIERS


# -------- NFT listing / pagination / images --------
def test_list_default(s):
    r = s.get(f"{API}/nfts", timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["total"] == TOTAL
    ranks = [it["rank"] for it in d["items"]]
    assert ranks == sorted(ranks)


def test_pagination_up_to_200(s):
    p1 = s.get(f"{API}/nfts?limit=200&page=1", timeout=20).json()
    p2 = s.get(f"{API}/nfts?limit=200&page=2", timeout=20).json()
    assert len(p1["items"]) == 200
    assert len(p2["items"]) == 96
    ids = set(i["token_id"] for i in p1["items"]) | set(i["token_id"] for i in p2["items"])
    assert len(ids) == TOTAL
    assert min(ids) == 1 and max(ids) == TOTAL


def test_all_items_have_image_url(s):
    d = s.get(f"{API}/nfts?limit=200&page=1", timeout=20).json()
    for it in d["items"]:
        img = it.get("image") or ""
        assert img, f"empty image for token {it['token_id']}"
        assert img.startswith("http") or "/api/render/" in img


def test_all_image_urls_are_unique(s):
    urls = []
    for page in (1, 2):
        d = s.get(f"{API}/nfts?limit=200&page={page}", timeout=20).json()
        urls.extend(item["image"] for item in d["items"])
    assert len(urls) == TOTAL
    assert len(set(urls)) == TOTAL


# -------- Filters --------
def test_filter_mythic_returns_three(s):
    r = s.get(f"{API}/nfts?tier=Mythic&limit=50", timeout=15).json()
    assert r["total"] == 3
    assert len(r["items"]) == 3
    assert all(it["tier"] == "Mythic" for it in r["items"])


def test_filter_trait_subset(s):
    # Filter by gender; must return only items with that gender
    r = s.get(f"{API}/nfts?gender=Male&limit=200", timeout=15).json()
    assert r["total"] > 0
    assert all(it["traits"].get("Gender") == "Male" for it in r["items"])


# -------- Sorting --------
def test_sort_id_asc(s):
    r = s.get(f"{API}/nfts?sort=id_asc&limit=10", timeout=15).json()
    ids = [it["token_id"] for it in r["items"]]
    assert ids == sorted(ids)
    assert ids[0] == 1


def test_sort_id_desc(s):
    r = s.get(f"{API}/nfts?sort=id_desc&limit=10", timeout=15).json()
    ids = [it["token_id"] for it in r["items"]]
    assert ids == sorted(ids, reverse=True)
    assert ids[0] == TOTAL


def test_sort_price_desc(s):
    r = s.get(f"{API}/nfts?sort=price_desc&limit=10", timeout=15).json()
    prices = [it["price_pol"] for it in r["items"]]
    assert prices == sorted(prices, reverse=True)


def test_sort_price_asc(s):
    r = s.get(f"{API}/nfts?sort=price_asc&limit=10", timeout=15).json()
    prices = [it["price_pol"] for it in r["items"]]
    assert prices == sorted(prices)


def test_sort_score_desc(s):
    r = s.get(f"{API}/nfts?sort=score_desc&limit=10", timeout=15).json()
    scores = [it["rarity_score"] for it in r["items"]]
    assert scores == sorted(scores, reverse=True)


def test_search_by_hash(s):
    r = s.get(f"{API}/nfts?search=%237", timeout=15).json()
    ids = [it["token_id"] for it in r["items"]]
    assert 7 in ids


def test_search_by_name(s):
    one = s.get(f"{API}/nfts/1").json()
    part = one["name"].split()[0]
    r = s.get(f"{API}/nfts?search={part}", timeout=15).json()
    assert r["total"] >= 1


# -------- NFT detail --------
def test_get_nft_1(s):
    d = s.get(f"{API}/nfts/1", timeout=15).json()
    assert d["token_id"] == 1
    assert "trait_rarity_pct" in d and d["trait_rarity_pct"]


def test_get_nft_296(s):
    d = s.get(f"{API}/nfts/{TOTAL}", timeout=15).json()
    assert d["token_id"] == TOTAL
    assert "trait_rarity_pct" in d


def test_get_nft_invalid(s):
    r = s.get(f"{API}/nfts/9999", timeout=15)
    assert r.status_code == 404


# -------- Render --------
def test_render_real_art_ok(s):
    # find a token whose image points to /api/render/
    d = s.get(f"{API}/nfts?limit=200&page=1", timeout=20).json()
    real = next(i for i in d["items"] if "/api/render/" in i["image"])
    r = s.get(f"{API}/render/{real['token_id']}", timeout=20)
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("image/")


def test_render_composite_fallback_ok(s):
    # Tokens without uploaded art now receive a unique SVG composite.
    for page in (1, 2):
        d = s.get(f"{API}/nfts?limit=200&page={page}", timeout=20).json()
        fb = next((i for i in d["items"] if i["token_id"] in {1, 3, 8, 9}), None)
        if fb:
            r = s.get(f"{API}/render/{fb['token_id']}", timeout=15)
            assert r.status_code == 200
            assert r.headers.get("content-type", "").startswith("image/svg+xml")
            return
    pytest.fail("no fallback-render token found")


# -------- Traits --------
def test_traits_sum(s):
    d = s.get(f"{API}/traits", timeout=15).json()
    assert d["total"] == TOTAL
    for cat in ["Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory", "Gender"]:
        assert cat in d["counts"]
        assert sum(d["counts"][cat].values()) == TOTAL


# -------- Trait lab --------
def test_trait_lab_estimate(s):
    payload = {"traits": {
        "Skin": "Gold", "Eyes": "Laser", "Headwear": "Crown",
        "Mouth": "Grin", "Outfit": "Hoodie", "Background": "Alley",
        "Accessory": "Chain", "Gender": "Male"
    }}
    r = s.post(f"{API}/trait-lab/estimate", json=payload, timeout=15)
    assert r.status_code == 200
    d = r.json()
    for k in ["score", "per_trait_pct", "percentile", "tier_guess", "rank_estimate"]:
        assert k in d


# -------- Metadata export --------
def test_metadata_export(s):
    d = s.get(f"{API}/metadata/export", timeout=30).json()
    assert isinstance(d, list) and len(d) == TOTAL
    for item in d[:5]:
        for k in ("name", "description", "image", "attributes"):
            assert k in item
        assert isinstance(item["attributes"], list)


# -------- Waitlist --------
@pytest.fixture(scope="session")
def waitlist_email():
    return f"test_{uuid.uuid4().hex[:8]}@hypeblock.io"


def test_waitlist_join_new(s, waitlist_email):
    r = s.post(f"{API}/waitlist", json={"email": waitlist_email, "wallet": "0xabc"})
    assert r.status_code == 200
    assert r.json()["ok"] is True


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
    r4 = s.delete(f"{API}/admin/waitlist/{eid}?key={ADMIN_KEY}")
    assert r4.status_code == 200
