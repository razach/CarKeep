"""
API routes for CarKeep core functionality.
Provides RESTful endpoints for accessing core features.
"""

from flask import jsonify, request, current_app
from pathlib import Path
import json
import os

from ..utils.decorators import require_auth, validate_request
from core.calculators.car_keep_runner import run_comparison_from_json
from core.calculators.run_scenarios import list_scenarios, run_scenario
from core.main import StateTaxRegistry, StateTaxConfig

from . import api_bp  # Import the blueprint from __init__.py

@api_bp.route('/scenarios', methods=['GET'])
def get_scenarios():
    """Get all scenarios."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        current_app.logger.debug(f"Looking for scenarios in: {data_folder}")
        data = list_scenarios(data_folder)
        current_app.logger.debug(f"Got data: {data}")
        response = jsonify(data)
        # Add CORS headers explicitly for Safari
        # Set CORS origin based on request origin
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:5001', 'http://127.0.0.1:5001']:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/scenarios', methods=['POST'])
@validate_request({'required': ['scenario_name', 'description', 'vehicle_name', 'msrp', 'financing_type', 'monthly_payment']})
def create_scenario():
    """Create a new scenario."""
    try:
        scenario_data = request.json
        data_folder = current_app.config['DATA_FOLDER']
        
        # Save scenario
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        scenarios = {}
        
        if scenarios_file.exists():
            with open(scenarios_file, 'r') as f:
                scenarios = json.load(f)
        
        scenarios[scenario_data['scenario_name']] = scenario_data
        
        os.makedirs(scenarios_file.parent, exist_ok=True)
        with open(scenarios_file, 'w') as f:
            json.dump(scenarios, f, indent=4)
        
        return jsonify({
            'success': True,
            'message': 'Scenario created successfully',
            'scenario': scenario_data
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/scenario/<scenario_name>', methods=['GET'])
def get_scenario(scenario_name):
    """Get a specific scenario."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        results = run_scenario(scenario_name, data_folder=data_folder)
        return jsonify(results)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@api_bp.route('/scenario/<scenario_name>', methods=['PUT'])
@validate_request({'required': ['description', 'vehicle_name', 'msrp', 'financing_type', 'monthly_payment']})
def update_scenario(scenario_name):
    """Update an existing scenario."""
    try:
        scenario_data = request.json
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        if not scenarios_file.exists():
            return jsonify({'success': False, 'error': 'Scenario not found'}), 404
            
        with open(scenarios_file, 'r') as f:
            scenarios = json.load(f)
            
        if scenario_name not in scenarios:
            return jsonify({'success': False, 'error': 'Scenario not found'}), 404
            
        scenarios[scenario_name].update(scenario_data)
        
        with open(scenarios_file, 'w') as f:
            json.dump(scenarios, f, indent=4)
            
        return jsonify({
            'success': True,
            'message': 'Scenario updated successfully',
            'scenario': scenarios[scenario_name]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/state-taxes', methods=['GET'])
def get_state_taxes():
    """Get all state tax configurations."""
    try:
        tax_registry = StateTaxRegistry()
        states = tax_registry.list_states()
        return jsonify(states)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/state-taxes', methods=['POST'])
@validate_request({'required': ['state_code', 'property_tax_rate', 'pptra_relief', 'relief_cap', 'state_name']})
def create_state_tax():
    """Create a new state tax configuration."""
    try:
        data = request.json
        tax_config = StateTaxConfig(
            property_tax_rate=float(data['property_tax_rate']) / 100,
            pptra_relief=float(data['pptra_relief']) / 100,
            relief_cap=float(data['relief_cap']),
            state_name=data['state_name']
        )
        
        tax_registry = StateTaxRegistry()
        tax_registry.add_state(data['state_code'], tax_config)
        
        return jsonify({
            'success': True,
            'message': 'State tax configuration created successfully',
            'config': data
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/comparison-results', methods=['GET'])
def get_comparison_results():
    """Get comparison results for all scenarios."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        # Load JSON data from file
        with open(scenarios_file, 'r') as f:
            json_data = json.load(f)
            
        # Run comparison with loaded JSON data
        results = run_comparison_from_json(json_data=json_data)
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error getting comparison results: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/cost-analysis', methods=['GET'])
def get_cost_analysis():
    """Get detailed cost analysis data."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        # Load JSON data from file
        with open(scenarios_file, 'r') as f:
            json_data = json.load(f)
            
        # Run comparison with loaded JSON data
        results = run_comparison_from_json(json_data=json_data)
        
        # Return the results in a format suitable for the cost analysis view
        return jsonify({
            'baseline': results.get('baseline', {}),
            'scenarios': results.get('scenarios', {}),
            'summaries': results.get('summaries', {}),
            'comparison_metrics': results.get('comparison_metrics', {})
        })
    except Exception as e:
        current_app.logger.error(f"Error getting cost analysis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500