import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { searchApi, locationApi } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Label, Select, Spinner, Alert } from '@/components/ui'
import { ArrowLeft, Save } from 'lucide-react'

interface CreateSearchOrderForm {
  location_id: number
  start_date: string
  end_date: string
  preferred_start_time: string
  preferred_end_time: string
  search_window_minutes: number
}

export function CreateSearchOrderPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { register, handleSubmit, formState: { errors }, watch } = useForm<CreateSearchOrderForm>({
    defaultValues: {
      search_window_minutes: 60,
    },
  })

  const { data: locations, isLoading: locationsLoading } = useQuery({
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
    createOrderMutation.mutate({
      ...data,
      is_active: true,
    })
  }

  const startDate = watch('start_date')

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
            <div>
              <Label htmlFor="location_id">Location</Label>
              <Select
                id="location_id"
                {...register('location_id', { required: 'Location is required' })}
                options={
                  locations?.map(location => ({
                    value: location.id,
                    label: location.name,
                  })) || []
                }
                className={errors.location_id ? 'border-red-500' : ''}
              />
              {errors.location_id && (
                <p className="text-sm text-red-600 mt-1">{errors.location_id.message}</p>
              )}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  {...register('start_date', { required: 'Start date is required' })}
                  className={errors.start_date ? 'border-red-500' : ''}
                />
                {errors.start_date && (
                  <p className="text-sm text-red-600 mt-1">{errors.start_date.message}</p>
                )}
              </div>
              <div>
                <Label htmlFor="end_date">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  {...register('end_date', {
                    required: 'End date is required',
                    validate: (value) => {
                      if (startDate && value < startDate) {
                        return 'End date must be after start date'
                      }
                      return true
                    }
                  })}
                  className={errors.end_date ? 'border-red-500' : ''}
                />
                {errors.end_date && (
                  <p className="text-sm text-red-600 mt-1">{errors.end_date.message}</p>
                )}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label htmlFor="preferred_start_time">Preferred Start Time</Label>
                <Input
                  id="preferred_start_time"
                  type="time"
                  {...register('preferred_start_time', { required: 'Start time is required' })}
                  className={errors.preferred_start_time ? 'border-red-500' : ''}
                />
                {errors.preferred_start_time && (
                  <p className="text-sm text-red-600 mt-1">{errors.preferred_start_time.message}</p>
                )}
              </div>
              <div>
                <Label htmlFor="preferred_end_time">Preferred End Time</Label>
                <Input
                  id="preferred_end_time"
                  type="time"
                  {...register('preferred_end_time', {
                    required: 'End time is required',
                    validate: (value) => {
                      const startTime = watch('preferred_start_time')
                      if (startTime && value <= startTime) {
                        return 'End time must be after start time'
                      }
                      return true
                    }
                  })}
                  className={errors.preferred_end_time ? 'border-red-500' : ''}
                />
                {errors.preferred_end_time && (
                  <p className="text-sm text-red-600 mt-1">{errors.preferred_end_time.message}</p>
                )}
              </div>
            </div>

            <div>
              <Label htmlFor="search_window_minutes">Search Window (minutes)</Label>
              <Input
                id="search_window_minutes"
                type="number"
                min="15"
                max="480"
                {...register('search_window_minutes', {
                  required: 'Search window is required',
                  min: { value: 15, message: 'Minimum 15 minutes' },
                  max: { value: 480, message: 'Maximum 8 hours' }
                })}
                className={errors.search_window_minutes ? 'border-red-500' : ''}
              />
              <p className="text-sm text-white/70 mt-1">
                How much time before/after your preferred time to search for availability
              </p>
              {errors.search_window_minutes && (
                <p className="text-sm text-red-600 mt-1">{errors.search_window_minutes.message}</p>
              )}
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