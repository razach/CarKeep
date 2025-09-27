# Deployment Guide

CarKeep uses a modern **Next.js React frontend + Flask API backend** architecture deployed on Render.com as two separate services.

## 🌐 Production URLs

- **Frontend**: https://carkeep-frontend.onrender.com (Next.js React UI)
- **API Server**: https://carkeep.onrender.com (Flask API)

## 🏗️ Architecture Overview

- **Frontend**: Next.js 15 + React 19 + TypeScript serving static assets
- **API**: Flask server providing REST endpoints under `/api/*`
- **Communication**: Frontend makes direct API calls from browser to backend
- **Deployment**: Both services auto-deploy from GitHub main branch

## 🚀 Render.com Setup

### 1) API Server (Flask) - **ALREADY DEPLOYED**

**Service Name**: `carkeep`  
**URL**: https://carkeep.onrender.com  
**Status**: ✅ Active and auto-deploying

- **Root Directory**: `/` (repository root)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run_api.py`
- **Environment Variables**:
  ```
  SECRET_KEY=production-secret-key-here
  FLASK_DEBUG=0
  FLASK_ENV=production
  ```

### 2) Frontend Service (Next.js) - **NEW DEPLOYMENT**

**Service Name**: `carkeep-frontend` (to be created)  
**URL**: https://carkeep-frontend.onrender.com  
**Type**: Static Site

**Configuration**:
- **Root Directory**: `/v0-frontend`
- **Build Command**: `npm ci && npm run build`
- **Publish Directory**: `out` (Next.js static export)
- **Environment Variables**:
  ```
  NEXT_PUBLIC_API_URL=https://carkeep.onrender.com
  ```

### 3) Render Deployment Steps

#### **Step 1: Configure Next.js for Static Export**
Add to `v0-frontend/next.config.js`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig
```

#### **Step 2: Create Render Static Site**
1. Go to Render Dashboard
2. Click "New" → "Static Site"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `carkeep-frontend`
   - **Root Directory**: `v0-frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Publish Directory**: `out`
   - **Environment Variables**: 
     - `NEXT_PUBLIC_API_URL` = `https://carkeep.onrender.com`

#### **Step 3: Configure Auto-Deploy**
- **Branch**: `main`
- **Auto-Deploy**: `Yes`
- **Build Filter**: `v0-frontend/**` (optional - deploy only on frontend changes)

## 🛠️ Development Workflow

### **Local Development**
```bash
# Terminal 1: Start API server
python run_api.py  # → http://localhost:5050

# Terminal 2: Start frontend
cd v0-frontend
npm run dev        # → http://localhost:3000
```

### **Environment Configuration**
Create `v0-frontend/.env.local`:
```bash
# For local development:
NEXT_PUBLIC_API_URL=http://localhost:5050

# For production testing:
# NEXT_PUBLIC_API_URL=https://carkeep.onrender.com
```

### **Deployment Process**
1. **Develop locally** with API server + frontend
2. **Test changes** thoroughly
3. **Commit and push** to GitHub main branch
4. **Render auto-deploys** both services
5. **Verify production** deployment

## 🔧 Technical Configuration

### **CORS Setup**
The Flask API (`run_api.py`) is configured to allow cross-origin requests from the frontend:
```python
CORS(app, origins=[
    "http://localhost:3000",  # Local development
    "https://carkeep-frontend.onrender.com"  # Production
])
```

### **API Integration**
Frontend uses a custom `useApi` hook (`src/hooks/use-api.ts`) for API communication:
- Automatic API URL resolution via `NEXT_PUBLIC_API_URL`
- Error handling and loading states
- TypeScript integration

### **Build Configuration**
Next.js is configured for static export to work with Render's static site hosting:
- Output mode: `export`
- Optimized for static hosting
- Environment variables injected at build time

## 📋 Pre-Deploy Checklist

- [x] API server deployed and running
- [ ] Create Next.js static site on Render
- [ ] Configure environment variables
- [ ] Test production deployment
- [ ] Update DNS/domain settings (optional)

## 🐛 Troubleshooting

### **API Connection Issues**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS configuration in `run_api.py`
- Ensure API server is accessible

### **Build Failures**
- Check Node.js version compatibility
- Verify all dependencies are installed
- Review build logs in Render dashboard

### **Static Export Issues**
- Ensure `next.config.js` has proper export configuration
- Check for dynamic features that don't work with static export
- Verify environment variables are available at build time
