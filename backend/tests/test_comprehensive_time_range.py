#!/usr/bin/env python3
"""
Test script demonstrating time range search functionality
"""
from datetime import date, time

from courtfinder.padelmate import PadelMateService
from services import AvailabilityService


def test_time_range_functionality():
    """Test the new time range search functionality"""
    service = PadelMateService()
    avail_service = AvailabilityService()

    print("=== TIME RANGE SEARCH FUNCTIONALITY TEST ===\n")

    # First, let's add some test availability data
    print("1. Adding test availability data...")

    # Create test location and court if they don't exist
    provider = avail_service.get_or_create_provider("TestProvider")
    location = avail_service.get_or_create_location("Test Club", provider.id)
    court = avail_service.get_or_create_court("Court 1", location.id)

    # Add availability slots for different times
    test_date = date(2025, 11, 15)
    availabilities = [
        # 60-minute slots
        (time(17, 0), time(18, 0), 60, "25.00 EUR"),  # 17:00-18:00
        (time(18, 0), time(19, 0), 60, "27.50 EUR"),  # 18:00-19:00
        (time(19, 0), time(20, 0), 60, "27.50 EUR"),  # 19:00-20:00
        (time(20, 0), time(21, 0), 60, "30.00 EUR"),  # 20:00-21:00
        (time(21, 0), time(22, 0), 60, "30.00 EUR"),  # 21:00-22:00
        # 90-minute slots
        (time(18, 30), time(20, 0), 90, "35.00 EUR"),  # 18:30-20:00
        (time(19, 30), time(21, 0), 90, "35.00 EUR"),  # 19:30-21:00
    ]

    for start_time, end_time, duration, price in availabilities:
        from models import Availability

        avail = Availability(
            court_id=court.id,
            date=test_date,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            price=price,
            available=True,
        )
        avail_service.add_availability(avail)

    print(f"   ✓ Added {len(availabilities)} test availability slots")

    # Test 1: Search for 60-minute slots between 18:00 and 21:00
    print("\n2. Test 1: Search for 60-minute slots between 18:00 and 21:00")
    results = service.search_available_courts(
        date_str="2025-11-15",
        start_time_range_str="18:00",
        end_time_range_str="21:00",
        duration=60,
    )

    print(f"   Found {len(results)} available courts:")
    for court_info in results:
        print(f"   - {court_info['court_name']} at {court_info['location']}")
        print(
            f"     Time: {court_info['start_time']} - {court_info['end_time']} | Price: {court_info['price']}"
        )

    # Should find: 18:00-19:00, 19:00-20:00, 20:00-21:00
    expected_times = ["18:00:00", "19:00:00", "20:00:00"]
    found_times = [r["start_time"] for r in results]
    if set(found_times) == set(expected_times):
        print("   ✓ Found expected time slots!")
    else:
        print(f"   ✗ Expected {expected_times}, found {found_times}")

    # Test 2: Search for 60-minute slots between 17:00 and 19:00
    print("\n3. Test 2: Search for 60-minute slots between 17:00 and 19:00")
    results = service.search_available_courts(
        date_str="2025-11-15",
        start_time_range_str="17:00",
        end_time_range_str="19:00",
        duration=60,
    )

    print(f"   Found {len(results)} available courts:")
    for court_info in results:
        print(f"   - Time: {court_info['start_time']} - {court_info['end_time']}")

    # Should find: 17:00-18:00, 18:00-19:00
    expected_times = ["17:00:00", "18:00:00"]
    found_times = [r["start_time"] for r in results]
    if set(found_times) == set(expected_times):
        print("   ✓ Found expected time slots!")
    else:
        print(f"   ✗ Expected {expected_times}, found {found_times}")

    # Test 3: Search for 90-minute slots between 18:00 and 21:00
    print("\n4. Test 3: Search for 90-minute slots between 18:00 and 21:00")
    results = service.search_available_courts(
        date_str="2025-11-15",
        start_time_range_str="18:00",
        end_time_range_str="21:00",
        duration=90,
    )

    print(f"   Found {len(results)} available courts:")
    for court_info in results:
        print(f"   - Time: {court_info['start_time']} - {court_info['end_time']}")

    # Should find: 18:30-20:00 and 19:30-21:00 (both fit within 21:00 end time)
    expected_times = ["18:30:00", "19:30:00"]
    found_times = [r["start_time"] for r in results]
    if set(found_times) == set(expected_times):
        print("   ✓ Found expected time slots!")
    else:
        print(f"   ✗ Expected {expected_times}, found {found_times}")

    # Test 4: Create a search order with time range
    print(
        "\n5. Test 4: Create search order with time range 18:00-21:00 for 60min slots"
    )
    search_order = service.create_search_order(
        date_str="2025-11-15",
        start_time_range_str="18:00",
        end_time_range_str="21:00",
        duration=60,
        indoor=None,
        user_id="test_user",
    )

    print(f"   ✓ Created search order {search_order.id}")

    # Get search order results
    order_results = service.get_search_order_results(search_order.id)
    print("   Search order details:")
    print(f"     Date: {order_results['date']}")
    print(
        f"     Time range: {order_results['start_time_range']} - {order_results['end_time_range']}"
    )
    print(f"     Duration: {order_results['duration']} minutes")
    print(f"     Matching courts: {order_results['total_matched_courts']}")

    print("\n=== TIME RANGE TEST COMPLETE ===")


if __name__ == "__main__":
    test_time_range_functionality()
