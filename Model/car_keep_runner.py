import pandas as pd
import numpy as np

def run_comparison_from_json(comparison_json):
    """
    Calculate and compare costs for a baseline vehicle vs. example vehicles from a JSON object.
    """
    baseline_data = comparison_json['baseline']
    all_results = {}

    for scenario_name, scenario_data in comparison_json['examples'].items():
        results = calculate_vehicle_costs(baseline_data, scenario_data, comparison_json.get('assumptions', {}))
        all_results[scenario_name] = results

    return all_results

def calculate_vehicle_costs(rdx_data, scenario_data, assumptions):
    # =============================================================================
    # INPUT PARAMETERS
    # =============================================================================
    rdx_principal_balance = rdx_data['loan_principal_balance']
    rdx_total_payment = rdx_data['monthly_payment'] + rdx_data['extra_payment']
    rdx_interest_rate = rdx_data['interest_rate']
    rdx_values_3yr = rdx_data['values_3yr']
    rdx_insurance_monthly = rdx_data['insurance_monthly']
    rdx_maintenance_annual = rdx_data['maintenance_annual']
    rdx_fuel_monthly = rdx_data['fuel_monthly']

    vehicle2_name = scenario_data['name']
    vehicle2_msrp = scenario_data['msrp']
    vehicle2_values_3yr = scenario_data['values_3yr']
    vehicle2_insurance_monthly = scenario_data['insurance_monthly']
    vehicle2_maintenance_annual = scenario_data['maintenance_annual']
    vehicle2_fuel_monthly = scenario_data['fuel_monthly']
    
    property_tax_rate = scenario_data['property_tax_rate']
    pptra_relief = scenario_data['pptra_relief']
    
    investment_return_rate = assumptions.get('investment_return_rate', 0.06)
    monthly_investment_rate = investment_return_rate / 12

    # =============================================================================
    # CALCULATIONS
    # =============================================================================

    def calculate_property_tax(vehicle_value):
        pptra_amount = min(vehicle_value, 20000) * property_tax_rate * pptra_relief
        tax_first_20k = min(vehicle_value, 20000) * property_tax_rate
        tax_over_20k = max(vehicle_value - 20000, 0) * property_tax_rate
        return (tax_first_20k + tax_over_20k - pptra_amount) / 12

    # --- Calculate Monthly Cost Arrays (36 months) ---
    rdx_monthly_costs = []
    v2_monthly_costs = []

    rdx_loan_balance = rdx_principal_balance
    
    # Calculate V2 monthly payment
    is_lease = scenario_data.get('type') == 'lease'
    
    if not is_lease:
        loan_amount = vehicle2_msrp - scenario_data['down_payment']
        monthly_rate = scenario_data['interest_rate'] / 12
        num_payments = scenario_data['loan_term']
        vehicle2_monthly_payment_base = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate)**-num_payments)
    else:
        # Lease logic
        vehicle2_monthly_payment_base = scenario_data['monthly_payment']
        lease_term = scenario_data.get('lease_term_months', 36)
        # Calculate effective monthly cost for extension (amortizing the down payment + monthly)
        # Explicit logic: Month 1-27 = Base; Month 28-36 = Effective Average
        lease_total_contract_cost = scenario_data['down_payment'] + (vehicle2_monthly_payment_base * lease_term)
        lease_extension_monthly_cost = lease_total_contract_cost / lease_term

    for month in range(1, 37):
        year_idx = (month - 1) // 12
        
        # RDX Costs
        rdx_loan_payment_monthly = 0
        if rdx_loan_balance > 0:
            monthly_interest = rdx_loan_balance * (rdx_interest_rate / 12)
            principal_paid = rdx_total_payment - monthly_interest
            rdx_loan_balance -= principal_paid
            rdx_loan_payment_monthly = rdx_total_payment
            if rdx_loan_balance < 0:
                rdx_loan_payment_monthly += rdx_loan_balance # Refund overpayment
                rdx_loan_balance = 0

        rdx_tax = calculate_property_tax(rdx_values_3yr[year_idx])
        rdx_maint = rdx_maintenance_annual[year_idx] / 12
        rdx_total_monthly = rdx_loan_payment_monthly + rdx_tax + rdx_insurance_monthly + rdx_maint + rdx_fuel_monthly
        rdx_monthly_costs.append(rdx_total_monthly)

        # Vehicle 2 Costs
        v2_tax = calculate_property_tax(vehicle2_values_3yr[year_idx])
        v2_maint = vehicle2_maintenance_annual[year_idx] / 12
        
        # Determine current month's payment (Lease vs Loan)
        current_v2_payment = vehicle2_monthly_payment_base
        if is_lease and month > lease_term:
             current_v2_payment = lease_extension_monthly_cost
             
        v2_total_monthly = current_v2_payment + v2_tax + vehicle2_insurance_monthly + v2_maint + vehicle2_fuel_monthly
        v2_monthly_costs.append(v2_total_monthly)

    # --- Calculate Expanded Opportunity Cost ---
    opportunity_cost = 0
    
    # 1. Opportunity Cost on Monthly Cash Flow Differences
    for month in range(36):
        # If RDX is cheaper, the difference is a positive opportunity to invest
        monthly_difference = v2_monthly_costs[month] - rdx_monthly_costs[month]
        
        # Calculate future value of this single month's difference invested until the end
        months_to_grow = 36 - (month + 1)
        fv_of_investment = monthly_difference * ((1 + monthly_investment_rate) ** months_to_grow)
        opportunity_cost += fv_of_investment

    # 2. Opportunity Cost on Upfront Cash Difference (Down Payment + MSD)
    # We need to know how much *more* cash V2 requires at Day 0 than keeping RDX.
    # Keep RDX: $0 upfront.
    # Buy/Lease V2: Down Payment (+ MSD if lease).
    # We assume 'trade_in_incentives' or equity usage is part of 'down_payment' logic usually,
    # but here 'down_payment' is explicitly the cash amount.
    
    # Logic: If you pay $10k down, you lost the ability to invest that $10k for 36 months.
    # Future Value of Down Payment = PV * (1+r)^36
    # Lost Opportunity = FV - PV.
    
    v2_upfront_cash = scenario_data.get('down_payment', 0)
    if is_lease:
        v2_upfront_cash += scenario_data.get('refundable_msd', 0)
        
    # We calculate the FV of this upfront cash if it had been invested instead
    fv_upfront = v2_upfront_cash * ((1 + monthly_investment_rate) ** 36)
    opp_cost_upfront = fv_upfront - v2_upfront_cash
    
    opportunity_cost += opp_cost_upfront

    # --- Totals for Summary Tables ---
    rdx_total_cost_3yr = sum(rdx_monthly_costs)
    v2_total_cost_3yr = sum(v2_monthly_costs)
    
    rdx_equity_end = rdx_values_3yr[-1]
    # Calculate total interest paid for summary tables
    def calculate_total_interest(principal, monthly_payment, interest_rate, months):
        balance = principal
        total_interest = 0
        for _ in range(months):
            interest = balance * (interest_rate / 12)
            principal_paid = monthly_payment - interest
            balance -= principal_paid
            total_interest += interest
        return total_interest

    rdx_months_to_payoff = next((i for i, cost in enumerate(rdx_monthly_costs) if cost < rdx_total_payment), 36)
    rdx_total_interest = calculate_total_interest(rdx_principal_balance, rdx_total_payment, rdx_interest_rate, rdx_months_to_payoff)

    if is_lease:
        # MSD Logic: You pay it upfront, you get it back at the end.
        refundable_msd = scenario_data.get('refundable_msd', 0)
        vehicle2_equity_end = refundable_msd
        
        # Interest (Rent Charge) Calculation
        # Rent Charge = Total Payments - Depreciation
        # Depreciation = (Adjusted Cap Cost - Residual)
        # Since we lack exact Adjusted Cap Cost in inputs, we estimate Interest using Money Factor
        # Rule of Thumb: Rent Charge ~ (Capitalized Cost + Residual) * Money Factor
        # We can approximate Cap Cost knowing the monthly payment and term, but let's be simpler:
        # We will use the Money Factor * 2400 as a proxy for APR to show context,
        # but for the exact "Interest Descrepancy" row, we might just omit it or simple estimate.
        # Better approach: 
        # Total Lease Cost = (Depreciation + Rent Charge).
        # We know Total Lease Cost (payments).
        # Let's estimate Rent Charge = Average Monthly Lease Balance * (Money Factor * 2400 / 12)? No.
        # Let's use the standard formula with estimated Cap Cost.
        # Cap Cost ~= MSRP - Incentives. We don't have incentives.
        # Reverse engineer: Monthly = (Cap - Residual)/Term * (1+Tax?) + (Cap+Residual)*MF * (1+Tax?)
        # This is too complex to guess.
        # DECISION: Show 'Imputed Interest' as (Payments - (MSRP - Residual))? No, that assumes MSRP deal.
        # DECISION 2: For lease, just set Interest to a small calculated value based on MF * Average Price.
        mf = scenario_data.get('money_factor', 0.002) # default to something if missing
        avg_value = (vehicle2_msrp + scenario_data.get('residual_value', vehicle2_msrp*0.53)) / 2
        lease_monthly_interest = avg_value * mf 
        vehicle2_interest = lease_monthly_interest * 36 # Projected over 3 years
        
        # Cash Flow for payments:
        # Month 0: Down Payment + MSD
        # Month 1-27: Monthly
        # Month 28-36: Extension Monthly
        v2_total_payments_3yr = (vehicle2_monthly_payment_base * lease_term) + (lease_extension_monthly_cost * (36 - lease_term))
        # Note: Down payment is handled in 'Down Payment' row, but MSD needs to be accounted for.
        # We will add MSD to the "Down Payment" row for display or separate it?
        # Standard: MSD is a separate outlay. We'll add it to the Down Payment SUM in the logic below if we want strict cash flow,
        # but since it returns as Equity, it cancels out in Net Cost except for Opportunity Cost.
        # To make "Down Payment" row accurate to the "Check you write", we should include it.
        effective_down_payment_cash_flow = scenario_data.get("down_payment", 0) + refundable_msd
    else:
        vehicle2_equity_end = vehicle2_values_3yr[-1]
        vehicle2_interest = calculate_total_interest(loan_amount, vehicle2_monthly_payment_base, scenario_data['interest_rate'], 36)
        v2_total_payments_3yr = vehicle2_monthly_payment_base * 36
        effective_down_payment_cash_flow = scenario_data.get("down_payment", 0)

    # =============================================================================
    # FORMAT OUTPUT
    # =============================================================================
    
    # Cost Difference Table
    total_diff = (v2_total_cost_3yr + effective_down_payment_cash_flow - vehicle2_equity_end) - (rdx_total_cost_3yr - rdx_equity_end)
    
    # Note: The opportunity cost is now part of the total difference calculation implicitly.
    # For the table, we present it as the cost of choosing the more expensive option.
    # If opportunity_cost is positive, it means V2 is more expensive, and that's the lost opportunity.h 0.
    
    # We need to update the Opportunity Cost loop to include MSD in Month 0 cost?
    # Currently Opportunity Cost references `rdx_monthly_costs` and `v2_monthly_costs`.
    # It does NOT verify the Down Payment opportunity cost explicitly in the loop (it might be missing!).
    # Wait, the opportunity_cost calculation in line 90+ only looks at monthly flows 0-36.
    # It misses the Month 0 Upfront completely!
    # "If RDX is cheaper... difference is positive... invest".
    # We should add the Down Payment difference to the Opportunity Cost logic.
    # Current code: `total_diff` calculation (line 127) adds down payment but not opp cost on it.
    # FIX: Add Opp Cost on Down Payment difference.
    
    initial_cash_diff = effective_down_payment_cash_flow - 0 # Assuming RDX has 0 down (it's existing).
    # Wait, RDX "Cost" is keeping it.
    # RDX has "Equity" which is like a down payment you already made?
    # No, RDX is "Keep". You don't pay a down payment. You just have the asset.
    # The comparison is:
    # Option A (RDX): Asset ($18k) - Loan ($8k) = $10k Equity.
    # Option B (Lease): Pay $5k Down + $3.5k MSD.
    # Cash Flow Diff at T=0: You SELL RDX (Get $10k cash). You PAY Lease ($8.5k).
    # Net Cash at T=0: You HAVE $1.5k extra in pocket!
    # So Lease actually starts with a POSITIVE cash event vs Keeping?
    # Wait, "Keep RDX": You do nothing. Bank acct = $X.
    # "Buy iX": Trade RDX ($10k equity) -> Down Payment. Bank acct = $X. (Neutral).
    # "Lease Polestar": Trade RDX ($10k). Pay $5.5k Down + $3.5k MSD = $9k.
    # You have $1k left over!
    # So the Opportunity Cost for Polestar needs to reflect that you INVEST that $1k?
    # OR if you don't trade RDX? The assumption is usually "Trade in existing vehicle".
    # Scenario says: "BMW_iX_CPO_Purchase": down_payment 10000. (Matches RDX equity).
    # Polestar: down_payment 5530 + 3500 = 9030.
    # So yes, it is roughly neutral.
    # I will calculate Opportunity Cost on the *monthly* flows only, as the upfronts are roughly washed out by the trade-in assumption.
    # I will proceed with just fixing the 'effective_down_payment' for the summary table.

    cost_difference_breakdown = {
        'columns': ['Cost Component', 'Amount', 'Description'],
        'data': [
            ['Loan/Lease Payment Difference', f'${v2_total_payments_3yr - (rdx_total_payment * rdx_months_to_payoff):.0f}', 'Difference in total monthly payments over 36 months'],
            ['Interest Difference', f'${vehicle2_interest - rdx_total_interest:.0f}', 'Interest/Rent Charge cost difference'],
            ['Down Payment & MSD', f'${effective_down_payment_cash_flow:.0f}', 'Upfront cash (Down Payment + Security Deposits)'],
            ['Property Tax Difference', f'${sum(calculate_property_tax(v2_val) for v2_val in vehicle2_values_3yr[:3]) * 12 - sum(calculate_property_tax(rdx_val) for rdx_val in rdx_values_3yr[:3]) * 12:.0f}', 'Higher property tax on more expensive vehicle'],
            ['Insurance Difference', f'${(vehicle2_insurance_monthly - rdx_insurance_monthly) * 36:.0f}', 'Higher insurance on new vehicle'],
            ['Maintenance Difference', f'${sum(vehicle2_maintenance_annual) - sum(rdx_maintenance_annual):.0f}', 'Difference in maintenance costs'],
            ['Fuel/Electricity Difference', f'${(vehicle2_fuel_monthly - rdx_fuel_monthly) * 36:.0f}', 'Savings from electricity vs gas'],
            ['Equity Difference', f'${rdx_equity_end - vehicle2_equity_end:.0f}', 'Difference in vehicle equity (RDX Value vs MSD Return)'],
            ['Lost Investment Opportunity', f'${opportunity_cost:.0f}', 'Compounded value of investing the monthly cost difference'],
            ['TOTAL COST DIFFERENCE', f'${total_diff + opportunity_cost:.0f}', 'Total additional cost of new vehicle including opportunity cost']
        ]
    }

    return {
        'results': {
            'cost_difference': cost_difference_breakdown
        }
    }
