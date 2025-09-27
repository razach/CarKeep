# CarKeep API Integration Guide for v0.app

## Project Structure for v0 Integration

### Current Structure (will be replaced)
```
CarKeep/
├── frontend/           # LEGACY - to be replaced by v0 output
├── run.py             # LEGACY - Flask frontend server
├── run_api.py         # KEEP - Backend API server
├── core/              # KEEP - Business logic
├── data/              # KEEP - JSON configurations
└── docs/              # KEEP - Documentation
```

### Recommended v0 Integration Structure
```
CarKeep/
├── v0-frontend/       # NEW - v0 generated frontend (Next.js/React)
├── run_api.py         # EXISTING - Backend API server
├── core/              # EXISTING - Business logic  
├── data/              # EXISTING - JSON configurations
└── docs/              # EXISTING - Documentation
```

## API Server Configuration

### Backend API (Port 5050)
**File**: `run_api.py`
**Status**: Ready for v0 integration - no changes needed
**CORS**: Already configured for localhost development
**Endpoints**: All documented below with real response structures

### Development Workflow
1. **Start Backend**: `python run_api.py` (port 5050)
2. **Verify API**: `curl http://localhost:5050/api/scenarios`
3. **Generate v0 Frontend**: Point to `http://localhost:5050` as API base
4. **Test Integration**: Frontend makes calls to localhost:5050/api/*

## Essential API Endpoints for v0

### Core Data Endpoints

#### GET /api/scenarios
**Purpose**: Retrieve all scenarios and baseline data
**Response Structure**:
```json
{
  "baseline": {
    "description": "Acura RDX - Keep current car (baseline)",
    "state": "VA",
    "vehicle": {
      "name": "Acura RDX",
      "current_value": 21000.0,
      "msrp": 0.0,
      "values_3yr": [21000, 18900, 17000, 15300],
      "impairment": 3000.0,
      "impairment_affects_taxes": false
    },
    "current_loan": {
      "monthly_payment": 564.1,
      "principal_balance": 9909.95,
      "interest_rate": 0.055,
      "extra_payment": 0.0
    }
  },
  "scenarios": {
    "scenario_name": {
      "description": "Human readable description",
      "scenario": {
        "type": "lease|loan",
        "vehicle": {
          "name": "Vehicle Name",
          "msrp": 45000,
          "current_value": 0,
          "values_3yr": [35000, 31500, 28350, 25515]
        },
        "financing": {
          // For loans:
          "monthly_payment": 1073.47,
          "loan_term": 36,
          "principal_balance": 35000
          
          // For leases:
          "monthly_payment": 368.0,
          "lease_terms": 36,
          "msrp": 72800.0,
          "incentives": {}
        }
      },
      "trade_in": {
        "trade_in_value": 18000,
        "loan_balance": 9909.95,
        "incentives": 0
      },
      "cost_overrides": {
        "insurance_monthly": {"Vehicle A": 120, "Vehicle B": 200},
        "maintenance_monthly": {"Vehicle A": 50, "Vehicle B": 35}
      }
    }
  }
}
```

#### GET /api/scenario/{scenario_name}
**Purpose**: Get detailed calculation results for a specific scenario
**Response Structure**:
```json
{
  "description": "Scenario description",
  "results": {
    "summary": {
      "columns": ["Cost Category", "Baseline Vehicle", "New Vehicle"],
      "data": [
        ["Lease/Loan Payment", "$10355", "$38645"],
        ["Property Tax", "$1147", "$2503"],
        ["Insurance", "$3600", "$0"],
        ["NET OUT-OF-POCKET", "$10074", "$19278"]
      ]
    },
    "monthly_payment": {
      "columns": ["Category", "New Vehicle", "Baseline (Current)", "Baseline (After Payoff)"],
      "data": [
        ["Payment", "$1073", "$564", "$0"],
        ["Property Tax", "$70", "$32", "$32"],
        ["TOTAL MONTHLY", "$1143", "$910", "$346"]
      ]
    },
    "cost_difference": {
      "columns": ["Cost Component", "Amount", "Description"],
      "data": [
        ["Depreciation Difference", "$-785", "Detailed explanation"],
        ["TOTAL COST DIFFERENCE", "$9204", "Total additional cost"]
      ]
    }
  }
}
```

#### GET /api/comparison-results
**Purpose**: Get comparison results for all scenarios
**Response**: Object with scenario names as keys, each containing the same structure as individual scenario results

#### GET /api/cost-analysis
**Purpose**: Get detailed financial analysis across all scenarios
**Response Structure**:
```json
{
  "analysis": {
    "baseline": {
      "scenario_name": "baseline",
      "vehicle_name": "Acura RDX",
      "monthly_payment": 564.1,
      "total_monthly": 864.1,
      "vs_baseline": 0
    },
    "scenarios": [
      {
        "scenario_name": "scenario_key",
        "description": "Description",
        "vehicle_name": "Vehicle Name",
        "monthly_payment": 368.0,
        "vs_baseline": -496.1,
        "total_monthly": 368.0
      }
    ],
    "detailed_analysis": [
      {
        "description": "Detailed scenario",
        "lease_loan_payment": 13248.0,
        "equity_36mo": 15759,
        "insurance": 7200,
        "maintenance": 1260,
        "fuel_electricity": 1620,
        "monthly_evolution": {
          "payment": 368.0,
          "property_tax": 172.67,
          "insurance": 200,
          "maintenance": 35,
          "fuel_electricity": 45
        }
      }
    ]
  }
}
```

### CRUD Operations

#### POST /api/scenarios
**Purpose**: Create new scenario
**Required Fields**: `scenario_name`, `description`, `vehicle_name`, `msrp`, `financing_type`, `monthly_payment`

#### PUT /api/scenario/{scenario_name}
**Purpose**: Update existing scenario
**Required Fields**: `description`, `vehicle_name`, `msrp`, `financing_type`, `monthly_payment`

#### DELETE /api/scenarios/{scenario_name}
**Purpose**: Delete scenario

#### POST /api/scenarios/{scenario_name}/duplicate
**Purpose**: Duplicate scenario with "_copy" suffix

### Baseline Management

#### GET /api/baseline
**Purpose**: Get baseline scenario data

#### PUT /api/baseline
**Purpose**: Update baseline scenario
**Required Fields**: `description`, `vehicle_name`, `current_value`, `state`

### State Tax Configuration

#### GET /api/state-taxes
**Purpose**: Get all state tax configurations
**Response**: Object with state codes as keys containing tax rates and relief information

#### POST /api/state-taxes
**Purpose**: Create new state tax configuration
**Required Fields**: `state_code`, `property_tax_rate`, `pptra_relief`, `relief_cap`, `state_name`

#### PUT /api/state-taxes/{state_code}
**Purpose**: Update state tax configuration

#### DELETE /api/state-taxes/{state_code}
**Purpose**: Delete state tax configuration (protected states: VA, TX, CA cannot be deleted)

## Recommended Modular Component Structure

### 1. Layout Components
```
/components/layout/
├── Header.tsx           # Navigation with active states
├── Footer.tsx           # Version info, links
├── Sidebar.tsx          # Optional sidebar navigation
└── Layout.tsx           # Main layout wrapper
```

### 2. Core Feature Modules

#### Scenarios Module
```
/components/scenarios/
├── ScenariosList.tsx        # Main scenarios overview (from /api/scenarios)
├── ScenarioCard.tsx         # Individual scenario card
├── ScenarioDetail.tsx       # Detailed scenario view (from /api/scenario/{name})
├── ScenarioForm.tsx         # Create/edit scenario form
├── ScenarioComparison.tsx   # Side-by-side comparison
└── ScenarioActions.tsx      # Delete, duplicate, edit actions
```

#### Baseline Module
```
/components/baseline/
├── BaselineOverview.tsx     # Baseline summary display
├── BaselineEdit.tsx         # Baseline editing form
└── BaselineCard.tsx         # Baseline info card component
```

#### Cost Analysis Module
```
/components/analysis/
├── CostAnalysisView.tsx     # Main cost analysis page
├── MonthlyBreakdown.tsx     # Monthly cost breakdown table
├── SummaryTable.tsx         # 3-year summary table  
├── CostDifferenceTable.tsx  # Cost difference breakdown
├── ComparisonChart.tsx      # Visual charts (Chart.js via CDN)
└── AnalysisFilters.tsx      # Filter/sort controls
```

#### State Taxes Module
```
/components/taxes/
├── StateTaxesList.tsx       # State tax configurations table
├── StateTaxForm.tsx         # Create/edit state tax form
├── StateTaxRow.tsx          # Editable table row component
└── TaxCalculatorInfo.tsx    # Tax calculation explanation
```

### 3. Shared Components
```
/components/shared/
├── DataTable.tsx            # Reusable table component
├── FormInput.tsx            # Standardized form inputs
├── LoadingSpinner.tsx       # Loading states
├── ErrorMessage.tsx         # Error display
├── Modal.tsx                # Modal dialog
├── Toast.tsx                # Success/error notifications
├── Badge.tsx                # Status badges (lease/loan, savings/cost)
├── Button.tsx               # Standardized buttons
└── Card.tsx                 # Card wrapper component
```

### 4. Hooks and Utilities
```
/hooks/
├── useApi.ts                # API integration hook
├── useScenarios.ts          # Scenarios data management
├── useBaseline.ts           # Baseline data management
└── useStateTaxes.ts         # State taxes data management

/utils/
├── api.ts                   # API client functions
├── formatters.ts            # Currency, percentage formatting
├── validators.ts            # Form validation
└── constants.ts             # API endpoints, defaults
```

## Key Development Patterns

### 1. API Integration Pattern
```typescript
// useApi hook example
const useApi = () => {
  const baseUrl = 'http://localhost:5050/api';
  
  const get = async (endpoint: string) => {
    const response = await fetch(`${baseUrl}${endpoint}`);
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return response.json();
  };
  
  return { get, post, put, delete };
};

// Usage in components
const ScenariosList = () => {
  const [scenarios, setScenarios] = useState(null);
  const [loading, setLoading] = useState(true);
  const { get } = useApi();
  
  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const data = await get('/scenarios');
        setScenarios(data);
      } catch (error) {
        console.error('Failed to fetch scenarios:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchScenarios();
  }, []);
  
  if (loading) return <LoadingSpinner />;
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Object.entries(scenarios.scenarios).map(([name, scenario]) => (
        <ScenarioCard key={name} name={name} scenario={scenario} />
      ))}
    </div>
  );
};
```

### 2. Form Handling Pattern
```typescript
const ScenarioForm = ({ scenario, onSave }) => {
  const [formData, setFormData] = useState({
    description: scenario?.description || '',
    vehicle_name: scenario?.scenario?.vehicle?.name || '',
    msrp: scenario?.scenario?.vehicle?.msrp || '',
    financing_type: scenario?.scenario?.type || 'lease',
    monthly_payment: scenario?.scenario?.financing?.monthly_payment || ''
  });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await onSave(formData);
      // Show success toast
    } catch (error) {
      // Show error toast
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <FormInput
        label="Description"
        value={formData.description}
        onChange={(value) => setFormData({...formData, description: value})}
        required
      />
      {/* Additional form fields */}
    </form>
  );
};
```

### 3. Data Display Pattern
```typescript
const DataTable = ({ columns, data, className = "" }) => {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="min-w-full bg-white border border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column, index) => (
              <th key={index} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-gray-50">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

## TailwindCSS Design System

### Color Palette
```css
/* Primary colors for financial data */
.text-profit { @apply text-green-600; }      /* Savings/lower costs */
.text-loss { @apply text-red-600; }          /* Higher costs */
.text-neutral { @apply text-gray-600; }      /* Equal costs */

.bg-profit { @apply bg-green-50 border-green-200; }
.bg-loss { @apply bg-red-50 border-red-200; }

/* Vehicle type badges */
.badge-lease { @apply bg-blue-100 text-blue-800; }
.badge-loan { @apply bg-purple-100 text-purple-800; }
```

### Component Classes
```css
/* Cards */
.card { @apply bg-white rounded-lg shadow-md border border-gray-200 p-6; }
.card-hover { @apply hover:shadow-lg transition-shadow duration-200; }

/* Buttons */
.btn-primary { @apply bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md; }
.btn-secondary { @apply bg-gray-200 hover:bg-gray-300 text-gray-900 px-4 py-2 rounded-md; }
.btn-danger { @apply bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md; }

/* Form inputs */
.form-input { @apply block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500; }
.form-label { @apply block text-sm font-medium text-gray-700 mb-1; }
```

## Testing API Integration

### Verify Backend Connection
```bash
# Test if backend is running
curl http://localhost:5050/api/scenarios

# Expected: JSON response with baseline and scenarios data
# If 404 or connection refused: Backend not running
```

### Common API Responses to Handle
- **200 OK**: Successful data retrieval
- **201 Created**: Successful creation
- **400 Bad Request**: Validation error (check required fields)
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Scenario name already exists
- **500 Internal Server Error**: Backend calculation error

## Development Workflow

1. **Start Backend API**:
   ```bash
   cd /path/to/carkeep
   python run_api.py  # Runs on port 5050
   ```

2. **Verify API Connection**:
   ```bash
   curl http://localhost:5050/api/scenarios
   ```

3. **Build Frontend Components**:
   - Start with layout and navigation
   - Build scenarios list and detail views
   - Add comparison and cost analysis features
   - Implement state tax management
   - Add forms for CRUD operations

4. **Key Integration Points**:
   - All monetary values are in dollars (no cents in API)
   - Percentages in API are decimals (0.055 = 5.5%)
   - 3-year depreciation curves are arrays of 4 values [Y0, Y1, Y2, Y3]
   - Cost differences: positive = new vehicle costs more, negative = saves money

## Performance Considerations

- **API Caching**: Consider caching scenario data that doesn't change frequently
- **Loading States**: Show spinners for API calls
- **Error Boundaries**: Handle API failures gracefully
- **Debounced Search**: For filtering scenarios
- **Lazy Loading**: For large comparison tables

This comprehensive guide should give v0.app all the context needed to build a modern, efficient frontend that properly integrates with your CarKeep backend API while maintaining the modular structure and TailwindCSS styling constraints you specified.