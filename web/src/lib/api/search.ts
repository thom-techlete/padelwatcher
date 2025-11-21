import { apiClient } from './client'
import type { SearchRequest, SearchResult, SearchOrder } from '@/types'

export const searchApi = {
  searchAvailable: (params: SearchRequest) =>
    apiClient.post<SearchResult>('/api/search/available', params),

  createOrder: (data: Omit<SearchOrder, 'id' | 'user_id' | 'created_at' | 'updated_at'>) =>
    apiClient.post<SearchOrder>('/api/search-orders', data),

  getOrders: () =>
    apiClient.get<{ search_orders: SearchOrder[] }>('/api/search-orders').then(res => res.search_orders),

  getOrder: (id: number) =>
    apiClient.get<SearchOrder>(`/api/search-orders/${id}`),

  updateOrder: (id: number, data: Partial<SearchOrder>) =>
    apiClient.put<SearchOrder>(`/api/search-orders/${id}`, data),

  deleteOrder: (id: number) =>
    apiClient.delete<void>(`/api/search-orders/${id}`),
}
