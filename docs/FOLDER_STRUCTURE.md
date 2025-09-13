# CarKeep Folder Structure

## 🗂️ **Organized for Maintainability**

### **Root Directory**
```
CarKeep/
├── app/                    # Web application
├── core/                   # Core business logic
├── data/                   # Data storage
├── scripts/                # Utility scripts
└── README.md
```

### **App Directory** (`/app`)
```
app/
├── templates/              # Page templates
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
├── components/             # Reusable template components
│   └── form_components.html # Shared form macros
├── static/                 # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript
│   └── img/               # Images
├── routes.py               # All route handlers
├── utils/                  # Web-specific utilities
└── __init__.py            # Flask app initialization
```

### **Core Directory** (`/core`)
```
core/
├── calculators/            # Calculation engines
│   ├── vehicle_cost_calculator.py  # Main calculator
│   ├── car_keep_runner.py          # Scenario runner
│   └── run_scenarios.py            # Scenario execution
├── models/                 # Data models (future)
├── utils/                  # Core utilities (future)
├── main.py                 # Main entry point
└── __init__.py            # Core module exports
```

### **Data Directory** (`/data`)
```
data/
├── scenarios/              # User scenario files
├── configs/                # Configuration files
│   └── state_tax_configs.json
└── exports/                # Generated reports
    ├── *.csv               # CSV exports
    └── *.json              # JSON exports
```

### **Scripts Directory** (`/scripts`)
```
scripts/
└── generate_comparison_matrix.py  # Matrix generation
```

## 🎯 **Benefits of This Structure**

### **1. Clear Separation of Concerns**
- **App**: Web interface and user interaction
- **Core**: Business logic and calculations
- **Data**: Storage and configuration
- **Scripts**: Utility and automation

### **2. Easy Maintenance**
- **Components**: Reusable template parts
- **Calculators**: Focused calculation logic
- **Routes**: Centralized web endpoints

### **3. Scalability**
- Easy to add new calculation engines
- Simple to extend with new components
- Clear place for new features

### **4. Developer Experience**
- Intuitive file locations
- Easy to find specific functionality
- Clear import paths

## 🔧 **Import Patterns**

### **From Templates**
```jinja2
{% from "components/form_components.html" import form_section %}
```

### **From Python**
```python
from core.calculators.vehicle_cost_calculator import VehicleCostCalculator
from app.components import form_components
```

## 📝 **Adding New Features**

### **New Calculation Engine**
1. Add to `core/calculators/`
2. Import in `core/main.py`
3. Export in `core/__init__.py`

### **New Template Component**
1. Add to `app/components/`
2. Import in templates as needed

### **New Route**
1. Add to `app/routes.py`
2. Keep related routes together

This structure makes CarKeep easy to understand, maintain, and extend! 🚗✨
