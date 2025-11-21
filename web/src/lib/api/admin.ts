import { apiClient } from './client'
import type { User, Location } from '@/types'

export const adminApi = {
  getUsers: () =>
    apiClient.get<{ users: User[] }>('/api/admin/users').then(res => res.users),

  approveUser: (userId: number) =>
    apiClient.post<User>(`/api/admin/users/${userId}/approve`),

  rejectUser: (userId: number) =>
    apiClient.delete<void>(`/api/admin/users/${userId}/reject`),

  activateUser: (userId: number) =>
    apiClient.post<User>(`/api/admin/users/${userId}/activate`),

  deactivateUser: (userId: number) =>
    apiClient.post<User>(`/api/admin/users/${userId}/deactivate`),

  getPendingUsers: () =>
    apiClient.get<{ pending_users: User[] }>('/api/admin/users/pending').then(res => res.pending_users),

  // Location management
  addLocation: (slug: string) =>
    apiClient.post<{ message: string; location: Location }>('/api/locations', { slug }),

  deleteLocation: (locationId: number) =>
    apiClient.delete<void>(`/api/locations/${locationId}`),

  // Cache management
  clearCache: (olderThanMinutes?: number) =>
    apiClient.post<{ message: string; deleted_count: number }>('/api/admin/cache/clear', { older_than_minutes: olderThanMinutes }),

  // Data refresh
  refreshAllData: () =>
    apiClient.post<{ message: string; locations_refreshed: number; courts_deleted: number; courts_added: number }>('/api/admin/refresh-all-data'),
}
