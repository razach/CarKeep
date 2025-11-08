#!/usr/bin/env python3
"""
Generate a consolidated comparison matrix CSV with all examples as columns.
"""

import json
import pandas as pd
from pathlib import Path
from car_keep_runner import run_comparison_from_json


def generate_comparison_matrix(data_folder=None):
    """Generate a consolidated cost difference CSV file."""
    if data_folder is None:
        data_folder = Path.cwd()
    
    print("Running all scenarios to generate comparison matrix...")
    
    # Load scenarios from JSON
    scenarios_file = data_folder / 'scenarios' / 'scenarios.json'
    with open(scenarios_file, 'r') as f:
        scenarios_data = json.load(f)
    
    # Run all scenarios
    all_results = run_comparison_from_json(scenarios_data)
    
    print("\nGenerating consolidated CSV files...")
    
    # Generate consolidated matrix
    cost_diff_matrix = create_cost_difference_matrix(all_results)
    
    # Save to CSV
    cost_diff_matrix.to_csv('cost_difference_matrix.csv', index=False)
    print("  Saved: cost_difference_matrix.csv")
    
    print("\nComparison matrix complete! All scenarios are now in consolidated CSV files.")


def create_cost_difference_matrix(all_results):
    """Create cost difference matrix with all scenarios as columns."""
    
    # Get the first result to determine structure
    first_result = list(all_results.values())[0]
    cost_diff_data = first_result['results']['cost_difference']
    
    # Create base matrix with cost components
    cost_components = [row[0] for row in cost_diff_data['data']]
    
    matrix_data = {
        'Cost Component': cost_components
    }
    
    # Add each scenario as columns with descriptions
    for scenario_name, results in all_results.items():
        cost_diff_data = results['results']['cost_difference']
        
        amounts = [row[1] for row in cost_diff_data['data']]
        descriptions = [row[2] for row in cost_diff_data['data']]
        
        matrix_data[f"{scenario_name}_amount"] = amounts
        matrix_data[f"{scenario_name}_description"] = descriptions
    
    # Create the DataFrame
    df = pd.DataFrame(matrix_data)
    
    # Add a summary row at the top
    summary_data = {'Cost Component': 'SCENARIO SUMMARY'}
    for scenario_name in all_results.keys():
        summary_data[f"{scenario_name}_amount"] = f"Amount for {scenario_name}"
        summary_data[f"{scenario_name}_description"] = f"Description for {scenario_name}"
    
    summary_row = pd.DataFrame([summary_data])
    
    # Combine summary row with main data
    final_df = pd.concat([summary_row, df], ignore_index=True)
    
    return final_df


if __name__ == "__main__":
    generate_comparison_matrix()
