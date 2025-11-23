import { useQuery } from '@tanstack/react-query'
import { locationApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent, Spinner, Alert, Badge } from '@/components/ui'
import { Dumbbell, Home, Trees, User, Users } from 'lucide-react'
import type { Location, Court } from '@/types'

export function CourtsPage() {
  const { data: locations, isLoading: locationsLoading, error: locationsError } = useQuery({
    queryKey: ['locations'],
    queryFn: locationApi.getAll,
  })

  if (locationsLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center">
          <Spinner />
        </div>
      </div>
    )
  }

  if (locationsError) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="error">
          Failed to load locations: {locationsError.message}
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Courts</h1>
        <p className="text-white/80 mt-2">
          Browse all available padel courts across locations
        </p>
      </div>

      {!locations || locations.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Dumbbell className="h-12 w-12 text-white mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground mb-2">No locations found</h3>
            <p className="text-white text-center">
              Add locations first to view their courts
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-8">
          {locations.map((location: Location) => (
            <LocationCourts key={location.id} location={location} />
          ))}
        </div>
      )}
    </div>
  )
}

interface LocationCourtsProps {
  location: Location
}

function LocationCourts({ location }: LocationCourtsProps) {
  const { data: courts, isLoading, error } = useQuery({
    queryKey: ['courts', location.id],
    queryFn: () => locationApi.getCourts(location.id),
  })

  return (
    <div>
      <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
        <Dumbbell className="mr-2 h-5 w-5" />
        {location.name}
      </h2>

      {isLoading ? (
        <div className="flex justify-center py-4">
          <Spinner size="sm" />
        </div>
      ) : error ? (
        <Alert variant="error" className="mb-4">
          Failed to load courts: {error.message}
        </Alert>
      ) : !courts || courts.length === 0 ? (
        <Card>
          <CardContent className="py-8">
            <p className="text-white text-center">No courts available at this location</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {courts.map((court: Court) => (
            <Card key={court.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">{court.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    {court.indoor ? (
                      <Badge variant="outline" className="flex items-center">
                        <Home className="mr-1 h-3 w-3" />
                        Indoor
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="flex items-center">
                        <Trees className="mr-1 h-3 w-3" />
                        Outdoor
                      </Badge>
                    )}
                    {court.double ? (
                      <Badge variant="outline" className="flex items-center">
                        <Users className="mr-1 h-3 w-3" />
                        Double
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="flex items-center">
                        <User className="mr-1 h-3 w-3" />
                        Single
                      </Badge>
                    )
                    }
                  </div>
                  <p className="text-sm text-white">
                    Location: {location.name}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
