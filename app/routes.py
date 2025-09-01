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
        # Handle form submission
        scenario_data = request.form.to_dict()
        # Process and save scenario
        return jsonify({'success': True, 'message': 'Scenario created'})
    
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
