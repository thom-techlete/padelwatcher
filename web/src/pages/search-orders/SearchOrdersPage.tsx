import { useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { searchApi, locationApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent, Button, Spinner, Alert, Badge } from '@/components/ui'
import { ListOrdered, Plus, Trash2, ToggleLeft, ToggleRight, Calendar, Clock } from 'lucide-react'
import type { SearchOrder, Location } from '@/types'

export function SearchOrdersPage() {
  const queryClient = useQueryClient()

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
            Manage your automated court availability monitoring
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
            const location = locationsMap.get(order.location_id)
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
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <div>
                      <p className="text-sm font-medium text-white">Location</p>
                      <p className="text-sm text-white">{location?.name || 'Unknown'}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white flex items-center">
                        <Calendar className="mr-1 h-4 w-4" />
                        Date Range
                      </p>
                      <p className="text-sm text-white">
                        {new Date(order.start_date).toLocaleDateString()} - {new Date(order.end_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white flex items-center">
                        <Clock className="mr-1 h-4 w-4" />
                        Time Window
                      </p>
                      <p className="text-sm text-white">
                        {order.preferred_start_time} - {order.preferred_end_time}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">Search Window</p>
                      <p className="text-sm text-white">{order.search_window_minutes} minutes</p>
                    </div>
                  </div>
                  <div className="mt-4 flex space-x-2">
                    {/* View Details link removed - detail page not implemented */}
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