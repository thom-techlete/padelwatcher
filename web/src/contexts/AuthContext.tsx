import { createContext, type ReactNode } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { authApi } from '@/lib/api'
import { tokenStorage } from '@/lib/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export { AuthContext }

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  // Fetch current user if token exists
  const { data: user, isLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authApi.getCurrentUser,
    enabled: tokenStorage.exists(),
    retry: false,
  })

  const userData = user ?? null

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      console.log('[AuthContext] Login successful, received data:', { 
        hasToken: !!data.token, 
        tokenPreview: data.token?.substring(0, 20) + '...',
        userId: data.user_id,
        email: data.email 
      })
      tokenStorage.set(data.token)
      console.log('[AuthContext] Token saved, invalidating queries')
      // Invalidate currentUser query to trigger refetch with new token
      queryClient.invalidateQueries({ queryKey: ['currentUser'] })
      console.log('[AuthContext] Queries invalidated')
    },
    onError: (error) => {
      console.error('[AuthContext] Login failed:', error)
    },
  })

  const registerMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: (data) => {
      tokenStorage.set(data.token)
      // Invalidate currentUser query to trigger refetch with new token
      queryClient.invalidateQueries({ queryKey: ['currentUser'] })
    },
  })

  const login = async (credentials: LoginRequest) => {
    await loginMutation.mutateAsync(credentials)
  }

  const register = async (data: RegisterRequest) => {
    await registerMutation.mutateAsync(data)
  }

  const logout = () => {
    tokenStorage.remove()
    queryClient.removeQueries({ queryKey: ['currentUser'] })
    queryClient.clear()
    navigate({ to: '/login' })
  }

  return (
    <AuthContext.Provider
      value={{
        user: userData,
        isLoading,
        isAuthenticated: !!userData,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
