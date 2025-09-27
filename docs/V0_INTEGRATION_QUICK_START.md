# CarKeep v0 Integration Guide

## Quick Setup for v0 Frontend Replacement

### Current State
- `frontend/` folder contains legacy Flask frontend (will be replaced)
- `run.py` is the Flask frontend server (will be removed/updated)  
- `run_api.py` is the backend API server (keep as-is)
- All data and business logic is in `core/` and `data/` (no changes needed)

### Integration Steps
1. **Use Public API**: Point v0 to `https://carkeep.onrender.com/api` 
2. **Generate v0 Frontend**: Create new frontend components
3. **Deploy Frontend**: Host v0 frontend separately from API
4. **Update Documentation**: This replaces the Flask frontend entirely

## API Endpoints (Essential for v0)

**Base URL**: `https://carkeep.onrender.com/api`

**Security**: 
- Rate limited to 100 requests/minute per IP
- CORS enabled for v0.dev domains
- No API key required currently (easy integration)
- See `docs/API_SECURITY.md` for production security options

### Primary Data Sources
- `GET /scenarios` - All scenarios + baseline data
- `GET /scenario/{name}` - Detailed results for one scenario  
- `GET /comparison-results` - All scenarios with calculations
- `GET /baseline` - Current vehicle details

### CRUD Operations
- `POST /scenarios` - Create new scenario
- `PUT /scenario/{name}` - Update scenario
- `DELETE /scenarios/{name}` - Delete scenario
- `PUT /baseline` - Update baseline vehicle

### Required Fields for New Scenario
```json
{
  "scenario_name": "unique_key",
  "description": "Human description", 
  "vehicle_name": "Car Name",
  "msrp": 45000,
  "financing_type": "lease",  // or "loan"
  "monthly_payment": 600
}
```

## Data Formatting for UI
- **Money**: Display as currency (API returns whole dollars)
- **Cost Differences**: Green for negative (savings), Red for positive (costs more)
- **Percentages**: API returns decimals, multiply by 100 for display
- **Vehicle Types**: Badge "lease" vs "loan" scenarios

## File Structure After Integration

### Option 1: Replace Existing
```
CarKeep/
├── frontend/          # Replace with v0 output
├── run.py            # Update to serve v0 static files (optional)
├── run_api.py        # Keep unchanged - backend API
└── ...
```

### Option 2: New Directory  
```
CarKeep/
├── v0-frontend/      # New v0 generated frontend
├── frontend/         # Old Flask frontend (can delete later)
├── run.py           # Legacy (can remove)
├── run_api.py       # Keep unchanged - backend API  
└── ...
```

## Testing Integration
```bash
# 1. Start backend
python run_api.py

# 2. Test API
curl https://carkeep.onrender.com/api/scenarios

# 3. Should return JSON with baseline + scenarios
# 4. All v0 API calls should work against the production API
```

## Key UI Pages Needed
1. **Scenarios List** - Cards showing all scenarios
2. **Scenario Detail** - Cost breakdown for individual scenario
3. **Comparison Table** - Side-by-side scenarios  
4. **Create/Edit Forms** - Add/modify scenarios
5. **Baseline Edit** - Modify current vehicle

No backend changes needed - API is ready for v0 integration.