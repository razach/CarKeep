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


def run_comparison_from_json(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run vehicle cost comparison from JSON input data."""
    
    # Parse configuration
    state = json_data.get('state', 'VA')
    calculator = VehicleCostCalculator(state=state)
    
    # Apply cost overrides if provided
    if 'cost_overrides' in json_data:
        cost_overrides = parse_cost_overrides(json_data['cost_overrides'])
        for cost_type, overrides in cost_overrides.items():
            getattr(calculator.cost_config, cost_type).update(overrides)
    
    # Parse vehicle configurations
    vehicle1_config = parse_vehicle_config(json_data['vehicle1'])
    vehicle2_config = parse_vehicle_config(json_data['vehicle2'])
    
    # Parse loan configuration (current vehicle)
    current_loan_config = parse_loan_config(json_data['current_loan'])
    
    # Parse financing configuration for vehicle2
    financing_type = FinancingType(json_data['vehicle2_financing']['type'])
    
    if financing_type == FinancingType.LEASE:
        # For lease, use lease_config directly
        lease_config = parse_lease_config(json_data['vehicle2_financing']['config'])
    else:
        # For loan, create lease_config structure to hold loan info
        loan_data = json_data['vehicle2_financing']['config']
        lease_config = LeaseConfig(
            monthly_payment=loan_data['monthly_payment'],
            lease_terms=loan_data.get('loan_term', 36),
            msrp=loan_data['principal_balance'],
            incentives={}
        )
    
    # Parse trade-in configuration
    trade_in_config = parse_trade_in_config(json_data['trade_in'])
    
    # Run comparison
    results = calculator.run_comparison(
        vehicle1_config, vehicle2_config, current_loan_config, 
        lease_config, trade_in_config, financing_type
    )
    
    # Convert DataFrames to dictionaries for JSON serialization
    json_results = {}
    for table_name, df in results.items():
        json_results[table_name] = {
            'columns': df.columns.tolist(),
            'data': df.values.tolist()
        }
    
    return {
        'comparison_type': f"{vehicle1_config.name} vs {vehicle2_config.name} ({financing_type.value})",
        'state': state,
        'results': json_results
    }


def main():
    """Main function that reads JSON input and runs comparison."""
    
    if len(sys.argv) != 2:
        print("Usage: python car_keep_runner.py <input_file.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        # Read JSON input file
        with open(input_file, 'r') as f:
            json_data = json.load(f)
        
        # Run comparison
        results = run_comparison_from_json(json_data)
        
        # Output results as JSON
        print(json.dumps(results, indent=2))
        
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
