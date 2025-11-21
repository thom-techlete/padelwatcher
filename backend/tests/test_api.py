#!/usr/bin/env python3
"""
Test script for Flask API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_register():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "testpass123"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code in [201, 409]  # 409 if user already exists

def test_login():
    """Test user login"""
    print("\n=== Testing Login ===")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "demo@example.com",
            "password": "demo123"
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        return data['token']
    return None

def test_locations(token):
    """Test getting locations"""
    print("\n=== Testing Get Locations ===")
    response = requests.get(
        f"{BASE_URL}/api/locations",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data.get('locations', []))} locations")
    return response.status_code == 200

def test_add_location(token):
    """Test adding a location"""
    print("\n=== Testing Add Location ===")
    response = requests.post(
        f"{BASE_URL}/api/locations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "slug": "padel-mate-amstelveen",
            "date": "2025-11-16"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code in [201, 400]  # 400 if already exists

def test_search_available(token):
    """Test searching for available courts"""
    print("\n=== Testing Search Available Courts ===")
    response = requests.post(
        f"{BASE_URL}/api/search/available",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "date": "2025-11-16",
            "start_time_range": "18:00",
            "end_time_range": "21:00",
            "duration": 60,
            "indoor": None
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data.get('count', 0)} available courts")
    return response.status_code == 200

def test_create_search_order(token):
    """Test creating a search order"""
    print("\n=== Testing Create Search Order ===")
    response = requests.post(
        f"{BASE_URL}/api/search-orders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "date": "2025-11-16",
            "start_time_range": "18:00",
            "end_time_range": "21:00",
            "duration": 60,
            "indoor": True
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 201:
        return data.get('search_order_id')
    return None

def test_get_search_orders(token):
    """Test getting user's search orders"""
    print("\n=== Testing Get Search Orders ===")
    response = requests.get(
        f"{BASE_URL}/api/search-orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data.get('search_orders', []))} search orders")
    return response.status_code == 200

def test_get_search_order_results(token, order_id):
    """Test getting search order results"""
    if not order_id:
        print("\n=== Skipping Get Search Order Results (no order_id) ===")
        return True
    
    print(f"\n=== Testing Get Search Order Results (ID: {order_id}) ===")
    response = requests.get(
        f"{BASE_URL}/api/search-orders/{order_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200

def test_unauthorized_access():
    """Test that endpoints require authentication"""
    print("\n=== Testing Unauthorized Access ===")
    response = requests.get(f"{BASE_URL}/api/locations")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 401

def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("PADEL WATCHER API TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    # Test 2: Unauthorized access
    results.append(("Unauthorized Access", test_unauthorized_access()))
    
    # Test 3: Register
    results.append(("Register User", test_register()))
    
    # Test 4: Login
    token = test_login()
    results.append(("Login", token is not None))
    
    if not token:
        print("\n❌ Cannot continue tests without token")
        return
    
    # Test 5: Get locations
    results.append(("Get Locations", test_locations(token)))
    
    # Test 6: Add location
    results.append(("Add Location", test_add_location(token)))
    
    # Test 7: Search available courts
    results.append(("Search Available Courts", test_search_available(token)))
    
    # Test 8: Create search order
    order_id = test_create_search_order(token)
    results.append(("Create Search Order", order_id is not None))
    
    # Test 9: Get search orders
    results.append(("Get Search Orders", test_get_search_orders(token)))
    
    # Test 10: Get search order results
    results.append(("Get Search Order Results", test_get_search_order_results(token, order_id)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the API is running: python api.py")
