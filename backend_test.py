#!/usr/bin/env python3
"""
HYPEBLOCK Backend API Test Suite
Tests all backend endpoints for the HYPEBLOCK NFT collection
"""
import requests
import json
import sys
from typing import Dict, Any, List

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
    """Test 1: GET /api/stats"""
    print("\n" + "="*80)
    print("TEST 1: GET /api/stats")
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
        
        # Check tiers
        expected_tiers = {
            "Common": 120,
            "Rare": 50,
            "Epic": 24,
            "Legendary": 5,
            "Mythic": 1
        }
        
        tiers = data.get("tiers", {})
        tier_match = True
        for tier_name, expected_count in expected_tiers.items():
            actual_count = tiers.get(tier_name, 0)
            if actual_count != expected_count:
                log_fail(f"Stats tier {tier_name}", f"Expected {expected_count}, got {actual_count}")
                tier_match = False
        
        if tier_match:
            log_pass("Stats tiers", "All 5 tiers correct (Common:120, Rare:50, Epic:24, Legendary:5, Mythic:1)")
        
        # Check released_count
        if data.get("released_count") != 200:
            log_fail("Stats released_count", f"Expected 200, got {data.get('released_count')}")
        else:
            log_pass("Stats released_count", "All 200 released")
        
        # Check creator_wallet
        if not data.get("creator_wallet"):
            log_fail("Stats creator_wallet", "Creator wallet missing")
        else:
            log_pass("Stats creator_wallet", f"Present: {data.get('creator_wallet')}")
        
    except Exception as e:
        log_fail("Stats endpoint", f"Exception: {str(e)}")

def test_nfts_list_pagination():
    """Test 2a: GET /api/nfts - pagination"""
    print("\n" + "="*80)
    print("TEST 2a: GET /api/nfts - Pagination")
    print("="*80)
    
    try:
        # Test default pagination
        response = requests.get(f"{BASE_URL}/nfts", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFTs list pagination", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        
        # Check total
        if data.get("total") != 200:
            log_fail("NFTs list total", f"Expected 200, got {data.get('total')}")
        else:
            log_pass("NFTs list total", "200 items")
        
        # Check pagination fields
        if "page" not in data or "limit" not in data or "items" not in data:
            log_fail("NFTs list pagination fields", "Missing page/limit/items fields")
        else:
            log_pass("NFTs list pagination fields", f"page={data['page']}, limit={data['limit']}, items count={len(data['items'])}")
        
        # Test custom pagination
        response2 = requests.get(f"{BASE_URL}/nfts?page=2&limit=10", timeout=10)
        if response2.status_code == 200:
            data2 = response2.json()
            if data2.get("page") == 2 and data2.get("limit") == 10:
                log_pass("NFTs list custom pagination", "page=2, limit=10 works")
            else:
                log_fail("NFTs list custom pagination", f"Expected page=2, limit=10, got page={data2.get('page')}, limit={data2.get('limit')}")
        
    except Exception as e:
        log_fail("NFTs list pagination", f"Exception: {str(e)}")

def test_nfts_filter_mythic():
    """Test 2b: GET /api/nfts?tier=Mythic"""
    print("\n" + "="*80)
    print("TEST 2b: GET /api/nfts?tier=Mythic")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/nfts?tier=Mythic", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFTs filter Mythic", f"Expected 200, got {response.status_code}")
            return None
        
        data = response.json()
        
        # Should return exactly 1 item
        if data.get("total") != 1:
            log_fail("NFTs filter Mythic count", f"Expected 1, got {data.get('total')}")
            return None
        
        if len(data.get("items", [])) != 1:
            log_fail("NFTs filter Mythic items", f"Expected 1 item, got {len(data.get('items', []))}")
            return None
        
        mythic_item = data["items"][0]
        print(f"Mythic item: {json.dumps(mythic_item, indent=2)}")
        
        # Check name is "Genesis King"
        if mythic_item.get("name") != "Genesis King":
            log_fail("NFTs filter Mythic name", f"Expected 'Genesis King', got '{mythic_item.get('name')}'")
        else:
            log_pass("NFTs filter Mythic name", "Genesis King")
        
        # Check price_pol is 0
        if mythic_item.get("price_pol") != 0:
            log_fail("NFTs filter Mythic price", f"Expected 0 (auction), got {mythic_item.get('price_pol')}")
        else:
            log_pass("NFTs filter Mythic price", "0 (auction)")
        
        log_pass("NFTs filter Mythic", "Returns exactly 1 Genesis King with price_pol=0")
        return mythic_item.get("token_id")
        
    except Exception as e:
        log_fail("NFTs filter Mythic", f"Exception: {str(e)}")
        return None

def test_nfts_filter_legendary():
    """Test 2c: GET /api/nfts?tier=Legendary"""
    print("\n" + "="*80)
    print("TEST 2c: GET /api/nfts?tier=Legendary")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/nfts?tier=Legendary", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFTs filter Legendary", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        
        # Should return exactly 5 items
        if data.get("total") != 5:
            log_fail("NFTs filter Legendary count", f"Expected 5, got {data.get('total')}")
        else:
            log_pass("NFTs filter Legendary", "Returns exactly 5 items")
        
    except Exception as e:
        log_fail("NFTs filter Legendary", f"Exception: {str(e)}")

def test_nfts_filter_trait():
    """Test 2d: GET /api/nfts with trait filter"""
    print("\n" + "="*80)
    print("TEST 2d: GET /api/nfts?skin=Zombie")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/nfts?skin=Zombie", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFTs filter trait (skin=Zombie)", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        items = data.get("items", [])
        
        # Verify all items have Zombie skin
        all_zombie = True
        for item in items:
            if item.get("traits", {}).get("Skin") != "Zombie":
                all_zombie = False
                break
        
        if all_zombie and len(items) > 0:
            log_pass("NFTs filter trait (skin=Zombie)", f"Returns {len(items)} Zombie-skin items")
        elif len(items) == 0:
            log_warning("NFTs filter trait (skin=Zombie)", "No Zombie-skin items found")
        else:
            log_fail("NFTs filter trait (skin=Zombie)", "Some items don't have Zombie skin")
        
    except Exception as e:
        log_fail("NFTs filter trait (skin=Zombie)", f"Exception: {str(e)}")

def test_nfts_sort():
    """Test 2e: GET /api/nfts with sort"""
    print("\n" + "="*80)
    print("TEST 2e: GET /api/nfts - Sort")
    print("="*80)
    
    try:
        # Test rank_asc - Mythic should be rank 1
        response = requests.get(f"{BASE_URL}/nfts?sort=rank_asc&limit=5", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFTs sort rank_asc", f"Expected 200, got {response.status_code}")
        else:
            data = response.json()
            items = data.get("items", [])
            if len(items) > 0:
                first_item = items[0]
                if first_item.get("rank") == 1 and first_item.get("tier") == "Mythic":
                    log_pass("NFTs sort rank_asc", "Mythic is rank #1")
                else:
                    log_fail("NFTs sort rank_asc", f"First item rank={first_item.get('rank')}, tier={first_item.get('tier')}")
        
        # Test price_desc
        response2 = requests.get(f"{BASE_URL}/nfts?sort=price_desc&limit=10", timeout=10)
        if response2.status_code == 200:
            data2 = response2.json()
            items2 = data2.get("items", [])
            if len(items2) >= 2:
                prices = [item.get("price_pol", 0) for item in items2]
                is_descending = all(prices[i] >= prices[i+1] for i in range(len(prices)-1))
                if is_descending:
                    log_pass("NFTs sort price_desc", f"Prices descending: {prices[:5]}")
                else:
                    log_fail("NFTs sort price_desc", f"Prices not descending: {prices[:5]}")
        
        # Test price_asc
        response3 = requests.get(f"{BASE_URL}/nfts?sort=price_asc&limit=10", timeout=10)
        if response3.status_code == 200:
            data3 = response3.json()
            items3 = data3.get("items", [])
            if len(items3) >= 2:
                prices = [item.get("price_pol", 0) for item in items3]
                is_ascending = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
                if is_ascending:
                    log_pass("NFTs sort price_asc", f"Prices ascending: {prices[:5]}")
                else:
                    log_fail("NFTs sort price_asc", f"Prices not ascending: {prices[:5]}")
        
    except Exception as e:
        log_fail("NFTs sort", f"Exception: {str(e)}")

def test_nft_detail(mythic_token_id: int = None):
    """Test 3: GET /api/nfts/{token_id}"""
    print("\n" + "="*80)
    print("TEST 3: GET /api/nfts/{token_id}")
    print("="*80)
    
    try:
        # Test Mythic token if we have it
        if mythic_token_id:
            print(f"\nTesting Mythic token_id: {mythic_token_id}")
            response = requests.get(f"{BASE_URL}/nfts/{mythic_token_id}", timeout=10)
            
            if response.status_code != 200:
                log_fail("NFT detail Mythic", f"Expected 200, got {response.status_code}")
            else:
                data = response.json()
                print(f"Mythic detail: {json.dumps(data, indent=2)}")
                
                # Check trait_rarity_pct exists
                if "trait_rarity_pct" not in data:
                    log_fail("NFT detail Mythic trait_rarity_pct", "Missing trait_rarity_pct")
                else:
                    log_pass("NFT detail Mythic trait_rarity_pct", "Present")
                
                # Check price_pol is 0
                if data.get("price_pol") != 0:
                    log_fail("NFT detail Mythic price", f"Expected 0, got {data.get('price_pol')}")
                else:
                    log_pass("NFT detail Mythic price", "0 (auction)")
        
        # Test a normal token (token_id=10)
        print(f"\nTesting normal token_id: 10")
        response2 = requests.get(f"{BASE_URL}/nfts/10", timeout=10)
        
        if response2.status_code != 200:
            log_fail("NFT detail normal", f"Expected 200, got {response2.status_code}")
        else:
            data2 = response2.json()
            
            # Check trait_rarity_pct exists
            if "trait_rarity_pct" not in data2:
                log_fail("NFT detail normal trait_rarity_pct", "Missing trait_rarity_pct")
            else:
                log_pass("NFT detail normal trait_rarity_pct", "Present")
            
            # Check price_pol > 0
            if data2.get("price_pol", 0) <= 0:
                log_fail("NFT detail normal price", f"Expected > 0, got {data2.get('price_pol')}")
            else:
                log_pass("NFT detail normal price", f"{data2.get('price_pol')} POL")
        
    except Exception as e:
        log_fail("NFT detail", f"Exception: {str(e)}")

def test_nft_metadata(mythic_token_id: int = None):
    """Test 4: GET /api/nfts/{token_id}/metadata"""
    print("\n" + "="*80)
    print("TEST 4: GET /api/nfts/{token_id}/metadata")
    print("="*80)
    
    try:
        # Test with token_id=1
        token_id = mythic_token_id if mythic_token_id else 1
        response = requests.get(f"{BASE_URL}/nfts/{token_id}/metadata", timeout=10)
        
        if response.status_code != 200:
            log_fail("NFT metadata", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        print(f"Metadata sample: {json.dumps(data, indent=2)}")
        
        # Check OpenSea-standard fields
        required_fields = ["name", "description", "image", "attributes"]
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            log_fail("NFT metadata structure", f"Missing fields: {missing_fields}")
        else:
            log_pass("NFT metadata structure", "All required fields present (name, description, image, attributes)")
        
        # Check attributes include Rarity and Rarity Rank
        attributes = data.get("attributes", [])
        trait_types = [attr.get("trait_type") for attr in attributes]
        
        if "Rarity" not in trait_types:
            log_fail("NFT metadata Rarity", "Missing Rarity attribute")
        else:
            log_pass("NFT metadata Rarity", "Present")
        
        if "Rarity Rank" not in trait_types:
            log_fail("NFT metadata Rarity Rank", "Missing Rarity Rank attribute")
        else:
            log_pass("NFT metadata Rarity Rank", "Present")
        
    except Exception as e:
        log_fail("NFT metadata", f"Exception: {str(e)}")

def test_metadata_export():
    """Test 5: GET /api/metadata/export"""
    print("\n" + "="*80)
    print("TEST 5: GET /api/metadata/export")
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
            log_pass("Metadata export count", "200 items")
        
        # Check Mythic item is present
        mythic_found = False
        for item in data:
            # Check if this is the Mythic by looking at attributes
            attrs = item.get("attributes", [])
            for attr in attrs:
                if attr.get("trait_type") == "Rarity" and attr.get("value") == "Mythic":
                    mythic_found = True
                    print(f"Found Mythic item: {item.get('name')}")
                    break
            if mythic_found:
                break
        
        if mythic_found:
            log_pass("Metadata export Mythic", "Mythic item present in export")
        else:
            log_fail("Metadata export Mythic", "Mythic item not found in export")
        
        # Verify structure of first item
        if len(data) > 0:
            first_item = data[0]
            required_fields = ["name", "description", "image", "attributes"]
            missing_fields = [f for f in required_fields if f not in first_item]
            
            if missing_fields:
                log_fail("Metadata export item structure", f"Missing fields: {missing_fields}")
            else:
                log_pass("Metadata export item structure", "All items have required fields")
        
    except Exception as e:
        log_fail("Metadata export", f"Exception: {str(e)}")

def test_traits_endpoint():
    """Test 6: GET /api/traits"""
    print("\n" + "="*80)
    print("TEST 6: GET /api/traits")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/traits", timeout=10)
        
        if response.status_code != 200:
            log_fail("Traits endpoint", f"Expected 200, got {response.status_code}")
            return
        
        data = response.json()
        print(f"Traits response: {json.dumps(data, indent=2)}")
        
        # Check counts object exists
        if "counts" not in data:
            log_fail("Traits endpoint counts", "Missing counts object")
        else:
            counts = data["counts"]
            if isinstance(counts, dict) and len(counts) > 0:
                log_pass("Traits endpoint", f"Returns counts object with {len(counts)} categories")
            else:
                log_fail("Traits endpoint counts", "Counts object is empty or invalid")
        
    except Exception as e:
        log_fail("Traits endpoint", f"Exception: {str(e)}")

def test_waitlist():
    """Test 7: Waitlist endpoints"""
    print("\n" + "="*80)
    print("TEST 7: Waitlist endpoints")
    print("="*80)
    
    try:
        # Generate unique email for testing
        import time
        unique_email = f"test_{int(time.time())}@example.com"
        
        # Test POST /api/waitlist
        print(f"\nTesting POST /api/waitlist with {unique_email}")
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
                log_pass("Waitlist POST", f"Added email, count={data['count']}")
            else:
                log_fail("Waitlist POST", f"Unexpected response: {data}")
        
        # Test duplicate email (should return 409)
        print(f"\nTesting duplicate POST with same email")
        response2 = requests.post(
            f"{BASE_URL}/waitlist",
            json={"email": unique_email},
            timeout=10
        )
        
        if response2.status_code != 409:
            log_fail("Waitlist POST duplicate", f"Expected 409, got {response2.status_code}")
        else:
            log_pass("Waitlist POST duplicate", "Returns 409 for duplicate email")
        
        # Test GET /api/waitlist/count
        print(f"\nTesting GET /api/waitlist/count")
        response3 = requests.get(f"{BASE_URL}/waitlist/count", timeout=10)
        
        if response3.status_code != 200:
            log_fail("Waitlist GET count", f"Expected 200, got {response3.status_code}")
        else:
            data3 = response3.json()
            if "count" in data3 and isinstance(data3["count"], int):
                log_pass("Waitlist GET count", f"Returns count={data3['count']}")
            else:
                log_fail("Waitlist GET count", f"Invalid response: {data3}")
        
    except Exception as e:
        log_fail("Waitlist endpoints", f"Exception: {str(e)}")

def test_admin():
    """Test 8: Admin endpoints"""
    print("\n" + "="*80)
    print("TEST 8: Admin endpoints")
    print("="*80)
    
    try:
        # Test with correct key
        print(f"\nTesting GET /api/admin/waitlist with correct key")
        response = requests.get(
            f"{BASE_URL}/admin/waitlist",
            params={"key": ADMIN_KEY},
            timeout=10
        )
        
        if response.status_code != 200:
            log_fail("Admin waitlist correct key", f"Expected 200, got {response.status_code}")
        else:
            data = response.json()
            if "entries" in data and "count" in data:
                log_pass("Admin waitlist correct key", f"Returns {data['count']} entries")
            else:
                log_fail("Admin waitlist correct key", f"Invalid response: {data}")
        
        # Test with wrong key (should return 401)
        print(f"\nTesting GET /api/admin/waitlist with wrong key")
        response2 = requests.get(
            f"{BASE_URL}/admin/waitlist",
            params={"key": "wrongkey123"},
            timeout=10
        )
        
        if response2.status_code != 401:
            log_fail("Admin waitlist wrong key", f"Expected 401, got {response2.status_code}")
        else:
            log_pass("Admin waitlist wrong key", "Returns 401 for invalid key")
        
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
    print("HYPEBLOCK BACKEND API TEST SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin Key: {ADMIN_KEY}")
    
    # Run all tests
    test_stats_endpoint()
    test_nfts_list_pagination()
    mythic_token_id = test_nfts_filter_mythic()
    test_nfts_filter_legendary()
    test_nfts_filter_trait()
    test_nfts_sort()
    test_nft_detail(mythic_token_id)
    test_nft_metadata(mythic_token_id)
    test_metadata_export()
    test_traits_endpoint()
    test_waitlist()
    test_admin()
    
    # Print summary
    exit_code = print_summary()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
