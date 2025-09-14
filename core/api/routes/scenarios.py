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

        # Helper to parse money strings like "$12,345" -> float
        import re
        def parse_money(value):
            try:
                if value is None:
                    return 0.0
                if isinstance(value, (int, float)):
                    return float(value)
                s = str(value)
                # Remove any non-numeric except minus and dot
                cleaned = re.sub(r'[^0-9\-\.]', '', s)
                if cleaned == '' or cleaned == '-':
                    return 0.0
                return float(cleaned)
            except Exception:
                return 0.0

        detailed_analysis = []
        baseline_net = None
        baseline_monthly = json_data.get('baseline', {}).get('current_loan', {}).get('monthly_payment', 0)

        monthly_totals = []
        scenario_nets = []

        # results is a mapping of scenario_name -> { description, results }
        for scenario_name, entry in results.items():
            desc = entry.get('description', '')
            res = entry.get('results', {})

            # Parse summary table (baseline is column index 1, scenario is column index 2)
            summary = res.get('summary', {})
            summary_rows = summary.get('data', [])

            def find_row_contains(substr):
                for r in summary_rows:
                    try:
                        if substr.lower() in str(r[0]).lower():
                            return r
                    except Exception:
                        continue
                return None

            def val_from_summary(row, col_idx):
                if not row or len(row) <= col_idx:
                    return 0.0
                return parse_money(row[col_idx])

            lease_row = find_row_contains('Lease/Loan Payment')
            loan_interest_row = find_row_contains('Loan Interest')
            property_tax_row = find_row_contains('Property Tax')
            insurance_row = find_row_contains('Insurance')
            maintenance_row = find_row_contains('Maintenance')
            fuel_row = find_row_contains('Fuel') or find_row_contains('Fuel/Electricity')
            subtotal_row = find_row_contains('SUBTOTAL')
            equity_row = find_row_contains('Equity')
            investment_row = find_row_contains('Investment Opportunity')
            net_row = find_row_contains('NET OUT-OF-POCKET')

            # For detailed analysis we want the scenario column (index 2)
            lease_loan_payment = val_from_summary(lease_row, 2)
            loan_interest = val_from_summary(loan_interest_row, 2)
            property_tax = val_from_summary(property_tax_row, 2)
            insurance = val_from_summary(insurance_row, 2)
            maintenance = val_from_summary(maintenance_row, 2)
            fuel_electricity = val_from_summary(fuel_row, 2)
            subtotal = val_from_summary(subtotal_row, 2)
            equity_36mo = val_from_summary(equity_row, 2)
            investment_opportunity = val_from_summary(investment_row, 2)
            net_out_of_pocket = val_from_summary(net_row, 2)

            # Parse monthly payment table (scenario value is index 1)
            monthly = res.get('monthly_payment', {})
            monthly_rows = monthly.get('data', [])

            def find_monthly(label):
                for r in monthly_rows:
                    try:
                        if label.lower() in str(r[0]).lower():
                            return r
                    except Exception:
                        continue
                return None

            mp_payment_row = find_monthly('Payment')
            mp_property_row = find_monthly('Property Tax')
            mp_insurance_row = find_monthly('Insurance')
            mp_maintenance_row = find_monthly('Maintenance')
            mp_fuel_row = find_monthly('Fuel') or find_monthly('Fuel/Electricity')
            mp_total_row = find_monthly('TOTAL MONTHLY')

            # scenario column for monthly tables is index 1
            mp_payment = val_from_summary(mp_payment_row, 1)
            mp_property = val_from_summary(mp_property_row, 1)
            mp_insurance = val_from_summary(mp_insurance_row, 1)
            mp_maintenance = val_from_summary(mp_maintenance_row, 1)
            mp_fuel = val_from_summary(mp_fuel_row, 1)
            mp_total = val_from_summary(mp_total_row, 1)

            # Save baseline net from the first scenario's summary (column index 1)
            if baseline_net is None:
                baseline_net = val_from_summary(net_row, 1)

            monthly_totals.append((scenario_name, mp_total))
            scenario_nets.append((scenario_name, net_out_of_pocket))

            vehicle_name = entry.get('description') or (entry.get('results', {}).get('summary', {}).get('columns', []) and entry.get('results', {}).get('summary', {}).get('columns')[-1]) or scenario_name

            detailed_analysis.append({
                'vehicle_name': vehicle_name,
                'description': desc,
                'lease_loan_payment': lease_loan_payment,
                'loan_interest': loan_interest,
                'property_tax': property_tax,
                'insurance': insurance,
                'maintenance': maintenance,
                'fuel_electricity': fuel_electricity,
                'subtotal': subtotal,
                'equity_36mo': equity_36mo,
                'investment_opportunity': investment_opportunity,
                'net_out_of_pocket': net_out_of_pocket,
                'monthly_evolution': {
                    'payment': mp_payment,
                    'property_tax': mp_property,
                    'insurance': mp_insurance,
                    'maintenance': mp_maintenance,
                    'fuel_electricity': mp_fuel,
                    'total': mp_total
                }
            })

        # Compute summary metrics
        if monthly_totals:
            lowest_name, lowest_monthly = min(monthly_totals, key=lambda x: (x[1] if x[1] is not None else float('inf')))
        else:
            lowest_name, lowest_monthly = (None, 0.0)

        if scenario_nets:
            best_scenario_name, best_scenario_net = min(scenario_nets, key=lambda x: x[1])
        else:
            best_scenario_name, best_scenario_net = (None, 0.0)

        # baseline_net might be None if parsing failed
        baseline_net = baseline_net or 0.0

        # best_net_cost defined as baseline_net - best_alternative_net (negative means baseline is cheaper)
        best_net_cost = baseline_net - (best_scenario_net or 0.0)

        analysis = {
            'baseline': {
                'total_monthly': baseline_monthly
            },
            'summary': {
                'lowest_monthly_cost': lowest_monthly,
                'lowest_scenario_name': lowest_name,
                'best_net_cost': best_net_cost,
                'best_scenario_name': best_scenario_name
            },
            'detailed_analysis': detailed_analysis
        }

        return jsonify({'analysis': analysis})
    except Exception as e:
        current_app.logger.error(f"Error getting cost analysis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500