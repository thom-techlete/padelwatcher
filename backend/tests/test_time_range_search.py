#!/usr/bin/env python3
"""
Test script for time range search functionality
"""
from datetime import date, time
from courtfinder.padelmate import PadelMateService

def test_time_range_search():
    """Test searching for courts within a time range"""
    service = PadelMateService()

    # Create a search order for 60-minute slots between 18:00 and 21:00
    search_order = service.create_search_order(
        date_str="2025-11-15",
        start_time_range_str="18:00",
        end_time_range_str="21:00",
        duration=60,
        indoor=None,
        user_id="test_user"
    )

    print(f"Created search order {search_order.id} for time range 18:00-21:00, 60min duration")

    # Test the search functionality
    results = service.search_available_courts(
        date_str="2025-11-15",
        start_time_range_str="18:00",
        end_time_range_str="21:00",
        duration=60
    )

    print(f"Found {len(results)} available courts in time range")

    # Show search order details
    order_details = service.get_search_order_results(search_order.id)
    print("Search order details:")
    print(f"  Date: {order_details['date']}")
    print(f"  Time range: {order_details['start_time_range']} - {order_details['end_time_range']}")
    print(f"  Duration: {order_details['duration']} minutes")
    print(f"  Status: {order_details['status']}")

    return search_order.id

if __name__ == "__main__":
    test_time_range_search()