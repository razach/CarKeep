# CarKeep AI Coding Assistant Instructions

## Architecture Overview

CarKeep is a **backend + frontend application** for vehicle cost comparison with two frontend options:

#### API Server (Core)
- **API Server** (`run_api.py` → port 5050): Core calculations, data management, `/api/*` endpoints
- **Deployed at**: https://carkeep.onrender.com (production API)

#### Frontend Options
- **Flask Frontend** (`run.py` → port 5001): Original server-rendered UI with Jinja templates
- **v0 Next.js Frontend** (`v0-frontend/` → port 3000): Modern React frontend generated from v0.app

The system uses a **baseline + scenarios** approach where all vehicle options are compared against keeping the current car (baseline).

## Core Data Flow

1. **Scenarios** are defined in `data/scenarios/scenarios.json` with baseline + examples structure
2. **Calculator engine** (`core/calculators/`) processes JSON → cost analysis via `VehicleCostCalculator`
3. **API endpoints** (`core/api/routes/scenarios.py`) expose CRUD operations
4. **Frontend routes** (`frontend/routes/views.py`) render templates using `APIClient` for server-side calls

## Key Architectural Patterns

### JSON-Driven Configuration
All scenarios are **pure JSON configuration** - no code changes needed to add vehicles:
```json
"my_scenario": {
  "scenario": {
    "type": "lease|loan",
    "vehicle": { "name": "...", "msrp": 50000, "values_3yr": [...] },
    "financing": { "monthly_payment": 600, ... }
  },
  "trade_in": { "trade_in_value": 18000, ... }
}
```

### State Tax System
Uses `StateTaxRegistry` with `data/configs/state_tax_configs.json` for property tax calculations. States can override baseline tax jurisdiction.

### Cost Override Pattern
Scenarios can override default costs with `cost_overrides` structure:
```json
"cost_overrides": {
  "insurance_monthly": { "Vehicle A": 120, "Vehicle B": 200 },
  "maintenance_monthly": { ... }
}
```

## Development Workflows

### Running the Application
**Always start servers manually in separate terminals** (no automated startup tools):

#### Option 1: Flask Frontend (Legacy)
```bash
# Start API server (terminal 1)
python run_api.py  # → http://localhost:5050

# Start frontend (terminal 2) 
python run.py      # → http://localhost:5001
```

#### Option 2: v0 Next.js Frontend (Current)
```bash
# Start API server (terminal 1) - REQUIRED for both options
python run_api.py  # → http://localhost:5050

# Start v0 Next.js frontend (terminal 2)
cd v0-frontend
npm run dev        # → http://localhost:3000
```

**Note**: The API server at localhost:5050 is required for both frontend options. The v0 frontend consumes the same REST API that the Flask frontend uses.

### Command-Line Tools
```bash
# List all scenarios
python core/calculators/run_scenarios.py list

# Run single scenario with CSV export
python core/calculators/run_scenarios.py scenario_name --csv

# Generate comparison matrix (all scenarios)
python scripts/generate_comparison_matrix.py
```

### Adding New Scenarios
1. Edit `data/scenarios/scenarios.json` - add to `examples` section
2. Restart API server to reload JSON
3. No code changes required

## Critical Integration Points

### Frontend ↔ API Communication
Frontend makes **server-side** calls to API (not browser-side). Use `current_app.api_client.get('/api/endpoint')` pattern in routes.

### Calculator Integration
Core calculations happen in `VehicleCostCalculator.calculate_comparison()`. All financial logic (depreciation, taxes, investment opportunity cost) is centralized here.

### Template Data Structure
Templates expect specific data shapes. Key transformations in `frontend/routes/views.py`:
- API responses → template-friendly formats
- Error handling with `error.html` fallback
- Cache headers prevent stale data

## Project-Specific Conventions

### File Organization
- `core/` = Business logic, calculations, API
- `frontend/` = Flask UI, templates, server-side client code  
- `v0-frontend/` = Next.js React frontend with shadcn/ui components
- `data/` = JSON configs, scenarios, exports
- `scripts/` = Standalone utilities, matrix generation

### v0 Frontend Architecture
- **Built with**: Next.js 15, React, TypeScript, Tailwind CSS, shadcn/ui
- **API Integration**: Custom `useApi` hook in `src/hooks/use-api.ts`
- **Environment**: Uses `.env.local` for API URL configuration
- **Components**: shadcn/ui components in `src/components/ui/`
- **Common Issue**: Avoid `useEffect` dependency arrays with non-memoized functions (causes infinite API calls)

### Error Handling
- API returns structured JSON errors
- Frontend catches exceptions → `error.html` template
- Calculator validates inputs and provides detailed error messages

### Development Philosophy
**Keep It Simple**: Server-rendered Flask + Jinja, incremental htmx enhancements. No SPA framework. See README "Project Direction" section.

## Essential Dependencies

- **Flask 2.3.3** with Blueprints (`frontend_bp`, API routes)
- **pandas/numpy** for financial calculations and CSV export
- **flask-cors** for API cross-origin (configured for localhost:5001)
- **requests** for frontend → API communication

## Common Tasks

### Debugging Calculations
Check `data/exports/` for CSV outputs with detailed breakdowns. Use `--csv` flag with scenarios for individual analysis.

### State Tax Issues
Modify `data/configs/state_tax_configs.json` and restart API server. Use `StateTaxRegistry.add_state()` for runtime additions.

### Template Issues
Templates use Jinja2. Key files: `base.html`, `index.html`, `scenario.html`, `comparison.html`. API client calls are in route handlers, not templates.