import json
import xlsxwriter
from car_keep_runner import run_comparison_from_json

def generate_excel_report():
    """
    Generate an Excel report by running the core calculation engine and
    writing the inputs and results to separate sheets.
    """
    # Load data from scenarios.json
    with open('scenarios/scenarios.json', 'r') as f:
        scenarios = json.load(f)

    # Run the core calculation engine to get definitive results
    results = run_comparison_from_json(scenarios)
    
    # We only have one scenario, so get the first one
    scenario_name = list(results.keys())[0]
    cost_difference_data = results[scenario_name]['results']['cost_difference']

    # Create a new Excel workbook
    workbook = xlsxwriter.Workbook('car_ownership_analysis.xlsx')
    
    # Add formats
    header_format = workbook.add_format({'bold': True, 'bg_color': '#F0F0F0', 'border': 1})
    
    # Add worksheets
    inputs_sheet = workbook.add_worksheet('Inputs')
    cost_diff_sheet = workbook.add_worksheet('Cost Difference')

    # Write data and formulas to the worksheets
    write_inputs_sheet(inputs_sheet, scenarios, header_format)
    write_cost_diff_sheet(cost_diff_sheet, cost_difference_data, header_format)

    # Close the workbook
    workbook.close()
    print("Excel report 'car_ownership_analysis.xlsx' generated successfully.")

def write_inputs_sheet(sheet, scenarios, header_format):
    """Write the raw input data from scenarios.json to the 'Inputs' worksheet."""
    sheet.set_column('A:A', 25)
    sheet.set_column('B:C', 30)
    
    sheet.write('A1', 'Category', header_format)
    sheet.write('B1', 'Acura RDX (Baseline)', header_format)
    sheet.write('C1', 'BMW iX (Purchase)', header_format)

    row = 1
    # Write baseline data
    for key, value in scenarios.get('baseline', {}).items():
        sheet.write(row, 0, key)
        sheet.write(row, 1, str(value))
        row += 1
        
    row = 1
    # Write example data
    example_data = scenarios.get('examples', {}).get('BMW_iX_CPO_Purchase', {})
    for key, value in example_data.items():
        sheet.write(row, 2, str(value))
        row += 1
        
    # Write assumptions
    row += 2 # Add a two-row gap
    sheet.write(row, 0, 'Assumptions', header_format)
    row += 1
    for key, value in scenarios.get('assumptions', {}).items():
        sheet.write(row, 0, key)
        sheet.write(row, 1, str(value))
        row += 1

def write_cost_diff_sheet(sheet, cost_difference_data, header_format):
    """Write the calculated cost difference breakdown to its worksheet."""
    sheet.set_column('A:A', 25)
    sheet.set_column('B:B', 15)
    sheet.set_column('C:C', 60)

    # Write headers
    headers = cost_difference_data.get('columns', [])
    for col, header in enumerate(headers):
        sheet.write(0, col, header, header_format)
        
    # Write data rows
    for row_idx, row_data in enumerate(cost_difference_data.get('data', []), 1):
        for col_idx, cell_data in enumerate(row_data):
            sheet.write(row_idx, col_idx, cell_data)

if __name__ == '__main__':
    generate_excel_report()
