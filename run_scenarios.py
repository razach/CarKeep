#!/usr/bin/env python3
"""
Helper script to run individual scenarios from the scenarios.json file.
"""

import json
import sys
import pandas as pd
from car_keep_runner import run_comparison_from_json


def list_scenarios():
    """List all available scenarios with descriptions."""
    with open('scenarios.json', 'r') as f:
        data = json.load(f)
    
    print("Available Scenarios:")
    print("=" * 50)
    
    # Show baseline info
    baseline = data.get('baseline', {})
    print(f"Baseline: {baseline.get('description', 'No baseline defined')}")
    print(f"  Vehicle: {baseline.get('vehicle', {}).get('name', 'Unknown')}")
    print(f"  State: {baseline.get('state', 'Unknown')}")
    print()
    
    # Show scenarios
    scenarios = data.get('examples', {})
    for i, (scenario_name, scenario_data) in enumerate(scenarios.items(), 1):
        print(f"{i}. {scenario_name}")
        print(f"   Description: {scenario_data.get('description', 'No description')}")
        scenario = scenario_data.get('scenario', {})
        print(f"   Type: {scenario.get('type', 'Unknown')}")
        print(f"   Vehicle: {scenario.get('vehicle', {}).get('name', 'Unknown')}")
        if scenario_data.get('state'):
            print(f"   State: {scenario_data['state']} (overrides baseline)")
        print()


def run_scenario(scenario_name: str, export_csv: bool = False):
    """Run a specific scenario by name."""
    with open('scenarios.json', 'r') as f:
        data = json.load(f)
    
    if scenario_name not in data.get('examples', {}):
        print(f"Scenario '{scenario_name}' not found!")
        return
    
    print(f"Running scenario: {scenario_name}")
    print("=" * 50)
    
    # Create comparison JSON for this single scenario
    comparison_json = {
        'baseline': data['baseline'],
        'examples': {
            scenario_name: data['examples'][scenario_name]
        }
    }
    
    # Run the comparison
    results = run_comparison_from_json(comparison_json, export_csv=export_csv)
    
    # Display results
    scenario_results = results[scenario_name]
    print(f"\nResults for: {scenario_results['description']}")
    print("=" * 50)
    
    for table_name, table_data in scenario_results['results'].items():
        print(f"\n{table_name.upper().replace('_', ' ')} TABLE")
        print("-" * 30)
        
        # Create DataFrame for display
        df = pd.DataFrame(table_data['data'], columns=table_data['columns'])
        print(df.to_string(index=False))


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_scenarios.py list                    # List all scenarios")
        print("  python run_scenarios.py <scenario_name> [--csv]  # Run specific scenario")
        print("  --csv    Export results to CSV files")
        print()
        print("Examples:")
        print("  python run_scenarios.py lucid_air_lease")
        print("  python run_scenarios.py cpo_bmw_x3_loan --csv")
        print("  python run_scenarios.py new_tesla_model_y")
        sys.exit(1)
    
    command = sys.argv[1]
    export_csv = "--csv" in sys.argv
    
    if command == "list":
        list_scenarios()
    else:
        run_scenario(command)


if __name__ == "__main__":
    main()
