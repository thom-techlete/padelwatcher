#!/usr/bin/env python3
"""
Simple API demo script - shows basic API usage
"""
import json

def demo():
    """Demonstrate API usage with curl examples"""
    
    print("=" * 70)
    print("PADEL WATCHER API - QUICK START DEMO")
    print("=" * 70)
    
    print("\n1. START THE API SERVER")
    print("-" * 70)
    print("Run in a separate terminal:")
    print("  python api.py")
    print("\nOr use:")
    print("  gunicorn -w 4 -b 0.0.0.0:5000 api:app")
    
    print("\n2. TEST HEALTH ENDPOINT")
    print("-" * 70)
    print("curl http://localhost:5000/health")
    
    print("\n3. LOGIN (Get JWT Token)")
    print("-" * 70)
    print("Demo credentials: demo@example.com / demo123")
    print()
    print("curl -X POST http://localhost:5000/api/auth/login \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"email\": \"demo@example.com\", \"password\": \"demo123\"}'")
    print()
    print("Save the token from the response!")
    
    print("\n4. SEARCH FOR AVAILABLE COURTS")
    print("-" * 70)
    print("curl -X POST http://localhost:5000/api/search/available \\")
    print("  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print("    \"date\": \"2025-11-16\",")
    print("    \"start_time_range\": \"18:00\",")
    print("    \"end_time_range\": \"21:00\",")
    print("    \"duration\": 60,")
    print("    \"indoor\": true")
    print("  }'")
    
    print("\n5. CREATE A SEARCH ORDER")
    print("-" * 70)
    print("curl -X POST http://localhost:5000/api/search-orders \\")
    print("  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print("    \"date\": \"2025-11-16\",")
    print("    \"start_time_range\": \"18:00\",")
    print("    \"end_time_range\": \"21:00\",")
    print("    \"duration\": 60")
    print("  }'")
    
    print("\n6. GET YOUR SEARCH ORDERS")
    print("-" * 70)
    print("curl http://localhost:5000/api/search-orders \\")
    print("  -H 'Authorization: Bearer YOUR_TOKEN_HERE'")
    
    print("\n7. ADD A NEW LOCATION")
    print("-" * 70)
    print("curl -X POST http://localhost:5000/api/locations \\")
    print("  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"slug\": \"padel-mate-amstelveen\"}'")
    
    print("\n8. FETCH AVAILABILITY DATA")
    print("-" * 70)
    print("curl -X POST http://localhost:5000/api/availability/fetch \\")
    print("  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"date\": \"2025-11-16\"}'")
    
    print("\n" + "=" * 70)
    print("PRODUCTION DEPLOYMENT")
    print("=" * 70)
    print("\nFor production, use gunicorn:")
    print("  pip install gunicorn")
    print("  gunicorn -w 4 -b 0.0.0.0:5000 api:app")
    print()
    print("Set environment variables:")
    print("  export SECRET_KEY='your-super-secret-key-here'")
    print("  export JWT_EXPIRATION_HOURS=24")
    print()
    print("See API_README.md for complete documentation.")
    print("=" * 70)

if __name__ == "__main__":
    demo()
