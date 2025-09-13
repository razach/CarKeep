"""
Main routes for CarKeep web application.
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app, make_response
from pathlib import Path
import json
import os
import sys
import time

# Add core directory to path for imports
core_path = Path(__file__).parent.parent / 'core'
sys.path.append(str(core_path))

# Import core functionality from new organized structure
from core.calculators.car_keep_runner import run_comparison_from_json
from core.calculators.run_scenarios import list_scenarios, run_scenario
from core.main import StateTaxRegistry, StateTaxConfig # Import for state tax management

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with scenario list."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        data = list_scenarios(data_folder)
        
        response = make_response(render_template('index.html', 
                             baseline=data['baseline'], 
                             scenarios=data['scenarios'],
                             timestamp=int(time.time())))
        
        # Add cache control headers to prevent browser caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@main_bp.route('/scenario/<scenario_name>')
def view_scenario(scenario_name):
    """View individual scenario results."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        results = run_scenario(scenario_name, data_folder=data_folder)
        return render_template('scenario.html', 
                             scenario_name=scenario_name, 
                             results=results)
    except Exception as e:
        return render_template('error.html', error=str(e)), 400

@main_bp.route('/comparison')
def comparison():
    """Simple scenario comparison view."""
    try:
        # Load scenarios data using existing function
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_data = list_scenarios(data_folder)
        
        if not scenarios_data:
            return render_template('comparison.html', scenarios=None, baseline=None)
        
        # Get baseline data
        baseline = scenarios_data.get('baseline', {})
        
        # Get alternative scenarios (exclude baseline)
        scenarios = []
        for scenario_name, scenario_data in scenarios_data.get('scenarios', {}).items():
            scenarios.append(scenario_data)
        
        return render_template('comparison.html', scenarios=scenarios, baseline=baseline)
        
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@main_bp.route('/create')
def create_scenario():
    """Create new scenario form."""
    return render_template('create.html')

@main_bp.route('/api/scenarios', methods=['POST'])
def api_create_scenario():
    """API endpoint to create a new scenario."""
    try:
        # Get form data
        scenario_data = request.json # Use request.json for API
        
        # Validate required fields
        required_fields = ['scenario_name', 'description', 'vehicle_name', 'msrp', 'financing_type', 'monthly_payment']
        for field in required_fields:
            if not scenario_data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Validate scenario name format
        import re
        if not re.match(r'^[a-z0-9_]+$', scenario_data['scenario_name']):
            return jsonify({'success': False, 'message': 'Scenario name must contain only lowercase letters, numbers, and underscores'}), 400
        
        # Load existing scenarios
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        # Check if scenario name already exists
        if scenario_data['scenario_name'] in data.get('examples', {}):
            return jsonify({'success': False, 'message': 'Scenario name already exists'}), 400
        
        # Create new scenario structure
        new_scenario = {
            'description': scenario_data['description'],
            'scenario': {
                'type': scenario_data['financing_type'],
                'vehicle': {
                    'name': scenario_data['vehicle_name'],
                    'msrp': float(scenario_data['msrp']),
                    'current_value': float(scenario_data.get('current_value', 0)),
                    'values_3yr': [float(scenario_data['msrp']), 0, 0, 0]  # Simplified for now
                },
                'financing': {}
            },
            'trade_in': {
                'trade_in_value': float(scenario_data.get('trade_in_value', 0)),
                'loan_balance': 0,
                'incentives': float(scenario_data.get('incentives', 0))
            },
            'cost_config': {
                'monthly_insurance': float(scenario_data.get('monthly_insurance', 100)),
                'monthly_maintenance': float(scenario_data.get('monthly_maintenance', 50)),
                'monthly_fuel': float(scenario_data.get('monthly_fuel', 150)),
                'investment_return_rate': float(scenario_data.get('investment_return_rate', 6)) / 100
            }
        }
        
        # Add state override if specified
        if scenario_data.get('state'):
            new_scenario['state'] = scenario_data['state']
        
        # Add financing-specific details
        if scenario_data['financing_type'] == 'lease':
            new_scenario['scenario']['financing'] = {
                'monthly_payment': float(scenario_data['monthly_payment']),
                'lease_terms': int(scenario_data.get('lease_terms', 36)),
                'msrp': float(scenario_data['msrp']),
                'incentives': {}
            }
        else:  # loan
            new_scenario['scenario']['financing'] = {
                'monthly_payment': float(scenario_data['monthly_payment']),
                'loan_term': int(scenario_data.get('loan_term', 60)),
                'principal_balance': float(scenario_data['msrp']),
                'interest_rate': float(scenario_data.get('interest_rate', 5.5)) / 100
            }
        
        # Add to scenarios
        if 'examples' not in data:
            data['examples'] = {}
        
        data['examples'][scenario_data['scenario_name']] = new_scenario
        
        # Save back to file
        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({
            'success': True, 
            'message': f'Scenario "{scenario_data["scenario_name"]}" created successfully!',
            'scenario_name': scenario_data['scenario_name']
        }), 201 # 201 Created
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating scenario: {str(e)}'}), 500

@main_bp.route('/api/scenarios')
def api_scenarios():
    """API endpoint to get all scenarios."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/scenario/<scenario_name>')
def api_scenario(scenario_name):
    """API endpoint to get specific scenario."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        if scenario_name in data.get('examples', {}):
            return jsonify(data['examples'][scenario_name])
        else:
            return jsonify({'error': 'Scenario not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/scenario/<scenario_name>', methods=['PUT'])
def api_update_scenario(scenario_name):
    """API endpoint to update an existing scenario."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        if scenario_name not in data.get('examples', {}):
            return jsonify({'success': False, 'message': f'Scenario "{scenario_name}" not found'}), 404
        
        scenario_data = data['examples'][scenario_name]
        form_data = request.json # Use request.json for API
        
        # Validate required fields
        required_fields = ['description', 'vehicle_name', 'msrp', 'financing_type', 'monthly_payment']
        for field in required_fields:
            if not form_data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Update scenario data
        scenario_data['description'] = form_data['description']
        scenario_data['scenario']['vehicle']['name'] = form_data['vehicle_name']
        scenario_data['scenario']['vehicle']['msrp'] = float(form_data['msrp'])
        scenario_data['scenario']['vehicle']['current_value'] = float(form_data.get('current_value', 0))
        scenario_data['scenario']['type'] = form_data['financing_type']
        
        # Update financing details
        if form_data['financing_type'] == 'lease':
            scenario_data['scenario']['financing'] = {
                'monthly_payment': float(form_data['monthly_payment']),
                'lease_terms': int(form_data.get('lease_terms', 36)),
                'msrp': float(form_data['msrp']),
                'incentives': {}
            }
        else:  # loan
            scenario_data['scenario']['financing'] = {
                'monthly_payment': float(form_data['monthly_payment']),
                'loan_term': int(form_data.get('loan_term', 60)),
                'principal_balance': float(form_data['msrp']),
                'interest_rate': float(form_data.get('interest_rate', 5.5)) / 100
            }
        
        # Update trade-in details
        scenario_data['trade_in']['trade_in_value'] = float(form_data.get('trade_in_value', 0))
        scenario_data['trade_in']['incentives'] = float(form_data.get('incentives', 0))
        
        # Update cost configuration
        if 'cost_config' not in scenario_data:
            scenario_data['cost_config'] = {}
        
        scenario_data['cost_config'].update({
            'monthly_insurance': float(form_data.get('monthly_insurance', 100)),
            'monthly_maintenance': float(form_data.get('monthly_maintenance', 50)),
            'monthly_fuel': float(form_data.get('monthly_fuel', 150)),
            'investment_return_rate': float(form_data.get('investment_return_rate', 6)) / 100
        })
        
        # Update state if specified
        if form_data.get('state'):
            scenario_data['state'] = form_data['state']
        elif 'state' in scenario_data:
            del scenario_data['state']
        
        # Save updated data
        data['examples'][scenario_name] = scenario_data
        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Scenario "{scenario_name}" updated successfully!',
            'scenario_name': scenario_name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating scenario: {str(e)}'}), 500

@main_bp.route('/scenario/<scenario_name>/delete', methods=['POST'])
def delete_scenario(scenario_name):
    """Delete a scenario."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        if scenario_name not in data.get('examples', {}):
            return jsonify({'success': False, 'message': f'Scenario "{scenario_name}" not found'}), 404
        
        # Remove the scenario
        del data['examples'][scenario_name]
        
        # Save updated data
        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Scenario "{scenario_name}" deleted successfully!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting scenario: {str(e)}'}), 500

@main_bp.route('/cost-analysis')
def cost_analysis():
    """Simple cost analysis view."""
    try:
        # Load scenarios data using existing function
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_data = list_scenarios(data_folder)
        
        if not scenarios_data:
            return render_template('cost_analysis.html', analysis=None)
        
        # Use core cost analyzer to prepare all data
        from core.calculators.cost_analyzer import analyze_scenarios_from_data
        analysis = analyze_scenarios_from_data(scenarios_data)
        
        return render_template('cost_analysis.html', analysis=analysis)
        
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@main_bp.route('/edit-baseline', methods=['GET', 'POST'])
def edit_baseline():
    """Edit baseline view route."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        if 'baseline' not in data:
            return render_template('error.html', error='Baseline not found'), 404
        
        baseline_data = data['baseline']
        
        if request.method == 'POST':
            try:
                # Get form data
                form_data = request.form.to_dict()
                
                # Validate required fields
                required_fields = ['vehicle_name', 'current_value', 'principal_balance', 'monthly_payment']
                for field in required_fields:
                    if not form_data.get(field):
                        return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
                
                # Update baseline data
                baseline_data['description'] = form_data.get('description', 'Your current vehicle (baseline)')
                baseline_data['vehicle']['name'] = form_data['vehicle_name']
                baseline_data['vehicle']['current_value'] = float(form_data['current_value'])
                baseline_data['vehicle']['msrp'] = float(form_data.get('msrp', form_data['current_value']))
                baseline_data['current_loan']['principal_balance'] = float(form_data['principal_balance'])
                baseline_data['current_loan']['monthly_payment'] = float(form_data['monthly_payment'])
                baseline_data['current_loan']['interest_rate'] = float(form_data.get('interest_rate', 5.5)) / 100
                baseline_data['current_loan']['extra_payment'] = float(form_data.get('extra_payment', 0))
                
                # Update state if specified
                if form_data.get('state'):
                    baseline_data['state'] = form_data['state']
                
                # Update cost configuration
                if 'cost_config' not in baseline_data:
                    baseline_data['cost_config'] = {}
                
                baseline_data['cost_config'].update({
                    'monthly_insurance': float(form_data.get('monthly_insurance', 100)),
                    'monthly_maintenance': float(form_data.get('monthly_maintenance', 50)),
                    'monthly_fuel': float(form_data.get('monthly_fuel', 150)),
                    'investment_return_rate': float(form_data.get('investment_return_rate', 6)) / 100
                })
                
                # Save updated data
                data['baseline'] = baseline_data
                with open(scenarios_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'message': 'Baseline updated successfully!'
                })
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error updating baseline: {str(e)}'}), 500
        
        return render_template('edit_baseline.html', baseline_data=baseline_data)
        
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@main_bp.route('/api/baseline', methods=['PUT'])
def api_update_baseline():
    """API endpoint to update the baseline scenario."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        if 'baseline' not in data:
            return jsonify({'success': False, 'message': 'Baseline not found'}), 404
        
        baseline_data = data['baseline']
        form_data = request.json # Use request.json for API
        
        # Validate required fields
        required_fields = ['vehicle_name', 'current_value', 'principal_balance', 'monthly_payment']
        for field in required_fields:
            if not form_data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Update baseline data
        baseline_data['description'] = form_data.get('description', 'Your current vehicle (baseline)')
        baseline_data['vehicle']['name'] = form_data['vehicle_name']
        baseline_data['vehicle']['current_value'] = float(form_data['current_value'])
        baseline_data['vehicle']['msrp'] = float(form_data.get('msrp', form_data['current_value']))
        baseline_data['current_loan']['principal_balance'] = float(form_data['principal_balance'])
        baseline_data['current_loan']['monthly_payment'] = float(form_data['monthly_payment'])
        baseline_data['current_loan']['interest_rate'] = float(form_data.get('interest_rate', 5.5)) / 100
        baseline_data['current_loan']['extra_payment'] = float(form_data.get('extra_payment', 0))
        
        # Update state if specified
        if form_data.get('state'):
            baseline_data['state'] = form_data['state']
        
        # Update cost configuration
        if 'cost_config' not in baseline_data:
            baseline_data['cost_config'] = {}
        
        baseline_data['cost_config'].update({
            'monthly_insurance': float(form_data.get('monthly_insurance', 100)),
            'monthly_maintenance': float(form_data.get('monthly_maintenance', 50)),
            'monthly_fuel': float(form_data.get('monthly_fuel', 150)),
            'investment_return_rate': float(form_data.get('investment_return_rate', 6)) / 100
        })
        
        # Save updated data
        data['baseline'] = baseline_data
        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Baseline updated successfully!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating baseline: {str(e)}'}), 500

@main_bp.route('/scenario/<scenario_name>/edit', methods=['GET', 'POST'])
def edit_scenario(scenario_name):
    """Edit an existing scenario."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        if scenario_name not in data.get('examples', {}):
            return render_template('error.html', error=f'Scenario "{scenario_name}" not found'), 404
        
        scenario_data = data['examples'][scenario_name]

        if request.method == 'POST':
            try:
                # Get form data
                form_data = request.form.to_dict()
                
                # Validate required fields
                required_fields = ['description', 'vehicle_name', 'msrp', 'financing_type', 'monthly_payment']
                for field in required_fields:
                    if not form_data.get(field):
                        return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
                
                # Update scenario data
                scenario_data['description'] = form_data['description']
                scenario_data['scenario']['vehicle']['name'] = form_data['vehicle_name']
                scenario_data['scenario']['vehicle']['msrp'] = float(form_data['msrp'])
                scenario_data['scenario']['vehicle']['current_value'] = float(form_data.get('current_value', 0))
                scenario_data['scenario']['type'] = form_data['financing_type']
                
                # Update financing details
                if form_data['financing_type'] == 'lease':
                    scenario_data['scenario']['financing'] = {
                        'monthly_payment': float(form_data['monthly_payment']),
                        'lease_terms': int(form_data.get('lease_terms', 36)),
                        'msrp': float(form_data['msrp']),
                        'incentives': {}
                    }
                else:  # loan
                    scenario_data['scenario']['financing'] = {
                        'monthly_payment': float(form_data['monthly_payment']),
                        'loan_term': int(form_data.get('loan_term', 60)),
                        'principal_balance': float(form_data['msrp']),
                        'interest_rate': float(form_data.get('interest_rate', 5.5)) / 100
                    }
                
                # Update trade-in details
                scenario_data['trade_in']['trade_in_value'] = float(form_data.get('trade_in_value', 0))
                scenario_data['trade_in']['incentives'] = float(form_data.get('incentives', 0))
                
                # Update cost configuration
                if 'cost_config' not in scenario_data:
                    scenario_data['cost_config'] = {}
                
                scenario_data['cost_config'].update({
                    'monthly_insurance': float(form_data.get('monthly_insurance', 100)),
                    'monthly_maintenance': float(form_data.get('monthly_maintenance', 50)),
                    'monthly_fuel': float(form_data.get('monthly_fuel', 150)),
                    'investment_return_rate': float(form_data.get('investment_return_rate', 6)) / 100
                })
                
                # Update state if specified
                if form_data.get('state'):
                    scenario_data['state'] = form_data['state']
                elif 'state' in scenario_data:
                    del scenario_data['state']
                
                # Save updated data
                data['examples'][scenario_name] = scenario_data
                with open(scenarios_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'message': f'Scenario "{scenario_name}" updated successfully!',
                    'scenario_name': scenario_name
                })
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error updating scenario: {str(e)}'}), 500
        
        return render_template('edit.html', scenario_name=scenario_name, scenario_data=scenario_data)
        
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@main_bp.route('/state-taxes')
def state_taxes():
    """Manage state tax configurations."""
    try:
        # Path to store state tax configurations
        TAX_CONFIG_FILE = current_app.config['DATA_FOLDER'] / 'configs' / 'state_tax_configs.json'
        
        def load_tax_configs():
            """Load state tax configurations from file."""
            if os.path.exists(TAX_CONFIG_FILE):
                try:
                    with open(TAX_CONFIG_FILE, 'r') as f:
                        configs = json.load(f)
                        # Convert back to StateTaxConfig objects
                        registry = StateTaxRegistry()
                        for state_code, config_data in configs.items():
                            config = StateTaxConfig(
                                property_tax_rate=config_data['property_tax_rate'],
                                pptra_relief=config_data['pptra_relief'],
                                relief_cap=config_data['relief_cap'],
                                state_name=config_data['state_name']
                            )
                            registry.states[state_code] = config
                        return registry
                except Exception as e:
                    print(f"Error loading tax configs: {e}")
            
            # Return default registry if file doesn't exist or error
            return StateTaxRegistry()
        
        tax_registry = load_tax_configs()
        states = tax_registry.list_states()
        
        return render_template('state_taxes.html', states=states)
        
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@main_bp.route('/api/state-taxes', methods=['GET'])
def api_get_state_taxes():
    """API endpoint to get all state tax configurations."""
    try:
        TAX_CONFIG_FILE = current_app.config['DATA_FOLDER'] / 'configs' / 'state_tax_configs.json'
        
        def load_tax_configs_json():
            if os.path.exists(TAX_CONFIG_FILE):
                with open(TAX_CONFIG_FILE, 'r') as f:
                    return json.load(f)
            return {}

        configs = load_tax_configs_json()
        return jsonify(configs)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching state taxes: {str(e)}'}), 500

@main_bp.route('/api/state-taxes', methods=['POST'])
def api_add_state_tax():
    """API endpoint to add a new state tax configuration."""
    try:
        form_data = request.json
        TAX_CONFIG_FILE = current_app.config['DATA_FOLDER'] / 'configs' / 'state_tax_configs.json'

        def load_tax_configs_registry():
            if os.path.exists(TAX_CONFIG_FILE):
                try:
                    with open(TAX_CONFIG_FILE, 'r') as f:
                        configs = json.load(f)
                        registry = StateTaxRegistry()
                        for state_code, config_data in configs.items():
                            config = StateTaxConfig(
                                property_tax_rate=config_data['property_tax_rate'],
                                pptra_relief=config_data['pptra_relief'],
                                relief_cap=config_data['relief_cap'],
                                state_name=config_data['state_name']
                            )
                            registry.states[state_code] = config
                        return registry
                except Exception as e:
                    print(f"Error loading tax configs: {e}")
            return StateTaxRegistry()

        def save_tax_configs_registry(registry):
            os.makedirs(TAX_CONFIG_FILE.parent, exist_ok=True)
            configs = {}
            for state_code, config in registry.states.items():
                configs[state_code] = {
                    'property_tax_rate': config.property_tax_rate,
                    'pptra_relief': config.pptra_relief,
                    'relief_cap': config.relief_cap,
                    'state_name': config.state_name
                }
            with open(TAX_CONFIG_FILE, 'w') as f:
                json.dump(configs, f, indent=2)

        tax_registry = load_tax_configs_registry()
        
        new_config = StateTaxConfig(
            property_tax_rate=float(form_data['property_tax_rate']) / 100,
            pptra_relief=float(form_data['pptra_relief']) / 100,
            relief_cap=float(form_data['relief_cap']),
            state_name=form_data['state_name']
        )
        tax_registry.add_state(form_data['state_code'], new_config)
        save_tax_configs_registry(tax_registry)
        
        return jsonify({
            'success': True,
            'message': f'State {form_data["state_code"]} added successfully!'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding state tax: {str(e)}'}), 500

@main_bp.route('/api/state-taxes/<state_code>', methods=['PUT'])
def api_update_state_tax(state_code):
    """API endpoint to update an existing state tax configuration."""
    try:
        form_data = request.json
        TAX_CONFIG_FILE = current_app.config['DATA_FOLDER'] / 'configs' / 'state_tax_configs.json'

        def load_tax_configs_registry():
            if os.path.exists(TAX_CONFIG_FILE):
                try:
                    with open(TAX_CONFIG_FILE, 'r') as f:
                        configs = json.load(f)
                        registry = StateTaxRegistry()
                        for sc, config_data in configs.items():
                            config = StateTaxConfig(
                                property_tax_rate=config_data['property_tax_rate'],
                                pptra_relief=config_data['pptra_relief'],
                                relief_cap=config_data['relief_cap'],
                                state_name=config_data['state_name']
                            )
                            registry.states[sc] = config
                        return registry
                except Exception as e:
                    print(f"Error loading tax configs: {e}")
            return StateTaxRegistry()

        def save_tax_configs_registry(registry):
            os.makedirs(TAX_CONFIG_FILE.parent, exist_ok=True)
            configs = {}
            for sc, config in registry.states.items():
                configs[sc] = {
                    'property_tax_rate': config.property_tax_rate,
                    'pptra_relief': config.pptra_relief,
                    'relief_cap': config.relief_cap,
                    'state_name': config.state_name
                }
            with open(TAX_CONFIG_FILE, 'w') as f:
                json.dump(configs, f, indent=2)

        tax_registry = load_tax_configs_registry()
        
        updated_config = StateTaxConfig(
            property_tax_rate=float(form_data['property_tax_rate']) / 100,
            pptra_relief=float(form_data['pptra_relief']) / 100,
            relief_cap=float(form_data['relief_cap']),
            state_name=form_data['state_name']
        )
        tax_registry.add_state(state_code, updated_config) # add_state also updates if exists
        save_tax_configs_registry(tax_registry)
        
        return jsonify({
            'success': True,
            'message': f'State {state_code} updated successfully!'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating state tax: {str(e)}'}), 500

@main_bp.route('/api/state-taxes/<state_code>', methods=['DELETE'])
def api_delete_state_tax(state_code):
    """API endpoint to delete a state tax configuration."""
    try:
        TAX_CONFIG_FILE = current_app.config['DATA_FOLDER'] / 'configs' / 'state_tax_configs.json'

        def load_tax_configs_registry():
            if os.path.exists(TAX_CONFIG_FILE):
                try:
                    with open(TAX_CONFIG_FILE, 'r') as f:
                        configs = json.load(f)
                        registry = StateTaxRegistry()
                        for sc, config_data in configs.items():
                            config = StateTaxConfig(
                                property_tax_rate=config_data['property_tax_rate'],
                                pptra_relief=config_data['pptra_relief'],
                                relief_cap=config_data['relief_cap'],
                                state_name=config_data['state_name']
                            )
                            registry.states[sc] = config
                        return registry
                except Exception as e:
                    print(f"Error loading tax configs: {e}")
            return StateTaxRegistry()

        def save_tax_configs_registry(registry):
            os.makedirs(TAX_CONFIG_FILE.parent, exist_ok=True)
            configs = {}
            for sc, config in registry.states.items():
                configs[sc] = {
                    'property_tax_rate': config.property_tax_rate,
                    'pptra_relief': config.pptra_relief,
                    'relief_cap': config.relief_cap,
                    'state_name': config.state_name
                }
            with open(TAX_CONFIG_FILE, 'w') as f:
                json.dump(configs, f, indent=2)

        tax_registry = load_tax_configs_registry()
        
        if state_code in ['VA', 'TX', 'CA']:
            return jsonify({
                'success': False,
                'message': 'Cannot delete default states (VA, TX, CA)'
            }), 400
        
        if state_code in tax_registry.states:
            del tax_registry.states[state_code]
            save_tax_configs_registry(tax_registry)
        
        return jsonify({
            'success': True,
            'message': f'State {state_code} removed successfully!'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting state tax: {str(e)}'}), 500

@main_bp.route('/api/comparison-results', methods=['GET'])
def api_comparison_results():
    """API endpoint to get comparison results."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_data = list_scenarios(data_folder)
        
        if not scenarios_data:
            return jsonify({'success': False, 'message': 'No scenarios data found'}), 404
        
        # Use core cost analyzer to prepare all data
        from core.calculators.cost_analyzer import analyze_scenarios_from_data
        analysis = analyze_scenarios_from_data(scenarios_data)
        
        return jsonify({'success': True, 'analysis': analysis})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching comparison results: {str(e)}'}), 500

@main_bp.route('/api/cost-analysis-results', methods=['GET'])
def api_cost_analysis_results():
    """API endpoint to get cost analysis results."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_data = list_scenarios(data_folder)
        
        if not scenarios_data:
            return jsonify({'success': False, 'message': 'No scenarios data found'}), 404
        
        # Use core cost analyzer to prepare all data
        from core.calculators.cost_analyzer import analyze_scenarios_from_data
        analysis = analyze_scenarios_from_data(scenarios_data)
        
        return jsonify({'success': True, 'analysis': analysis})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching cost analysis results: {str(e)}'}), 500