#!/usr/bin/env python
"""Test authentication flow to debug 401 errors"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Test 1: Login
print("=" * 60)
print("TEST 1: Login")
print("=" * 60)
login_data = {
    "email": "admin@padelwatcher.com",
    "password": "admin123"
}

response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    token = response.json()['token']
    print(f"\nToken (first 50 chars): {token[:50]}...")
    
    # Test 2: Get current user
    print("\n" + "=" * 60)
    print("TEST 2: Get current user (/api/auth/me)")
    print("=" * 60)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print(f"Authorization header: Bearer {token[:30]}...")
    
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 3: Get all users (admin endpoint)
    print("\n" + "=" * 60)
    print("TEST 3: Get all users (/api/admin/users)")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 4: Get pending users
    print("\n" + "=" * 60)
    print("TEST 4: Get pending users (/api/admin/users/pending)")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/admin/users/pending", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print("\nLogin failed! Cannot proceed with further tests.")
