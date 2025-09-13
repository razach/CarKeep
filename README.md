# CarKeep - Vehicle Cost Comparison Tool

A comprehensive tool for comparing the total cost of ownership between keeping your current vehicle and getting a new one (lease or loan).

## 🚗 **Structure: Baseline + Scenarios**

The system uses a **baseline + scenarios** approach that makes it easy to add new comparison scenarios:

### **Baseline (Do Nothing Option)**
- **Acura RDX** - Your current car that you're considering keeping
- All scenarios compare against this baseline
- Single source of truth for current vehicle data

### **Scenarios (What You Could Do Instead)**
Each scenario represents a different option you could choose instead of keeping the RDX:

1. **Lucid Air Lease** - Luxury EV lease
2. **CPO Acura MDX Loan** - Certified pre-owned SUV with financing
3. **Lucid Air Lease (Texas)** - Same car, different state costs
4. **CPO BMW X3 Loan** - German luxury SUV with financing
5. **CPO BMW X3 Lease** - Same car, lease financing
6. **CPO BMW X3 Custom Costs** - Same car, customized insurance/maintenance
7. **New Tesla Model Y** - Brand new EV lease (example of adding new scenarios)

## 📊 **Output Formats**

### **Individual Scenario Results**
- Run single scenarios: `python run_scenarios.py <scenario_name>`
- Export to CSV: `python run_scenarios.py <scenario_name> --csv`

### **Consolidated Comparison Matrix**
- All scenarios side-by-side: `python generate_comparison_matrix.py`
- Creates three consolidated CSV files:
  - `monthly_payment_matrix.csv` - Monthly costs across all scenarios
  - `summary_matrix.csv` - 3-year totals across all scenarios  
  - `cost_difference_matrix.csv` - Cost differences with dedicated description columns

## 🔧 **Adding New Scenarios**

Adding a new comparison scenario is incredibly simple! Just add to `data/scenarios/scenarios.json`:

```json
"my_new_scenario": {
  "description": "Acura RDX vs [Your New Car]",
  "scenario": {
    "type": "lease",  // or "loan"
    "vehicle": {
      "name": "Your Car Name",
      "msrp": 50000,
      "current_value": 0,
      "values_3yr": [50000, 40000, 32000, 25600]
    },
    "financing": {
      "monthly_payment": 600,
      "lease_terms": 36,  // or "loan_term" for loans
      "msrp": 50000,      // or "principal_balance" for loans
      "incentives": {
        "ev_credit": 7500,
        "dealer_discount": 1000
      }
    }
  },
  "trade_in": {
    "trade_in_value": 18000,
    "loan_balance": 9909.95,
    "incentives": 1000
  }
}
```

### **What You Need to Define:**
- **Vehicle details**: Name, MSRP, 3-year depreciation values
- **Financing**: Monthly payment, term, incentives
- **Trade-in**: Value, loan balance, incentives
- **Optional**: Custom costs, state overrides

### **What's Automatically Handled:**
- Property taxes (with state-specific rates)
- Insurance costs (with defaults)
- Maintenance costs (with defaults)
- Fuel/electricity costs (with defaults)
- Investment opportunity costs
- Equity calculations
- All comparison logic

## 🏗️ **System Architecture**

```
data/scenarios/scenarios.json (Baseline + Scenarios)
           ↓
car_keep_runner.py (Processes JSON)
           ↓
main.py (Core calculation engine)
           ↓
Output: Individual CSVs + Consolidated Matrix
```

## 📈 **Key Benefits of New Structure**

1. **Clear Baseline**: RDX is always the "do nothing" option
2. **Easy Scenario Addition**: Just add JSON, no code changes needed
3. **Consistent Comparisons**: All scenarios use same baseline data
4. **Flexible Financing**: Support for both lease and loan scenarios
5. **State Flexibility**: Override baseline state when needed
6. **Cost Customization**: Override default costs for specific scenarios

## 🚀 **Usage Examples**

### **List All Available Scenarios**
```bash
python run_scenarios.py list
```

### **Run a Specific Scenario**
```bash
python run_scenarios.py cpo_bmw_x3_lease
python run_scenarios.py lucid_air_lease_tx --csv
```

### **Generate Consolidated Matrix**
```bash
python generate_comparison_matrix.py
```

### **Run Individual Comparisons**
```bash
python car_keep_runner.py data/scenarios/scenarios.json
```

## 🔍 **What Gets Calculated**

For each scenario, the system calculates:

- **Monthly Costs**: Payment, taxes, insurance, maintenance, fuel
- **3-Year Totals**: All costs over the comparison period
- **Cost Differences**: How much more/less the new option costs
- **Equity Impact**: Value retention vs. depreciation
- **Investment Opportunity**: Lost returns from new vehicle costs

## 📋 **Dependencies**

- Python 3.8+
- pandas
- numpy
- dateutil

## 🌐 **Webapp Ready**

The JSON-based input system makes this ready for web application integration:
- RESTful API endpoints
- Dynamic scenario generation
- Real-time cost comparisons
- User-friendly scenario builders

## 📝 **Example: Adding Tesla Model Y**

The Tesla Model Y example demonstrates how easy it is to add new scenarios:

1. **Added to JSON**: New scenario with lease terms and incentives
2. **Automatic Processing**: System handles all calculations
3. **Matrix Update**: New scenario appears in consolidated output
4. **No Code Changes**: Pure configuration addition

This makes CarKeep a powerful, flexible tool for vehicle cost analysis that can easily adapt to new vehicles, financing options, and cost structures!
