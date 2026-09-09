#!/usr/bin/env python3
"""
Comprehensive backend API tests for HYPEBLOCK v6 (96-item collection)
Tests all endpoints against the rebuilt collection from user-uploaded art.
"""
import requests
import json
import sys
from pathlib import Path

# Read backend URL from frontend/.env
def get_backend_url():
    env_file = Path("/app/frontend/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL"):
                return line.split("=", 1)[1].strip().rstrip("/")
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

print(f"Testing HYPEBLOCK backend at: {API_URL}\n")

# Test results tracking
passed = 0
failed = 0
errors = []

def test(name, condition, error_msg=""):
    global passed, failed, errors
    if condition:
        print(f"✅ {name}")
        passed += 1
    else:
        print(f"❌ {name}")
        if error_msg:
            print(f"   Error: {error_msg}")
            errors.append(f"{name}: {error_msg}")
        failed += 1

# ============================================================================
# 1. GET /api/stats - verify collection v6 specs
# ============================================================================
print("=" * 70)
print("TEST 1: GET /api/stats")
print("=" * 70)
try:
    r = requests.get(f"{API_URL}/stats", timeout=10)
    test("Stats endpoint returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        test("total_supply = 96", data.get("total_supply") == 96, 
             f"Got {data.get('total_supply')}")
        test("released_count = 96", data.get("released_count") == 96,
             f"Got {data.get('released_count')}")
        
        tiers = data.get("tiers", {})
        test("Common tier = 50", tiers.get("Common") == 50, f"Got {tiers.get('Common')}")
        test("Rare tier = 24", tiers.get("Rare") == 24, f"Got {tiers.get('Rare')}")
        test("Epic tier = 13", tiers.get("Epic") == 13, f"Got {tiers.get('Epic')}")
        test("Legendary tier = 6", tiers.get("Legendary") == 6, f"Got {tiers.get('Legendary')}")
        test("Mythic tier = 3", tiers.get("Mythic") == 3, f"Got {tiers.get('Mythic')}")
        
        test("creator_wallet present", "creator_wallet" in data)
except Exception as e:
    test("Stats endpoint accessible", False, str(e))

# ============================================================================
# 2. GET /api/nfts - list, pagination, filters, sorting
# ============================================================================
print("\n" + "=" * 70)
print("TEST 2: GET /api/nfts - List, Pagination, Filters, Sorting")
print("=" * 70)

# 2a. Basic list
try:
    r = requests.get(f"{API_URL}/nfts", timeout=10)
    test("NFT list endpoint returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        test("Total NFTs = 96", data.get("total") == 96, f"Got {data.get('total')}")
        items = data.get("items", [])
        test("Items returned", len(items) > 0, f"Got {len(items)} items")
        
        if items:
            first_item = items[0]
            test("First item has released=true", first_item.get("released") == True,
                 f"Got {first_item.get('released')}")
except Exception as e:
    test("NFT list endpoint accessible", False, str(e))

# 2b. Pagination
try:
    r = requests.get(f"{API_URL}/nfts?page=1&limit=10", timeout=10)
    test("Pagination works (page=1, limit=10)", r.status_code == 200 and len(r.json().get("items", [])) == 10,
         f"Got {len(r.json().get('items', []))} items")
    
    r2 = requests.get(f"{API_URL}/nfts?page=2&limit=10", timeout=10)
    test("Pagination page 2 works", r2.status_code == 200 and len(r2.json().get("items", [])) == 10)
except Exception as e:
    test("Pagination test", False, str(e))

# 2c. Filter by tier=Mythic (should return exactly 3 items, all with price_pol=0)
try:
    r = requests.get(f"{API_URL}/nfts?tier=Mythic", timeout=10)
    test("Filter tier=Mythic returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        mythic_items = data.get("items", [])
        test("tier=Mythic returns exactly 3 items", len(mythic_items) == 3,
             f"Got {len(mythic_items)} items")
        
        if mythic_items:
            all_price_zero = all(item.get("price_pol") == 0 for item in mythic_items)
            test("All Mythic items have price_pol=0", all_price_zero,
                 f"Prices: {[item.get('price_pol') for item in mythic_items]}")
except Exception as e:
    test("Filter tier=Mythic test", False, str(e))

# 2d. Filter by skin (test with new values from v6 collection)
# First, let's get available skins from traits endpoint
try:
    r = requests.get(f"{API_URL}/traits", timeout=10)
    if r.status_code == 200:
        traits_data = r.json()
        counts = traits_data.get("counts", {})
        skins = counts.get("Skin", {})
        
        # Test Gold skin filter if it exists
        if "Gold" in skins:
            r_gold = requests.get(f"{API_URL}/nfts?skin=Gold", timeout=10)
            test("Filter skin=Gold returns 200", r_gold.status_code == 200)
            if r_gold.status_code == 200:
                gold_items = r_gold.json().get("items", [])
                test("skin=Gold returns items", len(gold_items) > 0,
                     f"Got {len(gold_items)} items, expected > 0")
                if gold_items:
                    all_gold = all(item.get("traits", {}).get("Skin") == "Gold" for item in gold_items)
                    test("All returned items have Skin=Gold", all_gold)
        
        # Test Zombie skin filter if it exists
        if "Zombie" in skins:
            r_zombie = requests.get(f"{API_URL}/nfts?skin=Zombie", timeout=10)
            test("Filter skin=Zombie returns 200", r_zombie.status_code == 200)
            if r_zombie.status_code == 200:
                zombie_items = r_zombie.json().get("items", [])
                test("skin=Zombie returns items", len(zombie_items) > 0,
                     f"Got {len(zombie_items)} items")
                if zombie_items:
                    all_zombie = all(item.get("traits", {}).get("Skin") == "Zombie" for item in zombie_items)
                    test("All returned items have Skin=Zombie", all_zombie)
except Exception as e:
    test("Skin filter test", False, str(e))

# 2e. Sorting tests
try:
    # sort=rank_asc - first item should be a Mythic (rank 1)
    r = requests.get(f"{API_URL}/nfts?sort=rank_asc&limit=1", timeout=10)
    test("Sort rank_asc returns 200", r.status_code == 200)
    if r.status_code == 200:
        items = r.json().get("items", [])
        if items:
            first = items[0]
            test("sort=rank_asc first item is Mythic (rank 1)", 
                 first.get("tier") == "Mythic" and first.get("rank") == 1,
                 f"Got tier={first.get('tier')}, rank={first.get('rank')}")
    
    # sort=price_desc - verify descending order
    r = requests.get(f"{API_URL}/nfts?sort=price_desc&limit=5", timeout=10)
    test("Sort price_desc returns 200", r.status_code == 200)
    if r.status_code == 200:
        items = r.json().get("items", [])
        if len(items) >= 2:
            prices = [item.get("price_pol", 0) for item in items]
            is_descending = all(prices[i] >= prices[i+1] for i in range(len(prices)-1))
            test("sort=price_desc orders correctly", is_descending,
                 f"Prices: {prices}")
    
    # sort=price_asc - verify ascending order
    r = requests.get(f"{API_URL}/nfts?sort=price_asc&limit=5", timeout=10)
    test("Sort price_asc returns 200", r.status_code == 200)
    if r.status_code == 200:
        items = r.json().get("items", [])
        if len(items) >= 2:
            prices = [item.get("price_pol", 0) for item in items]
            is_ascending = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
            test("sort=price_asc orders correctly", is_ascending,
                 f"Prices: {prices}")
except Exception as e:
    test("Sorting test", False, str(e))

# ============================================================================
# 3. GET /api/nfts/{token_id} - detail endpoint
# ============================================================================
print("\n" + "=" * 70)
print("TEST 3: GET /api/nfts/{token_id} - NFT Detail")
print("=" * 70)

# 3a. GET /api/nfts/1
try:
    r = requests.get(f"{API_URL}/nfts/1", timeout=10)
    test("GET /api/nfts/1 returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        nft = r.json()
        test("NFT 1 has released=true", nft.get("released") == True,
             f"Got {nft.get('released')}")
        test("NFT 1 has unlock_date=null", nft.get("unlock_date") is None,
             f"Got {nft.get('unlock_date')}")
        
        image_url = nft.get("image", "")
        test("NFT 1 image URL ends with /api/render/1", image_url.endswith("/api/render/1"),
             f"Got {image_url}")
        
        trait_rarity = nft.get("trait_rarity_pct")
        test("NFT 1 has trait_rarity_pct as object", isinstance(trait_rarity, dict),
             f"Got type {type(trait_rarity)}")
except Exception as e:
    test("GET /api/nfts/1 test", False, str(e))

# 3b. GET /api/nfts/96
try:
    r = requests.get(f"{API_URL}/nfts/96", timeout=10)
    test("GET /api/nfts/96 returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        nft = r.json()
        test("NFT 96 has released=true", nft.get("released") == True,
             f"Got {nft.get('released')}")
        test("NFT 96 has unlock_date=null", nft.get("unlock_date") is None,
             f"Got {nft.get('unlock_date')}")
        
        image_url = nft.get("image", "")
        test("NFT 96 image URL ends with /api/render/96", image_url.endswith("/api/render/96"),
             f"Got {image_url}")
        
        trait_rarity = nft.get("trait_rarity_pct")
        test("NFT 96 has trait_rarity_pct as object", isinstance(trait_rarity, dict),
             f"Got type {type(trait_rarity)}")
except Exception as e:
    test("GET /api/nfts/96 test", False, str(e))

# 3c. GET /api/nfts/97 - should return 404
try:
    r = requests.get(f"{API_URL}/nfts/97", timeout=10)
    test("GET /api/nfts/97 returns 404", r.status_code == 404, f"Got {r.status_code}")
except Exception as e:
    test("GET /api/nfts/97 test", False, str(e))

# 3d. GET /api/nfts/500 - should return 404
try:
    r = requests.get(f"{API_URL}/nfts/500", timeout=10)
    test("GET /api/nfts/500 returns 404", r.status_code == 404, f"Got {r.status_code}")
except Exception as e:
    test("GET /api/nfts/500 test", False, str(e))

# ============================================================================
# 4. GET /api/render/{token_id} - image serving
# ============================================================================
print("\n" + "=" * 70)
print("TEST 4: GET /api/render/{token_id} - Image Serving")
print("=" * 70)

# 4a. GET /api/render/1
try:
    r = requests.get(f"{API_URL}/render/1", timeout=10)
    test("GET /api/render/1 returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        content_type = r.headers.get("content-type", "")
        test("render/1 content-type is image/*", content_type.startswith("image/"),
             f"Got {content_type}")
        test("render/1 has image data", len(r.content) > 0,
             f"Got {len(r.content)} bytes")
except Exception as e:
    test("GET /api/render/1 test", False, str(e))

# 4b. GET /api/render/96
try:
    r = requests.get(f"{API_URL}/render/96", timeout=10)
    test("GET /api/render/96 returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        content_type = r.headers.get("content-type", "")
        test("render/96 content-type is image/*", content_type.startswith("image/"),
             f"Got {content_type}")
        test("render/96 has image data", len(r.content) > 0,
             f"Got {len(r.content)} bytes")
except Exception as e:
    test("GET /api/render/96 test", False, str(e))

# 4c. GET /api/render/97 - should return 404
try:
    r = requests.get(f"{API_URL}/render/97", timeout=10)
    test("GET /api/render/97 returns 404", r.status_code == 404, f"Got {r.status_code}")
except Exception as e:
    test("GET /api/render/97 test", False, str(e))

# ============================================================================
# 5. GET /api/metadata/export - OpenSea metadata export
# ============================================================================
print("\n" + "=" * 70)
print("TEST 5: GET /api/metadata/export - Metadata Export")
print("=" * 70)

try:
    r = requests.get(f"{API_URL}/metadata/export", timeout=10)
    test("Metadata export returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        test("Metadata export is array", isinstance(data, list), f"Got type {type(data)}")
        test("Metadata export has exactly 96 items", len(data) == 96,
             f"Got {len(data)} items")
        
        if data:
            first = data[0]
            test("First item has 'name' field", "name" in first)
            test("First item has 'description' field", "description" in first)
            test("First item has 'image' field", "image" in first)
            test("First item has 'attributes' field", "attributes" in first)
            
            if "attributes" in first:
                attrs = first["attributes"]
                test("Attributes is array", isinstance(attrs, list))
                if isinstance(attrs, list):
                    attr_types = [a.get("trait_type") for a in attrs]
                    test("Attributes include 'Rarity' trait", "Rarity" in attr_types,
                         f"Got traits: {attr_types}")
except Exception as e:
    test("Metadata export test", False, str(e))

# ============================================================================
# 6. GET /api/traits - trait counts
# ============================================================================
print("\n" + "=" * 70)
print("TEST 6: GET /api/traits - Trait Counts")
print("=" * 70)

try:
    r = requests.get(f"{API_URL}/traits", timeout=10)
    test("Traits endpoint returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        test("Traits has 'counts' field", "counts" in data)
        
        counts = data.get("counts", {})
        if counts:
            # Check that counts include expected categories
            expected_cats = ["Gender", "Skin", "Eyes", "Headwear", "Mouth", "Outfit", "Background", "Accessory"]
            for cat in expected_cats:
                test(f"Counts include '{cat}' category", cat in counts,
                     f"Available: {list(counts.keys())}")
            
            # Verify Gender counts sum to 96
            if "Gender" in counts:
                gender_counts = counts["Gender"]
                total_gender = sum(gender_counts.values())
                test("Gender counts sum to 96", total_gender == 96,
                     f"Got {total_gender}, counts: {gender_counts}")
except Exception as e:
    test("Traits endpoint test", False, str(e))

# ============================================================================
# 7. POST /api/trait-lab/estimate - trait rarity estimation
# ============================================================================
print("\n" + "=" * 70)
print("TEST 7: POST /api/trait-lab/estimate - Trait Lab")
print("=" * 70)

# 7a. Test with a high-rarity combo (should return high tier)
try:
    payload = {
        "traits": {
            "Gender": "Male",
            "Skin": "Gold",
            "Eyes": "Flame",
            "Headwear": "Crown",
            "Mouth": "Grin",
            "Outfit": "Chain-only",
            "Background": "Deep Purple",
            "Accessory": "Diamond Chain"
        }
    }
    r = requests.post(f"{API_URL}/trait-lab/estimate", json=payload, timeout=10)
    test("Trait lab estimate returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        test("Response has 'score' field", "score" in data)
        test("Response has 'per_trait_pct' field", "per_trait_pct" in data)
        test("Response has 'percentile' field", "percentile" in data)
        test("Response has 'tier_guess' field", "tier_guess" in data)
        test("Response has 'rank_estimate' field", "rank_estimate" in data)
        
        tier_guess = data.get("tier_guess")
        # High rarity combo should return Epic/Legendary/Mythic
        test("High rarity combo returns high tier (Epic/Legendary/Mythic)",
             tier_guess in ["Epic", "Legendary", "Mythic"],
             f"Got tier_guess={tier_guess}")
except Exception as e:
    test("Trait lab estimate test", False, str(e))

# ============================================================================
# 8. Waitlist endpoints
# ============================================================================
print("\n" + "=" * 70)
print("TEST 8: Waitlist Endpoints")
print("=" * 70)

# 8a. POST /api/waitlist with unique email
try:
    import time
    unique_email = f"test_{int(time.time())}@example.com"
    payload = {"email": unique_email}
    r = requests.post(f"{API_URL}/waitlist", json=payload, timeout=10)
    test("POST /api/waitlist with unique email returns 200", r.status_code == 200,
         f"Got {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        test("Response has 'ok' field", "ok" in data)
        test("Response has 'count' field", "count" in data)
except Exception as e:
    test("POST /api/waitlist unique email test", False, str(e))

# 8b. POST /api/waitlist with duplicate email (should return 409)
try:
    # Use the same email again
    r = requests.post(f"{API_URL}/waitlist", json={"email": unique_email}, timeout=10)
    test("POST /api/waitlist with duplicate email returns 409", r.status_code == 409,
         f"Got {r.status_code}")
except Exception as e:
    test("POST /api/waitlist duplicate email test", False, str(e))

# 8c. GET /api/waitlist/count
try:
    r = requests.get(f"{API_URL}/waitlist/count", timeout=10)
    test("GET /api/waitlist/count returns 200", r.status_code == 200, f"Got {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        test("Response has 'count' field", "count" in data)
        test("Count is a number", isinstance(data.get("count"), int),
             f"Got type {type(data.get('count'))}")
except Exception as e:
    test("GET /api/waitlist/count test", False, str(e))

# ============================================================================
# 9. Admin endpoints
# ============================================================================
print("\n" + "=" * 70)
print("TEST 9: Admin Endpoints")
print("=" * 70)

# 9a. GET /api/admin/waitlist with correct key
try:
    r = requests.get(f"{API_URL}/admin/waitlist?key=hypeblock2026", timeout=10)
    test("GET /api/admin/waitlist with correct key returns 200", r.status_code == 200,
         f"Got {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        test("Response has 'entries' field", "entries" in data)
        test("Response has 'count' field", "count" in data)
except Exception as e:
    test("GET /api/admin/waitlist with correct key test", False, str(e))

# 9b. GET /api/admin/waitlist with wrong key (should return 401)
try:
    r = requests.get(f"{API_URL}/admin/waitlist?key=wrongkey", timeout=10)
    test("GET /api/admin/waitlist with wrong key returns 401", r.status_code == 401,
         f"Got {r.status_code}")
except Exception as e:
    test("GET /api/admin/waitlist with wrong key test", False, str(e))

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Total: {passed + failed}")

if failed > 0:
    print("\n" + "=" * 70)
    print("FAILED TESTS DETAILS:")
    print("=" * 70)
    for error in errors:
        print(f"  • {error}")

sys.exit(0 if failed == 0 else 1)
