# Padel Watcher Frontend - Quick Reference

## 🚀 Quick Start Commands

```bash
# Development
npm install          # Install dependencies
npm run dev          # Start dev server (http://localhost:5173)
npm run build        # Build for production
npm run preview      # Preview production build

# Linting
npm run lint         # Run ESLint
```

## 📁 Project Structure

```
src/
├── components/       # UI Components
│   ├── ui/          # Button, Input, Card, etc.
│   ├── layout/      # Header, Footer, Layout
│   └── forms/       # Form components
├── pages/           # Page Components
│   ├── auth/        # Login, Register, PendingApproval
│   ├── dashboard/   # Dashboard
│   ├── admin/       # Admin Panel
│   └── public/      # Homepage
├── lib/             # Utilities
│   ├── api/         # API client & endpoints
│   ├── auth/        # Auth utilities
│   └── utils/       # Helpers (cn, formatDate, etc.)
├── contexts/        # React Contexts (AuthContext)
├── types/           # TypeScript types
├── router.tsx       # Route configuration
├── App.tsx          # App root
└── main.tsx         # Entry point
```

## 🔑 Key Patterns

### API Calls (TanStack Query)

```tsx
import { useQuery, useMutation } from '@tanstack/react-query'
import { locationApi } from '@/lib/api'

// Query (GET)
const { data, isLoading, error } = useQuery({
  queryKey: ['locations'],
  queryFn: locationApi.getAll,
})

// Mutation (POST/PUT/DELETE)
const mutation = useMutation({
  mutationFn: locationApi.create,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['locations'] })
  },
})
```

### Authentication

```tsx
import { useAuth } from '@/contexts'

const { user, isAuthenticated, login, logout } = useAuth()

// Check if user is admin
if (user?.is_admin) { /* ... */ }

// Login
await login({ email, password })

// Logout
logout()
```

### Routing

```tsx
import { Link, useNavigate } from '@tanstack/react-router'

// Navigation
<Link to="/dashboard">Dashboard</Link>

// Programmatic navigation
const navigate = useNavigate()
navigate({ to: '/dashboard' })
```

### Components

```tsx
import { Button, Card, Input, Label, Alert, Spinner } from '@/components/ui'

// Button variants
<Button>Default</Button>
<Button variant="outline">Outline</Button>
<Button variant="destructive">Delete</Button>
<Button variant="ghost">Ghost</Button>

// Card
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content</CardContent>
  <CardFooter>Footer</CardFooter>
</Card>

// Alert
<Alert variant="success">Success message</Alert>
<Alert variant="error">Error message</Alert>
<Alert variant="warning">Warning message</Alert>

// Form
<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" />
</div>
```

### Utilities

```tsx
import { cn, formatDate, formatTimeAgo } from '@/lib/utils'

// Merge Tailwind classes
<div className={cn('base-class', isActive && 'active-class')}>

// Format dates
formatDate('2024-11-16')           // "November 16, 2024"
formatTimeAgo('2024-11-16')        // "2 hours ago"
```

## 🎨 Tailwind CSS Quick Reference

### Layout
```css
flex items-center justify-between
grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4
container mx-auto px-4 py-8
```

### Spacing
```css
p-4          /* padding: 1rem */
px-4         /* padding-left/right: 1rem */
py-8         /* padding-top/bottom: 2rem */
space-y-4    /* vertical spacing between children */
gap-4        /* grid/flex gap */
```

### Typography
```css
text-sm text-base text-lg text-xl text-2xl text-3xl
font-normal font-medium font-semibold font-bold
text-white text-primary-500
```

### Colors
```css
bg-white bg-gray-50 bg-primary-500
text-muted-foreground text-white
border-gray-200
```

### Borders & Shadows
```css
border border-gray-200
rounded-lg rounded-md
shadow-sm shadow-md
```

### Responsive
```css
/* Mobile first */
md:grid-cols-2    /* Tablet */
lg:grid-cols-4    /* Desktop */
hidden md:flex    /* Show on tablet+ */
```

## 🔒 Environment Variables

```env
# .env.development
VITE_API_URL=http://localhost:5000

# .env.production
VITE_API_URL=https://api.yourdomain.com
```

Access in code:
```tsx
const apiUrl = import.meta.env.VITE_API_URL
```

## 🛣️ Routes

### Public Routes
- `/` - Homepage
- `/login` - Login page
- `/register` - Registration page
- `/pending-approval` - Pending approval page

### Protected Routes (Requires Auth)
- `/dashboard` - User dashboard
- `/search` - Search courts
- `/orders` - Manage search orders
- `/locations` - Browse locations
- `/settings` - User settings
- `/admin` - Admin panel (admin only)

## 📝 Common Tasks

### Add a New Page

1. Create page component:
```tsx
// src/pages/myfeature/MyPage.tsx
export function MyPage() {
  return <div>My Page</div>
}
```

2. Add route in `router.tsx`:
```tsx
const myRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/my-page',
  component: MyPage,
})

// Add to route tree
const routeTree = rootRoute.addChildren([
  // ... existing routes,
  myRoute,
])
```

### Add a New API Endpoint

1. Define types in `src/types/`:
```tsx
export interface MyData {
  id: number
  name: string
}
```

2. Create API function in `src/lib/api/`:
```tsx
export const myApi = {
  getAll: () => apiClient.get<MyData[]>('/api/my-data'),
  create: (data: Partial<MyData>) => 
    apiClient.post<MyData>('/api/my-data', data),
}
```

3. Use in component:
```tsx
const { data } = useQuery({
  queryKey: ['my-data'],
  queryFn: myApi.getAll,
})
```

### Style a Component

```tsx
// Use Tailwind utility classes
<div className="flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-200 hover:border-primary-500 transition-colors">
  <Icon className="h-5 w-5 text-gray-500" />
  <span className="text-sm font-medium text-muted-foreground">Label</span>
</div>

// Use cn() for conditional classes
<Button 
  className={cn(
    'base-styles',
    isActive && 'active-styles',
    isDisabled && 'disabled-styles'
  )}
/>
```

## 🐛 Debugging

### Check Authentication State
```tsx
const { user, isAuthenticated } = useAuth()
console.log('User:', user)
console.log('Authenticated:', isAuthenticated)
console.log('Token:', localStorage.getItem('padel_watcher_token'))
```

### Check API Calls
1. Open browser DevTools → Network tab
2. Filter by "Fetch/XHR"
3. Look for API calls to `/api/*`
4. Check request/response details

### React Query DevTools
The app includes TanStack Query DevTools (bottom-left in dev mode):
- View all queries and their state
- See cache contents
- Debug query/mutation status

## 📊 Build & Deploy

### Production Build
```bash
npm run build
# Output: dist/ directory
# Size: ~384KB JS (117KB gzipped)
```

### Deploy to Vercel
1. Connect GitHub repo
2. Set `VITE_API_URL` environment variable
3. Deploy automatically on push

### Deploy to Netlify
1. Upload `dist/` folder
2. Configure redirects: `/*  /index.html  200`

## 🎯 Performance Tips

1. **Code Splitting**: Routes are automatically split
2. **Lazy Loading**: Use `React.lazy()` for heavy components
3. **Memoization**: Use `useMemo()` and `useCallback()` for expensive operations
4. **Query Caching**: TanStack Query caches automatically (5min default)
5. **Image Optimization**: Use WebP format, lazy load images

## 🔗 Useful Links

- [Full Documentation](./DEVELOPMENT.md)
- [Backend API Docs](../backend/API_DOCUMENTATION.md)
- [Tailwind CSS Docs](https://tailwindcss.com)
- [TanStack Query Docs](https://tanstack.com/query)
- [React Docs](https://react.dev)

---

**Need Help?** Check DEVELOPMENT.md for detailed guides.
