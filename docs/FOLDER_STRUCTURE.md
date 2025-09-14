# CarKeep Folder Structure

## 🗂️ **Project Structure**

### **Current Structure** (Updated with UI/API Separation)
```
CarKeep/
├── app/                    # Legacy web application (being migrated)
├── frontend/              # Frontend application (New)
│   ├── app/
│   │   ├── static/       # Frontend assets (CSS, JS, images)
│   │   └── templates/    # Frontend templates
│   ├── routes/           # Frontend-specific routes
│   ├── utils/           # Frontend utilities
│   └── __init__.py       # Frontend initialization
├── core/                 # Backend + Business Logic
│   ├── api/             # API Layer (New)
│   │   ├── routes/      # API endpoints
│   │   └── utils/       # API-specific utilities
│   ├── calculators/     # Calculation engines
│   ├── models/          # Shared data models
│   └── utils/           # Core utilities
├── data/                # Shared data storage
│   ├── configs/         # Configuration files
│   ├── templates/       # Data templates
│   ├── scenarios/       # Scenario data
│   └── exports/         # Generated exports
├── tests/              # Test suites (New)
│   ├── frontend/       # Frontend tests
│   ├── core/          # Core logic tests
│   └── api/           # API endpoint tests
├── docs/              # Documentation
├── instance/          # Environment-specific configs
├── requirements/      # Dependencies by component (New)
│   ├── core.txt      # Core requirements
│   ├── frontend.txt  # Frontend-specific requirements
│   └── dev.txt       # Development requirements
└── run.py            # Application entry point

Migration Status:
✓ Directory structure created
✓ Route separation implemented
✓ Requirements split
✓ API endpoints defined
- Testing structure prepared
- Configuration separation pending
```

### **Target Structure** (Final State)
```
CarKeep/
├── frontend/              # Frontend application
│   ├── app/
│   │   ├── static/       # Frontend assets (CSS, JS, images)
│   │   └── templates/    # Frontend templates
│   ├── routes/           # Frontend-specific routes
│   └── __init__.py       # Frontend initialization
├── core/                 # Backend + Business Logic
│   ├── api/             # API Layer
│   │   ├── routes/      # API endpoints
│   │   └── utils/       # API-specific utilities
│   ├── calculators/     # Calculation engines
│   │   ├── vehicle_cost_calculator.py
│   │   ├── car_keep_runner.py
│   │   ├── cost_analyzer.py
│   │   └── run_scenarios.py
│   ├── models/          # Shared data models
│   └── utils/           # Core utilities
├── data/                # Shared data storage
│   ├── configs/         # Configuration files
│   ├── templates/       # Data templates
│   └── exports/         # Generated exports
├── instance/           # Environment-specific configs
│   ├── config.py      # Shared configuration
│   └── api_config.py  # API-specific settings
├── tests/             # Test suites
│   ├── frontend/      # Frontend tests
│   ├── core/          # Core logic tests
│   └── api/           # API endpoint tests
├── docs/              # Documentation
├── requirements/      # Dependencies by component
│   ├── core.txt      # Core requirements
│   ├── frontend.txt  # Frontend-specific requirements
│   └── dev.txt       # Development requirements
└── run.py            # Application entry point
├── data/                 # Shared data
│   ├── configs/         # Configuration files
│   ├── templates/       # Data templates
│   └── exports/         # Generated exports
├── instance/            # Instance configurations
│   ├── frontend.cfg     # Frontend config
│   └── backend.cfg      # Backend config
└── run.py              # Application entry point
```

### **App Directory** (`/app`)
```
app/
├── templates/              # Page templates
│   ├── components/        # Reusable template components
│   │   └── form_components.html
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── create.html        # Create scenario
│   ├── edit.html          # Edit scenario
│   ├── edit_baseline.html # Edit baseline
│   ├── comparison.html    # Scenario comparison
│   ├── cost_analysis.html # Cost analysis
│   ├── state_taxes.html   # State tax management
│   ├── scenario.html      # View scenario
│   └── error.html         # Error page
├── static/                 # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript modules
│   └── img/               # Images
├── utils/                  # Web-specific utilities
├── routes.py              # Route handlers and API endpoints
└── __init__.py            # Flask app initialization
```

### **Core Directory** (`/core`)
```
core/
├── calculators/           # Calculation engines
│   ├── vehicle_cost_calculator.py  # Main calculator
│   ├── car_keep_runner.py         # Scenario runner
│   ├── cost_analyzer.py           # Cost analysis
│   └── run_scenarios.py           # Scenario execution
├── models/                # Data models and schemas
├── utils/                 # Core calculation utilities
├── main.py               # Core functionality entry point
└── __init__.py           # Core module exports
```

### **Data Directory** (`/data`)
```
data/
├── scenarios/             # User scenario files
├── configs/               # Configuration files
│   └── state_tax_configs.json
├── templates/             # Data templates and defaults
└── exports/               # Generated reports
    ├── *.csv             # CSV exports
    └── *.json            # JSON exports
```

### **Scripts Directory** (`/scripts`)
```
scripts/
└── generate_comparison_matrix.py  # Matrix generation
```

### **Instance Directory** (`/instance`)
```
instance/
└── config.py             # Instance-specific configuration
```

## 🎯 **Design Principles and Progress**

### **1. Separation of Concerns**
- **Frontend** ✓
  - User interface and template rendering
  - API client integration
  - Route handling for views
- **Core/API** ✓
  - RESTful endpoints defined
  - Request validation
  - Response formatting
- **Core/Calculators** ✓
  - Business logic preserved
  - Calculation engines isolated
- **Data** ✓
  - Shared storage structure
  - Configuration management
- **Instance** (In Progress)
  - Environment-specific settings
  - Configuration separation

### **2. Modular Architecture**
- **Templates**: Reusable components in `frontend/templates/components/`
- **Static Assets**: Organized by type in `frontend/static/`
- **API Routes**: RESTful endpoints in `core/api/routes/`
- **Calculators**: Business logic in `core/calculators/`
- **Models**: Shared data models in `core/models/`
- **Utils**: Domain-specific utilities in respective directories

### **3. Configuration Management**
- **Frontend Config**: UI-specific settings
- **API Config**: API-specific settings in instance/api_config.py
- **Core Config**: Business logic configuration in data/configs
- **Environment Config**: Environment-specific settings in instance/config.py

### **4. Testing Strategy**
- **Frontend Tests**: Template rendering and UI interaction
- **Core Tests**: Business logic and calculations
- **API Tests**: Endpoint behavior and data validation
- **Integration Tests**: Cross-component functionality

### **5. Development Workflow**
- **Local Development**:
  - Frontend serves templates and static assets
  - Core/API handles data processing and calculations
  - Shared data accessed through API endpoints
- **Testing**:
  - Component-specific test suites
  - Integration tests for critical paths
  - Shared test utilities and fixtures
- **Deployment**:
  - Single deployment for monolithic setup
  - Option for separate deployment in future
  - Environment-specific configurations

## 🔧 **Import Patterns**

### **Template Imports**
```jinja2
{% from "components/form_components.html" import form_section %}
```

### **Python Imports**
```python
# Core functionality
from core.calculators.vehicle_cost_calculator import VehicleCostCalculator
from core.main import StateTaxRegistry

# App functionality
from app.utils.form_helpers import validate_scenario
```

## 📝 **Adding New Features**

### **New Calculation Feature**
1. Add calculator to `core/calculators/`
2. Update core exports in `core/__init__.py`
3. Create API endpoint in `app/routes.py`
4. Add frontend integration in `app/static/js/`

### **New UI Component**
1. Add template to `app/templates/components/`
2. Add related styles to `app/static/css/`
3. Add JavaScript module to `app/static/js/`

### **New Configuration Type**
1. Add schema to `core/models/`
2. Add template to `data/templates/`
3. Add configuration handler to `core/utils/`
4. Create management UI in `app/templates/`

This structure supports both current functionality and future expansion while maintaining clear separation of concerns and modularity. 🚗✨
