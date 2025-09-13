# CarKeep Folder Structure

## 🗂️ **Current Project Structure**

### **Root Directory**
```
CarKeep/
├── app/                    # Web application
├── core/                   # Core business logic
├── data/                   # Data storage and templates
├── docs/                   # Project documentation
├── instance/              # Flask instance configuration
├── scripts/               # Utility scripts
├── requirements.txt       # Python dependencies
└── run.py                 # Application entry point
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

## 🎯 **Design Principles**

### **1. Separation of Concerns**
- **App**: Web interface and API endpoints
- **Core**: Business logic and calculations
- **Data**: Storage, configuration, and templates
- **Instance**: Environment-specific settings

### **2. Modular Architecture**
- **Templates**: Reusable components in `templates/components/`
- **Static Assets**: Organized by type (CSS, JS, images)
- **Calculators**: Independent calculation modules
- **Utils**: Shared utilities separated by domain (web vs core)

### **3. Configuration Management**
- **App Config**: Basic Flask configuration
- **Instance Config**: Environment-specific settings
- **Data Config**: Business logic configuration (state taxes, etc.)

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
