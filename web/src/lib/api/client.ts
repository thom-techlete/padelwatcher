import { config } from './config'
import { tokenStorage } from '@/lib/auth'
import type { ApiError } from '@/types'

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = config.apiUrl) {
    this.baseUrl = (baseUrl ?? '').toString()
  }

  private getHeaders(): HeadersInit {
    const token = tokenStorage.get()
    console.log('[ApiClient] Getting headers, token:', token ? `${token.substring(0, 20)}...` : 'null')

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
      console.log('[ApiClient] Authorization header set')
    } else {
      console.log('[ApiClient] No token found, skipping Authorization header')
    }

    return headers
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      // Handle 401 Unauthorized - token is invalid/expired
      if (response.status === 401) {
        console.log('[ApiClient] 401 response received, clearing auth state')
        // Import here to avoid circular dependencies
        const { tokenStorage } = await import('@/lib/auth')
        tokenStorage.remove()

        // Redirect to login if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }

      const error: ApiError = await response.json().catch(() => ({
        error: 'An unexpected error occurred',
      }))
      throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`)
    }

    return response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: this.getHeaders(),
      credentials: 'include',
    })
    return this.handleResponse<T>(response)
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      credentials: 'include',
      body: data ? JSON.stringify(data) : undefined,
    })
    return this.handleResponse<T>(response)
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      credentials: 'include',
      body: data ? JSON.stringify(data) : undefined,
    })
    return this.handleResponse<T>(response)
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
      credentials: 'include',
    })
    return this.handleResponse<T>(response)
  }
}

export const apiClient = new ApiClient()
