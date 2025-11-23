import { createRootRoute, createRoute, createRouter, Outlet, redirect } from '@tanstack/react-router'
import { Layout } from '@/components/layout'
import { HomePage } from '@/pages/public'
import { LoginPage, RegisterPage, PendingApprovalPage } from '@/pages/auth'
import { DashboardPage } from '@/pages/dashboard'
import { AdminPage } from '@/pages/admin'
import { LocationsPage } from '@/pages/locations'
import { CourtsPage } from '@/pages/courts'
import { SearchOrdersPage, CreateSearchOrderPage } from '@/pages/search-orders'
import { SearchPage, SearchResultsPage } from '@/pages/public'
import { ProfilePage } from '@/pages/profile/ProfilePage'
import { tokenStorage } from '@/lib/auth'
import { AuthProvider } from '@/contexts'

// Root route
const rootRoute = createRootRoute({
  component: () => (
    <AuthProvider>
      <Layout>
        <Outlet />
      </Layout>
    </AuthProvider>
  ),
})

// Public routes
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
})

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: LoginPage,
})

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/register',
  component: RegisterPage,
})

const pendingApprovalRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/pending-approval',
  component: PendingApprovalPage,
})

// Protected routes
const dashboardRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/dashboard',
  component: DashboardPage,
  beforeLoad: () => {
    if (!tokenStorage.exists()) {
      throw redirect({ to: '/login' })
    }
  },
})

const adminRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/admin',
  component: AdminPage,
  beforeLoad: () => {
    if (!tokenStorage.exists()) {
      throw redirect({ to: '/login' })
    }
  },
})

// Placeholder routes for other pages
const searchRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/search',
  component: SearchPage,
  beforeLoad: () => {
    if (!tokenStorage.exists()) {
      throw redirect({ to: '/login' })
    }
  },
})

const searchResultsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/search-results',
  component: SearchResultsPage,
  beforeLoad: () => {
    if (!tokenStorage.exists()) {
      throw redirect({ to: '/login' })
    }
  },
})

const ordersRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/orders',
  component: SearchOrdersPage,
  beforeLoad: () => {
    if (!tokenStorage.exists()) {
      throw redirect({ to: '/login' })
    }
  },
})

const createOrderRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/orders/new',
  component: CreateSearchOrderPage,
  beforeLoad: () => {
    if (!tokenStorage.exists()) {
      throw redirect({ to: '/login' })
    }
  },
})

const locationsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/locations',
  component: LocationsPage,
})

const courtsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/courts',
  component: CourtsPage,
})

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
  component: () => <div className="container mx-auto px-4 py-8"><h1 className="text-2xl font-bold">Settings (Coming Soon)</h1></div>,
  beforeLoad: () => {
    if (!tokenStorage.exists()) {
      throw redirect({ to: '/login' })
    }
  },
})

const profileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/profile',
  component: ProfilePage,
  beforeLoad: () => {
    if (!tokenStorage.exists()) {
      throw redirect({ to: '/login' })
    }
  },
})

// Create route tree
const routeTree = rootRoute.addChildren([
  indexRoute,
  loginRoute,
  registerRoute,
  pendingApprovalRoute,
  dashboardRoute,
  adminRoute,
  searchRoute,
  searchResultsRoute,
  ordersRoute,
  createOrderRoute,
  locationsRoute,
  courtsRoute,
  settingsRoute,
  profileRoute,
])

// Create router
export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
})

// Register router for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
