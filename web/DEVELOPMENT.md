# Padel Watcher Frontend - Development Guide

## Quick Start

### 1. Install Dependencies
```bash
cd web
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env.development
```

Edit `.env.development` if needed (default API URL is http://localhost:5000)

### 3. Start Development Server
```bash
npm run dev
```

Access the app at http://localhost:5173

## Project Overview

This is a modern React frontend built with:
- **React 18** with TypeScript for type safety
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for utility-first styling
- **TanStack Router** for type-safe routing
- **TanStack Query** for server state management
- **JWT Authentication** with secure token storage

## Architecture

### State Management Strategy

1. **Server State**: TanStack Query (React Query)
   - All API data fetching
   - Automatic caching and background updates
   - Optimistic updates for mutations

2. **Authentication State**: React Context
   - User authentication status
   - Current user information
   - Login/logout actions

3. **Component State**: React hooks (useState, useReducer)
   - Local UI state
   - Form state (with React Hook Form)

### API Integration

All API calls go through the centralized API client (`lib/api/client.ts`):

```typescript
// Example: Using the API in a component
import { useQuery } from '@tanstack/react-query'
import { locationApi } from '@/lib/api'

function LocationsList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['locations'],
    queryFn: locationApi.getAll,
  })

  if (isLoading) return <Spinner />
  if (error) return <Alert variant="error">{error.message}</Alert>

  return <div>{/* Render locations */}</div>
}
```

### Authentication Flow

1. **Login**: User enters credentials → API returns JWT token + user data
2. **Token Storage**: Token saved to localStorage
3. **Authorization**: Token included in all API requests via Authorization header
4. **Protected Routes**: Routes check for token existence before rendering
5. **User Approval**: After registration, admin must approve user

### Routing

Routes are defined in `src/router.tsx`:

- **Public**: `/`, `/login`, `/register`
- **Protected**: `/dashboard`, `/search`, `/orders`, `/locations`, `/settings`
- **Admin Only**: `/admin`

Protection is handled via `beforeLoad` route hooks that check authentication.

## Component Structure

### UI Components (`components/ui/`)

Base components following shadcn/ui patterns:
- `Button`: Variants (default, outline, ghost, destructive)
- `Input`: Form inputs with validation styling
- `Card`: Content containers with header/content/footer
- `Label`: Form labels
- `Alert`: User feedback (success, error, warning, info)
- `Spinner`: Loading indicators

### Layout Components (`components/layout/`)

- `Header`: Navigation with auth-aware menu
- `Footer`: Site footer with links
- `Layout`: Main layout wrapper

### Pages

Organized by feature:
- `pages/auth/`: Login, Register, PendingApproval
- `pages/dashboard/`: User dashboard
- `pages/admin/`: Admin panel
- `pages/public/`: Homepage

## Styling Guide

### Tailwind CSS Usage

Use utility classes for styling:

```tsx
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm">
  <h2 className="text-xl font-semibold text-muted-foreground">Title</h2>
  <Button size="sm" variant="outline">Action</Button>
</div>
```

### Custom Colors

Defined in `tailwind.config.js`:
- `primary-*`: Blue (main brand color)
- `secondary-*`: Green (success, growth)
- `accent-*`: Orange (attention, warnings)

### Responsive Design

Mobile-first approach using Tailwind breakpoints:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Responsive grid */}
</div>
```

## Type Safety

### TypeScript Configuration

- Strict mode enabled
- Path aliases configured (`@/*` → `src/*`)
- Type checking on build

### Type Definitions

All types in `src/types/`:
- `auth.ts`: User, login, register types
- `location.ts`: Location, court, availability types
- `search.ts`: Search order, results types
- `api.ts`: API response types

## Best Practices

### Component Organization

```tsx
// 1. Imports
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button, Card } from '@/components/ui'
import { locationApi } from '@/lib/api'

// 2. Types/Interfaces
interface Props {
  title: string
}

// 3. Component
export function MyComponent({ title }: Props) {
  // Hooks
  const [isOpen, setIsOpen] = useState(false)
  const { data } = useQuery({...})

  // Handlers
  const handleClick = () => {
    setIsOpen(!isOpen)
  }

  // Render
  return (
    <Card>
      <h1>{title}</h1>
      <Button onClick={handleClick}>Toggle</Button>
    </Card>
  )
}
```

### Error Handling

Always handle loading and error states:

```tsx
const { data, isLoading, error } = useQuery({...})

if (isLoading) return <Spinner />
if (error) return <Alert variant="error">{error.message}</Alert>
if (!data) return <Alert>No data available</Alert>

return <div>{/* Render data */}</div>
```

### Form Handling

Use React Hook Form for complex forms:

```tsx
import { useForm } from 'react-hook-form'

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    // Handle form submission
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input {...register('email', { required: true })} />
      {errors.email && <span>Email is required</span>}
      <Button type="submit">Submit</Button>
    </form>
  )
}
```

## Testing

### Manual Testing Checklist

- [ ] Login with valid credentials works
- [ ] Login with invalid credentials shows error
- [ ] Registration creates new user (pending approval)
- [ ] Unapproved user sees pending approval page
- [ ] Approved user can access dashboard
- [ ] Admin can see and approve pending users
- [ ] Protected routes redirect to login when not authenticated
- [ ] Logout clears authentication and redirects
- [ ] Responsive design works on mobile, tablet, desktop

### Browser Testing

Test in:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Android)

## Performance Optimization

### Current Optimizations

1. **Code Splitting**: Route-based automatic splitting
2. **Query Caching**: TanStack Query caches API responses
3. **Lazy Loading**: Components loaded on demand
4. **Production Build**: Minified, tree-shaken, optimized

### Bundle Size

Current production build: ~384KB JS (117KB gzipped)

To analyze bundle:
```bash
npm run build
npx vite-bundle-visualizer
```

## Deployment

### Environment Setup

1. Create `.env.production`:
```env
VITE_API_URL=https://api.yourdomain.com
```

2. Build for production:
```bash
npm run build
```

3. Test production build locally:
```bash
npm run preview
```

### Deployment Platforms

**Vercel** (Recommended):
1. Connect GitHub repository
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push

**Netlify**:
1. Drag and drop `dist/` folder
2. Or connect GitHub for continuous deployment

**Static Hosting** (S3, Cloudflare Pages, etc.):
- Upload contents of `dist/` folder
- Configure SPA routing (redirect all to index.html)

## Troubleshooting

### Common Issues

**Build fails with TypeScript errors:**
```bash
# Check for type errors
npx tsc --noEmit
```

**API calls failing:**
- Check backend is running on correct port
- Verify VITE_API_URL in .env file
- Check browser console for CORS errors

**Tailwind classes not working:**
- Ensure postcss.config.js is correct
- Clear cache: `rm -rf node_modules/.cache`
- Rebuild: `npm run build`

**Authentication not persisting:**
- Check localStorage in browser DevTools
- Verify token is being set correctly
- Check token expiration

## Next Steps

### Features to Implement

1. **Court Search Interface**
   - Create search form
   - Display results in table/cards
   - Add filters (date, time, location, type)

2. **Search Orders Management**
   - List user's search orders
   - Create new search orders
   - Edit/delete existing orders
   - View notifications

3. **Location Management**
   - Browse all locations
   - Add new locations (by Playtomic slug)
   - View courts at each location
   - Manage court details

4. **Settings Page**
   - User profile editing
   - Password change
   - Notification preferences
   - Default search settings

5. **Notifications System**
   - Real-time notifications
   - Notification history
   - Mark as read/unread
   - Push notifications (PWA)

### Technical Improvements

- Add unit tests (Vitest)
- Add E2E tests (Playwright)
- Implement error boundary
- Add analytics integration
- Set up Sentry for error tracking
- Implement PWA features
- Add dark mode support
- Internationalization (i18n)

## Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [TanStack Query](https://tanstack.com/query)
- [TanStack Router](https://tanstack.com/router)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript](https://www.typescriptlang.org)

## Support

For questions or issues:
1. Check this documentation
2. Review existing code examples
3. Check browser console for errors
4. Review backend API documentation

---

Happy coding! 🎾
