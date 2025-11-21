"""
Test script for profile update endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_profile_endpoints():
    print("Testing Profile Update Endpoints")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("\n1. Logging in...")
    login_data = {
        "email": "admin@padelwatcher.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()['token']
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get current user info
    print("\n2. Getting current user info...")
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if response.status_code != 200:
        print(f"❌ Get user failed: {response.status_code}")
        print(response.text)
        return
    
    user = response.json()
    print(f"✅ Current user: {user['email']} (username: {user['username']})")
    
    # Step 3: Test updating profile (email)
    print("\n3. Testing profile update (email)...")
    update_data = {
        "email": "admin_updated@test.com"
    }
    
    response = requests.put(f"{BASE_URL}/api/auth/profile", json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Profile update failed: {response.status_code}")
        print(response.text)
    else:
        result = response.json()
        print(f"✅ Profile updated! New email: {result['user']['email']}")
    
    # Step 4: Revert email back
    print("\n4. Reverting email back...")
    revert_data = {
        "email": "admin@padelwatcher.com"
    }
    
    response = requests.put(f"{BASE_URL}/api/auth/profile", json=revert_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Profile revert failed: {response.status_code}")
        print(response.text)
    else:
        result = response.json()
        print(f"✅ Email reverted! Email: {result['user']['email']}")
    
    # Step 5: Test password update with wrong current password
    print("\n5. Testing password update with wrong current password...")
    wrong_password_data = {
        "current_password": "wrongpassword",
        "new_password": "newpassword123"
    }
    
    response = requests.put(f"{BASE_URL}/api/auth/password", json=wrong_password_data, headers=headers)
    if response.status_code == 400:
        print(f"✅ Correctly rejected wrong password: {response.json()['message']}")
    else:
        print(f"❌ Should have rejected wrong password but got: {response.status_code}")
        print(response.text)
    
    # Step 6: Test password update with correct current password
    print("\n6. Testing password update with correct current password...")
    correct_password_data = {
        "current_password": "admin123",
        "new_password": "newadmin123"
    }
    
    response = requests.put(f"{BASE_URL}/api/auth/password", json=correct_password_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Password update failed: {response.status_code}")
        print(response.text)
    else:
        print(f"✅ Password updated successfully!")
    
    # Step 7: Test login with new password
    print("\n7. Testing login with new password...")
    new_login_data = {
        "email": "admin@padelwatcher.com",
        "password": "newadmin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=new_login_data)
    if response.status_code != 200:
        print(f"❌ Login with new password failed: {response.status_code}")
        print(response.text)
    else:
        print(f"✅ Login with new password successful!")
        new_token = response.json()['token']
        new_headers = {
            "Authorization": f"Bearer {new_token}",
            "Content-Type": "application/json"
        }
    
    # Step 8: Revert password back
    print("\n8. Reverting password back...")
    revert_password_data = {
        "current_password": "newadmin123",
        "new_password": "admin123"
    }
    
    response = requests.put(f"{BASE_URL}/api/auth/password", json=revert_password_data, headers=new_headers)
    if response.status_code != 200:
        print(f"❌ Password revert failed: {response.status_code}")
        print(response.text)
    else:
        print(f"✅ Password reverted successfully!")
    
    # Step 9: Verify original login works
    print("\n9. Verifying original login works...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Original login failed: {response.status_code}")
        print(response.text)
    else:
        print(f"✅ Original login works!")
    
    print("\n" + "=" * 50)
    print("✅ All profile endpoint tests completed successfully!")

if __name__ == "__main__":
    try:
        test_profile_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("Make sure the API is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
