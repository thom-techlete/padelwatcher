---
agent: agent
---

# Build Padel Watcher Frontend

## Overview
Build a modern, responsive React frontend for the Padel Watcher application using React, Vite, Tailwind CSS, TanStack Query/Router, and shadcn/ui. The application is a SaaS-style platform for padel court availability tracking with user approval system.

## Technical Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with shadcn/ui component library
- **Routing**: TanStack Router
- **State Management**: TanStack Query for server state, React Context for client state
- **Authentication**: JWT-based with secure token management
- **HTTP Client**: TanStack Query (React Query) for API calls
- **Forms**: React Hook Form with validation
- **Icons**: Lucide React
- **Date/Time**: date-fns

## Project Structure
```
web/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── layout/         # Layout components
│   │   └── forms/          # Form components
│   ├── pages/              # Page components
│   │   ├── auth/           # Authentication pages
│   │   ├── dashboard/      # Dashboard pages
│   │   ├── admin/          # Admin pages
│   │   └── public/         # Public pages
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utilities and configurations
│   │   ├── api/            # API client and endpoints
│   │   ├── auth/           # Authentication utilities
│   │   ├── utils/          # Helper functions
│   │   └── validations/    # Form validations
│   ├── contexts/           # React contexts
│   ├── types/              # TypeScript type definitions
│   └── styles/             # Global styles and Tailwind config
├── public/                 # Static assets
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Design System & Styling Guide

### Color Palette
- **Primary**: Blue (#3b82f6) - Professional, trustworthy
- **Secondary**: Green (#10b981) - Success, growth
- **Accent**: Orange (#f59e0b) - Attention, warnings
- **Neutral**: Gray scale (#f8fafc to #0f172a)
- **Background**: Clean whites and light grays

### Typography
- **Font Family**: Inter (system font stack fallback)
- **Headings**: 600 weight, proper hierarchy
- **Body**: 400 weight, good readability
- **Sizes**: Mobile-first responsive scaling

### Component Guidelines
- **shadcn/ui** as base components
- **Consistent spacing**: 4px grid system
- **Border radius**: 8px for cards, 6px for buttons
- **Shadows**: Subtle shadows for depth
- **Focus states**: Clear focus indicators for accessibility

### SaaS Styling Principles
- **Clean and minimal**: White space, clear hierarchy
- **Professional**: Corporate feel without being sterile
- **Trustworthy**: Consistent, polished appearance
- **Scalable**: Design tokens for easy theming
- **Accessible**: WCAG AA compliance

## Authentication System

### Requirements
- JWT token-based authentication
- Secure token storage (httpOnly cookies or secure localStorage)
- Automatic token refresh
- Route protection based on authentication status
- Role-based access (admin vs regular user)

### Implementation Approach
- Use TanStack Query for auth API calls
- React Context for auth state management
- Protected routes with TanStack Router
- Automatic logout on token expiry
- Loading states during auth checks

## Core Features & Pages

### 1. Authentication Pages
- **Login Page**: Email/password form with validation
- **Registration Page**: User registration form
- **Pending Approval Page**: Shown to unapproved users

### 2. Dashboard (Regular Users)
- **Overview**: Welcome message, quick stats
- **Search Orders**: List of user's active search orders
- **Recent Activity**: Latest search results
- **Quick Actions**: Create new search order

### 3. Court Search Interface
- **Search Form**: Date range, time preferences, court type
- **Results Display**: Available courts in table/card format
- **Create Search Order**: Convert search to monitored order

### 4. Search Orders Management
- **List View**: All user's search orders with status
- **Order Details**: View results, edit, cancel orders
- **Notifications**: Show pending notifications

### 5. Court/Location Management
- **Browse Locations**: View available padel clubs
- **Add Location**: Form to add new court locations
- **Location Details**: View courts at a location
- **Manage Courts**: Add/edit courts at locations

### 6. Admin Panel (Admin Users Only)
- **User Management**: View all users, approve/reject pending
- **System Overview**: User stats, system health
- **Pending Approvals**: Dedicated interface for user approvals

### 7. Settings/Profile
- **Profile Management**: Update user information
- **Preferences**: Search preferences, notifications
- **Account Security**: Change password

## API Integration

### Base Configuration
- **Base URL**: `http://localhost:5000` (configurable via environment)
- **Authentication**: Bearer token in Authorization header
- **Error Handling**: Consistent error responses and user feedback

### Key Endpoints to Integrate
- **Auth**: `/api/auth/register`, `/api/auth/login`
- **Locations**: `/api/locations`, `/api/locations/{id}/courts`
- **Search**: `/api/search/available`, `/api/search-orders`
- **Admin**: `/api/admin/users/*` (admin only)
- **Health**: `/health` for connectivity checks

### Data Fetching Strategy
- TanStack Query for all API calls
- Optimistic updates where appropriate
- Background refetching for real-time data
- Proper loading and error states

## Best Practices Implementation

### Performance
- **Code Splitting**: Route-based and component-based splitting
- **Lazy Loading**: Images, heavy components
- **Query Optimization**: Proper caching, background updates
- **Bundle Analysis**: Keep bundle sizes optimized

### Security
- **Input Validation**: Client and server-side validation
- **XSS Prevention**: Proper sanitization
- **CSRF Protection**: Token-based protection
- **Secure Headers**: Proper CSP, HSTS in production

### Accessibility
- **WCAG AA Compliance**: Proper ARIA labels, keyboard navigation
- **Screen Reader Support**: Semantic HTML, alt texts
- **Color Contrast**: Minimum 4.5:1 ratio
- **Focus Management**: Clear focus indicators

### UX/UI Excellence
- **Loading States**: Skeleton screens, spinners
- **Error Handling**: User-friendly error messages
- **Empty States**: Helpful guidance when no data
- **Responsive Design**: Mobile-first approach
- **Progressive Enhancement**: Works without JavaScript

### Code Quality
- **TypeScript**: Strict typing throughout
- **Component Composition**: Reusable, composable components
- **Custom Hooks**: Business logic extraction
- **Error Boundaries**: Graceful error handling
- **Testing Setup**: Unit and integration test structure

## MVP Constraints & Expansion Planning

### MVP Scope
- Core authentication flow
- Basic court search functionality
- Search order management
- Admin user approval interface
- Responsive design for mobile and desktop

### Future Expansion Points
- **Modular Architecture**: Easy to add new features
- **Scalable State**: Query invalidation patterns ready
- **Component Library**: Consistent design system
- **Internationalization**: i18n-ready structure
- **PWA Features**: Service worker setup ready
- **Analytics**: Event tracking hooks ready

### Technical Debt Prevention
- **Clean Architecture**: Separation of concerns
- **Documentation**: Inline comments and README
- **Linting**: ESLint + Prettier configuration
- **Git Hooks**: Pre-commit quality checks

## Success Criteria

### Functional Requirements
- [ ] User can register and wait for approval
- [ ] Approved users can login and access dashboard
- [ ] Court search works with real-time results
- [ ] Search orders can be created and managed
- [ ] Admin can approve/reject users
- [ ] Location/court management interface works
- [ ] All forms have proper validation
- [ ] Responsive design works on all devices

### Technical Requirements
- [ ] TypeScript strict mode enabled
- [ ] No console errors in production
- [ ] Lighthouse score > 90 for performance
- [ ] WCAG AA accessibility compliance
- [ ] Bundle size < 500KB (gzipped)
- [ ] All API endpoints integrated
- [ ] Proper error handling throughout

### Quality Requirements
- [ ] Clean, maintainable code structure
- [ ] Comprehensive component documentation
- [ ] Proper TypeScript types
- [ ] Consistent styling and design
- [ ] Mobile-first responsive design
- [ ] Loading states and error handling

## Development Workflow

1. **Setup**: Initialize Vite + React + TypeScript project
2. **Styling**: Configure Tailwind + shadcn/ui
3. **Routing**: Set up TanStack Router with protected routes
4. **Authentication**: Implement JWT auth system
5. **API Integration**: Set up TanStack Query with API client
6. **Core Pages**: Build authentication and dashboard
7. **Features**: Implement search, orders, admin panel
8. **Polish**: Add responsive design, accessibility, performance
9. **Testing**: Add basic tests and documentation

## Environment Configuration

Create `.env` files for different environments:
- `.env.development`: Local API URL
- `.env.production`: Production API URL
- Environment variables for API keys, feature flags

## Deployment Readiness

- **Build Optimization**: Proper Vite production build
- **Asset Optimization**: Image optimization, code splitting
- **SEO**: Meta tags, proper HTML structure
- **Monitoring**: Error tracking setup (Sentry ready)
- **Analytics**: Event tracking hooks (Google Analytics ready)

This frontend should serve as a solid foundation for the Padel Watcher SaaS platform, balancing MVP simplicity with production-ready architecture and best practices.
