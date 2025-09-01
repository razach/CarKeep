#!/usr/bin/env python3
"""
CarKeep Vehicle Cost Comparison Runner
A callable script that takes JSON input and runs vehicle cost comparisons.
"""

import json
import sys
from typing import Dict, Any, List
from main import VehicleCostCalculator, VehicleConfig, LoanConfig, LeaseConfig, TradeInConfig, FinancingType


def parse_vehicle_config(data: Dict[str, Any]) -> VehicleConfig:
    """Parse vehicle configuration from JSON data."""
    return VehicleConfig(
        name=data['name'],
        msrp=data.get('msrp', 0),
        current_value=data.get('current_value', 0),
        values_3yr=data['values_3yr'],
        impairment=data.get('impairment', 0),
        impairment_affects_taxes=data.get('impairment_affects_taxes', False)
    )


def parse_loan_config(data: Dict[str, Any]) -> LoanConfig:
    """Parse loan configuration from JSON data."""
    return LoanConfig(
        principal_balance=data['principal_balance'],
        monthly_payment=data['monthly_payment'],
        extra_payment=data.get('extra_payment', 0),
        interest_rate=data['interest_rate']
    )


def parse_lease_config(data: Dict[str, Any]) -> LeaseConfig:
    """Parse lease configuration from JSON data."""
    return LeaseConfig(
        monthly_payment=data['monthly_payment'],
        lease_terms=data['lease_terms'],
        msrp=data['msrp'],
        incentives=data.get('incentives', {})
    )


def parse_trade_in_config(data: Dict[str, Any]) -> TradeInConfig:
    """Parse trade-in configuration from JSON data."""
    return TradeInConfig(
        trade_in_value=data['trade_in_value'],
        loan_balance=data['loan_balance'],
        incentives=data.get('incentives', 0)
    )


def parse_cost_overrides(data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Parse cost overrides from JSON data."""
    cost_overrides = {}
    
    if 'insurance_monthly' in data:
        cost_overrides['insurance_monthly'] = data['insurance_monthly']
    
    if 'maintenance_monthly' in data:
        cost_overrides['maintenance_monthly'] = data['maintenance_monthly']
    
    if 'fuel_monthly' in data:
        cost_overrides['fuel_monthly'] = data['fuel_monthly']
    
    return cost_overrides


def run_comparison_from_json(json_data: Dict[str, Any], export_csv: bool = False) -> Dict[str, Any]:
    """
    Run a vehicle cost comparison from JSON data.
    
    Expected JSON structure:
    {
        "baseline": {
            "description": "Baseline vehicle description",
            "state": "VA",
            "vehicle": {...},
            "current_loan": {...}
        },
        "examples": {
            "scenario_name": {
                "description": "Scenario description",
                "state": "VA",  # Optional, defaults to baseline state
                "scenario": {
                    "type": "lease" | "loan",
                    "vehicle": {...},
                    "financing": {...}
                },
                "trade_in": {...},
                "cost_overrides": {...}  # Optional
            }
        }
    }
    """
    
    # Extract baseline data
    baseline = json_data.get('baseline', {})
    baseline_state = baseline.get('state', 'VA')
    baseline_vehicle = baseline.get('vehicle', {})
    baseline_loan = baseline.get('current_loan', {})
    
    # Extract examples
    examples = json_data.get('examples', {})
    
    results = {}
    
    for example_name, example_data in examples.items():
        print(f"  Processing: {example_data.get('description', example_name)}")
        
        # Use example state if provided, otherwise use baseline state
        state = example_data.get('state', baseline_state)
        
        # Extract scenario data
        scenario = example_data.get('scenario', {})
        scenario_type = scenario.get('type', 'lease')
        scenario_vehicle = scenario.get('vehicle', {})
        scenario_financing = scenario.get('financing', {})
        
        # Extract trade-in and cost overrides
        trade_in = example_data.get('trade_in', {})
        cost_overrides = example_data.get('cost_overrides', {})
        
        # Create VehicleConfig objects
        vehicle1_config = VehicleConfig(
            name=baseline_vehicle.get('name', 'Current Vehicle'),
            msrp=baseline_vehicle.get('msrp', 0),
            current_value=baseline_vehicle.get('current_value', 0),
            values_3yr=baseline_vehicle.get('values_3yr', [0, 0, 0, 0]),
            impairment=baseline_vehicle.get('impairment', 0),
            impairment_affects_taxes=baseline_vehicle.get('impairment_affects_taxes', False)
        )
        
        vehicle2_config = VehicleConfig(
            name=scenario_vehicle.get('name', 'New Vehicle'),
            msrp=scenario_vehicle.get('msrp', 0),
            current_value=scenario_vehicle.get('current_value', 0),
            values_3yr=scenario_vehicle.get('values_3yr', [0, 0, 0, 0]),
            impairment=0,
            impairment_affects_taxes=False
        )
        
        # Create LoanConfig for current loan
        current_loan_config = LoanConfig(
            principal_balance=baseline_loan.get('principal_balance', 0),
            monthly_payment=baseline_loan.get('monthly_payment', 0),
            extra_payment=baseline_loan.get('extra_payment', 0),
            interest_rate=baseline_loan.get('interest_rate', 0)
        )
        
        # Create financing config based on type
        if scenario_type == 'lease':
            vehicle2_financing = LeaseConfig(
                monthly_payment=scenario_financing.get('monthly_payment', 0),
                lease_terms=scenario_financing.get('lease_terms', 36),
                msrp=scenario_financing.get('msrp', 0),
                incentives=scenario_financing.get('incentives', {})
            )
            financing_type = FinancingType.LEASE
        else:  # loan
            vehicle2_financing = LeaseConfig(  # Reusing LeaseConfig for loan data
                monthly_payment=scenario_financing.get('monthly_payment', 0),
                lease_terms=scenario_financing.get('loan_term', 36),
                msrp=scenario_financing.get('principal_balance', 0),
                incentives={}
            )
            financing_type = FinancingType.LOAN
        
        # Create TradeInConfig
        trade_in_config = TradeInConfig(
            trade_in_value=trade_in.get('trade_in_value', 0),
            loan_balance=trade_in.get('loan_balance', 0),
            incentives=trade_in.get('incentives', 0)
        )
        
        # Create calculator and run comparison
        calculator = VehicleCostCalculator(state)
        comparison_results = calculator.run_comparison(
            vehicle1_config=vehicle1_config,
            vehicle2_config=vehicle2_config,
            loan_config=current_loan_config,
            lease_config=vehicle2_financing,
            trade_in_config=trade_in_config,
            financing_type=financing_type
        )
        
        # Store results
        results[example_name] = {
            'description': example_data.get('description', example_name),
            'results': comparison_results
        }
    
    # Export CSV files if requested
    if export_csv:
        for example_name, example_results in results.items():
            for table_name, df in example_results['results'].items():
                filename = f"{example_name}_{table_name}_comparison.csv"
                df.to_csv(filename, index=False)
                print(f"Saved {filename}")
    
    # Convert DataFrames to dictionaries for JSON serialization
    json_results = {}
    for example_name, example_results in results.items():
        json_results[example_name] = {
            'description': example_results['description'],
            'results': {}
        }
        
        for table_name, df in example_results['results'].items():
            json_results[example_name]['results'][table_name] = {
                'columns': df.columns.tolist(),
                'data': df.values.tolist()
            }
    
    return json_results


def main():
    """Main function that reads JSON input and runs comparison."""
    
    if len(sys.argv) < 2:
        print("Usage: python car_keep_runner.py <input_file.json> [--csv]")
        print("  --csv    Export results to CSV files")
        sys.exit(1)
    
    input_file = sys.argv[1]
    export_csv = "--csv" in sys.argv
    
    try:
        # Read JSON input file
        with open(input_file, 'r') as f:
            json_data = json.load(f)
        
        # Run comparison
        results = run_comparison_from_json(json_data, export_csv)
        
        # Output results as JSON
        print(json.dumps(results, indent=2))
        
        if export_csv:
            print("\nCSV files have been generated for further processing and visualization.")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing required field in JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
