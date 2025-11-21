# Padel Watcher Frontend

Modern React frontend for the Padel Watcher court availability tracking platform.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom component library
- **Routing**: TanStack Router
- **State Management**: TanStack Query (React Query)
- **Authentication**: JWT-based authentication
- **Forms**: React Hook Form
- **Icons**: Lucide React
- **Date/Time**: date-fns

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Running Padel Watcher backend API (default: http://localhost:5000)

### Installation

```bash
# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env.development

# Start development server
npm run dev
```

The application will be available at http://localhost:5173

### Environment Variables

Create a `.env.development` file:

```env
VITE_API_URL=http://localhost:5000
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (Button, Input, Card, etc.)
│   ├── layout/         # Layout components (Header, Footer, Layout)
│   └── forms/          # Form components
├── pages/              # Page components
│   ├── auth/           # Authentication pages
│   ├── dashboard/      # Dashboard pages
│   ├── admin/          # Admin pages
│   └── public/         # Public pages
├── hooks/              # Custom React hooks
├── lib/                # Utilities and configurations
│   ├── api/            # API client and endpoints
│   ├── auth/           # Authentication utilities
│   └── utils/          # Helper functions
├── contexts/           # React contexts
├── types/              # TypeScript type definitions
└── router.tsx          # Route configuration
```

## Features

### Implemented

- ✅ User authentication (login/register)
- ✅ JWT token management
- ✅ User approval workflow
- ✅ Protected routes
- ✅ Responsive design
- ✅ Admin dashboard
- ✅ User dashboard
- ✅ Modern UI with Tailwind CSS

### Coming Soon

- 🔄 Court search interface
- 🔄 Search order management
- 🔄 Location/court browsing
- 🔄 Notifications system
- 🔄 User settings and preferences

## Development Guidelines

### Code Style

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Implement proper error handling
- Keep components small and focused

### Component Guidelines

- Use the custom UI components from `@/components/ui`
- Maintain consistent styling with Tailwind
- Ensure accessibility (ARIA labels, keyboard navigation)
- Add loading and error states

### API Integration

All API calls use TanStack Query:

```typescript
import { useQuery } from '@tanstack/react-query'
import { locationApi } from '@/lib/api'

const { data, isLoading, error } = useQuery({
  queryKey: ['locations'],
  queryFn: locationApi.getAll,
})
```

### Authentication

Access auth state via the `useAuth` hook:

```typescript
import { useAuth } from '@/contexts'

const { user, isAuthenticated, login, logout } = useAuth()
```

## Deployment

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Environment Configuration

Update `.env.production` with production API URL:

```env
VITE_API_URL=https://api.yourdomain.com
```

### Deployment Options

- **Vercel**: Connect your repo and deploy automatically
- **Netlify**: Drag and drop the `dist` folder
- **AWS S3 + CloudFront**: Upload to S3 and serve via CloudFront
- **Docker**: Use the included Dockerfile (to be added)

## Contributing

1. Follow the existing code structure
2. Maintain TypeScript strict mode compliance
3. Add proper error handling
4. Test responsiveness on mobile devices
5. Ensure accessibility standards

## License

Part of the Padel Watcher project.
