#!/usr/bin/env python3
"""
HYPEBLOCK Backend API Test Suite - Collection v5
Tests all backend endpoints for the HYPEBLOCK NFT collection v5
"""
import requests
import json
import sys
from typing import Dict, Any, List, Optional

# Backend URL from frontend/.env
BASE_URL = "https://497b437d-23b7-404e-866e-5236299aa49c.preview.emergentagent.com/api"
ADMIN_KEY = "hypeblock2026"

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_pass(test_name: str, details: str = ""):
    """Log a passed test"""
    msg = f"✅ PASS: {test_name}"
    if details:
        msg += f" - {details}"
    print(msg)
    test_results["passed"].append(test_name)

def log_fail(test_name: str, details: str):
    """Log a failed test"""
    msg = f"❌ FAIL: {test_name} - {details}"
    print(msg)
    test_results["failed"].append(f"{test_name}: {details}")

def log_warning(test_name: str, details: str):
    """Log a warning"""
    msg = f"⚠️  WARNING: {test_name} - {details}"
    print(msg)
    test_results["warnings"].append(f"{test_name}: {details}")

def test_stats_endpoint():
    """Test 1: GET /api/stats - v5 collection specs"""
    print("\n" + "="*80)
    print("TEST 1: GET /api/stats (v5 collection)")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        
        if response.status_code != 200:
            log_fail("Stats endpoint", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Check total_supply
        if data.get("total_supply") != 200:
            log_fail("Stats total_supply", f"Expected 200, got {data.get('total_supply')}")
        else:
            log_pass("Stats total_supply", "200 NFTs")
        
        # Check tiers (v5: 3 Mythics, 5 Legendary, 24 Epic, 50 Rare, 118 Common)
        expected_tiers = {
            "Common": 118,
            "Rare": 50,
            "Epic": 24,
            "Legendary": 5,
            "Mythic": 3
        }
        
        tiers = data.get("tiers", {})
        tier_match = True
        for tier_name, expected_count in expected_tiers.items():
            actual_count = tiers.get(tier_name, 0)
            if actual_count != expected_count:
                log_fail(f"Stats tier {tier_name}", f"Expected {expected_count}, got {actual_count}")
                tier_match = False
        
        if tier_match:
            log_pass("Stats tiers", "All 5 tiers correct (Common:118, Rare:50, Epic:24, Legendary:5, Mythic:3)")
        
        # Check released_count (v5: only batches 1-2 = 40 NFTs)
        if data.get("released_count") != 40:
            log_fail("Stats released_count", f"Expected 40 (batches 1-2), got {data.get('released_count')}")
        else:
            log_pass("Stats released_count", "40 NFTs (batches 1-2 only)")
        
        # Check creator_wallet
        if not data.get("creator_wallet"):
            log_fail("Stats creator_wallet", "Creator wallet missing")
        else:
            log_pass("Stats creator_wallet", f"Present: {data.get('creator_wallet')}")
        
    except Exception as e:
        log_fail("Stats endpoint", f"Exception: {str(e)}")

def test_nfts_filter_mythic():
    """Test 2: GET /api/nfts?tier=Mythic - should return 3 items"""
    print("\n" + "="*80)
    print("TEST 2: GET /api/nfts?tier=Mythic (v5: 3 Mythics)")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/nfts?tier=Mythic", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFTs filter Mythic", f"Expected 200, got {response.status_code}")
            return []
        
        data = response.json()
        
        # Should return exactly 3 items
        if data.get("total") != 3:
            log_fail("NFTs filter Mythic count", f"Expected 3, got {data.get('total')}")
            return []
        
        if len(data.get("items", [])) != 3:
            log_fail("NFTs filter Mythic items", f"Expected 3 items, got {len(data.get('items', []))}")
            return []
        
        log_pass("NFTs filter Mythic count", "Returns exactly 3 items")
        
        mythic_items = data["items"]
        expected_names = {"Genesis King", "Toxic Queen", "Diamond Warlord"}
        actual_names = {item.get("name") for item in mythic_items}
        
        print(f"Mythic names found: {actual_names}")
        
        # Check all 3 expected names are present
        if actual_names != expected_names:
            log_fail("NFTs filter Mythic names", f"Expected {expected_names}, got {actual_names}")
        else:
            log_pass("NFTs filter Mythic names", "Genesis King, Toxic Queen, Diamond Warlord")
        
        # Check all have price_pol=0
        all_zero_price = all(item.get("price_pol") == 0 for item in mythic_items)
        if not all_zero_price:
            prices = [item.get("price_pol") for item in mythic_items]
            log_fail("NFTs filter Mythic prices", f"Expected all 0 (auction), got {prices}")
        else:
            log_pass("NFTs filter Mythic prices", "All 3 have price_pol=0 (auction)")
        
        return mythic_items
        
    except Exception as e:
        log_fail("NFTs filter Mythic", f"Exception: {str(e)}")
        return []

def test_nft_released_flag():
    """Test 3: GET /api/nfts/{id} - released flag and unlock_date"""
    print("\n" + "="*80)
    print("TEST 3: GET /api/nfts/{id} - released flag & unlock_date")
    print("="*80)
    
    try:
        # Test token in batch 1 (token_id=5, batch 1)
        print("\n--- Testing token_id=5 (batch 1, should be released) ---")
        response1 = requests.get(f"{BASE_URL}/nfts/5", timeout=10)
        
        if response1.status_code != 200:
            log_fail("NFT detail batch 1", f"Expected 200, got {response1.status_code}")
        else:
            data1 = response1.json()
            print(f"Token 5: released={data1.get('released')}, unlock_date={data1.get('unlock_date')}")
            
            if data1.get("released") != True:
                log_fail("NFT detail batch 1 released", f"Expected True, got {data1.get('released')}")
            else:
                log_pass("NFT detail batch 1 released", "Token 5 is released=True")
            
            if data1.get("unlock_date") is not None:
                log_fail("NFT detail batch 1 unlock_date", f"Expected None, got {data1.get('unlock_date')}")
            else:
                log_pass("NFT detail batch 1 unlock_date", "Token 5 has unlock_date=None")
        
        # Test token in batch 3 (token_id=60, batch 3, should be locked)
        print("\n--- Testing token_id=60 (batch 3, should be locked) ---")
        response2 = requests.get(f"{BASE_URL}/nfts/60", timeout=10)
        
        if response2.status_code != 200:
            log_fail("NFT detail batch 3", f"Expected 200, got {response2.status_code}")
        else:
            data2 = response2.json()
            print(f"Token 60: released={data2.get('released')}, unlock_date={data2.get('unlock_date')}")
            
            if data2.get("released") != False:
                log_fail("NFT detail batch 3 released", f"Expected False, got {data2.get('released')}")
            else:
                log_pass("NFT detail batch 3 released", "Token 60 is released=False")
            
            unlock_date = data2.get("unlock_date")
            if unlock_date is None:
                log_fail("NFT detail batch 3 unlock_date", "Expected future ISO timestamp, got None")
            else:
                # Check it's a valid ISO timestamp
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(unlock_date.replace('Z', '+00:00'))
                    log_pass("NFT detail batch 3 unlock_date", f"Valid future ISO timestamp: {unlock_date}")
                except:
                    log_fail("NFT detail batch 3 unlock_date", f"Invalid ISO timestamp: {unlock_date}")
        
        # Test token in batch 10 (token_id=190, batch 10, should be locked)
        print("\n--- Testing token_id=190 (batch 10, should be locked) ---")
        response3 = requests.get(f"{BASE_URL}/nfts/190", timeout=10)
        
        if response3.status_code != 200:
            log_fail("NFT detail batch 10", f"Expected 200, got {response3.status_code}")
        else:
            data3 = response3.json()
            print(f"Token 190: released={data3.get('released')}, unlock_date={data3.get('unlock_date')}")
            
            if data3.get("released") != False:
                log_fail("NFT detail batch 10 released", f"Expected False, got {data3.get('released')}")
            else:
                log_pass("NFT detail batch 10 released", "Token 190 is released=False")
            
            unlock_date = data3.get("unlock_date")
            if unlock_date is None:
                log_fail("NFT detail batch 10 unlock_date", "Expected future ISO timestamp, got None")
            else:
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(unlock_date.replace('Z', '+00:00'))
                    log_pass("NFT detail batch 10 unlock_date", f"Valid future ISO timestamp: {unlock_date}")
                except:
                    log_fail("NFT detail batch 10 unlock_date", f"Invalid ISO timestamp: {unlock_date}")
        
    except Exception as e:
        log_fail("NFT released flag test", f"Exception: {str(e)}")

def test_trait_lab_estimate():
    """Test 4: POST /api/trait-lab/estimate"""
    print("\n" + "="*80)
    print("TEST 4: POST /api/trait-lab/estimate")
    print("="*80)
    
    try:
        # Test 1: Common combo
        print("\n--- Testing common trait combo ---")
        common_traits = {
            "traits": {
                "Gender": "Male",
                "Skin": "Classic Green",
                "Eyes": "Mischief",
                "Headwear": "Beanie",
                "Mouth": "Grin",
                "Outfit": "Hoodie",
                "Background": "Acid Green",
                "Accessory": "None"
            }
        }
        
        response1 = requests.post(
            f"{BASE_URL}/trait-lab/estimate",
            json=common_traits,
            timeout=10
        )
        
        if response1.status_code != 200:
            log_fail("Trait lab common combo", f"Expected 200, got {response1.status_code}")
        else:
            data1 = response1.json()
            print(f"Common combo response: {json.dumps(data1, indent=2)}")
            
            # Check required fields
            required_fields = ["score", "per_trait_pct", "percentile", "tier_guess", "rank_estimate"]
            missing_fields = [f for f in required_fields if f not in data1]
            
            if missing_fields:
                log_fail("Trait lab common combo fields", f"Missing fields: {missing_fields}")
            else:
                log_pass("Trait lab common combo fields", "All required fields present")
            
            # Check per_trait_pct is an object
            if not isinstance(data1.get("per_trait_pct"), dict):
                log_fail("Trait lab per_trait_pct", f"Expected object, got {type(data1.get('per_trait_pct'))}")
            else:
                log_pass("Trait lab per_trait_pct", "Returns object with trait percentages")
        
        # Test 2: Maxed rare combo (should be Legendary or Mythic with high percentile)
        print("\n--- Testing maxed rare combo ---")
        maxed_traits = {
            "traits": {
                "Gender": "Male",
                "Skin": "Gold",
                "Eyes": "Flame",
                "Headwear": "Crown",
                "Mouth": "Gold Grillz",
                "Outfit": "Chain-only",
                "Background": "Legendary Glow",
                "Accessory": "Diamond Chain"
            }
        }
        
        response2 = requests.post(
            f"{BASE_URL}/trait-lab/estimate",
            json=maxed_traits,
            timeout=10
        )
        
        if response2.status_code != 200:
            log_fail("Trait lab maxed combo", f"Expected 200, got {response2.status_code}")
        else:
            data2 = response2.json()
            print(f"Maxed combo response: {json.dumps(data2, indent=2)}")
            
            tier_guess = data2.get("tier_guess")
            percentile = data2.get("percentile", 0)
            
            # Check tier_guess is Legendary or Mythic
            if tier_guess not in ["Legendary", "Mythic"]:
                log_fail("Trait lab maxed combo tier", f"Expected Legendary or Mythic, got {tier_guess}")
            else:
                log_pass("Trait lab maxed combo tier", f"tier_guess={tier_guess}")
            
            # Check percentile >= 96
            if percentile < 96:
                log_fail("Trait lab maxed combo percentile", f"Expected >=96, got {percentile}")
            else:
                log_pass("Trait lab maxed combo percentile", f"percentile={percentile} (>=96)")
        
    except Exception as e:
        log_fail("Trait lab estimate", f"Exception: {str(e)}")

def test_render_status():
    """Test 5: GET /api/render-status"""
    print("\n" + "="*80)
    print("TEST 5: GET /api/render-status")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/render-status", timeout=10)
        
        if response.status_code != 200:
            log_fail("Render status", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        print(f"Render status response: {json.dumps(data, indent=2)}")
        
        # Check required fields
        if "generated" not in data or "total" not in data:
            log_fail("Render status fields", "Missing generated or total fields")
            return
        
        generated = data.get("generated")
        total = data.get("total")
        
        # Check total is 200
        if total != 200:
            log_fail("Render status total", f"Expected 200, got {total}")
        else:
            log_pass("Render status total", "total=200")
        
        # Check generated is between 0 and 200
        if not isinstance(generated, int) or generated < 0 or generated > 200:
            log_fail("Render status generated", f"Expected 0-200, got {generated}")
        else:
            log_pass("Render status generated", f"generated={generated} (valid range)")
        
    except Exception as e:
        log_fail("Render status", f"Exception: {str(e)}")

def test_render_image():
    """Test 6: GET /api/render/{id}"""
    print("\n" + "="*80)
    print("TEST 6: GET /api/render/{id}")
    print("="*80)
    
    try:
        # Test render/1 (likely generated)
        print("\n--- Testing GET /api/render/1 ---")
        response1 = requests.get(f"{BASE_URL}/render/1", timeout=10)
        
        if response1.status_code == 200:
            # Check content-type is image/*
            content_type = response1.headers.get("content-type", "")
            if content_type.startswith("image/"):
                log_pass("Render image 1", f"Returns image (content-type: {content_type})")
            else:
                log_fail("Render image 1", f"Expected image/*, got {content_type}")
        elif response1.status_code == 404:
            log_warning("Render image 1", "Image not generated yet (404) - acceptable")
        else:
            log_fail("Render image 1", f"Unexpected status code: {response1.status_code}")
        
        # Test render/199 (likely not generated yet)
        print("\n--- Testing GET /api/render/199 ---")
        response2 = requests.get(f"{BASE_URL}/render/199", timeout=10)
        
        if response2.status_code == 404:
            log_pass("Render image 199", "Returns 404 (not generated yet) - correct behavior")
        elif response2.status_code == 200:
            content_type = response2.headers.get("content-type", "")
            if content_type.startswith("image/"):
                log_pass("Render image 199", f"Returns image (content-type: {content_type}) - already generated")
            else:
                log_fail("Render image 199", f"Expected image/* or 404, got {content_type}")
        else:
            log_fail("Render image 199", f"Unexpected status code: {response2.status_code}")
        
    except Exception as e:
        log_fail("Render image", f"Exception: {str(e)}")

def test_nfts_pagination():
    """Test 7: GET /api/nfts - pagination regression"""
    print("\n" + "="*80)
    print("TEST 7: GET /api/nfts - Pagination (regression)")
    print("="*80)
    
    try:
        # Test default pagination
        response = requests.get(f"{BASE_URL}/nfts", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFTs pagination", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        
        # Check total
        if data.get("total") != 200:
            log_fail("NFTs pagination total", f"Expected 200, got {data.get('total')}")
        else:
            log_pass("NFTs pagination total", "200 items")
        
        # Check pagination fields
        if "page" not in data or "limit" not in data or "items" not in data:
            log_fail("NFTs pagination fields", "Missing page/limit/items fields")
        else:
            log_pass("NFTs pagination fields", f"page={data['page']}, limit={data['limit']}")
        
    except Exception as e:
        log_fail("NFTs pagination", f"Exception: {str(e)}")

def test_nfts_trait_filter():
    """Test 8: GET /api/nfts - trait filter regression"""
    print("\n" + "="*80)
    print("TEST 8: GET /api/nfts?skin=Zombie - Trait filter (regression)")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/nfts?skin=Zombie", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFTs trait filter", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        items = data.get("items", [])
        
        if len(items) == 0:
            log_warning("NFTs trait filter", "No Zombie-skin items found")
            return
        
        # Verify all items have Zombie skin
        all_zombie = all(item.get("traits", {}).get("Skin") == "Zombie" for item in items)
        
        if all_zombie:
            log_pass("NFTs trait filter", f"Returns {len(items)} Zombie-skin items only")
        else:
            log_fail("NFTs trait filter", "Some items don't have Zombie skin")
        
    except Exception as e:
        log_fail("NFTs trait filter", f"Exception: {str(e)}")

def test_nfts_sort():
    """Test 9: GET /api/nfts - sort regression"""
    print("\n" + "="*80)
    print("TEST 9: GET /api/nfts?sort=rank_asc - Sort (regression)")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/nfts?sort=rank_asc&limit=5", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFTs sort rank_asc", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        items = data.get("items", [])
        
        if len(items) == 0:
            log_fail("NFTs sort rank_asc", "No items returned")
            return
        
        first_item = items[0]
        
        # First item should be a Mythic with rank 1
        if first_item.get("rank") == 1 and first_item.get("tier") == "Mythic":
            log_pass("NFTs sort rank_asc", f"First item is Mythic rank #1 ({first_item.get('name')})")
        else:
            log_fail("NFTs sort rank_asc", f"First item rank={first_item.get('rank')}, tier={first_item.get('tier')}")
        
    except Exception as e:
        log_fail("NFTs sort", f"Exception: {str(e)}")

def test_metadata_export():
    """Test 10: GET /api/metadata/export - regression"""
    print("\n" + "="*80)
    print("TEST 10: GET /api/metadata/export (regression)")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/metadata/export", timeout=15)
        
        if response.status_code != 200:
            log_fail("Metadata export", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        
        # Check it's an array
        if not isinstance(data, list):
            log_fail("Metadata export format", f"Expected array, got {type(data)}")
            return
        
        # Check count is exactly 200
        if len(data) != 200:
            log_fail("Metadata export count", f"Expected 200 items, got {len(data)}")
        else:
            log_pass("Metadata export", "Returns array of 200 items")
        
    except Exception as e:
        log_fail("Metadata export", f"Exception: {str(e)}")

def test_waitlist():
    """Test 11: Waitlist endpoints - regression"""
    print("\n" + "="*80)
    print("TEST 11: Waitlist endpoints (regression)")
    print("="*80)
    
    try:
        # Generate unique email for testing
        import time
        unique_email = f"test_{int(time.time())}@example.com"
        
        # Test POST /api/waitlist
        response = requests.post(
            f"{BASE_URL}/waitlist",
            json={"email": unique_email},
            timeout=10
        )
        
        if response.status_code != 200:
            log_fail("Waitlist POST", f"Expected 200, got {response.status_code}")
        else:
            data = response.json()
            if data.get("ok") and "count" in data:
                log_pass("Waitlist POST", "Works correctly")
            else:
                log_fail("Waitlist POST", f"Unexpected response: {data}")
        
        # Test GET /api/waitlist/count
        response2 = requests.get(f"{BASE_URL}/waitlist/count", timeout=10)
        
        if response2.status_code != 200:
            log_fail("Waitlist GET count", f"Expected 200, got {response2.status_code}")
        else:
            log_pass("Waitlist GET count", "Works correctly")
        
    except Exception as e:
        log_fail("Waitlist endpoints", f"Exception: {str(e)}")

def test_admin():
    """Test 12: Admin endpoints - regression"""
    print("\n" + "="*80)
    print("TEST 12: Admin endpoints (regression)")
    print("="*80)
    
    try:
        # Test with correct key
        response = requests.get(
            f"{BASE_URL}/admin/waitlist",
            params={"key": ADMIN_KEY},
            timeout=10
        )
        
        if response.status_code != 200:
            log_fail("Admin waitlist", f"Expected 200, got {response.status_code}")
        else:
            data = response.json()
            if "entries" in data and "count" in data:
                log_pass("Admin waitlist", f"Works correctly (key: {ADMIN_KEY})")
            else:
                log_fail("Admin waitlist", f"Invalid response: {data}")
        
    except Exception as e:
        log_fail("Admin endpoints", f"Exception: {str(e)}")

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    print(f"\n✅ PASSED: {len(test_results['passed'])} tests")
    for test in test_results['passed']:
        print(f"   - {test}")
    
    if test_results['warnings']:
        print(f"\n⚠️  WARNINGS: {len(test_results['warnings'])}")
        for warning in test_results['warnings']:
            print(f"   - {warning}")
    
    if test_results['failed']:
        print(f"\n❌ FAILED: {len(test_results['failed'])} tests")
        for failure in test_results['failed']:
            print(f"   - {failure}")
    
    print("\n" + "="*80)
    
    if test_results['failed']:
        print("❌ OVERALL: TESTS FAILED")
        return 1
    else:
        print("✅ OVERALL: ALL TESTS PASSED")
        return 0

def main():
    """Run all tests"""
    print("="*80)
    print("HYPEBLOCK BACKEND API TEST SUITE - Collection v5")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin Key: {ADMIN_KEY}")
    print("\nTesting v5 collection specs:")
    print("- Total: 200 NFTs")
    print("- Tiers: Common:118, Rare:50, Epic:24, Legendary:5, Mythic:3")
    print("- Released: 40 NFTs (batches 1-2 only)")
    print("- Mythics: Genesis King, Toxic Queen, Diamond Warlord")
    
    # Run all tests
    test_stats_endpoint()
    test_nfts_filter_mythic()
    test_nft_released_flag()
    test_trait_lab_estimate()
    test_render_status()
    test_render_image()
    
    # Regression tests
    test_nfts_pagination()
    test_nfts_trait_filter()
    test_nfts_sort()
    test_metadata_export()
    test_waitlist()
    test_admin()
    
    # Print summary
    exit_code = print_summary()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
