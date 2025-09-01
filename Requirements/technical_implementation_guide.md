# CarKeep Web App - Technical Implementation Guide

## 🛠️ **Development Environment Setup**

### **Prerequisites**
- Python 3.8+
- pip (Python package manager)
- Git (for version control)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### **Required Python Packages**
```bash
# Core Flask dependencies
Flask==2.3.3
Werkzeug==2.3.7

# Data processing (existing)
pandas==2.3.2
numpy==2.3.2

# Development tools
python-dotenv==1.0.0
Flask-DebugToolbar==0.13.1

# Testing
pytest==7.4.2
pytest-flask==1.2.0
```

### **Installation Commands**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🏗️ **File Structure Implementation**

### **1. Create Directory Structure**
```bash
mkdir -p app/{templates,static/{css,js,img},utils}
mkdir -p core
mkdir -p data/templates
```

### **2. Move Existing Files**
```bash
# Move core functionality
mv main.py core/
mv car_keep_runner.py core/
mv run_scenarios.py core/
mv generate_comparison_matrix.py core/

# Move data files
mv scenarios.json data/
```

### **3. Create Core Package**
```python
# core/__init__.py
"""
Core CarKeep functionality package.
Contains all the calculation logic and data processing.
"""

from .main import VehicleCostCalculator, VehicleConfig, LoanConfig, LeaseConfig, TradeInConfig, FinancingType
from .car_keep_runner import run_comparison_from_json
from .run_scenarios import list_scenarios, run_scenario
from .generate_comparison_matrix import generate_comparison_matrix

__all__ = [
    'VehicleCostCalculator',
    'VehicleConfig', 
    'LoanConfig',
    'LeaseConfig',
    'TradeInConfig',
    'FinancingType',
    'run_comparison_from_json',
    'list_scenarios',
    'run_scenario',
    'generate_comparison_matrix'
]
```

## 🚀 **Flask Application Structure**

### **1. Main Application Entry Point**
```python
# web_app.py
from flask import Flask
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### **2. Flask App Factory**
```python
# app/__init__.py
from flask import Flask
from pathlib import Path

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure app
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATA_FOLDER=Path(__file__).parent.parent / 'data',
        CORE_FOLDER=Path(__file__).parent.parent / 'core'
    )
    
    if test_config is None:
        # Load the instance config, if it exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)
    
    # Ensure the instance folder exists
    try:
        Path(app.instance_path).mkdir(exist_ok=True)
    except OSError:
        pass
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
```

### **3. Route Structure**
```python
# app/routes.py
from flask import Blueprint, render_template, request, jsonify, send_file
from pathlib import Path
import json
import tempfile
import os

# Import core functionality
import sys
sys.path.append(str(Path(__file__).parent.parent / 'core'))
from car_keep_runner import run_comparison_from_json
from run_scenarios import list_scenarios, run_scenario

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with scenario list."""
    scenarios = list_scenarios()
    return render_template('index.html', scenarios=scenarios)

@main_bp.route('/scenario/<scenario_name>')
def view_scenario(scenario_name):
    """View individual scenario results."""
    try:
        results = run_scenario(scenario_name)
        return render_template('scenario.html', 
                             scenario_name=scenario_name, 
                             results=results)
    except Exception as e:
        return render_template('error.html', error=str(e)), 400

@main_bp.route('/comparison')
def comparison_matrix():
    """Show comparison matrix of all scenarios."""
    try:
        from generate_comparison_matrix import generate_comparison_matrix
        generate_comparison_matrix()
        
        # Read the generated CSV files
        csv_files = {}
        for filename in ['monthly_payment_matrix.csv', 'summary_matrix.csv', 'cost_difference_matrix.csv']:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    csv_files[filename] = f.read()
        
        return render_template('comparison.html', csv_files=csv_files)
    except Exception as e:
        return render_template('error.html', error=str(e)), 400

@main_bp.route('/create', methods=['GET', 'POST'])
def create_scenario():
    """Create new scenario form."""
    if request.method == 'POST':
        # Handle form submission
        scenario_data = request.form.to_dict()
        # Process and save scenario
        return jsonify({'success': True, 'message': 'Scenario created'})
    
    return render_template('create.html')

@main_bp.route('/api/scenarios')
def api_scenarios():
    """API endpoint to get all scenarios."""
    try:
        with open('data/scenarios.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/scenario/<scenario_name>')
def api_scenario(scenario_name):
    """API endpoint to get specific scenario."""
    try:
        with open('data/scenarios.json', 'r') as f:
            data = json.load(f)
        
        if scenario_name in data.get('examples', {}):
            return jsonify(data['examples'][scenario_name])
        else:
            return jsonify({'error': 'Scenario not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## 🎨 **Template Structure**

### **1. Base Template**
```html
<!-- app/templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CarKeep{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="{{ url_for('main.index') }}">CarKeep</a>
        </div>
        <ul class="nav-menu">
            <li><a href="{{ url_for('main.index') }}">Scenarios</a></li>
            <li><a href="{{ url_for('main.comparison_matrix') }}">Comparison</a></li>
            <li><a href="{{ url_for('main.create_scenario') }}">Create New</a></li>
        </ul>
    </nav>
    
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

### **2. Homepage Template**
```html
<!-- app/templates/index.html -->
{% extends "base.html" %}

{% block title %}CarKeep - Vehicle Cost Scenarios{% endblock %}

{% block content %}
<div class="scenarios-list">
    <h1>Vehicle Cost Scenarios</h1>
    
    <div class="baseline-info">
        <h2>Baseline: Acura RDX</h2>
        <p>Your current car - the reference point for all comparisons.</p>
    </div>
    
    <div class="scenarios-grid">
        {% for scenario_name, scenario_data in scenarios.items() %}
        <div class="scenario-card">
            <h3>{{ scenario_data.description }}</h3>
            <div class="scenario-meta">
                <span class="type {{ scenario_data.scenario.type }}">
                    {{ scenario_data.scenario.type|title }}
                </span>
                <span class="vehicle">{{ scenario_data.scenario.vehicle.name }}</span>
            </div>
            <div class="scenario-actions">
                <a href="{{ url_for('main.view_scenario', scenario_name=scenario_name) }}" 
                   class="btn btn-primary">View Results</a>
                <button class="btn btn-secondary" onclick="editScenario('{{ scenario_name }}')">
                    Edit
                </button>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="actions">
        <a href="{{ url_for('main.create_scenario') }}" class="btn btn-success">
            Create New Scenario
        </a>
        <a href="{{ url_for('main.comparison_matrix') }}" class="btn btn-info">
            View Comparison Matrix
        </a>
    </div>
</div>
{% endblock %}
```

## 🎯 **Data Processing Utilities**

### **1. Form Helpers**
```python
# app/utils/form_helpers.py
from typing import Dict, Any, List, Tuple
import json
from pathlib import Path

def validate_scenario_form(form_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate scenario creation form data."""
    errors = []
    
    # Required fields
    required_fields = ['name', 'type', 'monthly_payment', 'msrp']
    for field in required_fields:
        if not form_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    # Type validation
    if form_data.get('type') not in ['lease', 'loan']:
        errors.append("Type must be 'lease' or 'loan'")
    
    # Numeric validation
    numeric_fields = ['monthly_payment', 'msrp', 'trade_in_value']
    for field in numeric_fields:
        if form_data.get(field):
            try:
                float(form_data[field])
            except ValueError:
                errors.append(f"{field.replace('_', ' ').title()} must be a number")
    
    return len(errors) == 0, errors

def create_scenario_json(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert form data to scenario JSON structure."""
    scenario = {
        "description": form_data['name'],
        "scenario": {
            "type": form_data['type'],
            "vehicle": {
                "name": form_data['vehicle_name'],
                "msrp": float(form_data['msrp']),
                "current_value": 0,
                "values_3yr": [float(form_data['msrp']), 0, 0, 0]
            },
            "financing": {}
        },
        "trade_in": {
            "trade_in_value": float(form_data.get('trade_in_value', 0)),
            "loan_balance": 0,
            "incentives": float(form_data.get('incentives', 0))
        }
    }
    
    # Add financing-specific fields
    if form_data['type'] == 'lease':
        scenario['scenario']['financing'] = {
            "monthly_payment": float(form_data['monthly_payment']),
            "lease_terms": int(form_data.get('lease_terms', 36)),
            "msrp": float(form_data['msrp']),
            "incentives": {}
        }
    else:  # loan
        scenario['scenario']['financing'] = {
            "monthly_payment": float(form_data['monthly_payment']),
            "loan_term": int(form_data.get('loan_term', 36)),
            "principal_balance": float(form_data['msrp'])
        }
    
    return scenario

def save_scenario_to_json(scenario_name: str, scenario_data: Dict[str, Any], 
                         data_folder: Path) -> bool:
    """Save new scenario to scenarios.json file."""
    try:
        scenarios_file = data_folder / 'scenarios.json'
        
        # Read existing scenarios
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        # Add new scenario
        data['examples'][scenario_name] = scenario_data
        
        # Write back to file
        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving scenario: {e}")
        return False
```

### **2. Data Helpers**
```python
# app/utils/data_helpers.py
from typing import Dict, Any, List
import json
from pathlib import Path

def load_scenarios(data_folder: Path) -> Dict[str, Any]:
    """Load scenarios from JSON file."""
    try:
        scenarios_file = data_folder / 'scenarios.json'
        with open(scenarios_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading scenarios: {e}")
        return {"baseline": {}, "examples": {}}

def get_scenario_names(data_folder: Path) -> List[str]:
    """Get list of all scenario names."""
    data = load_scenarios(data_folder)
    return list(data.get('examples', {}).keys())

def get_scenario_data(scenario_name: str, data_folder: Path) -> Dict[str, Any]:
    """Get data for specific scenario."""
    data = load_scenarios(data_folder)
    return data.get('examples', {}).get(scenario_name, {})

def backup_scenarios_file(data_folder: Path) -> bool:
    """Create backup of scenarios.json before modifications."""
    try:
        scenarios_file = data_folder / 'scenarios.json'
        backup_file = data_folder / f'scenarios_backup_{int(time.time())}.json'
        
        import shutil
        shutil.copy2(scenarios_file, backup_file)
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
```

## 🧪 **Testing Structure**

### **1. Test Configuration**
```python
# tests/conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path
from app import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'DATA_FOLDER': Path(tempfile.mkdtemp()),
        'CORE_FOLDER': Path(__file__).parent.parent / 'core'
    })
    
    yield app
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)
    shutil.rmtree(app.config['DATA_FOLDER'])

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
```

### **2. Basic Tests**
```python
# tests/test_routes.py
def test_index_page(client):
    """Test that the index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Vehicle Cost Scenarios' in response.data

def test_scenario_view(client):
    """Test viewing a specific scenario."""
    response = client.get('/scenario/lucid_air_lease')
    assert response.status_code == 200

def test_api_scenarios(client):
    """Test the scenarios API endpoint."""
    response = client.get('/api/scenarios')
    assert response.status_code == 200
    data = response.get_json()
    assert 'baseline' in data
    assert 'examples' in data
```

## 🚀 **Running the Application**

### **1. Development Mode**
```bash
# Set environment variables
export FLASK_APP=web_app.py
export FLASK_ENV=development

# Run the application
flask run
```

### **2. Production Mode**
```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### **3. Docker Support (Optional)**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web_app:app"]
```

## 📊 **Performance Considerations**

### **1. Caching Strategy**
- Cache scenario data in memory
- Cache calculation results
- Implement request-level caching

### **2. Async Processing**
- Use background tasks for heavy calculations
- Implement progress indicators for long operations
- Queue system for multiple scenario processing

### **3. Data Optimization**
- Lazy loading of scenario data
- Pagination for large scenario lists
- Efficient JSON parsing and validation

---

**Document Version**: 1.0  
**Last Updated**: September 2024  
**Status**: Technical Planning  
**Next Review**: After Phase 1 implementation
