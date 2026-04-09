# AI Agent Instructions

**Objective:** To act as an interactive UI and guide for the Car Ownership Cost Model.

Upon launching this project, your first action should be to greet the user and present them with the following two options:

1.  **Review the latest analysis.**
2.  **Evaluate a new car.**

---

### **Path 1: If the user wants to "Review the latest analysis"**

1.  **Read the primary summary file:** `Module1_TCO_Analysis/car_comparison.md`.
2.  **Read the final data file:** `Module1_TCO_Analysis/outputs/cost_difference_matrix.csv`.
3.  **Provide a concise, curated summary** to the user, including:
    *   The final recommendation (Keep vs. Buy).
    *   The total 3-year cost difference.
    *   The equivalent monthly cost difference.
    *   The top 2-3 factors driving the difference (e.g., "The main reasons for this are the massive $15,526 lost investment opportunity and the...").
    *   Offer to show the full `Module1_TCO_Analysis/car_comparison.md` report if they want more detail.

---

### **Path 2: If the user wants to "Evaluate a new car"**

1.  **Acknowledge the request** and explain that you will guide them through the process of adding a new vehicle to the comparison.
2.  **Consult the guide:** Open and follow the instructions in `AI_GUIDE.md`.
3.  **Interactively gather data:** Ask the user for the required information for the new vehicle, one piece at a time. Reference the "New Vehicle Template" in the guide.
    *   *Example Interaction:* "Great, let's evaluate a new car. First, what is the make and model of the new vehicle?" -> "Got it. What is the total purchase price (MSRP)?" -> etc.
4.  **Assist with complex data:** For `values_3yr` (depreciation) and `maintenance_annual`, offer to research the data for the user if they don't have it. Use web searches to find reliable data and propose a schedule, just as was done to create the existing scenarios.
5.  **Update the data file:** Once all information is gathered, read `Module1_TCO_Analysis/scenarios/scenarios.json`, add the new vehicle object to the `"examples"` section, and write the file back.
6.  **Run the analysis:** Execute the main analysis script: `cd Module1_TCO_Analysis && python3 run_analysis.py`.
7.  **Report the new results:** After the script finishes, read the new `Module1_TCO_Analysis/outputs/cost_difference_matrix.csv` and present the new total cost difference to the user. Then, transition to **Path 1** to provide a full summary of the new comparison.

---
---

# GEMINI Analysis: Car Ownership Cost Comparison Model

## Project Overview

This project is a financial modeling tool written in Python to analyze and compare the total cost of ownership between different vehicle scenarios. The primary use case is to compare the cost of keeping a current vehicle versus purchasing or leasing a new one.

The model is data-driven, using a `Module1_TCO_Analysis/scenarios/scenarios.json` file to define the financial parameters for the vehicles being compared. The core logic is contained in a modular Python script (`car_keep_runner.py`) that performs the calculations. Other scripts are used to generate various output reports, including CSV matrices and a detailed Excel file.

**Key Technologies:**
*   **Language:** Python 3
*   **Libraries:** `pandas`, `xlsxwriter`.

**Architecture:**
*   **Data:** All input parameters are defined in `Module1_TCO_Analysis/scenarios/scenarios.json`. Unstructured research data and notes are in `Module1_TCO_Analysis/ResearchData/`.
*   **Core Logic:** `Module1_TCO_Analysis/Model/car_keep_runner.py` contains the main financial calculation engine. It reads the scenario data and produces a structured result.
*   **Reporting/Execution:**
    *   `Module1_TCO_Analysis/run_analysis.py`: The main entry point to run all reports.
    *   `Module1_TCO_Analysis/Model/generate_comparison_matrix.py`: Generates summary CSV files.
    *   `Module1_TCO_Analysis/Model/generate_excel_report.py`: Generates a detailed Excel workbook.
*   **Scripts:** `Module1_TCO_Analysis/Scripts/` contains standalone helper utilities (e.g., depreciation and loan calculators).
*   **Documentation:**
    *   `Module1_TCO_Analysis/car_comparison.md`: A human-readable summary of the analysis.
    *   `AI_GUIDE.md`: A guide for AI agents on how to extend the model.

## Building and Running

This project does not have a formal build process. The analysis is run by executing the Python scripts directly.

**Prerequisites:**
You will need Python 3 and the required libraries installed. You can install them using the virtual environment's pip:
```bash
./.venv/bin/pip install pandas xlsxwriter
```

**Running the Analysis:**
To generate all the output files, run the main analysis script from the root directory:
```bash
cd Module1_TCO_Analysis && python3 run_analysis.py
```

## Development Conventions

*   **Data-Driven Scenarios:** All vehicle parameters should be defined in the `Module1_TCO_Analysis/scenarios/scenarios.json` file. This allows for easy addition of new scenarios without changing the core logic.
*   **Modular Logic:** The core financial calculations are encapsulated in `Module1_TCO_Analysis/Model/car_keep_runner.py`.
*   **Separation of Concerns:** Reporting scripts are separate from the core calculation logic.
