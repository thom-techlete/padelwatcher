import { Link } from '@tanstack/react-router'
import { useAuth } from '@/contexts'
import { Card, CardHeader, CardTitle, CardContent, Button } from '@/components/ui'
import { Search, ListOrdered, MapPin, TrendingUp, Dumbbell, Users } from 'lucide-react'

export function DashboardPage() {
  const { user } = useAuth()

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
            <div className="text-2xl text-accent-300 font-bold">0</div>
            <p className="text-xs text-white mt-1">No active search orders</p>
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
            <div className="text-2xl text-accent-300 font-bold">0</div>
            <p className="text-xs text-white mt-1">Add locations to track</p>
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
            <div className="text-2xl text-accent-300 font-bold">0</div>
            <p className="text-xs text-white mt-1">Start searching courts</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link to="/search">
              <Button className="w-full justify-start" variant="outline">
                <Search className="mr-2 h-4 w-4" />
                Search for Available Courts
              </Button>
            </Link>
            <Link to="/orders">
              <Button className="w-full justify-start" variant="outline">
                <ListOrdered className="mr-2 h-4 w-4" />
                Manage Search Orders
              </Button>
            </Link>
            <Link to="/locations">
              <Button className="w-full justify-start" variant="outline">
                <MapPin className="mr-2 h-4 w-4" />
                Browse Locations
              </Button>
            </Link>
            <Link to="/courts">
              <Button className="w-full justify-start" variant="outline">
                <Dumbbell className="mr-2 h-4 w-4" />
                View All Courts
              </Button>
            </Link>
            {user?.is_admin && (
              <Link to="/admin">
                <Button className="w-full justify-start" variant="outline">
                  <Users className="mr-2 h-4 w-4" />
                  Admin Panel
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-white/60">
              <p className="text-sm">No recent activity</p>
              <p className="text-xs mt-2">Start by creating a search order</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-2 text-sm text-white">
            <li>Add locations you're interested in tracking</li>
            <li>Search for available courts at specific times</li>
            <li>Create search orders to monitor availability automatically</li>
            <li>Get notified when courts become available</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  )
}
