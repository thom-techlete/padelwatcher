import { apiClient } from './client'
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '@/types'

export interface UpdateProfileRequest {
  email?: string
}

export interface UpdatePasswordRequest {
  current_password: string
  new_password: string
}

export interface RegisterResponse {
  message: string
  user_id: string
}

export const authApi = {
  login: (credentials: LoginRequest) =>
    apiClient.post<AuthResponse>('/api/auth/login', credentials),

  register: (data: RegisterRequest) =>
    apiClient.post<RegisterResponse>('/api/auth/register', data),

  getCurrentUser: () =>
    apiClient.get<User>('/api/auth/me'),

  updateProfile: (data: UpdateProfileRequest) =>
    apiClient.put<{ message: string; user: User }>('/api/auth/profile', data),

  updatePassword: (data: UpdatePasswordRequest) =>
    apiClient.put<{ message: string }>('/api/auth/password', data),
}
