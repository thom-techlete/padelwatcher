export interface SearchOrder {
  id: number
  user_id: number
  location_id: number
  start_date: string
  end_date: string
  preferred_start_time: string
  preferred_end_time: string
  search_window_minutes: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SearchOrderNotification {
  id: number
  search_order_id: number
  court_id: number
  availability_id: number
  sent_at: string
  is_read: boolean
}

export interface SearchRequest {
  location_ids?: number[]
  date: string
  start_time: string
  end_time: string
  duration_minutes?: number
  court_type?: 'all' | 'indoor' | 'outdoor'
  court_config?: 'all' | 'single' | 'double'
  live_search?: boolean
  force_live_search?: boolean
}

export interface SearchResult {
  courts: Array<{
    court: {
      id: number
      name: string
      court_type: string
      is_indoor: boolean
      is_double: boolean
    }
    location: {
      id: number
      name: string
      address?: string
    }
    availabilities: Array<{
      id: number
      date: string
      start_time: string
      end_time: string
      price?: number
    }>
  }>
  cached: boolean
  cache_timestamp?: string
}
