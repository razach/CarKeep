"""
Main routes for CarKeep web application.
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from pathlib import Path
import json
import os
import sys

# Add core directory to path for imports
core_path = Path(__file__).parent.parent / 'core'
sys.path.append(str(core_path))

# Import core functionality
from car_keep_runner import run_comparison_from_json
from run_scenarios import list_scenarios, run_scenario

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with scenario list."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        data = list_scenarios(data_folder)
        return render_template('index.html', 
                             baseline=data['baseline'], 
                             scenarios=data['scenarios'])
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
def comparison_matrix():
    """Show comparison matrix of all scenarios."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        from generate_comparison_matrix import generate_comparison_matrix
        generate_comparison_matrix(data_folder)
        
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
        try:
            # Get form data
            scenario_data = request.form.to_dict()
            
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
            scenarios_file = data_folder / 'scenarios.json'
            
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
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error creating scenario: {str(e)}'}), 500
    
    return render_template('create.html')

@main_bp.route('/api/scenarios')
def api_scenarios():
    """API endpoint to get all scenarios."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios.json'
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
        scenarios_file = data_folder / 'scenarios.json'
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        if scenario_name in data.get('examples', {}):
            return jsonify(data['examples'][scenario_name])
        else:
            return jsonify({'error': 'Scenario not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/scenario/<scenario_name>/edit', methods=['GET', 'POST'])
def edit_scenario(scenario_name):
    """Edit an existing scenario."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios.json'
        
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

@main_bp.route('/scenario/<scenario_name>/delete', methods=['POST'])
def delete_scenario(scenario_name):
    """Delete a scenario."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios.json'
        
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
