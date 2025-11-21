"""
Test script to demonstrate the search order workflow.

Flow:
1. User creates a search order (date, time, duration, indoor/outdoor)
2. Periodically search and fetch availability
3. Track matches and notification candidates
"""

from courtfinder.padelmate import PadelMateService
from datetime import date, time
import json

service = PadelMateService()

print("=" * 80)
print("PADEL WATCHER - SEARCH ORDER WORKFLOW TEST")
print("=" * 80)

# First, ensure we have data by adding the clubs
print("\n1. Setting up clubs...")
try:
    club1 = service.add_location_by_slug("padel-mate-club-amstelveen")
    print(f"   ✓ Added/Updated: {club1.name.strip()}")
except Exception as e:
    print(f"   ⚠ Club 1: {e}")

try:
    club2 = service.add_location_by_slug("padel-mate-club-ntc-de-kegel")
    print(f"   ✓ Added/Updated: {club2.name.strip()}")
except Exception as e:
    print(f"   ⚠ Club 2: {e}")

# Create search orders
print("\n2. Creating search orders...")
search_date = date(2025, 11, 13)
search_time = time(18, 0)
duration = 60

# Search order 1: Indoor courts at 18:00 for 60 mins
search_order_1 = service.create_search_order(
    date_str="2025-11-13",
    start_time_range_str="18:00",
    end_time_range_str="18:00",  # Same as start for exact time match
    duration=60,
    indoor=True,
    user_id="user123"
)
print(f"   ✓ Created search order {search_order_1.id}: Indoor courts at 18:00-19:00")

# Search order 2: Outdoor courts at 20:00 for 60 mins
search_order_2 = service.create_search_order(
    date_str="2025-11-13",
    start_time_range_str="20:00",
    end_time_range_str="20:00",  # Same as start for exact time match
    duration=60,
    indoor=False,
    user_id="user456"
)
print(f"   ✓ Created search order {search_order_2.id}: Outdoor courts at 20:00-21:00")

# Search order 3: Any courts at 19:00 for 90 mins
search_order_3 = service.create_search_order(
    date_str="2025-11-13",
    start_time_range_str="19:00",
    end_time_range_str="19:00",  # Same as start for exact time match
    duration=90,
    indoor=None,
    user_id="user789"
)
print(f"   ✓ Created search order {search_order_3.id}: Any courts at 19:00-20:30")

# Test the search and fetch workflow
print("\n3. Executing search and fetch workflow (this runs every 15 mins)...")
print(f"   Search Order {search_order_1.id}: Indoor courts at 18:00-19:00")
try:
    result = service.fetch_and_search_availability(search_order_1.id)
    print(f"   ✓ Fetched {result['fetched_slots']} slots")
    print(f"   ✓ Found {result['total_matched_courts']} matching courts")
    print(f"   ✓ {len(result['notification_candidates'])} new notification candidates")
    
    if result['notification_candidates']:
        print("\n   NOTIFICATION CANDIDATES FOR SEARCH ORDER 1:")
        for i, candidate in enumerate(result['notification_candidates'], 1):
            print(f"      {i}. {candidate['court_name']} at {candidate['location']}")
            print(f"         Time: {candidate['start_time']} - {candidate['end_time']} | Price: {candidate['price']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print(f"\n   Search Order {search_order_2.id}: Outdoor courts at 20:00-21:00")
try:
    result = service.fetch_and_search_availability(search_order_2.id)
    print(f"   ✓ Fetched {result['fetched_slots']} slots")
    print(f"   ✓ Found {result['total_matched_courts']} matching courts")
    print(f"   ✓ {len(result['notification_candidates'])} new notification candidates")
    
    if result['notification_candidates']:
        print("\n   NOTIFICATION CANDIDATES FOR SEARCH ORDER 2:")
        for i, candidate in enumerate(result['notification_candidates'], 1):
            print(f"      {i}. {candidate['court_name']} at {candidate['location']}")
            print(f"         Time: {candidate['start_time']} - {candidate['end_time']} | Price: {candidate['price']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print(f"\n   Search Order {search_order_3.id}: Any courts at 19:00-20:30")
try:
    result = service.fetch_and_search_availability(search_order_3.id)
    print(f"   ✓ Fetched {result['fetched_slots']} slots")
    print(f"   ✓ Found {result['total_matched_courts']} matching courts")
    print(f"   ✓ {len(result['notification_candidates'])} new notification candidates")
    
    if result['notification_candidates']:
        print("\n   NOTIFICATION CANDIDATES FOR SEARCH ORDER 3:")
        for i, candidate in enumerate(result['notification_candidates'], 1):
            print(f"      {i}. {candidate['court_name']} at {candidate['location']}")
            print(f"         Time: {candidate['start_time']} - {candidate['end_time']} | Price: {candidate['price']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Show search order results
print("\n4. Search order results summary...")
for order_id in [search_order_1.id, search_order_2.id, search_order_3.id]:
    results = service.get_search_order_results(order_id)
    if results:
        print(f"\n   Search Order {order_id}:")
        print(f"      Date: {results['date']}, Time Range: {results['start_time_range']}-{results['end_time_range']}, Duration: {results['duration']}min")
        print(f"      Status: {results['status']}")
        print(f"      Matching courts: {results['total_matched_courts']}")
        print(f"      Notifications: {results['notified']} sent, {results['pending_notifications']} pending")

# Test direct search without creating order
print("\n5. Testing direct search (without creating order)...")
direct_results = service.search_available_courts(
    date_str="2025-11-13",
    start_time_range_str="20:00",
    end_time_range_str="20:00",  # Same as start for exact time match
    duration=60,
    indoor=False
)
print(f"   Found {len(direct_results)} outdoor courts at 20:00-21:00")
if direct_results:
    for i, court in enumerate(direct_results[:3], 1):
        print(f"      {i}. {court['court_name']} at {court['location']}")
        print(f"         Time: {court['start_time']} - {court['end_time']} | Price: {court['price']}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
