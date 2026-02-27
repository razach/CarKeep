#!/usr/bin/env python3
"""
Main entry point to run the full car ownership cost analysis.

This script orchestrates the execution of the different reporting
and analysis modules, providing a single command to generate all
project outputs.
"""

import sys
from pathlib import Path

# Add the Model directory to the system path to allow for module imports
project_root = Path(__file__).parent
model_path = project_root / 'Model'
sys.path.append(str(model_path))

try:
    from generate_comparison_matrix import generate_comparison_matrix
    from generate_excel_report import generate_excel_report
except ImportError as e:
    print(f"Error: Could not import necessary modules from the 'Model' directory.")
    print(f"Please ensure the 'Model' directory and its contents are intact.")
    print(f"Import error: {e}")
    sys.exit(1)

def run_full_analysis():
    """
    Runs all parts of the financial analysis and generates all reports.
    """
    print("--- Starting Car Ownership Cost Analysis ---")
    
    try:
        # 1. Generate the CSV comparison matrices
        print("\n[Step 1/2] Generating CSV comparison matrices...")
        generate_comparison_matrix()
        print("[Step 1/2] CSV reports generated successfully.")
        
        # 2. Generate the detailed Excel report
        print("\n[Step 2/2] Generating detailed Excel report...")
        generate_excel_report()
        print("[Step 2/2] Excel report generated successfully.")
        
        print("\n--- Analysis Complete ---")
        print("All output files have been updated.")
        
    except Exception as e:
        print(f"\nAn error occurred during the analysis: {e}")
        print("Please check the data in 'scenarios/scenarios.json' and ensure all scripts in the 'Model' directory are correct.")
        sys.exit(1)

if __name__ == "__main__":
    run_full_analysis()
