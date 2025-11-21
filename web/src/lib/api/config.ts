const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const config = {
  apiUrl: API_BASE_URL,
  tokenKey: 'padel_watcher_token',
}
