# AI Agent's Guide to the Car Ownership Cost Model

This guide is intended for a future AI agent tasked with extending or maintaining this financial model.

## 1. Project Overview

This project is a Python-based financial model designed to compare the total cost of ownership between a baseline vehicle (the "keep" scenario) and one or more alternative vehicles (the "buy" scenarios).

The entire project is data-driven and modular. The core principle is to **separate data from logic**. All inputs are stored in a single JSON file, and all calculations are performed by Python scripts. The final outputs are a series of reports in CSV, Excel, and Markdown formats.

## 2. Core Architecture

The project consists of the following key components:

*   `run_analysis.py`:
    *   **Role:** The main entry point for the entire project.
    *   **Action:** Execute this script (`python3 run_analysis.py`) to run the complete analysis and generate all output files. It orchestrates the other scripts.

*   `scenarios/scenarios.json`:
    *   **Role:** The single source of truth for all input data. This is the heart of the model.
    *   **Structure:**
        *   `"assumptions"`: Contains global variables that affect all calculations (e.g., `investment_return_rate`).
        *   `"baseline"`: An object containing all data for the current vehicle (the "keep" scenario).
        *   `"examples"`: An object containing one or more nested objects, where each nested object represents a new vehicle to be compared.

*   `Model/car_keep_runner.py`:
    *   **Role:** The core calculation engine. It reads the data from `scenarios.json`, performs all the financial calculations (depreciation, maintenance, opportunity cost, etc.), and returns the final results.
    *   **Note:** If the fundamental financial logic needs to be changed, this is the primary file to modify.

*   `Model/generate_comparison_matrix.py`:
    *   **Role:** A reporting script that takes the results from the core runner and generates the summary `cost_difference_matrix.csv`.

*   `Model/generate_excel_report.py`:
    *   **Role:** A reporting script that takes the results from the core runner and generates the `car_ownership_analysis.xlsx` file.

*   `car_comparison.md`:
    *   **Role:** A human-readable summary and analysis of the final results. This file is updated manually after the model is run to provide interpretation and recommendations.

## 3. How to Add a New Vehicle for Comparison

To extend the analysis to a new vehicle, you do **not** need to modify any Python code. You only need to add a new entry to the `scenarios/scenarios.json` file.

**Step-by-step instructions:**

1.  **Open `scenarios/scenarios.json`**.
2.  Navigate to the `"examples"` object.
3.  Add a new vehicle object inside `"examples"`. Use a descriptive key for the new vehicle (e.g., `"Tesla_Model_Y_Purchase"`).
4.  Populate the new vehicle object using the template below. **It is critical to research and provide data-driven values for each field.**

### New Vehicle Template

```json
"Your_New_Vehicle_Name": {
  "type": "purchase",
  "name": "Vehicle Make and Model",
  "msrp": 50000,
  "values_3yr": [50000, 42500, 36125, 30706],
  "loan_term": 72,
  "interest_rate": 0.055,
  "trade_in_incentives": 0,
  "down_payment": 10000.00,
  "insurance_monthly": 150.00,
  "maintenance_annual": [300, 450, 600],
  "fuel_monthly": 50.00,
  "property_tax_rate": 0.0457,
  "pptra_relief": 0.30
}
```

### New Lease Template

```json
"Your_Lease_Name": {
  "type": "lease",
  "name": "Polestar 3",
  "msrp": 76600,
  "values_3yr": [76600, 61280, 52088, 44428],
  "down_payment": 5530.00,
  "refundable_msd": 3500.00,
  "monthly_payment": 312.00,
  "lease_term_months": 27,
  "money_factor": 0.00045,
  "residual_value": 40598,
  "insurance_monthly": 168.04,
  "maintenance_annual": [0, 0, 0],
  "fuel_monthly": 45.00,
  "property_tax_rate": 0.0457,
  "pptra_relief": 0.30
}
```

### Field Explanations:

*   `type`: "purchase" or "lease".
*   `refundable_msd` (Lease only): Refundable Security Deposits. This is modeled as an upfront cash outflow that is returned as "Equity" at the end of the analysis.
*   `money_factor` (Lease only): Used to calculate implicit financing costs (Rent Charge).
*   `lease_term_months`: Length of the lease. If less than 36 months, the model will simulate a pro-rata extension to allow for a fair 3-year comparison.
*   `residual_value`: The buy-back price at lease end. Used for rent charge calculations.
*   `name`: The display name of the car.
*   `msrp`: The purchase price of the vehicle.
*   `values_3yr`: A 4-element array representing the vehicle's value at Year 0, Year 1, Year 2, and Year 3. The first value should be the same as `msrp`. Use the `calculate_depreciation.py` script to generate this based on research.
*   `loan_term`: The loan term in months.
*   `interest_rate`: The annual interest rate as a decimal (e.g., 5.5% is `0.055`).
*   `down_payment`: The total down payment amount.
*   `insurance_monthly`: The estimated monthly insurance cost.
*   `maintenance_annual`: A 3-element array representing the total maintenance cost for Year 1, Year 2, and Year 3.
*   `fuel_monthly`: The estimated monthly cost for fuel or electricity.

5.  **Save the `scenarios/scenarios.json` file.**
6.  **Execute the main analysis script** from the root directory:
    ```bash
    python3 run_analysis.py
    ```

The script will automatically detect the new vehicle scenario and include it in all generated reports. You can then review the updated `cost_difference_matrix.csv` and `car_ownership_analysis.xlsx` files.
