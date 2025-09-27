# CarKeep v0 Frontend

Modern React frontend for CarKeep vehicle cost comparison tool, built with Next.js 15, React 19, TypeScript, and shadcn/ui components.

## 🌐 Live Application

- **Production**: https://carkeep-frontend.onrender.com
- **Development**: http://localhost:3000

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- CarKeep API server running (see root README)

### Local Development
```bash
# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

### Production Build
```bash
# Build for static export
npm run build

# Serve locally (optional)
npm start
```

## 🛠️ Configuration

### Environment Variables
Create `.env.local` with:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5050  # Local development
# NEXT_PUBLIC_API_URL=https://carkeep.onrender.com  # Production API
```

### API Integration
The frontend communicates with the CarKeep Flask API:
- **Local API**: http://localhost:5050
- **Production API**: https://carkeep.onrender.com
- **Endpoints**: `/api/scenarios`, `/api/baseline`, `/api/state-taxes`

## 🏗️ Architecture

### Tech Stack
- **Framework**: Next.js 15 with App Router
- **UI Library**: React 19 with TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **Icons**: Lucide React
- **Forms**: React Hook Form + Zod validation
- **Build**: Turbopack (development) + Static Export (production)

### Project Structure
```
src/
├── app/                    # Next.js App Router pages
│   ├── compare/           # Comparison pages
│   ├── state-taxes/       # State tax management
│   └── page.tsx           # Main dashboard
├── components/            # Reusable React components
│   ├── ui/               # shadcn/ui base components
│   └── *.tsx             # Custom components
├── hooks/                # Custom React hooks
│   └── use-api.ts        # API integration hook
├── lib/                  # Utility functions
│   ├── dataTransforms.ts # API data transformation
│   └── formatters.ts     # Display formatting
└── types/                # TypeScript definitions
```

## 🔧 Development

### Adding New Components
```bash
# Add shadcn/ui components
npx shadcn@latest add button
npx shadcn@latest add dialog
```

### API Integration
Use the `useApi` hook for all API calls:
```typescript
import { useApi } from '@/hooks/use-api'

function MyComponent() {
  const { get, put, post, delete: del } = useApi()
  
  const loadData = async () => {
    const data = await get('/scenarios')
    setData(data)
  }
}
```

### Styling Guidelines
- Use Tailwind CSS utility classes
- Leverage shadcn/ui components for consistency
- Follow the existing design system patterns

## 📦 Deployment

### Render.com Static Site
The frontend deploys as a static site on Render.com:

1. **Build Command**: `npm ci && npm run build`
2. **Publish Directory**: `out`
3. **Environment**: `NEXT_PUBLIC_API_URL=https://carkeep.onrender.com`

### Auto-Deployment
- **Branch**: `main`
- **Trigger**: Changes to `v0-frontend/**`
- **Build Time**: ~2-3 minutes

## 🐛 Troubleshooting

### Common Issues

**Build Failures**
- Ensure Node.js version compatibility (18+)
- Clear `.next` folder and rebuild
- Check for TypeScript errors

**API Connection Issues**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check API server is running and accessible
- Confirm CORS configuration allows your domain

**Static Export Problems**
- Avoid dynamic Next.js features not supported in static export
- Ensure all environment variables are prefixed with `NEXT_PUBLIC_`
- Check `next.config.js` export configuration

### Debug Commands
```bash
# Clear all caches
rm -rf .next out node_modules package-lock.json
npm install

# Run type checking
npx tsc --noEmit

# Build and inspect output
npm run build
ls -la out/
```

## 📋 Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production (static export)
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## 🤝 Contributing

1. Follow existing code patterns and TypeScript conventions
2. Use the established component structure
3. Test changes locally before committing
4. Ensure builds pass before deployment

---

**Need help?** Check the main CarKeep README or deployment documentation in `/docs/DEPLOYMENT.md`
