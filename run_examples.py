#!/usr/bin/env python3
"""
Helper script to run individual examples from the example_inputs.json file.
"""

import json
import sys
from car_keep_runner import run_comparison_from_json


def list_examples():
    """List all available examples."""
    try:
        with open('examples.json', 'r') as f:
            data = json.load(f)
        
        print("Available examples:")
        for example_name, example_data in data['examples'].items():
            print(f"  {example_name}: {example_data['description']}")
        
    except FileNotFoundError:
        print("Error: examples.json not found.")
        sys.exit(1)


def run_example(example_name: str):
    """Run a specific example by name."""
    try:
        with open('examples.json', 'r') as f:
            data = json.load(f)
        
        if example_name not in data['examples']:
            print(f"Error: Example '{example_name}' not found.")
            print("Use 'python run_example.py list' to see available examples.")
            sys.exit(1)
        
        example_data = data['examples'][example_name]
        print(f"Running: {example_data['description']}")
        print("=" * 60)
        
        # Run the comparison
        results = run_comparison_from_json(example_data)
        
        # Print results in a readable format
        print(f"Comparison: {results['comparison_type']}")
        print(f"State: {results['state']}")
        print()
        
        for table_name, table_data in results['results'].items():
            print(f"{table_name.upper().replace('_', ' ')} TABLE")
            print("-" * 40)
            
            # Print headers
            print(" | ".join(table_data['columns']))
            print("-" * 40)
            
            # Print data rows
            for row in table_data['data']:
                print(" | ".join(str(cell) for cell in row))
            
            print()
        
    except FileNotFoundError:
        print("Error: examples.json not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_example.py list                    # List all examples")
        print("  python run_example.py <example_name>          # Run specific example")
        print()
        print("Examples:")
        print("  python run_example.py basic_lease_comparison")
        print("  python run_example.py cpo_loan_comparison")
        print("  python run_example.py custom_costs_comparison")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_examples()
    else:
        run_example(command)


if __name__ == "__main__":
    main()
