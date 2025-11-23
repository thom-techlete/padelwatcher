import { Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/contexts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui'
import { Search, ListOrdered, MapPin, TrendingUp, Signpost, Users } from 'lucide-react'
import { searchApi } from '@/lib/api/search'
import { locationApi } from '@/lib/api/locations'

export function DashboardPage() {
  const { user } = useAuth()

  const { data: orders, isLoading: ordersLoading } = useQuery({
    queryKey: ['search-orders'],
    queryFn: searchApi.getOrders,
  })

  const { data: locations, isLoading: locationsLoading } = useQuery({
    queryKey: ['locations'],
    queryFn: locationApi.getAll,
  })

  const activeOrders = orders?.filter(order => order.is_active) || []
  const trackedLocations = locations || []
  const searchesToday = orders?.filter(order => {
    const createdDate = new Date(order.created_at).toDateString()
    const today = new Date().toDateString()
    return createdDate === today
  }) || []
  const recentActivity = orders?.sort((a, b) =>
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ).slice(0, 5) || []

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">
          Welcome back, {user?.username}!
        </h1>
        <p className="text-white/80 mt-2">
          Track padel court availability and manage your search orders
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-white">
              Active Orders
            </CardTitle>
            <ListOrdered className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-accent-300 font-bold">
              {ordersLoading ? '...' : activeOrders.length}
            </div>
            <p className="text-xs text-white mt-1">
              {activeOrders.length === 0 ? 'No active search orders' : `active search order${activeOrders.length === 1 ? '' : 's'}`}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-white">
              Tracked Locations
            </CardTitle>
            <MapPin className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-accent-300 font-bold">
              {locationsLoading ? '...' : trackedLocations.length}
            </div>
            <p className="text-xs text-white mt-1">
              {trackedLocations.length === 0 ? 'Add locations to track' : `location${trackedLocations.length === 1 ? '' : 's'} tracked`}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-white">
              New Notifications
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-accent-300 font-bold">0</div>
            <p className="text-xs text-white mt-1">All caught up!</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-white">
              Searches Today
            </CardTitle>
            <Search className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-accent-300 font-bold">
              {ordersLoading ? '...' : searchesToday.length}
            </div>
            <p className="text-xs text-white mt-1">
              {searchesToday.length === 0 ? 'Start searching courts' : `${searchesToday.length} search${searchesToday.length === 1 ? '' : 'es'} today`}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-1 mb-8">
        <Card className="">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <Link to="/search" className="group">
                <div className="h-full p-4 rounded-lg bg-gradient-to-br from-accent-500/10 to-accent-500/5 border border-accent-500/30 group-hover:border-accent-500/60 group-hover:bg-accent-500/15 transition-all">
                  <Search className="h-6 w-6 text-accent-500 mb-2" />
                  <h3 className="text-sm font-semibold text-white group-hover:text-accent-300">Search Courts</h3>
                  <p className="text-xs text-white/60 mt-1">Find available padel courts</p>
                </div>
              </Link>
              <Link to="/orders" className="group">
                <div className="h-full p-4 rounded-lg bg-gradient-to-br from-accent-500/10 to-accent-500/5 border border-accent-500/30 group-hover:border-accent-500/60 group-hover:bg-accent-500/15 transition-all">
                  <ListOrdered className="h-6 w-6 text-accent-500 mb-2" />
                  <h3 className="text-sm font-semibold text-white group-hover:text-accent-300">Search Orders</h3>
                  <p className="text-xs text-white/60 mt-1">Manage your orders</p>
                </div>
              </Link>
              <Link to="/locations" className="group">
                <div className="h-full p-4 rounded-lg bg-gradient-to-br from-accent-500/10 to-accent-500/5 border border-accent-500/30 group-hover:border-accent-500/60 group-hover:bg-accent-500/15 transition-all">
                  <MapPin className="h-6 w-6 text-accent-500 mb-2" />
                  <h3 className="text-sm font-semibold text-white group-hover:text-accent-300">Locations</h3>
                  <p className="text-xs text-white/60 mt-1">Browse all locations</p>
                </div>
              </Link>
              <Link to="/courts" className="group">
                <div className="h-full p-4 rounded-lg bg-gradient-to-br from-accent-500/10 to-accent-500/5 border border-accent-500/30 group-hover:border-accent-500/60 group-hover:bg-accent-500/15 transition-all">
                  <Signpost className="h-6 w-6 text-accent-500 mb-2" />
                  <h3 className="text-sm font-semibold text-white group-hover:text-accent-300">All Courts</h3>
                  <p className="text-xs text-white/60 mt-1">View all available courts</p>
                </div>
              </Link>
              {user?.is_admin && (
                <Link to="/admin" className="group">
                  <div className="h-full p-4 rounded-lg bg-gradient-to-br from-accent-500/10 to-accent-500/5 border border-accent-500/30 group-hover:border-accent-500/60 group-hover:bg-accent-500/15 transition-all">
                    <Users className="h-6 w-6 text-accent-500 mb-2" />
                    <h3 className="text-sm font-semibold text-white group-hover:text-accent-300">Admin Panel</h3>
                    <p className="text-xs text-white/60 mt-1">Manage system</p>
                  </div>
                </Link>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {ordersLoading ? (
              <div className="text-center py-8 text-white/60">
                <p className="text-sm">Loading...</p>
              </div>
            ) : recentActivity.length === 0 ? (
              <div className="text-center py-8 text-white/60">
                <p className="text-sm">No recent activity</p>
                <p className="text-xs mt-2">Start by creating a search order</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentActivity.map((order) => (
                  <div key={order.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <ListOrdered className="h-4 w-4 text-accent-300" />
                      <div>
                        <p className="text-sm font-medium text-white">
                          Search Order #{order.id}
                        </p>
                        <p className="text-xs text-white/60">
                          {new Date(order.date).toLocaleDateString()} • {order.start_time} - {order.end_time}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`text-xs px-2 py-1 rounded ${
                        order.is_active
                          ? 'bg-green-500/20 text-green-300'
                          : 'bg-gray-500/20 text-gray-300'
                      }`}>
                        {order.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
