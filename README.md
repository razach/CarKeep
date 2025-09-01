# CarKeep Vehicle Cost Comparison Tool

A comprehensive vehicle cost comparison tool that supports both lease and loan financing scenarios for the second vehicle. The system can evaluate keeping your current vehicle vs. leasing a new one or buying a CPO vehicle with a loan.

## Features

- **Dual Financing Support**: Compare keeping current vehicle vs. lease OR loan for new vehicle
- **CPO Vehicle Analysis**: Evaluate Certified Pre-Owned vehicle purchases with realistic depreciation curves
- **State-Specific Calculations**: Support for different states with custom cost configurations
- **Flexible Input**: JSON-based input system for easy integration with web applications
- **Comprehensive Analysis**: Monthly payment breakdowns, 3-year summaries, and cost difference analysis

## Quick Start

### 1. Run a Single Comparison

```bash
python car_keep_runner.py input.json
```

### 2. Run Examples

```bash
# List available examples
python run_examples.py list

# Run specific example
python run_examples.py cpo_loan_comparison
```

## System Architecture

- **`main.py`** - Core calculation engine and data structures
- **`car_keep_runner.py`** - Main script that takes JSON input and runs comparisons
- **`examples.json`** - Collection of example inputs for testing
- **`run_examples.py`** - Helper script to run examples

## JSON Input Format

```json
{
  "description": "Description of the comparison",
  "state": "VA",
  "vehicle1": {
    "name": "Current Vehicle Name",
    "msrp": 0,
    "current_value": 21000,
    "values_3yr": [21000, 18900, 17000, 15300],
    "impairment": 3000,
    "impairment_affects_taxes": false
  },
  "vehicle2": {
    "name": "New Vehicle Name",
    "msrp": 45000,
    "current_value": 0,
    "values_3yr": [35000, 31500, 28350, 25515]
  },
  "current_loan": {
    "principal_balance": 9909.95,
    "monthly_payment": 564.10,
    "extra_payment": 85.90,
    "interest_rate": 0.0439
  },
  "vehicle2_financing": {
    "type": "loan",
    "config": {
      "monthly_payment": 1073.47,
      "loan_term": 36,
      "principal_balance": 35000
    }
  },
  "trade_in": {
    "trade_in_value": 18000,
    "loan_balance": 9909.95,
    "incentives": 0
  }
}
```

## Financing Types

### Lease Financing
```json
"vehicle2_financing": {
  "type": "lease",
  "config": {
    "monthly_payment": 368,
    "lease_terms": 36,
    "msrp": 72800,
    "incentives": {
      "ev_credit": 7500,
      "dealer_discount": 2000
    }
  }
}
```

### Loan Financing
```json
"vehicle2_financing": {
  "type": "loan",
  "config": {
    "monthly_payment": 1073.47,
    "loan_term": 36,
    "principal_balance": 35000
  }
}
```

## Available Examples

1. **`basic_lease_comparison`** - Acura RDX vs Lucid Air (Lease, VA)
2. **`cpo_loan_comparison`** - Acura RDX vs CPO Acura MDX (Loan, VA)
3. **`custom_costs_comparison`** - Acura RDX vs Lucid Air with Texas costs (Lease, TX)
4. **`cpo_bmw_x3_loan`** - Acura RDX vs CPO BMW X3 (Loan, VA)
5. **`cpo_bmw_x3_lease`** - Acura RDX vs CPO BMW X3 (Lease, VA)
6. **`cpo_with_custom_costs`** - CPO BMW X3 with custom cost configurations (VA)

## Output Format

The system outputs structured JSON with three main result tables:

1. **`monthly_payment`** - Monthly cost breakdown
2. **`summary`** - 3-year total cost summary  
3. **`cost_difference`** - Detailed cost difference analysis

## Cost Customization

Override default costs for specific vehicles:

```json
"cost_overrides": {
  "insurance_monthly": {
    "CPO BMW X3": 160,
    "CPO Acura MDX": 140
  },
  "maintenance_monthly": {
    "CPO BMW X3": 85,
    "CPO Acura MDX": 65
  },
  "fuel_monthly": {
    "CPO BMW X3": 180,
    "CPO Acura MDX": 200
  }
}
```

## State Support

- **VA** (Virginia) - Default with Fairfax County property tax calculations
- **TX** (Texas) - Custom cost configurations

## Dependencies

- Python 3.8+
- pandas
- numpy

## Webapp Integration

The JSON-based system is perfect for web applications:

- **Input**: Accept JSON from web forms or API calls
- **Processing**: Call `run_comparison_from_json()` function  
- **Output**: Return structured JSON results for frontend display

## Future Enhancements

- Additional state tax calculations
- More sophisticated depreciation models
- API endpoints for web integration
- Database storage for comparison history
- Export to various formats (CSV, Excel, PDF)
