# Structural Changes for v0 Integration

## Recommended Project Prep

### 1. Add to .gitignore
```
# v0 Integration
v0-frontend/
.next/
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
```

### 2. Development Workflow (Two Services)
```bash
# Terminal 1: Backend API
python run_api.py  # Port 5050

# Terminal 2: v0 Frontend (recommended approach)
cd v0-frontend
npm run dev  # Port 5001 with hot reload
```

### 3. Alternative: Static Serving via Python (if needed)
```python
#!/usr/bin/env python3
"""
Alternative: Serve static v0 frontend files via Python
Only use if you need single-service deployment
"""
from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')  
def serve_v0_frontend(path):
    if path != "" and os.path.exists(f"v0-frontend/out/{path}"):
        return send_from_directory('v0-frontend/out', path)
    else:
        return send_from_directory('v0-frontend/out', 'index.html')

if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=True)
```

### 4. Environment Variables for v0 Frontend
Create `v0-frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:5050
API_BASE_URL=http://localhost:5050/api

# For production (Render):
# NEXT_PUBLIC_API_URL=https://carkeep-api.onrender.com
```

### 5. Package.json Configuration  
Ensure v0 output includes these scripts:
```json
{
  "scripts": {
    "dev": "next dev -p 5001",
    "build": "next build",
    "start": "next start -p 5001",
    "export": "next export"
  }
}
```

## Deployment Strategy (Render)

### Recommended: Two Services
1. **carkeep-api** (Python Web Service)
   - Repository: Point to root directory
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run_api.py`
   
2. **carkeep-frontend** (Node.js Web Service)  
   - Repository: Point to `v0-frontend/` directory
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`

### Alternative: Single Python Service
- Build v0 frontend to static files: `cd v0-frontend && npm run build && npm run export`
- Deploy Python service serving static files from `v0-frontend/out/`

## Cutover Checklist

### Development Setup
- [ ] Generate v0 frontend in `v0-frontend/` directory
- [ ] Configure v0 to point to `http://localhost:5050` for API calls
- [ ] Test two-terminal workflow: `python run_api.py` + `npm run dev`
- [ ] Verify all API endpoints work with v0 frontend on port 5001

### Production Preparation  
- [ ] Backup existing `frontend/` directory
- [ ] Set up Render services (API + Frontend) or choose single service
- [ ] Configure environment variables for production API URLs
- [ ] Test build process: `npm run build` in v0-frontend
- [ ] Update CORS settings in `run_api.py` if using different domains

### Post-Cutover Cleanup
- [ ] Remove Flask frontend dependencies from `requirements.txt`
- [ ] Archive or remove legacy `frontend/` directory
- [ ] Update documentation references to new structure

## No Changes Needed
- `run_api.py` - Backend API server
- `core/` - Business logic
- `data/` - JSON configurations  
- API endpoints or responses