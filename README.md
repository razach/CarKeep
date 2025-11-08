# CarKeep v2

A financial modeling tool to analyze and compare the total cost of ownership between different vehicle scenarios - keeping your current vehicle vs. purchasing or leasing a new one.

> **Note:** This is version 2 - a complete rewrite with an AI-first, data-driven approach. The original version (with web frontend) is preserved in the [`v1-archive`](https://github.com/razach/CarKeep/tree/v1-archive) branch.

## Features

- **Data-driven analysis** using JSON configuration
- **Comprehensive cost modeling** including depreciation, financing, insurance, maintenance, and opportunity costs
- **Multiple output formats**: Excel reports, CSV matrices, and markdown summaries
- **Easy scenario comparison** - add new vehicles and instantly see the financial impact

## Quick Start

1. Install dependencies:
```bash
pip install pandas xlsxwriter
```

2. Configure your scenarios in `scenarios/scenarios.json`

3. Run the analysis:
```bash
python3 run_analysis.py
```

## Project Structure

- `scenarios/scenarios.json` - Define vehicle parameters and scenarios
- `Model/car_keep_runner.py` - Core financial calculation engine
- `run_analysis.py` - Main entry point to generate all reports
- `car_comparison.md` - Human-readable analysis summary
- `AI_GUIDE.md` - Guide for extending the model

## Output Files

- `car_ownership_analysis.xlsx` - Detailed Excel report with step-by-step calculations
- `cost_difference_matrix.csv` - Summary comparison of all scenarios
- `monthly_payment_matrix.csv` - Monthly payment breakdowns
- `summary_matrix.csv` - High-level cost overview

## Documentation

See `AI_GUIDE.md` for detailed instructions on adding new vehicles and extending the model.

## License

MIT
