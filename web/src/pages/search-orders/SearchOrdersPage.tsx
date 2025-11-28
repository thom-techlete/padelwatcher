import { useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from '@tanstack/react-router'
import { searchApi, locationApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent, Button, Spinner, Alert, Badge } from '@/components/ui'
import { ListOrdered, Plus, Trash2, ToggleLeft, ToggleRight, Calendar, Clock, MapPin, Timer, Play, Search } from 'lucide-react'
import type { SearchOrder, Location } from '@/types'
import { format, parseISO } from 'date-fns'
import { useAuth } from '@/hooks/useAuth'

export function SearchOrdersPage() {
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const navigate = useNavigate()

  const { data: orders, isLoading, error } = useQuery({
    queryKey: ['search-orders'],
    queryFn: searchApi.getOrders,
  })

  // Fetch locations for mapping
  const { data: locations } = useQuery({
    queryKey: ['locations'],
    queryFn: locationApi.getAll,
  })

  const locationsMap = useMemo(() => {
    if (!locations) return new Map<number, Location>()
    return new Map(locations.map((loc: Location) => [loc.id, loc]))
  }, [locations])

  const toggleOrderMutation = useMutation({
    mutationFn: async ({ id, is_active }: { id: number; is_active: boolean }) =>
      searchApi.updateOrder(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['search-orders'] })
    },
  })

  const deleteOrderMutation = useMutation({
    mutationFn: searchApi.deleteOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['search-orders'] })
    },
  })

  const executeOrderMutation = useMutation({
    mutationFn: searchApi.executeOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['search-orders'] })
    },
  })

  const handleToggleActive = (order: SearchOrder) => {
    toggleOrderMutation.mutate({
      id: order.id,
      is_active: !order.is_active,
    })
  }

  const handleDeleteOrder = (id: number) => {
    if (confirm('Are you sure you want to delete this search order?')) {
      deleteOrderMutation.mutate(id)
    }
  }

  const handleExecuteOrder = (id: number) => {
    if (confirm('Are you sure you want to execute this search order now?')) {
      executeOrderMutation.mutate(id)
    }
  }

  const handleSearchOrder = (order: SearchOrder) => {
    // Format date from YYYY-MM-DD to DD/MM/YYYY
    const [year, month, day] = order.date.split('-')
    const formattedDate = `${day}/${month}/${year}`

    // Ensure times are in HH:MM format (strip any seconds if present)
    const formatTime = (timeStr: string) => {
      // If it's already HH:MM, return as is
      if (timeStr.match(/^\d{2}:\d{2}$/)) {
        return timeStr
      }
      // If it's HH:MM:SS, extract HH:MM
      if (timeStr.match(/^\d{2}:\d{2}:\d{2}$/)) {
        return timeStr.substring(0, 5)
      }
      return timeStr
    }

    const startTime = formatTime(order.start_time)
    const endTime = formatTime(order.end_time)

    // Navigate to search results page with order parameters
    const searchParams = new URLSearchParams({
      date: formattedDate,
      start_time: startTime,
      end_time: endTime,
      duration_minutes: order.duration_minutes.toString(),
      court_type: order.court_type,
      court_config: order.court_config,
      location_ids: order.location_ids.join(','),
      live_search: 'true'
    })

    navigate({
      to: '/search-results',
      search: Object.fromEntries(searchParams)
    })
  }

  const getLocationNames = (locationIds: number[]) => {
    const names = locationIds
      .map(id => locationsMap.get(id)?.name)
      .filter(Boolean)

    if (names.length === 0) return 'Unknown'
    if (names.length === 1) return names[0]
    if (names.length === 2) return names.join(' & ')
    return `${names[0]} & ${names.length - 1} more`
  }

  const getCourtTypeLabel = (courtType: string) => {
    switch (courtType) {
      case 'indoor': return 'Indoor Only'
      case 'outdoor': return 'Outdoor Only'
      default: return 'All Courts'
    }
  }

  const getCourtConfigLabel = (courtConfig: string) => {
    switch (courtConfig) {
      case 'single': return 'Single'
      case 'double': return 'Double'
      default: return 'All'
    }
  }

  const formatLastCheckTime = (timestamp: string | undefined) => {
    if (!timestamp) return 'Never'
    try {
      const date = parseISO(timestamp)
      // Get current user's timezone offset
      const offset = new Date().getTimezoneOffset()
      // Adjust the date by adding the offset (getTimezoneOffset returns negative for ahead of UTC)
      const adjustedDate = new Date(date.getTime() - offset * 60 * 1000)
      return format(adjustedDate, 'HH:mm')
    } catch {
      return 'Invalid'
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
        <Alert variant="error">
          Failed to load search orders: {error.message}
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Search Orders</h1>
          <p className="text-white/80 mt-2">
            Automated court availability monitoring (checks every 15 minutes)
          </p>
        </div>
        <Link to="/orders/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Order
          </Button>
        </Link>
      </div>

      {!orders || orders.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <ListOrdered className="h-12 w-12 text-white mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground mb-2">No search orders yet</h3>
            <p className="text-white text-center mb-6">
              Create your first search order to automatically monitor court availability
            </p>
            <Link to="/orders/new">
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Order
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {orders.map((order: SearchOrder) => {
            const locationNames = getLocationNames(order.location_ids)
            return (
              <Card key={order.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center">
                      <ListOrdered className="mr-2 h-5 w-5" />
                      Order #{order.id}
                    </CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge variant={order.is_active ? 'default' : 'secondary'}>
                        {order.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      {order.last_check_at && (
                        <Badge variant="outline" className="text-xs">
                          Last check: {formatLastCheckTime(order.last_check_at)}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <div>
                      <p className="text-sm font-medium text-white flex items-center">
                        <MapPin className="mr-1 h-4 w-4" />
                        Locations
                      </p>
                      <p className="text-sm text-white" title={order.location_ids.map(id => locationsMap.get(id)?.name).join(', ')}>
                        {locationNames}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white flex items-center">
                        <Calendar className="mr-1 h-4 w-4" />
                        Date
                      </p>
                      <p className="text-sm text-white">
                        {format(parseISO(order.date), 'MMM d, yyyy')}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white flex items-center">
                        <Clock className="mr-1 h-4 w-4" />
                        Time Window
                      </p>
                      <p className="text-sm text-white">
                        {order.start_time} - {order.end_time}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white flex items-center">
                        <Timer className="mr-1 h-4 w-4" />
                        Duration
                      </p>
                      <p className="text-sm text-white">{order.duration_minutes} minutes</p>
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <Badge variant="outline">{getCourtTypeLabel(order.court_type)}</Badge>
                    <Badge variant="outline">{getCourtConfigLabel(order.court_config)}</Badge>
                  </div>
                  <div className="mt-4 flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleSearchOrder(order)}
                      className="text-green-600 hover:text-green-700"
                    >
                      <Search className="mr-2 h-4 w-4" />
                      Search Now
                    </Button>
                    {user?.is_admin && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleExecuteOrder(order.id)}
                        disabled={executeOrderMutation.isPending}
                        className="text-blue-600 hover:text-blue-700"
                      >
                        <Play className="mr-2 h-4 w-4" />
                        Execute Now
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggleActive(order)}
                      disabled={toggleOrderMutation.isPending}
                    >
                      {order.is_active ? (
                        <>
                          <ToggleRight className="mr-2 h-4 w-4" />
                          Deactivate
                        </>
                      ) : (
                        <>
                          <ToggleLeft className="mr-2 h-4 w-4" />
                          Activate
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteOrder(order.id)}
                      disabled={deleteOrderMutation.isPending}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
