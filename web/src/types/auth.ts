export interface User {
  id: number
  email: string
  username: string
  is_admin: boolean
  is_approved: boolean
  active: boolean
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface AuthResponse {
  token: string
  user_id: string
  email: string
  is_admin: boolean
  is_approved: boolean
  expires_in: number
}
