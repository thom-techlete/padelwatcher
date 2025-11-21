import { apiClient } from './client'
import type { Location, Court, CourtAvailability } from '@/types'

export const locationApi = {
  getAll: () =>
    apiClient.get<{ locations: Location[] }>('/api/locations').then(res => res.locations),

  getById: (id: number) =>
    apiClient.get<Location>(`/api/locations/${id}`),

  create: (slug: string) =>
    apiClient.post<Location>('/api/locations', { slug }),

  getCourts: (locationId: number) =>
    apiClient.get<{ courts: Court[] }>(`/api/locations/${locationId}/courts`).then(res => res.courts),

  getAvailability: (courtId: number, startDate: string, endDate: string) =>
    apiClient.get<CourtAvailability[]>(
      `/api/courts/${courtId}/availability?start_date=${startDate}&end_date=${endDate}`
    ),
}
