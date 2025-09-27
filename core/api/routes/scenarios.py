"""
API routes for CarKeep core functionality.
Provides RESTful endpoints for accessing core features.
"""

from flask import jsonify, request, current_app
from pathlib import Path
import json
import os

from ..utils.decorators import require_auth, validate_request
from ..security import rate_limit, check_api_key
from core.calculators.car_keep_runner import run_comparison_from_json
from core.calculators.run_scenarios import list_scenarios, run_scenario
from core.main import StateTaxRegistry, StateTaxConfig

from . import api_bp  # Import the blueprint from __init__.py

@api_bp.route('/scenarios', methods=['GET'])
@rate_limit
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

        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        data = {}
        if scenarios_file.exists():
            with open(scenarios_file, 'r') as f:
                data = json.load(f)

        examples = data.get('examples', {})
        name = scenario_data['scenario_name']
        if name in examples:
            return jsonify({'success': False, 'error': 'Scenario already exists'}), 409

        # Remove external name field from stored payload if present
        stored = {k: v for k, v in scenario_data.items() if k != 'scenario_name'}
        examples[name] = stored
        data['examples'] = examples

        os.makedirs(scenarios_file.parent, exist_ok=True)
        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=4)

        return jsonify({
            'success': True,
            'message': 'Scenario created successfully',
            'scenario_name': name,
            'scenario': stored
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/scenarios/<scenario_name>', methods=['DELETE'])
def delete_scenario(scenario_name):
    """Delete an existing scenario."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'

        if not scenarios_file.exists():
            return jsonify({'success': False, 'error': 'Scenario not found'}), 404

        with open(scenarios_file, 'r') as f:
            data = json.load(f)

        examples = data.get('examples', {})
        if scenario_name not in examples:
            return jsonify({'success': False, 'error': 'Scenario not found'}), 404

        # Remove the scenario
        del examples[scenario_name]
        data['examples'] = examples

        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=4)

        return jsonify({'success': True, 'message': 'Scenario deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/scenarios/<scenario_name>/duplicate', methods=['POST'])
def duplicate_scenario(scenario_name):
    """Duplicate an existing scenario under a new name ("_copy" with index)."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'

        if not scenarios_file.exists():
            return jsonify({'success': False, 'error': 'Scenario not found'}), 404

        with open(scenarios_file, 'r') as f:
            data = json.load(f)

        examples = data.get('examples', {})
        if scenario_name not in examples:
            return jsonify({'success': False, 'error': 'Scenario not found'}), 404

        original = examples[scenario_name]

        # Generate a new unique name
        base = f"{scenario_name}_copy"
        new_name = base
        i = 1
        while new_name in examples:
            new_name = f"{base}{i}"
            i += 1

        # Clone the scenario
        import copy as _copy
        cloned = _copy.deepcopy(original)
        # Optionally tweak description to indicate copy
        desc = cloned.get('description') or scenario_name
        cloned['description'] = f"{desc} (Copy)"

        examples[new_name] = cloned
        data['examples'] = examples

        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=4)

        return jsonify({'success': True, 'message': 'Scenario duplicated', 'scenario_name': new_name, 'scenario': cloned}), 201
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
            data = json.load(f)

        examples = data.get('examples', {})
        if scenario_name not in examples:
            return jsonify({'success': False, 'error': 'Scenario not found'}), 404

        examples[scenario_name].update(scenario_data)
        data['examples'] = examples

        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=4)

        return jsonify({
            'success': True,
            'message': 'Scenario updated successfully',
            'scenario': examples[scenario_name]
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
        tax_registry.save()

        return jsonify({
            'success': True,
            'message': 'State tax configuration created successfully',
            'config': data
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/state-taxes/<state_code>', methods=['PUT'])
def update_state_tax(state_code):
    """Update an existing state tax configuration."""
    try:
        payload = request.json
        if not isinstance(payload, dict):
            return jsonify({'success': False, 'error': 'Invalid payload'}), 400

        # Normalize numbers: expect percentages as numbers (not strings)
        prop_rate = float(payload.get('property_tax_rate')) / 100.0
        relief_pct = float(payload.get('pptra_relief')) / 100.0
        relief_cap = float(payload.get('relief_cap', 0))
        state_name = payload.get('state_name') or state_code

        registry = StateTaxRegistry()
        registry.add_state(state_code, StateTaxConfig(
            property_tax_rate=prop_rate,
            pptra_relief=relief_pct,
            relief_cap=relief_cap,
            state_name=state_name
        ))
        registry.save()

        return jsonify({'success': True, 'message': 'State tax configuration updated', 'state_code': state_code})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/state-taxes/<state_code>', methods=['DELETE'])
def delete_state_tax(state_code):
    """Delete a state tax configuration (except protected defaults)."""
    try:
        protected = {'VA', 'TX', 'CA'}
        if state_code.upper() in protected:
            return jsonify({'success': False, 'error': 'Cannot delete default state'}), 400

        registry = StateTaxRegistry()
        removed = registry.remove_state(state_code)
        if not removed:
            return jsonify({'success': False, 'error': 'State not found'}), 404
        registry.save()
        return jsonify({'success': True, 'message': 'State deleted', 'state_code': state_code})
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

@api_bp.route('/baseline', methods=['GET'])
def get_baseline():
    """Get baseline scenario data."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        if not scenarios_file.exists():
            return jsonify({'success': False, 'error': 'No baseline data found'}), 404
        
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        baseline = data.get('baseline', {})
        if not baseline:
            return jsonify({'success': False, 'error': 'No baseline configuration found'}), 404
            
        return jsonify({
            'success': True,
            'baseline': baseline
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/baseline', methods=['PUT'])
@validate_request({'required': ['description', 'vehicle_name', 'current_value', 'state']})
def update_baseline():
    """Update baseline scenario data."""
    try:
        baseline_data = request.json
        data_folder = current_app.config['DATA_FOLDER']
        scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
        
        if not scenarios_file.exists():
            return jsonify({'success': False, 'error': 'No scenarios file found'}), 404
        
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        
        # Update baseline data structure
        baseline = data.setdefault('baseline', {})
        
        # Update basic info
        baseline['description'] = baseline_data['description']
        baseline['state'] = baseline_data['state']
        
        # Update vehicle info
        vehicle = baseline.setdefault('vehicle', {})
        vehicle['name'] = baseline_data['vehicle_name']
        vehicle['current_value'] = float(baseline_data['current_value'])
        vehicle['msrp'] = float(baseline_data.get('msrp', 0))
        
        # Preserve or update 3-year values (can be calculated or provided)
        if 'values_3yr' not in vehicle:
            current_val = vehicle['current_value']
            # Simple depreciation estimate: 10% first year, 10% second, 10% third
            vehicle['values_3yr'] = [
                current_val,
                current_val * 0.9,
                current_val * 0.81,
                current_val * 0.729
            ]
        
        # Update or preserve impairment data
        vehicle['impairment'] = float(baseline_data.get('impairment', vehicle.get('impairment', 0)))
        vehicle['impairment_affects_taxes'] = baseline_data.get('impairment_affects_taxes', 
                                                             vehicle.get('impairment_affects_taxes', False))
        
        # Update loan info
        current_loan = baseline.setdefault('current_loan', {})
        current_loan['monthly_payment'] = float(baseline_data.get('monthly_payment', 0))
        current_loan['principal_balance'] = float(baseline_data.get('principal_balance', 0))
        current_loan['interest_rate'] = float(baseline_data.get('interest_rate', 0.055))
        current_loan['extra_payment'] = float(baseline_data.get('extra_payment', 0))
        
        data['baseline'] = baseline
        
        with open(scenarios_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        return jsonify({
            'success': True,
            'message': 'Baseline updated successfully',
            'baseline': baseline
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/cost-analysis', methods=['GET'])
def get_cost_analysis():
    """Get detailed cost analysis data."""
    try:
        data_folder = current_app.config['DATA_FOLDER']
        json_data = list_scenarios(data_folder)
        
        # Use the CostAnalyzer to get structured analysis data
        from core.calculators.cost_analyzer import CostAnalyzer
        analyzer = CostAnalyzer()
        analysis = analyzer.analyze_scenarios(json_data)
        
        return jsonify({
            'success': True,
            'analysis': {
                'baseline': analysis.baseline,
                'scenarios': analysis.scenarios,
                'detailed_analysis': analysis.detailed_analysis,
                'summary': analysis.summary
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500