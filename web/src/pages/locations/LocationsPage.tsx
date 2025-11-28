import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { locationApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent, Button, Spinner, Alert, Dialog } from '@/components/ui'
import { MapPin, Plus, Gamepad2 } from 'lucide-react'
import { AddLocationForm } from '@/components/forms/AddLocationForm'
import { useAuth } from '@/hooks/useAuth'
import type { Location, Court } from '@/types'

interface Address {
  street?: string
  postal_code?: string
  city?: string
  sub_administrative_area?: string
  administrative_area?: string
  country?: string
  country_code?: string
  coordinate?: {
    lat: number
    lon: number
  }
  timezone?: string
}

function formatAddress(addressData: string | Address | undefined): string {
  if (!addressData) return 'No address available'

  try {
    // Handle both string (JSON) and object (JSONB) formats
    const address: Address = typeof addressData === 'string'
      ? JSON.parse(addressData)
      : addressData

    const parts = []
    if (address.street) parts.push(address.street)
    if (address.postal_code && address.city) {
      parts.push(`${address.postal_code} ${address.city}`)
    } else if (address.city) {
      parts.push(address.city)
    }
    if (address.country) parts.push(address.country)

    return parts.length > 0 ? parts.join(', ') : 'No address available'
  } catch {
    return 'No address available' // Fallback if parsing fails
  }
}

export function LocationsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [expandedLocations, setExpandedLocations] = useState<Set<number>>(new Set())
  const { isAuthenticated } = useAuth()
  const { data: locations, isLoading, error } = useQuery({
    queryKey: ['locations'],
    queryFn: locationApi.getAll,
  })

  const toggleLocationExpanded = (locationId: number) => {
    setExpandedLocations(prev => {
      const newSet = new Set(prev)
      if (newSet.has(locationId)) {
        newSet.delete(locationId)
      } else {
        newSet.add(locationId)
      }
      return newSet
    })
  }

  // Get courts for expanded locations
  const expandedLocationIds = Array.from(expandedLocations)
  const { data: courtsData } = useQuery({
    queryKey: ['courts', expandedLocationIds],
    queryFn: async (): Promise<Record<number, Court[]>> => {
      if (expandedLocationIds.length === 0) return {}

      const results: Record<number, Court[]> = {}
      await Promise.all(
        expandedLocationIds.map(async (locationId) => {
          try {
            results[locationId] = await locationApi.getCourts(locationId)
          } catch (error) {
            console.error(`Failed to load courts for location ${locationId}:`, error)
            results[locationId] = []
          }
        })
      )
      return results
    },
    enabled: expandedLocationIds.length > 0,
  })

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
          Failed to load locations: {error.message}
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Locations</h1>
          <p className="text-white/80 mt-2">
            Browse and manage padel court locations
          </p>
        </div>
        {isAuthenticated && (
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Location
          </Button>
        )}
      </div>

      {!locations || locations.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <MapPin className="h-12 w-12 text-white mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground mb-2">No locations yet</h3>
            <p className="text-white text-center mb-6">
              {isAuthenticated
                ? "Add your first location to start tracking court availability"
                : "Please log in to add locations"
              }
            </p>
            {isAuthenticated && (
              <Button onClick={() => setIsModalOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Location
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {locations.map((location: Location) => {
            const isExpanded = expandedLocations.has(location.id)
            const locationCourts = courtsData?.[location.id] || []

            return (
              <Card key={location.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="truncate">{location.name}</span>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleLocationExpanded(location.id)}
                        className="text-accent-400 hover:text-accent-300"
                      >
                        {isExpanded ? 'Hide Courts' : 'View Courts'}
                      </Button>
                      <MapPin className="h-5 w-5 text-white flex-shrink-0 ml-2" />
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-white">
                    <p><strong>Provider:</strong> {location.provider}</p>
                    {location.city && <p><strong>City:</strong> {location.city}</p>}
                    {location.address && <p><strong>Address:</strong> {formatAddress(location.address)}</p>}
                    {location.phone && <p><strong>Phone:</strong> {location.phone}</p>}
                  </div>

                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-white/10">
                      <div className="flex items-center gap-2 mb-3">
                        <Gamepad2 className="h-4 w-4 text-accent-400" />
                        <span className="text-sm font-medium text-white">
                          Courts ({locationCourts.length})
                        </span>
                      </div>

                      {locationCourts.length === 0 ? (
                        <p className="text-sm text-white/60">No courts found</p>
                      ) : (
                        <div className="space-y-2">
                          {locationCourts.map((court) => (
                            <div
                              key={court.id}
                              className="flex items-center justify-between p-2 bg-white/5 rounded-md"
                            >
                              <div className="flex items-center gap-2">
                                <Gamepad2 className="h-3 w-3 text-accent-400" />
                                <span className="text-sm text-white">{court.name}</span>
                              </div>
                              <div className="flex gap-1">
                                {court.indoor && (
                                  <span className="px-1.5 py-0.5 text-xs bg-blue-500/20 text-blue-300 rounded">
                                    Indoor
                                  </span>
                                )}
                                {court.double && (
                                  <span className="px-1.5 py-0.5 text-xs bg-green-500/20 text-green-300 rounded">
                                    Double
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  <div className="mt-4 flex space-x-2">
                    {/* View Details link removed - detail page not implemented */}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {isAuthenticated && (
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <Dialog.Content>
            <Dialog.Header>
              <Dialog.Title>Add New Location</Dialog.Title>
              <Dialog.Description>
                Enter the location slug or full Playtomic URL to add a new padel court location
              </Dialog.Description>
            </Dialog.Header>
            <AddLocationForm onSuccess={() => setIsModalOpen(false)} />
          </Dialog.Content>
        </Dialog>
      )}
    </div>
  )
}
