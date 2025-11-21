---
applyTo: 'web/**'
---

# Padel Watcher Frontend - Agent Instructions

## Project Overview

Padel Watcher is a comprehensive padel court availability tracking and notification system. The frontend is a modern React application that provides a SaaS-style platform for users to track court availability, manage search orders, and receive notifications.

### Core Features
- **User Authentication**: JWT-based auth with user approval workflow
- **Court Search**: Real-time court availability search across locations
- **Search Orders**: Automated monitoring of court availability
- **Admin Panel**: User management and system administration
- **Responsive Design**: Mobile-first approach with modern UI

## Tech Stack

### Core Framework
- **React 18** with TypeScript (strict mode enabled)
- **Vite** for build tooling and development server
- **TanStack Router** for file-based routing with type safety

### State Management
- **TanStack Query (React Query)** for server state management
- **React Context** for client-side state (authentication)
- **React hooks** for local component state

### Styling & UI
- **Tailwind CSS** for utility-first styling
- **shadcn/ui** component library for consistent UI components
- **Lucide React** for icons
- **Custom design tokens** for brand consistency matching the Padel Watcher logo

### Brand Colors (from Padel Watcher Logo)
- **Primary (Teal)**: `#14b8a6` - Main brand color for primary actions and accents
- **Secondary (Navy Blue)**: `#1e293b` - Dark color for supporting elements and backgrounds
- **Accent (Orange)**: `#ff8c00` - Bright orange for highlights, CTAs, and important interactive elements

### Development Tools
- **ESLint** with TypeScript rules
- **TypeScript** with strict configuration
- **Path aliases** (`@/*` → `src/*`)
- **Environment variables** for configuration

### API Integration
- **Custom API client** with JWT authentication
- **RESTful endpoints** with proper error handling
- **Type-safe API calls** with full TypeScript support

## Project Structure

```
web/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # shadcn/ui base components
│   │   ├── layout/         # Layout components (Header, Footer)
│   │   └── forms/          # Form components
│   ├── pages/              # Page components by feature
│   │   ├── auth/           # Authentication pages
│   │   ├── dashboard/      # Dashboard pages
│   │   ├── admin/          # Admin pages
│   │   └── public/         # Public pages
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utilities and configurations
│   │   ├── api/            # API client and endpoints
│   │   ├── auth/           # Authentication utilities
│   │   └── utils/          # Helper functions
│   ├── contexts/           # React contexts
│   ├── types/              # TypeScript type definitions
│   ├── router.tsx          # Route configuration
│   ├── App.tsx             # App root component
│   └── main.tsx            # Application entry point
├── public/                 # Static assets
├── index.html              # HTML template
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
├── package.json            # Dependencies and scripts
└── .env.*                  # Environment variables
```

## Coding Standards

### TypeScript Guidelines

1. **Strict Mode**: Always use strict TypeScript settings
2. **Type Definitions**: Define interfaces for all data structures
3. **Generic Types**: Use generics for reusable components and functions
4. **Union Types**: Prefer union types over `any` for better type safety
5. **Optional Properties**: Use `?` for optional properties, avoid `| undefined`

### Component Patterns

1. **Functional Components**: Use function components with hooks
2. **Named Exports**: Prefer named exports over default exports
3. **Props Interface**: Define props interfaces for all components
4. **Destructuring**: Destructure props in function parameters
5. **Early Returns**: Use early returns for conditional rendering

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  onClick?: () => void
}

export function Button({ variant = 'primary', size = 'md', children, onClick }: ButtonProps) {
  // Component implementation
}
```

### File Organization

1. **One Component Per File**: Each component in its own file
2. **Index Files**: Use `index.ts` for clean imports
3. **Feature Folders**: Group related files in feature folders
4. **Consistent Naming**: Use PascalCase for components, camelCase for utilities

### Import Order

1. React imports first
2. Third-party libraries
3. Internal imports (absolute paths with `@/`)
4. Relative imports (only when necessary)
5. Type imports (use `import type`)

```typescript
import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui'
import { apiClient } from '@/lib/api'
import type { User } from '@/types'
```

## State Management Guidelines

### TanStack Query Usage

1. **Query Keys**: Use descriptive, hierarchical query keys
2. **Error Handling**: Always handle loading and error states
3. **Caching**: Leverage built-in caching and background updates
4. **Optimistic Updates**: Use for immediate UI feedback
5. **Invalidation**: Invalidate queries after mutations

```typescript
// Good query usage
const { data, isLoading, error } = useQuery({
  queryKey: ['locations', locationId],
  queryFn: () => locationApi.getById(locationId),
  enabled: !!locationId,
})

// Good mutation with invalidation
const mutation = useMutation({
  mutationFn: locationApi.create,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['locations'] })
  },
})
```

### Context Usage

1. **Minimal Contexts**: Only use context for app-wide state
2. **Type Safety**: Strongly type context values
3. **Error Boundaries**: Provide clear error messages
4. **Separation of Concerns**: Keep contexts focused on single responsibilities

## API Integration Patterns

### API Client Structure

1. **Centralized Client**: Single API client instance
2. **Automatic Auth**: JWT tokens added automatically
3. **Error Handling**: Consistent error response handling
4. **Type Safety**: Full TypeScript support for all endpoints

### Request/Response Patterns

1. **Consistent Structure**: Standardize API response formats
2. **Loading States**: Always show loading indicators
3. **Error Messages**: User-friendly error messages
4. **Retry Logic**: Implement appropriate retry strategies

```typescript
// API call pattern
const { data, isLoading, error } = useQuery({
  queryKey: ['users'],
  queryFn: adminApi.getUsers,
  retry: 1,
  staleTime: 5 * 60 * 1000, // 5 minutes
})

if (isLoading) return <Spinner />
if (error) return <Alert variant="error">{error.message}</Alert>
if (!data) return <div>No data available</div>
```

## Component Development

### UI Component Guidelines

1. **Composition**: Build complex components from simpler ones
2. **Props API**: Design flexible, extensible props APIs
3. **Accessibility**: Include ARIA labels and keyboard navigation
4. **Responsive**: Mobile-first responsive design
5. **Performance**: Memoize expensive computations

### Form Handling

1. **React Hook Form**: Use for complex forms
2. **Validation**: Client-side validation with clear error messages
3. **Type Safety**: Strongly typed form data
4. **User Experience**: Real-time validation feedback

```typescript
import { useForm } from 'react-hook-form'

interface LoginForm {
  email: string
  password: string
}

export function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>()

  const onSubmit = (data: LoginForm) => {
    // Handle form submission
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email', { required: true })} />
      {errors.email && <span>Email is required</span>}
    </form>
  )
}
```

## Styling Guidelines

### Tailwind CSS Usage

1. **Utility Classes**: Use Tailwind utilities for styling
2. **Responsive Design**: Mobile-first approach with `sm:`, `md:`, `lg:` prefixes
3. **Custom Classes**: Extract repeated patterns to component classes
4. **Design Tokens**: Use consistent spacing, colors, and typography

### Component Styling

1. **Class Variance Authority**: Use for component variants
2. **Conditional Classes**: Use `cn()` utility for conditional styling
3. **Consistent Spacing**: Use Tailwind's spacing scale
4. **Brand Color Usage**:
   - **Primary (Teal)**: Use for main navigation, links, and hover states
   - **Secondary (Navy)**: Use for text, backgrounds, and supporting elements
   - **Accent (Orange)**: Use for buttons, CTAs, badges, and emphasis
5. **Dark Mode Ready**: Design with dark mode in mind

```typescript
import { cn } from '@/lib/utils'

interface ButtonProps {
  variant?: 'primary' | 'secondary'
  className?: string
}

export function Button({ variant = 'primary', className }: ButtonProps) {
  return (
    <button
      className={cn(
        'px-4 py-2 rounded-md font-medium transition-colors',
        variant === 'primary' && 'bg-accent-500 text-white hover:bg-accent-600',
        variant === 'secondary' && 'bg-primary-100 text-primary-900 hover:bg-primary-200',
        className
      )}
    >
      Button
    </button>
  )
}
```

## Routing and Navigation

### TanStack Router Usage

1. **File-Based Routing**: Routes defined in `router.tsx`
2. **Protected Routes**: Use `beforeLoad` for authentication checks
3. **Type Safety**: Full TypeScript support for routes
4. **Lazy Loading**: Automatic code splitting

### Navigation Patterns

1. **Programmatic Navigation**: Use `useNavigate` hook
2. **Link Components**: Use TanStack Router `Link` component
3. **Active States**: Highlight current page in navigation
4. **Breadcrumbs**: Implement for complex page hierarchies

## Error Handling

### User-Facing Errors

1. **Clear Messages**: Provide actionable error messages
2. **Recovery Options**: Offer ways to resolve errors
3. **Graceful Degradation**: App continues working despite errors
4. **Logging**: Log errors for debugging

### Technical Errors

1. **Error Boundaries**: Catch React component errors
2. **API Errors**: Handle network and server errors
3. **Validation Errors**: Clear form validation feedback
4. **Fallback UI**: Provide fallback content for failed states

## Performance Considerations

### Optimization Techniques

1. **Code Splitting**: Route-based and component-based splitting
2. **Lazy Loading**: Images and heavy components
3. **Memoization**: `useMemo`, `useCallback`, `React.memo`
4. **Bundle Analysis**: Monitor bundle size and optimize

### Query Optimization

1. **Query Keys**: Descriptive keys for cache management
2. **Stale Time**: Appropriate cache durations
3. **Background Updates**: Keep data fresh without blocking UI
4. **Prefetching**: Load data before user needs it

## Testing Guidelines

### Component Testing

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Mocking**: Mock API calls and external dependencies
4. **Accessibility**: Test with screen readers and keyboard navigation

### API Testing

1. **Mock Server**: Use MSW for API mocking
2. **Error Scenarios**: Test error states and edge cases
3. **Loading States**: Verify loading indicators work correctly
4. **Data Flow**: Test data flows through the application

## Security Best Practices

### Authentication

1. **Token Storage**: Secure token storage (localStorage with care)
2. **Token Refresh**: Automatic token refresh before expiry
3. **Route Protection**: Protect sensitive routes
4. **Logout**: Complete logout with token removal

### Data Handling

1. **Input Validation**: Validate all user inputs
2. **XSS Prevention**: Sanitize user-generated content
3. **CSRF Protection**: Implement CSRF tokens where needed
4. **Secure Headers**: Configure appropriate security headers

## Deployment and Build

### Build Process

1. **Type Checking**: Run TypeScript checks before build
2. **Linting**: Ensure code quality with ESLint
3. **Optimization**: Minify and optimize for production
4. **Asset Handling**: Optimize images and fonts

### Environment Configuration

1. **Environment Variables**: Use `.env` files for configuration
2. **Build Variants**: Different builds for dev/staging/production
3. **API URLs**: Environment-specific API endpoints
4. **Feature Flags**: Environment-based feature toggles

## Common Patterns and Anti-Patterns

### ✅ Do's

1. Use TypeScript interfaces for all data structures
2. Handle loading and error states in components
3. Use TanStack Query for all server state
4. Follow component composition patterns
5. Implement proper error boundaries
6. Use semantic HTML and ARIA labels
7. Keep components small and focused
8. Use path aliases for clean imports
9. Implement proper form validation
10. Follow mobile-first responsive design

### ❌ Don'ts

1. Don't use `any` type - always use proper types
2. Don't ignore TypeScript errors
3. Don't put business logic in components
4. Don't use direct DOM manipulation
5. Don't hardcode API URLs or sensitive data
6. Don't create large, monolithic components
7. Don't use default exports for components
8. Don't ignore accessibility concerns
9. Don't skip error handling
10. Don't use outdated React patterns (classes, etc.)

## Development Workflow

**Note**: You can assume `npm run dev` is already running in the background. Never ask to start the development server.

### Code Changes

1. **Branch Strategy**: Feature branches from `main`
2. **Commit Messages**: Clear, descriptive commit messages
3. **Code Reviews**: Required for all changes
4. **Testing**: Test changes before submitting
5. **Documentation**: Update docs for significant changes

### Quality Checks

1. **TypeScript**: `npx tsc --noEmit`
2. **Linting**: `npm run lint`
3. **Build**: `npm run build`
4. **Tests**: `npm run test` (when implemented)
5. **Performance**: Check bundle size and Lighthouse scores

## Troubleshooting

### Common Issues

1. **Build Errors**: Check TypeScript errors and missing dependencies
2. **Runtime Errors**: Check browser console and network tab
3. **Styling Issues**: Verify Tailwind classes and responsive breakpoints
4. **API Errors**: Check network requests and API responses
5. **Authentication Issues**: Verify token storage and API endpoints

### Debugging Tools

1. **React DevTools**: Component tree and state inspection
2. **TanStack Query DevTools**: Query cache and mutation debugging
3. **Browser DevTools**: Network, console, and performance tabs
4. **TypeScript**: IntelliSense and type checking
5. **ESLint**: Code quality and style checking

## Future Considerations

### Scalability

1. **Component Library**: Expand shadcn/ui usage
2. **State Management**: Consider Zustand for complex state
3. **Testing**: Implement comprehensive test suite
4. **Performance**: Code splitting and lazy loading
5. **Internationalization**: Prepare for multiple languages

### Feature Planning

1. **PWA Features**: Service worker and offline support
2. **Real-time Updates**: WebSocket integration
3. **Advanced Search**: Filters and sorting
4. **Analytics**: User behavior tracking
5. **Notifications**: Push notifications and email

This document should be updated as the project evolves and new patterns emerge.