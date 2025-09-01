#!/usr/bin/env python3
"""
Generate a consolidated comparison matrix CSV with all examples as columns.
This creates a single CSV file that shows all examples side by side for easy comparison.
"""

import json
import pandas as pd
from car_keep_runner import run_comparison_from_json


def generate_comparison_matrix():
    """Generate consolidated CSV files with all scenarios as columns."""
    print("Running all scenarios to generate comparison matrix...")
    
    # Load scenarios from JSON
    with open('scenarios.json', 'r') as f:
        scenarios_data = json.load(f)
    
    # Run all scenarios
    all_results = {}
    
    # Process each scenario
    for scenario_name, scenario_data in scenarios_data['examples'].items():
        # Create a single comparison JSON for this scenario
        comparison_json = {
            'baseline': scenarios_data['baseline'],
            'examples': {
                scenario_name: scenario_data
            }
        }
        
        # Run the comparison
        results = run_comparison_from_json(comparison_json)
        all_results[scenario_name] = results[scenario_name]
    
    print("\nGenerating consolidated CSV files...")
    
    # Generate consolidated matrices
    monthly_payment_matrix = create_monthly_payment_matrix(all_results)
    summary_matrix = create_summary_matrix(all_results)
    cost_diff_matrix = create_cost_difference_matrix(all_results)
    
    # Save to CSV
    monthly_payment_matrix.to_csv('monthly_payment_matrix.csv', index=False)
    print("  Saved: monthly_payment_matrix.csv")
    
    summary_matrix.to_csv('summary_matrix.csv', index=False)
    print("  Saved: summary_matrix.csv")
    
    cost_diff_matrix.to_csv('cost_difference_matrix.csv', index=False)
    print("  Saved: cost_difference_matrix.csv")
    
    print("\nComparison matrix complete! All scenarios are now in consolidated CSV files.")


def create_monthly_payment_matrix(all_results):
    """Create monthly payment matrix with all scenarios as columns."""
    
    # Get the first result to determine structure
    first_result = list(all_results.values())[0]
    monthly_data = first_result['results']['monthly_payment']
    
    # Create base matrix with categories
    categories = []
    for row in monthly_data['data']:
        categories.append(row[0])  # Category column
    
    matrix_data = {
        'Category': categories
    }
    
    # Add each scenario as a column
    for scenario_name, results in all_results.items():
        monthly_data = results['results']['monthly_payment']
        
        # Find the vehicle2 column (new vehicle)
        vehicle2_col = None
        for col in monthly_data['columns']:
            if 'Lease' in col or 'Loan' in col:
                vehicle2_col = col
                break
        
        if vehicle2_col:
            # Extract the values for this column
            col_values = []
            for row in monthly_data['data']:
                col_idx = monthly_data['columns'].index(vehicle2_col)
                col_values.append(row[col_idx])
            
            # Add to matrix
            matrix_data[f"{scenario_name}"] = col_values
    
    return pd.DataFrame(matrix_data)


def create_summary_matrix(all_results):
    """Create summary matrix with all scenarios as columns."""
    
    # Get the first result to determine structure
    first_result = list(all_results.values())[0]
    summary_data = first_result['results']['summary']
    
    # Create base matrix with cost categories
    cost_categories = []
    for row in summary_data['data']:
        cost_categories.append(row[0])  # Cost Category column
    
    matrix_data = {
        'Cost Category': cost_categories
    }
    
    # Add each scenario as columns
    for scenario_name, results in all_results.items():
        summary_data = results['results']['summary']
        
        # Extract the vehicle2 column (new vehicle)
        vehicle2_col = None
        for col in summary_data['columns']:
            if 'Lease' in col or 'Loan' in col:
                vehicle2_col = col
                break
        
        if vehicle2_col:
            col_values = []
            for row in summary_data['data']:
                col_idx = summary_data['columns'].index(vehicle2_col)
                col_values.append(row[col_idx])
            
            matrix_data[f"{scenario_name}"] = col_values
    
    return pd.DataFrame(matrix_data)


def create_cost_difference_matrix(all_results):
    """Create cost difference matrix with all scenarios as columns."""
    
    # Get the first result to determine structure
    first_result = list(all_results.values())[0]
    cost_diff_data = first_result['results']['cost_difference']
    
    # Create base matrix with cost components
    cost_components = []
    for row in cost_diff_data['data']:
        cost_components.append(row[0])  # Cost Component column
    
    matrix_data = {
        'Cost Component': cost_components
    }
    
    # Add each scenario as columns with descriptions
    for scenario_name, results in all_results.items():
        cost_diff_data = results['results']['cost_difference']
        
        # Extract the Amount values
        amounts = []
        descriptions = []
        for row in cost_diff_data['data']:
            amounts.append(row[1])  # Amount column
            descriptions.append(row[2])  # Description column
        
        # Add amounts column with better header
        matrix_data[f"{scenario_name}_amount"] = amounts
        
        # Add descriptions column
        matrix_data[f"{scenario_name}_description"] = descriptions
    
    # Create the DataFrame
    df = pd.DataFrame(matrix_data)
    
    # Reorder columns to group amounts and descriptions together
    column_order = ['Cost Component']
    for scenario_name in all_results.keys():
        column_order.append(f"{scenario_name}_amount")
        column_order.append(f"{scenario_name}_description")
    
    # Add a summary row at the top
    summary_data = {'Cost Component': ['SCENARIO SUMMARY']}
    for col in column_order[1:]:
        if col.endswith('_amount'):
            scenario_name = col.replace('_amount', '')
            summary_data[col] = [f"Amount for {scenario_name}"]
        elif col.endswith('_description'):
            scenario_name = col.replace('_description', '')
            summary_data[col] = [f"Description for {scenario_name}"]
    
    summary_row = pd.DataFrame(summary_data)
    
    # Combine summary row with main data
    final_df = pd.concat([summary_row, df], ignore_index=True)
    
    return final_df


if __name__ == "__main__":
    generate_comparison_matrix()
