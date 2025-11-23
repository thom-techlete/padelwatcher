import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi, locationApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent, Button, Alert, Spinner, Input, Label } from '@/components/ui'
import { CheckCircle2, XCircle, Users, UserCheck, UserX, MapPin, Plus, Trash2, Database } from 'lucide-react'
import { formatDate } from '@/lib/utils'

export function AdminPage() {
  const [locationSlug, setLocationSlug] = useState('')
  const [cacheOlderThan, setCacheOlderThan] = useState('')
  const queryClient = useQueryClient()

  const { data: users, isLoading } = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: adminApi.getUsers,
  })

  const { data: pendingUsers } = useQuery({
    queryKey: ['admin', 'pending-users'],
    queryFn: adminApi.getPendingUsers,
  })

  const { data: locations } = useQuery({
    queryKey: ['locations'],
    queryFn: locationApi.getAll,
  })

  const approveMutation = useMutation({
    mutationFn: adminApi.approveUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin'] })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: adminApi.rejectUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin'] })
    },
  })

  const activateMutation = useMutation({
    mutationFn: adminApi.activateUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin'] })
    },
  })

  const deactivateMutation = useMutation({
    mutationFn: adminApi.deactivateUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin'] })
    },
  })

  const deleteLocationMutation = useMutation({
    mutationFn: adminApi.deleteLocation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
    },
  })

  const addLocationMutation = useMutation({
    mutationFn: adminApi.addLocation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
      setLocationSlug('')
    },
  })

  const clearCacheMutation = useMutation({
    mutationFn: (olderThanMinutes?: number) => adminApi.clearCache(olderThanMinutes),
    onSuccess: () => {
      // Optionally invalidate search-related queries
      queryClient.invalidateQueries({ queryKey: ['search'] })
    },
  })

  const refreshAllDataMutation = useMutation({
    mutationFn: adminApi.refreshAllData,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
      queryClient.invalidateQueries({ queryKey: ['admin'] })
    },
  })

  const handleAddLocation = (e: React.FormEvent) => {
    e.preventDefault()
    if (locationSlug.trim()) {
      let slug = locationSlug.trim()
      // Extract slug from full URL if provided
      if (slug.includes('/clubs/')) {
        const parts = slug.split('/clubs/')
        if (parts.length > 1) {
          slug = parts[1].split(/[/?]/)[0] // Take everything before / or ?
        }
      }
      addLocationMutation.mutate(slug)
    }
  }

  const handleClearCache = () => {
    const olderThanMinutes = cacheOlderThan ? parseInt(cacheOlderThan) : undefined
    clearCacheMutation.mutate(olderThanMinutes)
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 flex justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  const pendingCount = pendingUsers?.length || 0
  const approvedCount = users?.filter(u => u.approved).length || 0
  const totalUsers = users?.length || 0

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
        <p className="text-white/80 mt-2">Manage users and system settings</p>
      </div>

      {/* Stats */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-white">
              Total Users
            </CardTitle>
            <Users className="h-4 w-4 text-white" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalUsers}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-white">
              Approved Users
            </CardTitle>
            <UserCheck className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-400">{approvedCount}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-white">
              Pending Approval
            </CardTitle>
            <UserX className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">{pendingCount}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-white">
              Total Locations
            </CardTitle>
            <MapPin className="h-4 w-4 text-accent-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-accent-400">{locations?.length || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Pending Approvals */}
      {pendingCount > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Pending Approvals</CardTitle>
          </CardHeader>
          <CardContent>
            <Alert variant="warning" className="mb-4">
              {pendingCount} user{pendingCount !== 1 ? 's' : ''} waiting for approval
            </Alert>
            <div className="space-y-4">
              {pendingUsers?.map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-4 border border-white/20 rounded-lg bg-white/5"
                >
                  <div>
                    <p className="font-medium text-white">{user.username}</p>
                    <p className="text-sm text-white/80">{user.email}</p>
                    <p className="text-xs text-white/50 mt-1">
                      Registered {formatDate(user.created_at)}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="default"
                      onClick={() => approveMutation.mutate(user.id)}
                      disabled={approveMutation.isPending}
                    >
                      <CheckCircle2 className="h-4 w-4 mr-1" />
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => rejectMutation.mutate(user.id)}
                      disabled={rejectMutation.isPending}
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      Reject
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* All Users */}
      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {users?.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between p-4 border border-white/20 rounded-lg bg-white/5"
              >
                <div className="flex items-center gap-4">
                  <div>
                    <p className="font-medium text-white">{user.username}</p>
                    <p className="text-sm text-white/80">{user.email}</p>
                  </div>
                  {user.is_admin && (
                    <span className="px-2 py-1 text-xs font-medium bg-accent-500/20 text-accent-300 rounded">
                      Admin
                    </span>
                  )}
                  {user.approved ? (
                    <span className="px-2 py-1 text-xs font-medium bg-green-500/20 text-green-300 rounded">
                      Approved
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-medium bg-yellow-500/20 text-yellow-300 rounded">
                      Pending
                    </span>
                  )}
                  {user.approved && (
                    user.active ? (
                      <span className="px-2 py-1 text-xs font-medium bg-accent-500/20 text-accent-300 rounded">
                        Active
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-red-500/20 text-red-300 rounded">
                        Inactive
                      </span>
                    )
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {user.approved && (
                    <>
                      {user.active ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => deactivateMutation.mutate(user.id)}
                          disabled={deactivateMutation.isPending}
                        >
                          Deactivate
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => activateMutation.mutate(user.id)}
                          disabled={activateMutation.isPending}
                        >
                          Activate
                        </Button>
                      )}
                    </>
                  )}
                  <p className="text-xs text-white/50">
                    Joined {formatDate(user.created_at)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Location Management */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Location Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <h3 className="text-lg font-medium mb-4 text-white">Add New Location</h3>
            <form onSubmit={handleAddLocation} className="flex gap-4">
              <div className="flex-1">
                <Label htmlFor="location-slug">Location Slug</Label>
                <Input
                  id="location-slug"
                  type="text"
                  placeholder="e.g., club-name-city or https://playtomic.com/clubs/club-name-city"
                  value={locationSlug}
                  onChange={(e) => setLocationSlug(e.target.value)}
                  className="mt-1"
                />
                <p className="text-sm text-white/70 mt-1">
                  Enter the slug identifier or full URL for the location (slug will be extracted automatically from URLs)
                </p>
              </div>
              <div className="flex items-center">
                <Button
                  type="submit"
                  disabled={addLocationMutation.isPending || !locationSlug.trim()}
                >
                  {addLocationMutation.isPending ? <Spinner size="sm" /> : <Plus className="h-4 w-4 mr-2" />}
                  {addLocationMutation.isPending ? 'Adding...' : 'Add Location'}
                </Button>
              </div>
            </form>
            {addLocationMutation.isSuccess && (
              <Alert variant="success" className="mt-4">
                Location added successfully!
              </Alert>
            )}
            {addLocationMutation.isError && (
              <Alert variant="error" className="mt-4">
                Failed to add location: {addLocationMutation.error?.message}
              </Alert>
            )}
          </div>

          {/* Existing Locations */}
          <div className="mt-8 pt-8 border-t border-white/10">
            <h3 className="text-lg font-medium mb-4 text-white">Existing Locations ({locations?.length || 0})</h3>
            {!locations || locations.length === 0 ? (
              <p className="text-white/70">No locations added yet.</p>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {locations.map((location) => (
                  <div
                    key={location.id}
                    className="p-4 border border-white/20 rounded-lg bg-white/5"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center">
                        <MapPin className="h-5 w-5 text-accent-400 mr-2 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-white">{location.name}</p>
                          <p className="text-sm text-white/80">Slug: {location.slug}</p>
                          {location.city && (
                            <p className="text-sm text-white/80">City: {location.city}</p>
                          )}
                        </div>
                      </div>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => {
                          if (confirm(`Are you sure you want to delete the location "${location.name}"? This will also delete all associated courts and availability data.`)) {
                            deleteLocationMutation.mutate(location.id)
                          }
                        }}
                        disabled={deleteLocationMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Cache Management */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Cache Management
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-white/80 mb-4">
                Clear the search cache to force fresh data fetching. This will remove cached search results and require new API calls for subsequent searches.
              </p>

              <div className="flex gap-4 items-center">
                <div className="flex-1">
                  <Label htmlFor="cache-older-than">Clear cache older than (minutes)</Label>
                  <Input
                    id="cache-older-than"
                    type="number"
                    placeholder="Leave empty to clear all cache"
                    value={cacheOlderThan}
                    onChange={(e) => setCacheOlderThan(e.target.value)}
                    className="mt-1"
                    min="1"
                  />
                  <p className="text-xs text-white/50 mt-1">
                    Optional: Only clear cache entries older than the specified minutes. Leave empty to clear all cache.
                  </p>
                </div>
                <Button
                  variant="destructive"
                  onClick={handleClearCache}
                  disabled={clearCacheMutation.isPending}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  {clearCacheMutation.isPending ? 'Clearing...' : 'Clear Cache'}
                </Button>
              </div>
            </div>

            {clearCacheMutation.isSuccess && (
              <Alert variant="success">
                {clearCacheMutation.data?.message}
              </Alert>
            )}
            {clearCacheMutation.isError && (
              <Alert variant="error">
                Failed to clear cache: {clearCacheMutation.error?.message}
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Data Refresh */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Data Refresh
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-white/80 mb-4">
                Refresh all location data by clearing and re-fetching court information from Playtomic. This will delete all courts and availability data, then re-download them from the API while keeping the location records.
              </p>

              <Button
                variant="destructive"
                onClick={() => {
                  if (confirm('This will delete all courts and availability data and re-fetch them from the API. This may take a while. Continue?')) {
                    refreshAllDataMutation.mutate()
                  }
                }}
                disabled={refreshAllDataMutation.isPending}
              >
                <Database className="h-4 w-4 mr-2" />
                {refreshAllDataMutation.isPending ? 'Refreshing...' : 'Refresh All Data'}
              </Button>
            </div>

            {refreshAllDataMutation.isSuccess && (
              <Alert variant="success">
                {refreshAllDataMutation.data?.message}
              </Alert>
            )}
            {refreshAllDataMutation.isError && (
              <Alert variant="error">
                Failed to refresh data: {refreshAllDataMutation.error?.message}
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
