export interface Location {
  id: number
  name: string
  slug: string
  provider: string
  address?: string
  city?: string
  phone?: string
  email?: string
  website?: string
  created_at: string
  updated_at: string
}

export interface Court {
  id: number
  location_id: number
  name: string
  court_type: string
  is_indoor: boolean
  is_double: boolean
  created_at: string
}

export interface CourtAvailability {
  id: number
  court_id: number
  date: string
  start_time: string
  end_time: string
  price?: number
  is_available: boolean
  created_at: string
}
