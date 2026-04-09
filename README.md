# CarKeep v2

A financial modeling tool to analyze and compare the total cost of ownership between different vehicle scenarios - keeping your current vehicle vs. purchasing or leasing a new one.

> **Note:** This is version 2 - a complete rewrite with an AI-first, data-driven approach. The original version (with web frontend) is preserved in the [`v1-archive`](https://github.com/razach/CarKeep/tree/v1-archive) branch.

## Features

- **Data-driven analysis** using JSON configuration
- **Comprehensive cost modeling** including depreciation, financing, insurance, maintenance, and opportunity costs
- **Multiple output formats**: Excel reports, CSV matrices, and markdown summaries
- **Easy scenario comparison** - add new vehicles and instantly see the financial impact
- **Supported Models**: Lease vs. Purchase, Loan Amortization, Lease Extensions, Lost Opportunity Cost

## Current Scenarios
- **Baseline**: Keep Acura RDX
- **Purchase**: BMW iX xDrive50 (CPO)
- **Lease**: Polestar 3
- **Lease**: BMW iX xDrive45

## Quick Start

1. Install dependencies:
```bash
pip install pandas xlsxwriter playwright playwright-stealth matplotlib seaborn numpy
playwright install chromium
```

2. Configure your scenarios in `Module1_TCO_Analysis/scenarios/scenarios.json`

3. **Run the TCO analysis:** (Module 1)
```bash
cd Module1_TCO_Analysis && python3 run_analysis.py
```

4. **Run the CPO Prospecting tracker:** (Module 2)
```bash
./Module2_Prospecting/scrapers/daily_run.sh
```

## Project Structure

- **Module1_TCO_Analysis/** - Answers "What should I buy?"
  - `scenarios/scenarios.json` - Define vehicle parameters and scenarios
  - `Model/` - Core financial calculation engine and reporting modules
  - `Scripts/` - Helper scripts and standalone tools
  - `ResearchData/` - General research notes, actuals, and reference materials
  - `run_analysis.py` - Main entry point to generate all reports
  - `car_comparison.md` - Human-readable analysis summary

- **Module2_Prospecting/** - Answers "Which specific iX is the best deal?"
  - `data/prospects_db.json` - Normalized persistent database tracking market inventory and prices over time
  - `scrapers/daily_run.sh` - Automated end-to-end execution wrapper
  - `scrapers/bmw_cpo_scraper.py` - Playwright stealth scraper bypassing bot detection
  - `scrapers/update_inventory.py` - Upserts daily scraped json into the main prospects database
  - `reports/generate_report.py` - Generates statistical Market Value graphs via Seaborn
  - `reports/daily_summary.md` - AI-generated markdown summary containing best value targets and pricing metrics

- `AI_GUIDE.md` - Guide for extending the model

## Output Files

- **Module 1 Outputs**: `car_ownership_analysis.xlsx`, `cost_difference_matrix.csv`, `monthly_payment_matrix.csv`, `summary_matrix.csv`
- **Module 2 Outputs**: `value_matrix.png`, `daily_summary.md`

## Documentation

See `AI_GUIDE.md` for detailed instructions on adding new vehicles and extending the model.

## License

MIT
