import { config } from '../api/config'

export const tokenStorage = {
  get: (): string | null => {
    const token = localStorage.getItem(config.tokenKey)
    console.log('[TokenStorage] Getting token:', token ? `${token.substring(0, 20)}...` : 'null')
    return token
  },

  set: (token: string): void => {
    console.log('[TokenStorage] Saving token:', token.substring(0, 20) + '...')
    localStorage.setItem(config.tokenKey, token)
    console.log('[TokenStorage] Token saved to localStorage with key:', config.tokenKey)
  },

  remove: (): void => {
    console.log('[TokenStorage] Removing token')
    localStorage.removeItem(config.tokenKey)
  },

  exists: (): boolean => {
    const exists = !!localStorage.getItem(config.tokenKey)
    console.log('[TokenStorage] Token exists:', exists)
    return exists
  },
}
