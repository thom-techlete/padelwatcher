import { useEffect, useState, useCallback, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useSearch } from '@tanstack/react-router'
import { Card, CardHeader, CardTitle, CardContent, Button, Progress, Alert, Badge } from '@/components/ui'
import { Search, Clock, MapPin, ArrowLeft, Euro, Zap, ExternalLink, XCircle, Loader2 } from 'lucide-react'
import { useNavigate } from '@tanstack/react-router'
import { searchApi } from '@/lib/api'
import { useAuth } from '@/contexts'
import type { SearchTask, SearchResult } from '@/types'

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

type SearchState = 'idle' | 'starting' | 'polling' | 'completed' | 'failed' | 'cancelled'

export function SearchResultsPage() {
  const navigate = useNavigate()
  const params = useSearch({ from: '/search-results' }) as SearchParams
  const { user } = useAuth()

  // State for task-based search
  const [searchState, setSearchState] = useState<SearchState>('idle')
  const [taskId, setTaskId] = useState<string | null>(null)
  const [taskStatus, setTaskStatus] = useState<SearchTask | null>(null)
  const [results, setResults] = useState<SearchResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Polling interval reference
  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  // Track if search has been initiated to avoid re-triggering
  const searchInitiatedRef = useRef(false)

  // Start search task mutation
  const startTaskMutation = useMutation({
    mutationFn: async () => {
      const locationIds = params.location_ids
        ? params.location_ids.split(',').map(Number).filter(id => !isNaN(id))
        : undefined

      const courtType = (params.court_type || 'all') as 'all' | 'indoor' | 'outdoor'
      const courtConfig = (params.court_config || 'all') as 'all' | 'single' | 'double'
      const forceLiveSearch = params.force_live_search === 'true'

      return await searchApi.startSearchTask({
        date: params.date,
        start_time: params.start_time,
        end_time: params.end_time,
        duration_minutes: Number(params.duration_minutes),
        court_type: courtType,
        court_config: courtConfig,
        location_ids: locationIds,
        force_live_search: forceLiveSearch,
      })
    },
    onSuccess: (data) => {
      setTaskId(data.task_id)
      setSearchState('polling')
    },
    onError: (err: Error) => {
      setError(err.message)
      setSearchState('failed')
    },
  })

  // Cancel task mutation
  const cancelTaskMutation = useMutation({
    mutationFn: async () => {
      if (!taskId) throw new Error('No task to cancel')
      return await searchApi.cancelSearchTask(taskId)
    },
    onSuccess: () => {
      setSearchState('cancelled')
      stopPolling()
    },
  })

  // Stop polling
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
  }, [])

  // Poll for task status
  const pollTaskStatus = useCallback(async () => {
    if (!taskId) return

    try {
      const status = await searchApi.getSearchTaskStatus(taskId)
      setTaskStatus(status)

      if (status.status === 'completed' && status.results) {
        setResults(status.results)
        setSearchState('completed')
        stopPolling()
      } else if (status.status === 'failed') {
        setError(status.error_message || 'Search failed')
        setSearchState('failed')
        stopPolling()
      } else if (status.status === 'cancelled') {
        setSearchState('cancelled')
        stopPolling()
      }
    } catch (err) {
      console.error('Error polling task status:', err)
    }
  }, [taskId, stopPolling])

  // Start polling when we have a task ID
  useEffect(() => {
    if (searchState === 'polling' && taskId) {
      // Set up polling interval (every 500ms for responsive updates)
      // The first poll happens via setTimeout to avoid synchronous setState
      const initialPollTimeout = setTimeout(pollTaskStatus, 0)
      pollingIntervalRef.current = setInterval(pollTaskStatus, 200)

      return () => {
        clearTimeout(initialPollTimeout)
        stopPolling()
      }
    }
  }, [searchState, taskId, pollTaskStatus, stopPolling])

  // Start search when page loads
  useEffect(() => {
    if (params.date && !searchInitiatedRef.current) {
      searchInitiatedRef.current = true
      // Use setTimeout to avoid synchronous setState in effect
      setTimeout(() => {
        setSearchState('starting')
        startTaskMutation.mutate()
      }, 0)
    }
  }, [params.date, startTaskMutation])

  // Cleanup on unmount
  useEffect(() => {
    return () => stopPolling()
  }, [stopPolling])

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

  // Render loading/progress state
  if (searchState === 'starting' || searchState === 'polling') {
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
          <h1 className="text-3xl font-bold text-white">Searching Courts</h1>
          <p className="text-white/80 mt-2">
            {formatDate(params.date)}
          </p>
        </div>

        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Loader2 className="mr-2 h-5 w-5 animate-spin text-accent-400" />
              Searching for available courts...
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <Progress
              value={taskStatus?.progress || 0}
              showLabel
              label={taskStatus?.current_step || 'Initializing search...'}
              size="lg"
              variant="accent"
            />

            {taskStatus && taskStatus.total_locations > 0 && (
              <div className="flex justify-between text-sm text-white/70">
                <span>
                  Processing location {taskStatus.processed_locations} of {taskStatus.total_locations}
                </span>
                <span>
                  {Math.round((taskStatus.processed_locations / taskStatus.total_locations) * 100)}% complete
                </span>
              </div>
            )}

            <div className="flex justify-center pt-4">
              <Button
                variant="outline"
                onClick={() => cancelTaskMutation.mutate()}
                disabled={cancelTaskMutation.isPending}
                className="text-red-400 border-red-400/50 hover:bg-red-400/10"
              >
                <XCircle className="mr-2 h-4 w-4" />
                Cancel Search
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Render error state
  if (searchState === 'failed' || error) {
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
          Search failed: {error || 'An unknown error occurred'}
        </Alert>
        <div className="mt-4 flex justify-center">
          <Button onClick={() => {
            setError(null)
            setSearchState('idle')
            setTaskId(null)
            setTaskStatus(null)
          }}>
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  // Render cancelled state
  if (searchState === 'cancelled') {
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
        <Card className="max-w-2xl mx-auto">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <XCircle className="h-12 w-12 text-yellow-400 mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">Search Cancelled</h3>
            <p className="text-white/70 text-center mb-6">
              The search was cancelled before completion.
            </p>
            <Button onClick={() => navigate({ to: '/search', search: params })}>
              Start New Search
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Calculate total courts and slots from the results
  const totalCourts = results?.locations?.reduce((sum, loc) => sum + loc.courts.length, 0) || 0
  const totalSlots = results?.locations?.reduce((sum, loc) =>
    sum + loc.courts.reduce((courtSum, court) => courtSum + court.availabilities.length, 0), 0
  ) || 0

  // Render results
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
                to: '/search-results',
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
