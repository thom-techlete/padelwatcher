import { Link } from '@tanstack/react-router'
import { useAuth } from '@/contexts'
import { LogOut, Settings, User } from 'lucide-react'
import { Button } from '@/components/ui'

export function Header() {
  const { user, logout, isAuthenticated } = useAuth()

  return (
    <header className="sticky top-0 z-50 w-full border-b-4 border-accent-500 bg-secondary-700 shadow-lg backdrop-blur-sm bg-opacity-95">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link to={isAuthenticated ? "/dashboard" : "/"} className="flex items-center gap-3">
            <img
              src="/padelwatcher.png"
              alt="Padel Watcher Logo"
              className="h-12 w-16"
            />
          </Link>

          {isAuthenticated && (
            <nav className="hidden md:flex items-center gap-4">
              <Link
                to="/search"
                className="text-sm font-semibold text-white hover:text-accent-400 transition-colors"
              >
                Search Courts
              </Link>
              <Link
                to="/orders"
                className="text-sm font-semibold text-white hover:text-accent-400 transition-colors"
              >
                My Orders
              </Link>
              <Link
                to="/locations"
                className="text-sm font-semibold text-white hover:text-accent-400 transition-colors"
              >
                Locations
              </Link>
              {user?.is_admin && (
                <Link
                  to="/admin"
                  className="text-sm font-semibold text-accent-400 hover:text-accent-300 transition-colors bg-white/10 px-3 py-1 rounded-lg backdrop-blur-sm"
                >
                  Admin
                </Link>
              )}
            </nav>
          )}
        </div>

        <div className="flex items-center gap-4">
          {isAuthenticated && user ? (
            <>
              <div className="hidden md:flex items-center gap-2">
                <User className="h-4 w-4 text-white" />
                <span className="text-sm font-semibold text-white">{user.username}</span>
              </div>
              <Link to="/profile">
                <Button variant="ghost" size="icon" title="Profile" className="hover:bg-white/20 hover:text-accent-300 text-white">
                  <Settings className="h-5 w-5" />
                </Button>
              </Link>
              <Button variant="ghost" size="icon" onClick={logout} title="Logout" className="hover:bg-white/20 hover:text-accent-300 text-white">
                <LogOut className="h-5 w-5" />
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="outline" className="border-white text-white hover:bg-white/20 backdrop-blur-sm">Log In</Button>
              </Link>
              <Link to="/register">
                <Button className="bg-accent-500 text-white hover:bg-accent-600">Sign Up</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
