# Court Finder Providers

This directory contains provider implementations for different court booking platforms. All providers inherit from `BaseCourtProvider` to ensure a consistent interface across different platforms.

## Architecture

### Base Class: `BaseCourtProvider`

The `BaseCourtProvider` class (in `base_provider.py`) defines the common interface that all providers must implement. It includes:

#### Abstract Methods (Must Be Implemented)

These methods **must** be implemented by every provider:

1. **`fetch_availability(tenant_id, date_str, sport_id)`**
   - Fetch raw availability data from the provider's API
   - Returns: Raw API response data

2. **`parse_availability(data, provider, location)`**
   - Parse raw API data into standardized internal format
   - Returns: List of dictionaries with standardized availability data

3. **`fetch_club_info(club_slug, date_str)`**
   - Fetch club/location information from the provider
   - Returns: Dictionary containing club information

4. **`add_location_by_slug(slug, date_str, provider_name)`**
   - Add a new location to the database using its slug/identifier
   - Returns: Location object from database

#### Common Methods (Already Implemented)

These methods are implemented in the base class and work for all providers:

- `fetch_and_store_availability()` - Fetch and store availability for a location
- `fetch_and_store_all_availability()` - Fetch for all locations
- `get_available_courts()` - Query available courts in a time range
- `get_available_indoor_courts()` - Query available indoor courts
- `search_available_courts()` - Search with flexible parameters
- `create_search_order()` - Create automated search orders
- `fetch_and_search_availability()` - Complete search workflow
- `get_search_order_results()` - Retrieve search order results
- `get_all_clubs()` - Get all clubs from database
- `get_courts_for_location()` - Get courts for a specific location

#### Optional Methods (Can Be Implemented)

These methods are provider-specific and will raise `NotImplementedError` unless overridden:

- `find_courts(location)` - Search for courts by location (if provider supports it)
- `book_court(court_id, time_slot)` - Book a court programmatically (if provider supports it)

## Existing Providers

### PlaytomicProvider (`padelmate.py`)

Provider for Playtomic.com court booking platform.

**Features:**
- Fetches availability from Playtomic API
- Scrapes club info from Playtomic web pages
- Supports automatic court discovery
- Handles indoor/outdoor and single/double court configurations

**Usage:**
```python
from app.courtfinder import PlaytomicProvider

provider = PlaytomicProvider()

# Add a new location
location = provider.add_location_by_slug("my-club-slug")

# Fetch and store availability
slots = provider.fetch_and_store_availability(location.id, "2025-11-24")

# Search for courts
results = provider.search_available_courts(
    date_str="2025-11-24",
    start_time_range_str="18:00",
    end_time_range_str="22:00",
    duration=90,
    indoor=True
)
```

**Backward Compatibility:**
The old `PadelMateService` name is still available as an alias to `PlaytomicProvider`.

## Creating a New Provider

To add support for a new court booking platform:

1. **Copy the example template:**
   ```bash
   cp backend/app/courtfinder/example_provider.py backend/app/courtfinder/your_provider.py
   ```

2. **Rename the class:**
   ```python
   class YourProviderName(BaseCourtProvider):
   ```

3. **Implement the required abstract methods:**
   - `fetch_availability()` - Call your provider's API
   - `parse_availability()` - Convert response to standard format
   - `fetch_club_info()` - Get club details
   - `add_location_by_slug()` - Add location to database

4. **Optionally implement provider-specific features:**
   - `find_courts()` - If your provider has location search
   - `book_court()` - If your provider supports programmatic booking

5. **Update `__init__.py`:**
   ```python
   from app.courtfinder.your_provider import YourProviderName

   __all__ = [..., "YourProviderName"]
   ```

6. **Test your provider:**
   ```python
   provider = YourProviderName()
   location = provider.add_location_by_slug("test-slug")
   provider.fetch_and_store_availability(location.id)
   ```

### Standard Data Format

All providers must return availability data in this format:

```python
{
    "provider": str,              # Provider name
    "court": str,                 # Court identifier from API
    "location": str,              # Location/club name
    "date": str,                  # YYYY-MM-DD format
    "timeslot": str,              # HH:MM-HH:MM format
    "price": float or str,        # Price (will be stored as string)
    "available": bool             # Availability status
}
```

## Directory Structure

```
courtfinder/
├── __init__.py              # Module exports and aliases
├── base_provider.py         # Abstract base class
├── padelmate.py            # Playtomic provider implementation
├── example_provider.py     # Template for new providers
└── README.md               # This file
```

## Benefits of This Architecture

1. **Consistency**: All providers have the same interface
2. **Reusability**: Common functionality is implemented once in the base class
3. **Extensibility**: Easy to add new providers
4. **Type Safety**: Abstract methods ensure required functionality is implemented
5. **Documentation**: Clear contract for what each provider must provide
6. **Testing**: Can test providers against the same test suite

## Testing Providers

When testing a new provider, ensure it can:

1. ✅ Fetch availability data
2. ✅ Parse data into standard format
3. ✅ Add locations by slug/identifier
4. ✅ Create and update courts
5. ✅ Handle missing or invalid data gracefully
6. ✅ Work with the common search and notification workflows

## Future Enhancements

Potential additions to the provider architecture:

- Provider registry for dynamic provider selection
- Provider-specific configuration management
- Rate limiting and caching per provider
- Provider health checks and monitoring
- Multi-provider search aggregation
- Provider comparison and price tracking
