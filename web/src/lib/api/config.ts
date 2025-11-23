const rawApiBase = import.meta.env.VITE_API_BASE_URL ?? ''
// Strip surrounding single/double quotes and trim whitespace
const stripped = rawApiBase.trim().replace(/^['"]|['"]$/g, '')
// Remove trailing slashes
const API_BASE_URL = stripped.replace(/\/+$/g, '')

export const config = {
  apiUrl: API_BASE_URL,
  tokenKey: 'padel_watcher_token',
}
