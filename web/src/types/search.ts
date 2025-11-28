export interface SearchOrder {
  id: number
  user_id: string
  location_ids: number[]
  date: string
  start_time: string
  end_time: string
  duration_minutes: number
  court_type: 'all' | 'indoor' | 'outdoor'
  court_config: 'all' | 'single' | 'double'
  is_active: boolean
  created_at: string
  updated_at?: string
  last_check_at?: string
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
  locations: Array<{
    location: {
      id: number
      name: string
      slug: string
      address?: string
    }
    courts: Array<{
      court: {
        id: number
        name: string
        court_type: string
        is_indoor: boolean
        is_double: boolean
      }
      availabilities: Array<{
        id: number
        date: string
        start_time: string
        end_time: string
        price?: number
        booking_url?: string
      }>
    }>
  }>
  cached: boolean
  cache_timestamp?: string
}

// Background search task types
export type SearchTaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface SearchTask {
  task_id: string
  status: SearchTaskStatus
  progress: number
  current_step: string
  total_locations: number
  processed_locations: number
  error_message?: string
  results?: SearchResult
  created_at?: string
  started_at?: string
  completed_at?: string
}

export interface SearchTaskStartResponse {
  task_id: string
  status: string
  message: string
}
