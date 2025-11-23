import { useMemo } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, useSearch } from '@tanstack/react-router'
import { locationApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent, Button, Label, MultiSelect, Select, Spinner, DatePicker, Checkbox, TimePicker } from '@/components/ui'
import { Search, RefreshCw, Zap } from 'lucide-react'
import { format, parse } from 'date-fns'
import { useAuth } from '@/contexts'

interface SearchParams {
  date?: string
  start_time?: string
  end_time?: string
  duration_minutes?: string
  court_type?: string
  court_config?: string
  location_ids?: string
  live_search?: string
  force_live_search?: string
}

interface SearchForm {
  location_ids: number[]
  date: Date | null
  start_time: string
  end_time: string
  duration_minutes: number
  court_type: 'all' | 'indoor' | 'outdoor'
  court_config: 'all' | 'single' | 'double'
  live_search: boolean
  force_live_search: boolean
}

export function SearchPage() {
  const navigate = useNavigate()
  const params = useSearch({ from: '/search' }) as SearchParams
  const { user } = useAuth()
  const { data: locations = [], isLoading: locationsLoading } = useQuery({
    queryKey: ['locations'],
    queryFn: () => locationApi.getAll(),
  })

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<SearchForm>({
    defaultValues: {
      location_ids: params.location_ids
        ? params.location_ids.split(',').map(Number).filter(id => !isNaN(id))
        : locations.map(l => l.id),
      date: params.date ? parse(params.date, 'dd/MM/yyyy', new Date()) : new Date(),
      start_time: params.start_time || '17:00',
      end_time: params.end_time || '22:00',
      duration_minutes: params.duration_minutes ? Number(params.duration_minutes) : 90,
      court_type: (params.court_type as 'all' | 'indoor' | 'outdoor') || 'indoor',
      court_config: (params.court_config as 'all' | 'single' | 'double') || 'double',
      live_search: params.live_search === 'true',
      force_live_search: params.force_live_search === 'true',
    },
  })

  const onSubmit = async (data: SearchForm) => {
    if (!data.date) return

    // Navigate to search results page with query parameters
    navigate({
      to: '/search-results',
      search: {
        date: format(data.date, 'dd/MM/yyyy'),
        start_time: data.start_time,
        end_time: data.end_time,
        duration_minutes: String(data.duration_minutes),
        court_type: data.court_type,
        court_config: data.court_config,
        location_ids: data.location_ids.join(','),
        live_search: data.live_search ? 'true' : 'false',
        force_live_search: data.force_live_search ? 'true' : 'false',
      },
    })
  }

  const locationOptions = useMemo(
    () =>
      locations.map(location => ({
        value: location.id,
        label: location.name,
      })),
    [locations]
  )

  return (
    <div className="min-h-screen bg-secondary-800 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Search className="w-5 h-5 text-accent-500" />
              Search for Court Availability
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-6">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Location Selection */}
              <div>
                <Label>Locations</Label>
                <Controller
                  name="location_ids"
                  control={control}
                  rules={{
                    validate: (value) =>
                      value.length > 0 || 'Select at least one location',
                  }}
                  render={({ field }) => (
                    <MultiSelect
                      options={locationOptions}
                      value={field.value}
                      onChange={field.onChange}
                      placeholder="Select locations..."
                    />
                  )}
                />
                {errors.location_ids && (
                  <p className="text-sm text-red-500 mt-1">
                    {errors.location_ids.message}
                  </p>
                )}
              </div>

              {/* Date Selection */}
              <div>
                <Label>Date</Label>
                <Controller
                  name="date"
                  control={control}
                  rules={{ required: 'Date is required' }}
                  render={({ field }) => (
                    <DatePicker
                      value={field.value || undefined}
                      onChange={field.onChange}
                    />
                  )}
                />
                {errors.date && (
                  <p className="text-sm text-red-500 mt-1">
                    {errors.date.message}
                  </p>
                )}
              </div>

              {/* Time Range */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Start Time</Label>
                  <Controller
                    name="start_time"
                    control={control}
                    rules={{ required: 'Start time is required' }}
                    render={({ field }) => (
                      <TimePicker
                        value={field.value}
                        onChange={field.onChange}
                      />
                    )}
                  />
                  {errors.start_time && (
                    <p className="text-sm text-red-500 mt-1">
                      {errors.start_time.message}
                    </p>
                  )}
                </div>
                <div>
                  <Label>End Time</Label>
                  <Controller
                    name="end_time"
                    control={control}
                    rules={{
                      required: 'End time is required',
                      validate: (value) => {
                        const startTime = watch('start_time')
                        return value > startTime || 'End time must be after start time'
                      },
                    }}
                    render={({ field }) => (
                      <TimePicker
                        value={field.value}
                        onChange={field.onChange}
                      />
                    )}
                  />
                  {errors.end_time && (
                    <p className="text-sm text-red-500 mt-1">
                      {errors.end_time.message}
                    </p>
                  )}
                </div>
              </div>

              {/* Duration Selection */}
              <div>
                <Label>Court Duration</Label>
                <Controller
                  name="duration_minutes"
                  control={control}
                  rules={{ required: 'Duration is required' }}
                  render={({ field }) => (
                    <Select
                      options={[
                        { value: '60', label: '60 minutes' },
                        { value: '90', label: '90 minutes' },
                        { value: '120', label: '120 minutes' },
                      ]}
                      value={String(field.value)}
                      onChange={(e) => field.onChange(parseInt(e.target.value))}
                    />
                  )}
                />
                {errors.duration_minutes && (
                  <p className="text-sm text-red-500 mt-1">
                    {errors.duration_minutes.message}
                  </p>
                )}
              </div>

              {/* Court Type Filter */}
              <div>
                <Label>Court Type</Label>
                <Controller
                  name="court_type"
                  control={control}
                  render={({ field }) => (
                    <Select
                      options={[
                        { value: 'all', label: 'All Courts' },
                        { value: 'indoor', label: 'Indoor Only' },
                        { value: 'outdoor', label: 'Outdoor Only' },
                      ]}
                      value={field.value}
                      onChange={(e) => field.onChange(e.target.value)}
                    />
                  )}
                />
              </div>

              {/* Court Configuration Filter */}
              <div>
                <Label>Court Configuration</Label>
                <Controller
                  name="court_config"
                  control={control}
                  render={({ field }) => (
                    <Select
                      options={[
                        { value: 'all', label: 'All Configurations' },
                        { value: 'single', label: 'Single Courts' },
                        { value: 'double', label: 'Double Courts' },
                      ]}
                      value={field.value}
                      onChange={(e) => field.onChange(e.target.value)}
                    />
                  )}
                />
              </div>

              {/* Live Search Option */}
              <div className="flex items-center space-x-2">
                <Controller
                  name="live_search"
                  control={control}
                  render={({ field }) => (
                    <Checkbox
                      id="live_search"
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  )}
                />
                <div className="grid gap-1.5 leading-none">
                  <Label
                    htmlFor="live_search"
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center gap-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Live Search
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    Fetch fresh availability data from booking platform (slower but most up-to-date)
                  </p>
                </div>
              </div>

              {/* Force Live Fetch Option (Admin Only) */}
              {user?.is_admin && (
                <div className="flex items-center space-x-2">
                  <Controller
                    name="force_live_search"
                    control={control}
                    render={({ field }) => (
                      <Checkbox
                        id="force_live_search"
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    )}
                  />
                  <div className="grid gap-1.5 leading-none">
                    <Label
                      htmlFor="force_live_search"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center gap-2"
                    >
                      <Zap className="w-4 h-4" />
                      Force Live Fetch
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      Admin override: Always fetch fresh data, ignoring cache (slowest but guaranteed up-to-date)
                    </p>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <div className="pt-4">
                <Button
                  type="submit"
                  disabled={isSubmitting || locationsLoading}
                  className="w-full bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 text-white font-semibold text-lg shadow-lg"
                  size="lg"
                >
                  {isSubmitting ? (
                    <>
                      <Spinner className="w-4 h-4 mr-2" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4 mr-2" />
                      Search Courts
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}