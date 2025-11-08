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
    loan_amount = vehicle2_msrp - scenario_data['down_payment']
    monthly_rate = scenario_data['interest_rate'] / 12
    num_payments = scenario_data['loan_term']
    vehicle2_monthly_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate)**-num_payments)

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
        v2_total_monthly = vehicle2_monthly_payment + v2_tax + vehicle2_insurance_monthly + v2_maint + vehicle2_fuel_monthly
        v2_monthly_costs.append(v2_total_monthly)

    # --- Calculate Expanded Opportunity Cost ---
    opportunity_cost = 0
    for month in range(36):
        # If RDX is cheaper, the difference is a positive opportunity to invest
        monthly_difference = v2_monthly_costs[month] - rdx_monthly_costs[month]
        
        # Calculate future value of this single month's difference invested until the end
        months_to_grow = 36 - (month + 1)
        fv_of_investment = monthly_difference * ((1 + monthly_investment_rate) ** months_to_grow)
        opportunity_cost += fv_of_investment

    # --- Totals for Summary Tables ---
    rdx_total_cost_3yr = sum(rdx_monthly_costs)
    v2_total_cost_3yr = sum(v2_monthly_costs)
    
    rdx_equity_end = rdx_values_3yr[-1]
    vehicle2_equity_end = vehicle2_values_3yr[-1]

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
    vehicle2_interest = calculate_total_interest(loan_amount, vehicle2_monthly_payment, scenario_data['interest_rate'], 36)

    # =============================================================================
    # FORMAT OUTPUT
    # =============================================================================
    
    # Cost Difference Table
    total_diff = (v2_total_cost_3yr + scenario_data['down_payment'] - vehicle2_equity_end) - (rdx_total_cost_3yr - rdx_equity_end)
    
    # Note: The opportunity cost is now part of the total difference calculation implicitly.
    # For the table, we present it as the cost of choosing the more expensive option.
    # If opportunity_cost is positive, it means V2 is more expensive, and that's the lost opportunity.
    
    cost_difference_breakdown = {
        'columns': ['Cost Component', 'Amount', 'Description'],
        'data': [
            ['Loan Payment Difference', f'${(vehicle2_monthly_payment * 36) - (rdx_total_payment * rdx_months_to_payoff):.0f}', 'Difference in total loan payments over 36 months'],
            ['Interest Difference', f'${vehicle2_interest - rdx_total_interest:.0f}', 'Interest on new loan vs remaining interest on RDX loan'],
            ['Down Payment', f'${scenario_data.get("down_payment", 0):.0f}', 'Upfront down payment for the new vehicle'],
            ['Property Tax Difference', f'${sum(calculate_property_tax(v2_val) for v2_val in vehicle2_values_3yr[:3]) * 12 - sum(calculate_property_tax(rdx_val) for rdx_val in rdx_values_3yr[:3]) * 12:.0f}', 'Higher property tax on more expensive vehicle'],
            ['Insurance Difference', f'${(vehicle2_insurance_monthly - rdx_insurance_monthly) * 36:.0f}', 'Higher insurance on new vehicle'],
            ['Maintenance Difference', f'${sum(vehicle2_maintenance_annual) - sum(rdx_maintenance_annual):.0f}', 'Difference in maintenance costs'],
            ['Fuel/Electricity Difference', f'${(vehicle2_fuel_monthly - rdx_fuel_monthly) * 36:.0f}', 'Savings from electricity vs gas'],
            ['Equity Difference', f'${rdx_equity_end - vehicle2_equity_end:.0f}', 'Difference in vehicle equity after 36 months'],
            ['Lost Investment Opportunity', f'${opportunity_cost:.0f}', 'Compounded value of investing the monthly cost difference'],
            ['TOTAL COST DIFFERENCE', f'${total_diff + opportunity_cost:.0f}', 'Total additional cost of new vehicle including opportunity cost']
        ]
    }

    return {
        'results': {
            'cost_difference': cost_difference_breakdown
        }
    }
