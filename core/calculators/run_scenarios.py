#!/usr/bin/env python3
"""
Helper script to run individual scenarios from the data/scenarios/scenarios.json file.
"""

import json
import sys
import pandas as pd
from pathlib import Path
from .car_keep_runner import run_comparison_from_json


def list_scenarios(data_folder=None):
    """List all available scenarios with descriptions."""
    if data_folder is None:
        data_folder = Path.cwd()
    
    scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
    with open(scenarios_file, 'r') as f:
        data = json.load(f)
    
    # Return data for Flask app instead of printing
    return {
        'baseline': data.get('baseline', {}),
        'scenarios': data.get('examples', {})
    }


def run_scenario(scenario_name: str, export_csv: bool = False, data_folder=None):
    """Run a specific scenario by name."""
    if data_folder is None:
        data_folder = Path.cwd()
    
    scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
    with open(scenarios_file, 'r') as f:
        data = json.load(f)
    
    if scenario_name not in data.get('examples', {}):
        raise ValueError(f"Scenario '{scenario_name}' not found!")
    
    # Create comparison JSON for this single scenario
    comparison_json = {
        'baseline': data['baseline'],
        'examples': {
            scenario_name: data['examples'][scenario_name]
        }
    }
    
    # Run the comparison
    results = run_comparison_from_json(comparison_json, export_csv=export_csv)
    
    # Return results for Flask app instead of printing
    return results[scenario_name]


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
        try:
            scenario_results = run_scenario(command, export_csv=export_csv)
            print(f"\nResults for: {scenario_results['description']}")
            print("=" * 50)
            
            for table_name, table_data in scenario_results['results'].items():
                print(f"\n{table_name.upper().replace('_', ' ')} TABLE")
                print("-" * 30)
                
                # Create DataFrame for display
                df = pd.DataFrame(table_data['data'], columns=table_data['columns'])
                print(df.to_string(index=False))
        except ValueError as e:
            print(e)
            sys.exit(1)


if __name__ == "__main__":
    main()
