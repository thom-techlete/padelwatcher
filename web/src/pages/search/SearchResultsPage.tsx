import { useQuery } from '@tanstack/react-query'
import { useSearch } from '@tanstack/react-router'
import { Card, CardHeader, CardTitle, CardContent, Button, Spinner, Alert, Badge } from '@/components/ui'
import { Search, Clock, MapPin, ArrowLeft, Euro, Zap, ExternalLink } from 'lucide-react'
import { useNavigate } from '@tanstack/react-router'
import { searchApi } from '@/lib/api'
import { useAuth } from '@/contexts'

interface SearchParams {
  date: string
  start_time: string
  end_time: string
  duration_minutes: string
  court_type?: string
  court_config?: string
  location_ids?: string
  live_search?: string
  force_live_search?: string
}

interface Address {
  street?: string
  city?: string
  postal_code?: string
}

export function SearchResultsPage() {
  const navigate = useNavigate()
  const params = useSearch({ from: '/search-results' }) as SearchParams
  const { user } = useAuth()

  const { data: results, isLoading, error } = useQuery({
    queryKey: ['search-results', params],
    queryFn: async () => {
      const locationIds = params.location_ids
        ? params.location_ids.split(',').map(Number).filter(id => !isNaN(id))
        : undefined

      const courtType = (params.court_type || 'all') as 'all' | 'indoor' | 'outdoor'
      const courtConfig = (params.court_config || 'all') as 'all' | 'single' | 'double'
      const liveSearch = params.live_search === 'true'
      const forceLiveSearch = params.force_live_search === 'true'

      const searchData = {
        date: params.date,
        start_time: params.start_time,
        end_time: params.end_time,
        duration_minutes: Number(params.duration_minutes),
        court_type: courtType,
        court_config: courtConfig,
        location_ids: locationIds,
        live_search: liveSearch,
        force_live_search: forceLiveSearch,
      }

      return await searchApi.searchAvailable(searchData)
    },
    enabled: !!params.date,
  })

  // Helper function to format address from JSON or object
  const formatAddress = (address: string | Address) => {
    try {
      let addressObj: Address

      // Handle both JSON string and object formats
      if (typeof address === 'string') {
        addressObj = JSON.parse(address)
      } else {
        addressObj = address
      }

      const parts = []
      if (addressObj.street) parts.push(addressObj.street)
      if (addressObj.city) parts.push(addressObj.city)
      if (addressObj.postal_code) parts.push(addressObj.postal_code)
      return parts.join(', ')
    } catch {
      return typeof address === 'string' ? address : 'Address not available'
    }
  }

  // Helper function to format time in 24-hour format
  const formatTime = (timeStr: string) => {
    try {
      const [hours, minutes] = timeStr.split(':')
      return `${hours}:${minutes}`
    } catch {
      return timeStr
    }
  }

  // Helper function to format date in friendly format
  const formatDate = (dateStr: string) => {
    try {
      const [day, month, year] = dateStr.split('/')
      const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
      return date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
    } catch {
      return dateStr
    }
  }


  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center">
          <Spinner />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate({ to: '/search' })}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Search
          </Button>
        </div>
        <Alert variant="error">
          Search failed: {error.message}
        </Alert>
      </div>
    )
  }

  // Calculate total courts and slots from the API response
  const totalCourts = results?.locations?.reduce((sum, loc) => sum + loc.courts.length, 0) || 0
  const totalSlots = results?.locations?.reduce((sum, loc) =>
    sum + loc.courts.reduce((courtSum, court) => courtSum + court.availabilities.length, 0), 0
  ) || 0

  function calculateDuration(start_time: string, end_time: string): string {
    try {
      const start = new Date(`2000-01-01T${start_time}`)
      const end = new Date(`2000-01-01T${end_time}`)
      const diffMs = end.getTime() - start.getTime()
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      return `${diffMinutes} min`
    } catch {
      return 'Unknown'
    }
  }

  console.log('Search Results:', results)

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <Button
            variant="ghost"
            onClick={() => navigate({
              to: '/search',
              search: params
            })}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Search
          </Button>
          {user?.is_admin && (
            <Button
              variant="outline"
              onClick={() => navigate({
                to: '/search',
                search: {
                  ...params,
                  force_live_search: 'true'
                }
              })}
              className="flex items-center"
            >
              <Zap className="mr-2 h-4 w-4" />
              Force Live Fetch
            </Button>
          )}
        </div>
        <h1 className="text-3xl font-bold text-white">Search Results</h1>
        <p className="text-white/80 mt-2">
          {formatDate(params.date)}
        </p>
        <p className="text-white/70 mt-1 text-sm">
          Showing available courts between {formatTime(params.start_time)} - {formatTime(params.end_time)}
        </p>
      </div>

      {!results?.locations || results.locations.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Search className="h-12 w-12 text-white/60 mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No courts available</h3>
            <p className="text-white/70 text-center mb-6">
              Try adjusting your search parameters or expanding your time window
            </p>
            <Button onClick={() => navigate({
              to: '/search',
              search: params
            })}>
              New Search
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white">Courts Found</h2>
              {results.cached && results.cache_timestamp && (
                <p className="text-sm text-white/70 mt-1">
                  Using cached data from {new Date(results.cache_timestamp).toLocaleString()}
                </p>
              )}
            </div>
            <Badge variant="secondary">{totalCourts} courts · {totalSlots} slots</Badge>
          </div>

          {results.locations.map((locationGroup) => (
            <div key={locationGroup.location.id} className="space-y-4">
              <div className="border-b border-white/20 pb-2 flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-white flex items-center">
                    <MapPin className="mr-2 h-5 w-5" />
                    {locationGroup.location.name}
                  </h3>
                  <p className="text-sm text-white/70 mt-1">
                    {locationGroup.location.address ? formatAddress(locationGroup.location.address) : 'Address not available'}
                  </p>
                </div>
                <a
                  href={`https://playtomic.com/clubs/${locationGroup.location.slug}?date=${params.date.split('/').reverse().join('-')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-accent-400 hover:text-accent-300 transition-colors whitespace-nowrap"
                >
                  <ExternalLink className="h-4 w-4" />
                  View on Playtomic
                </a>
              </div>

              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {locationGroup.courts.map((courtItem) => (
                  <Card key={courtItem.court.id} className="hover:shadow-md transition-shadow flex flex-col">
                    <CardHeader>
                      <div className="space-y-2">
                        <CardTitle className="flex items-center justify-between">
                          <span className="truncate text-lg">
                            {courtItem.court.name || 'Unnamed Court'}
                          </span>
                          <div className="flex gap-1">
                            <Badge variant="outline" className="text-xs">
                              {courtItem.court.is_indoor ? 'Indoor' : 'Outdoor'}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {courtItem.court.is_double ? 'Double' : 'Single'}
                            </Badge>
                          </div>
                        </CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col">
                      <div className="space-y-3 flex-1">
                        <h4 className="font-medium text-white">Available Slots ({courtItem.availabilities.length})</h4>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                          {courtItem.availabilities.map((availability: { id: number; date: string; start_time: string; end_time: string; price?: number; booking_url?: string }) => (
                            <div
                              key={availability.id}
                              className="p-3 bg-white/10 rounded-md border border-white/20"
                            >
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center space-x-2 flex-1">
                                    <Clock className="h-4 w-4 text-accent-400 flex-shrink-0" />
                                    <div>
                                      <div className="text-sm font-semibold text-white">
                                        {formatTime(availability.start_time)} - {formatTime(availability.end_time)}
                                      </div>
                                      <div className="text-xs text-white/70">
                                        Duration: {calculateDuration(availability.start_time, availability.end_time)}
                                      </div>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                                    {availability.price && (
                                      <div className="text-right">
                                        <div className="flex items-center text-sm font-bold text-accent-400">
                                          <Euro className="h-4 w-4 mr-1" />
                                          {availability.price}
                                        </div>
                                      </div>
                                    )}
                                    {availability.booking_url && (
                                      <a
                                        href={availability.booking_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-accent-400 hover:text-accent-300 transition-colors flex-shrink-0"
                                        title="Book this slot"
                                      >
                                        <ExternalLink className="h-5 w-5" />
                                      </a>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="mt-4 pt-4 border-t">
                        <a
                          href={`https://playtomic.com/clubs/${locationGroup.location.slug}?date=${params.date.split('/').reverse().join('-')}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center justify-center w-full gap-2 px-4 py-2 text-sm font-medium bg-accent-500 text-white hover:bg-accent-600 transition-colors rounded-md"
                        >
                          <ExternalLink className="h-4 w-4" />
                          Book Now
                        </a>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
