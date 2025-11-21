import { useMemo } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { searchApi, locationApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent, Button, Label, MultiSelect, Select, Spinner, Alert, DatePicker, TimePicker } from '@/components/ui'
import { ArrowLeft, Save } from 'lucide-react'
import { format } from 'date-fns'

interface CreateSearchOrderForm {
  location_ids: number[]
  date: Date | null
  start_time: string
  end_time: string
  duration_minutes: number
  court_type: 'all' | 'indoor' | 'outdoor'
  court_config: 'all' | 'single' | 'double'
}

export function CreateSearchOrderPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { control, handleSubmit, formState: { errors }, watch } = useForm<CreateSearchOrderForm>({
    defaultValues: {
      location_ids: [],
      date: new Date(),
      start_time: '09:00',
      end_time: '21:00',
      duration_minutes: 90,
      court_type: 'all',
      court_config: 'double',
    },
  })

  const { data: locations = [], isLoading: locationsLoading } = useQuery({
    queryKey: ['locations'],
    queryFn: locationApi.getAll,
  })

  const createOrderMutation = useMutation({
    mutationFn: searchApi.createOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['search-orders'] })
      navigate({ to: '/orders' })
    },
  })

  const onSubmit = (data: CreateSearchOrderForm) => {
    if (!data.date) return

    createOrderMutation.mutate({
      location_ids: data.location_ids,
      date: format(data.date, 'yyyy-MM-dd'),
      start_time: data.start_time,
      end_time: data.end_time,
      duration_minutes: data.duration_minutes,
      court_type: data.court_type,
      court_config: data.court_config,
      is_active: true,
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

  if (locationsLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center">
          <Spinner />
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => navigate({ to: '/orders' })}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Search Orders
        </Button>
        <h1 className="text-3xl font-bold text-white">Create Search Order</h1>
        <p className="text-white/80 mt-2">
          Set up automated monitoring for court availability
        </p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Search Order Details</CardTitle>
        </CardHeader>
        <CardContent>
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
                    placeholder="Select locations to monitor..."
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

            {createOrderMutation.isError && (
              <Alert variant="error">
                Failed to create search order: {createOrderMutation.error.message}
              </Alert>
            )}

            <div className="flex space-x-4">
              <Button
                type="submit"
                disabled={createOrderMutation.isPending}
                className="flex-1"
              >
                {createOrderMutation.isPending ? (
                  <Spinner className="mr-2 h-4 w-4" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                Create Search Order
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate({ to: '/orders' })}
                disabled={createOrderMutation.isPending}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}