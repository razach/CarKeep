# CarKeep - Vehicle Cost Comparison Tool

A comprehensive Python tool for comparing the total cost of ownership between keeping your current vehicle (with loan) versus leasing a new vehicle.

## Features

- **Generalized Design**: Compare any two vehicles with customizable configurations
- **Comprehensive Cost Analysis**: Includes loan payments, lease payments, property taxes, insurance, maintenance, fuel/electricity costs
- **Investment Opportunity Calculation**: Accounts for freed-up cash flow after loan payoff
- **Vehicle Impairment Handling**: Supports damage/accident history impact on values
- **State-Specific Tax Calculations**: Currently supports Virginia (VA) with extensible design
- **DataFrame Output**: Returns pandas DataFrames for further processing and visualization
- **CSV Export**: Automatically saves results to CSV files

## Quick Start

### Basic Usage

```python
from main import VehicleCostCalculator, VehicleConfig, LoanConfig, LeaseConfig, TradeInConfig

# Initialize calculator
calculator = VehicleCostCalculator(state="VA")

# Configure vehicles
current_vehicle = VehicleConfig(
    name="Acura RDX",
    current_value=21000,
    values_3yr=[21000, 18900, 17000, 15300],
    impairment=3000,
    impairment_affects_taxes=False
)

new_vehicle = VehicleConfig(
    name="Lucid Air",
    msrp=72800,
    values_3yr=[71400, 55100, 41500, 31059]
)

# Configure loan terms
loan_config = LoanConfig(
    principal_balance=9909.95,
    monthly_payment=564.10,
    extra_payment=85.90,
    interest_rate=4.39 / 100
)

# Configure lease terms
lease_config = LeaseConfig(
    monthly_payment=368,
    lease_terms=36,
    msrp=72800,
    incentives={
        'air_credit': 15000,
        'ev_credit': 7500,
        'onsite_credit': 2000
    }
)

# Configure trade-in
trade_in_config = TradeInConfig(
    trade_in_value=18000,
    loan_balance=9909.95,
    incentives=2000
)

# Run comparison
results = calculator.run_comparison(
    current_vehicle, new_vehicle, loan_config, lease_config, trade_in_config
)

# Access results
monthly_table = results['monthly_payment']
summary_table = results['summary']
cost_difference_table = results['cost_difference']
```

### Running the Sample Analysis

```bash
# Activate virtual environment
source venv/bin/activate

# Run the main analysis (Acura RDX vs Lucid Air)
python main.py

# Run example comparisons
python example_usage.py
```

## Configuration Classes

### VehicleConfig
- `name`: Vehicle name (used for cost lookups)
- `msrp`: Manufacturer's Suggested Retail Price
- `current_value`: Current market value
- `values_3yr`: List of 4 values [current, year1, year2, year3]
- `impairment`: Damage/accident history reduction (default: 0)
- `impairment_affects_taxes`: Whether impairment affects property taxes (default: False)

### LoanConfig
- `principal_balance`: Current loan balance
- `monthly_payment`: Base monthly payment
- `extra_payment`: Additional monthly payment
- `interest_rate`: Annual interest rate (as decimal)

### LeaseConfig
- `monthly_payment`: Monthly lease payment
- `lease_terms`: Lease duration in months
- `msrp`: Vehicle MSRP
- `incentives`: Dictionary of incentive amounts
- `residual_value`: Optional residual value (auto-calculated if not provided)

### TradeInConfig
- `trade_in_value`: Trade-in value offered
- `loan_balance`: Remaining loan balance
- `incentives`: Additional trade-in incentives

## Output Tables

The system generates three main DataFrames:

1. **Monthly Payment Table**: Monthly cost breakdown for each scenario
2. **Summary Table**: 3-year total costs by category
3. **Cost Difference Table**: Detailed breakdown of cost differences

## Cost Categories Included

- **Loan/Lease Payments**: Principal and interest
- **Property Taxes**: State-specific calculations with relief programs
- **Insurance**: Monthly insurance costs
- **Maintenance**: Estimated maintenance costs
- **Fuel/Electricity**: Operating costs
- **Equity**: Vehicle value retention
- **Investment Opportunity**: Returns on freed-up cash flow

## State Support

Currently configured for Virginia (VA) with:
- Property tax rate: $4.57 per $100 of assessed value
- PPTRA relief: 51% on first $20,000
- Extensible design for other states

## Modular Design

The code is structured for easy modularization:

- `VehicleCostCalculator`: Main calculation engine
- Configuration classes: Data structures for inputs
- Individual calculation methods: Can be extracted to separate modules
- State-specific configurations: Can be moved to separate files

## Dependencies

- pandas
- numpy
- Python 3.7+

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Example Output

The tool generates comprehensive cost comparisons showing:

- Monthly payment breakdowns
- 3-year total cost summaries
- Detailed cost difference analysis
- Investment opportunity calculations
- Property tax impacts
- Equity retention vs lease return

## Future Enhancements

- Support for additional states
- Web interface
- Database integration
- Advanced visualization options
- Multiple vehicle comparison scenarios
