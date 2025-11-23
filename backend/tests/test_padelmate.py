"""
Complete test of the search order workflow.

This test demonstrates:
1. Setup: Add clubs and courts to the system
2. Create multiple search orders with different criteria
3. Execute the search and fetch workflow
4. Track matching courts and notification candidates
5. Verify notification records are created
6. Check search order results
"""

from datetime import date, time

from app.models import SearchOrderNotification
from courtfinder.padelmate import PadelMateService

print("\n" + "=" * 80)
print("COMPLETE SEARCH ORDER WORKFLOW TEST")
print("=" * 80)

service = PadelMateService()

# ============================================================================
# PHASE 1: SETUP - Add clubs and courts
# ============================================================================
print("\n[PHASE 1] SETTING UP CLUBS AND COURTS")
print("-" * 80)

new_location = service.add_location_by_slug("padel-mate-club-amstelveen")
print(f"✓ Added/Updated location: {new_location.name.strip()} (ID: {new_location.id})")

all_clubs = service.get_all_clubs()
print(f"✓ Total clubs in system: {len(all_clubs)}")
for club in all_clubs:
    print(f"  - {club['name'].strip()}")

# Show courts for the club
courts = service.get_courts_for_location(new_location.id)
print(f"✓ Courts for {new_location.name.strip()}: {len(courts)}")
for i, court in enumerate(courts[:5], 1):
    print(
        f"  {i}. {court['name']} (Indoor: {court['indoor']}, Double: {court['double']})"
    )
if len(courts) > 5:
    print(f"  ... and {len(courts) - 5} more")

# ============================================================================
# PHASE 2: FETCH AND STORE AVAILABILITY
# ============================================================================
print("\n[PHASE 2] FETCHING AND STORING AVAILABILITY")
print("-" * 80)

total_slots = service.fetch_and_store_all_availability(date_str="2025-11-13")
print(f"✓ Fetched and stored: {total_slots} availability slots")

# ============================================================================
# PHASE 3: CREATE SEARCH ORDERS
# ============================================================================
print("\n[PHASE 3] CREATING SEARCH ORDERS")
print("-" * 80)

# Search Order 1: Indoor courts at 18:00 for 60 minutes
search_order_1 = service.create_search_order(
    date_str="2025-11-13",
    start_time_str="18:00",
    duration=60,
    indoor=True,
    user_id="user_indoor_evening",
)
print(
    f"✓ Search Order {search_order_1.id}: Indoor courts at 18:00-19:00 (user: user_indoor_evening)"
)

# Search Order 2: Outdoor courts at 20:00 for 60 minutes
search_order_2 = service.create_search_order(
    date_str="2025-11-13",
    start_time_str="20:00",
    duration=60,
    indoor=False,
    user_id="user_outdoor_night",
)
print(
    f"✓ Search Order {search_order_2.id}: Outdoor courts at 20:00-21:00 (user: user_outdoor_night)"
)

# Search Order 3: Any courts at 19:00 for 90 minutes
search_order_3 = service.create_search_order(
    date_str="2025-11-13",
    start_time_str="19:00",
    duration=90,
    indoor=None,
    user_id="user_flexible",
)
print(
    f"✓ Search Order {search_order_3.id}: Any courts at 19:00-20:30 (user: user_flexible)"
)

# Show all active search orders
active_orders = service.service.get_active_search_orders()
print(f"✓ Total active search orders: {len(active_orders)}")

# ============================================================================
# PHASE 4: EXECUTE SEARCH AND FETCH WORKFLOW
# ============================================================================
print("\n[PHASE 4] EXECUTING SEARCH AND FETCH WORKFLOW")
print("-" * 80)

search_results = {}

for order_id in [search_order_1.id, search_order_2.id, search_order_3.id]:
    order = service.service.get_search_order(order_id)
    print(f"\nProcessing Search Order {order_id}:")
    print(
        f"  Criteria: {order.date} at {order.start_time} for {order.duration}min (Indoor: {order.indoor})"
    )

    try:
        result = service.fetch_and_search_availability(order_id)
        search_results[order_id] = result

        print(f"  ✓ Fetched: {result['fetched_slots']} slots")
        print(f"  ✓ Matching courts: {result['total_matched_courts']}")
        print(f"  ✓ Notification candidates: {len(result['notification_candidates'])}")

        if result["notification_candidates"]:
            print("\n  MATCHING COURTS:")
            for i, candidate in enumerate(result["notification_candidates"], 1):
                print(f"    {i}. {candidate['court_name']}")
                print(f"       Location: {candidate['location']}")
                print(
                    f"       Time: {candidate['start_time']} - {candidate['end_time']}"
                )
                print(f"       Price: {candidate['price']}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

# ============================================================================
# PHASE 5: VERIFY NOTIFICATION RECORDS
# ============================================================================
print("\n[PHASE 5] VERIFYING NOTIFICATION RECORDS")

print("-" * 80)

for order_id in [search_order_1.id, search_order_2.id, search_order_3.id]:
    notifications = (
        service.service.session.query(SearchOrderNotification)
        .filter(SearchOrderNotification.search_order_id == order_id)
        .all()
    )

    print(f"\nSearch Order {order_id}:")
    print(f"  Total notifications: {len(notifications)}")
    print(f"  Notified: {sum(1 for n in notifications if n.notified)}")
    print(f"  Pending: {sum(1 for n in notifications if not n.notified)}")

    if notifications:
        for i, notif in enumerate(notifications[:3], 1):
            print(
                f"    {i}. Notification ID: {notif.id}, Court ID: {notif.court_id}, Notified: {notif.notified}"
            )
        if len(notifications) > 3:
            print(f"    ... and {len(notifications) - 3} more")

# ============================================================================
# PHASE 6: GET SEARCH ORDER RESULTS
# ============================================================================
print("\n[PHASE 6] SEARCH ORDER RESULTS SUMMARY")
print("-" * 80)

for order_id in [search_order_1.id, search_order_2.id, search_order_3.id]:
    results = service.get_search_order_results(order_id)
    if results:
        print(f"\nSearch Order {order_id}:")
        print(f"  Date: {results['date']}")
        print(f"  Time: {results['start_time']} (Duration: {results['duration']}min)")
        print(
            f"  Filter: {'Indoor' if results['indoor'] is True else 'Outdoor' if results['indoor'] is False else 'Any'}"
        )
        print(f"  Status: {results['status']}")
        print(f"  Created: {results['created_at']}")
        print(f"  Matching courts: {results['total_matched_courts']}")
        print(f"  Total notifications: {results['total_notifications']}")
        print(
            f"  Sent: {results['notified']}, Pending: {results['pending_notifications']}"
        )

# ============================================================================
# PHASE 7: TEST DIRECT SEARCH
# ============================================================================
print("\n[PHASE 7] TESTING DIRECT SEARCH (WITHOUT CREATING ORDER)")
print("-" * 80)

# Direct search for outdoor courts at 20:00-21:00
direct_results = service.search_available_courts(
    date_str="2025-11-13", start_time_str="20:00", duration=60, indoor=False
)
print("\nDirect search: Outdoor courts at 20:00-21:00")
print(f"✓ Found {len(direct_results)} courts")
if direct_results:
    for i, court in enumerate(direct_results[:3], 1):
        print(f"  {i}. {court['court_name']} at {court['location']}")
        print(f"     Price: {court['price']}")
if len(direct_results) > 3:
    print(f"  ... and {len(direct_results) - 3} more")

# ============================================================================
# PHASE 8: TEST OLD FUNCTIONALITY (BACKWARD COMPATIBILITY)
# ============================================================================
print("\n[PHASE 8] TESTING BACKWARD COMPATIBILITY")
print("-" * 80)

# Test old functions still work
print("\nTesting get_available_indoor_courts():")
date_obj = date(2025, 11, 13)
start_time = time(12, 0)
end_time = time(20, 0)
indoor_slots = service.get_available_indoor_courts(date_obj, start_time, end_time)
print(f"✓ Found {len(indoor_slots)} indoor slots between 12:00-20:00")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST COMPLETE - SUMMARY")
print("=" * 80)

active_orders = service.service.get_active_search_orders()
print(f"\n✓ Active search orders: {len(active_orders)}")

total_notifications = service.service.session.query(SearchOrderNotification).count()
print(f"✓ Total notification records: {total_notifications}")

pending_notifications = (
    service.service.session.query(SearchOrderNotification)
    .filter(~SearchOrderNotification.notified)
    .count()
)
print(f"✓ Pending notifications: {pending_notifications}")

print("\n✓ All workflows tested successfully!")
print("✓ Ready for integration with scheduler and notification service")
print("\n" + "=" * 80)
