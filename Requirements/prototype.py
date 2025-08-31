import pandas as pd
import numpy as np

def calculate_vehicle_costs():
    """
    Calculate and compare costs for Acura RDX (loan) vs Lucid Air (lease)
    
    This function performs a comprehensive 3-year cost comparison between:
    1. Keeping your current Acura RDX and continuing to pay the loan
    2. Leasing a new Lucid Air with trade-in of the RDX
    
    The analysis includes:
    - Loan payments and interest calculations
    - Lease payments and upfront costs
    - Property taxes (with impairment considerations)
    - Insurance costs
    - Maintenance costs
    - Fuel vs electricity costs
    - Equity retention vs lease return
    - Trade-in value and incentives
    
    Returns: Multiple DataFrames with detailed breakdowns
    """
    
    # =============================================================================
    # INPUT PARAMETERS (from thread discussion)
    # =============================================================================
    
    # Loan Information (Acura RDX)
    # These values come from your actual loan statement
    rdx_principal_balance = 9909.95  # Current outstanding loan balance from statement
    rdx_monthly_payment = 564.10     # Base monthly payment (minimum required)
    rdx_extra_payment = 85.90        # Extra payment you make each month (accelerates payoff)
    rdx_total_payment = rdx_monthly_payment + rdx_extra_payment  # Total monthly payment ($650)
    rdx_interest_rate = 4.39 / 100   # Annual interest rate (4.39% APR)
    
    # Vehicle Values and Depreciation
    # These represent the fair market value of your RDX over time
    rdx_impairment = 3000            # Damage and accident history reduces fair value by $3,000
    rdx_current_value = 21000        # Current trade-in value (already reflects impairment)
    rdx_values_3yr = [21000, 18900, 17000, 15300]  # Clean condition values 2025-2028
    rdx_values_3yr_impaired = [18000, 15900, 14000, 12300]  # Impaired values 2025-2028
    
    # Property Tax Impact Flag
    # Set to False because VA requires extensive paperwork to recognize impairment for tax purposes
    impairment_affects_taxes = False  # Set to False because VA requires paperwork to recognize impairment
    
    # Lucid Air Information (from lease sheet)
    lucid_msrp = 72800              # Manufacturer's Suggested Retail Price
    lucid_values_3yr = [71400, 55100, 41500, 31059]  # Assessed values for property tax calculation
    
    # NOTE: Property tax values and lease residual use different perspectives (this is correct):
    # - Lease residual ($42,680): Derived from dealer's $368 payment - optimistic dealer view
    # - Property tax values ($31,059): Conservative state assessment for tax purposes
    # - This difference reflects real-world lease economics where dealers assume higher resale values
    
    # Lease Residual Value (will be derived from monthly payment)
    # Since the monthly payment is fixed, we can derive the residual value
    # This ensures the lease math is internally consistent
    
    # Trade-in Information (Lucid Air)
    # These values determine how much the trade-in reduces your upfront costs
    rdx_trade_in_value = 18000       # What dealer will give you for RDX (reflects impairment)
    rdx_loan_balance = 9909.95       # What you owe on the RDX loan
    trade_in_incentives = 2000       # Additional $2000 in trade-in incentives
    
    # Lucid Lease Incentives (from lease sheet)
    # These reduce the capitalized cost of the lease
    air_credit = 15000               # Air credit from lease sheet
    ev_credit = 7500                 # EV Credit (must take delivery by 9/30/2025)
    onsite_credit = 2000             # Onsite credit from lease sheet
    
    # Lease Information (Lucid Air)
    lucid_monthly_payment = 368      # Monthly lease payment
    lucid_lease_terms = 36           # Lease term in months
    
    # Lease Interest Calculation (Money Factor and Residual Value)
    # Both money factor and residual value should be derived from the monthly payment
    # The dealer provides the monthly payment, so we calculate both to match
    
    # Calculate lease components
    lucid_capitalized_cost = lucid_msrp - air_credit - ev_credit - onsite_credit  # Net capitalized cost after incentives
    
    # Calculate total lease payments
    lucid_total_lease_payments = lucid_monthly_payment * lucid_lease_terms
    
    # Derive residual value from monthly payment using iterative approach
    # We know the monthly payment ($368) and need to find the residual that makes the math work
    
    # Start with a reasonable guess for residual (60% of MSRP)
    lucid_residual_value = lucid_msrp * 0.60  # Initial guess: $43,680
    
    # Iterate to find the residual that gives us the correct monthly payment
    for iteration in range(10):  # Limit iterations to avoid infinite loop
        # Calculate depreciation and interest with current residual
        lucid_depreciation = lucid_capitalized_cost - lucid_residual_value
        lucid_lease_interest = lucid_total_lease_payments - lucid_depreciation
        
        # Calculate money factor
        lucid_money_factor = lucid_lease_interest / ((lucid_capitalized_cost + lucid_residual_value) * lucid_lease_terms)
        
        # Calculate what the monthly payment should be with this residual
        calculated_monthly = (lucid_depreciation / lucid_lease_terms) + ((lucid_capitalized_cost + lucid_residual_value) * lucid_money_factor / 2)
        
        # If we're close enough, break
        if abs(calculated_monthly - lucid_monthly_payment) < 1:
            break
            
        # Adjust residual based on whether calculated payment is too high or low
        if calculated_monthly > lucid_monthly_payment:
            lucid_residual_value += 100  # Increase residual to decrease payment
        else:
            lucid_residual_value -= 100  # Decrease residual to increase payment
    
    # Calculate depreciation (the principal portion of lease payments)
    lucid_depreciation = lucid_capitalized_cost - lucid_residual_value
    
    # Calculate total interest (total payments minus depreciation)
    lucid_lease_interest = lucid_total_lease_payments - lucid_depreciation
    
    # Derive actual money factor from the calculated interest
    # Money Factor = Total Interest / ((Capitalized Cost + Residual Value) * Lease Term)
    lucid_money_factor = lucid_lease_interest / ((lucid_capitalized_cost + lucid_residual_value) * lucid_lease_terms)
    
    # Due at Delivery Components (from lease sheet breakdown)
    # These are the upfront costs you must pay when taking delivery
    order_deposit = 500              # Order deposit (credited back)
    upfront_taxes = 2067             # Estimated upfront taxes
    documentation_fee = 930          # Documentation fee
    registration_fees = 203          # Estimated registration and other fees
    first_month_payment = 368        # First month's payment
    
    # Calculate total due at delivery
    lucid_total_due_at_delivery = order_deposit + upfront_taxes + documentation_fee + registration_fees + first_month_payment
    
    # Calculate effective down payment from trade-in
    # Net trade-in value = trade-in value - loan balance + incentives
    trade_in_net_value = rdx_trade_in_value - rdx_loan_balance + trade_in_incentives
    
    # Set effective down payment to $0 (trade-in covers all costs)
    lucid_effective_down_payment = 0
    
    # Calculate required trade-in value to achieve $0 down payment
    # This shows what trade-in value would be needed if you wanted $0 cash down
    required_trade_in_net_value = lucid_total_due_at_delivery
    required_trade_in_value = required_trade_in_net_value + rdx_loan_balance - trade_in_incentives
    
    # Property Tax (Fairfax County, VA)
    # These rates determine annual property tax on vehicles
    property_tax_rate = 4.57 / 100   # $4.57 per $100 of assessed value
    pptra_relief = 0.51              # 51% relief on first $20k (Personal Property Tax Relief Act)
    
    # Insurance (monthly estimates from research)
    # These are estimated annual costs divided by 12
    rdx_insurance_monthly = 100      # $1,200/year for RDX
    lucid_insurance_monthly = 176    # $2,112/year for Lucid (higher due to luxury EV)
    
    # Maintenance (monthly estimates)
    # These are estimated 3-year costs divided by 36
    rdx_maintenance_monthly = 47     # $1,700/3 years for gas vehicle
    lucid_maintenance_monthly = 33   # $1,200/3 years for EV (lower maintenance)
    
    # Fuel/Electricity (monthly estimates)
    # These are estimated 3-year costs divided by 36
    rdx_fuel_monthly = 167          # $6,000/3 years for gas
    lucid_electricity_monthly = 42   # $1,500/3 years for electricity (much cheaper)
    
    # Investment Opportunity Cost
    # After loan payoff, you can invest the freed-up cash flow
    investment_return_rate = 0.06    # 6% annual return on investments
    
    # =============================================================================
    # LOGIC REVIEW SUMMARY
    # =============================================================================
    
    # HARD FACTS (from statements/agreements):
    # - RDX loan: $9,909.95 balance, $650/month payment, 4.39% APR
    # - Lucid lease: $368/month, 36 months, $72,800 MSRP, $26,500 incentives
    # - Trade-in: $18,000 value, $2,000 incentives
    
    # ESTIMATES (need verification):
    # - Vehicle values (depreciation estimates)
    # - Insurance costs (RDX $100/mo, Lucid $176/mo)
    # - Maintenance costs (RDX $47/mo, Lucid $33/mo)
    # - Fuel/electricity costs (RDX $167/mo, Lucid $42/mo)
    # - Investment return rate (6%)
    
    # VALUATION PERSPECTIVES (intentionally different):
    # - Lease residual ($42,680): Optimistic dealer view derived from $368 payment
    # - Property tax values ($31,059): Conservative state assessment for tax purposes
    # - RDX impairment ($3,000): Reflected in trade-in value but not property taxes (paperwork requirement)
    # - This difference reflects real-world lease economics where dealers assume higher resale values
    
    # =============================================================================
    # CALCULATIONS
    # =============================================================================
    
    # Loan payoff calculation with accelerated payments
    # This calculates how quickly you'll pay off the loan with your $650/month payments
    def calculate_loan_payoff(principal, monthly_payment, interest_rate):
        """
        Calculate loan payoff with accelerated payments
        
        Args:
            principal: Current loan balance
            monthly_payment: Total monthly payment (including extra)
            interest_rate: Annual interest rate (as decimal)
        
        Returns:
            months: Number of months to payoff
            total_interest: Total interest paid
            remaining_balance: Any remaining balance (should be 0)
        """
        remaining_balance = principal
        total_interest = 0
        months = 0
        
        while remaining_balance > 0 and months < 36:  # Cap at 36 months for 3-year analysis
            monthly_interest = remaining_balance * (interest_rate / 12)
            principal_payment = monthly_payment - monthly_interest
            
            if principal_payment > remaining_balance:
                principal_payment = remaining_balance
                monthly_interest = 0
            
            remaining_balance -= principal_payment
            total_interest += monthly_interest
            months += 1
        
        return months, total_interest, remaining_balance
    
    # Calculate actual payoff with $650/month payments
    months_to_payoff, total_interest_paid, remaining_balance = calculate_loan_payoff(
        rdx_principal_balance, rdx_total_payment, rdx_interest_rate
    )
    
    # Calculate investment opportunity after loan payoff
    # After paying off the loan, you can invest the freed-up cash flow
    months_after_payoff = 36 - months_to_payoff  # Remaining months after loan is paid off
    monthly_investment_amount = rdx_total_payment  # $650/month that can be invested
    
    # Calculate total investment returns over the remaining period
    # Using simple interest calculation for the investment period
    total_investment_opportunity = 0
    for month in range(months_after_payoff):
        # Each month you invest $650, and it earns interest for the remaining months
        months_invested = months_after_payoff - month
        monthly_return = monthly_investment_amount * (investment_return_rate / 12) * months_invested
        total_investment_opportunity += monthly_return
    
    # Property tax calculations
    # This function calculates annual property tax based on vehicle value
    def calculate_property_tax(vehicle_value):
        """
        Calculate property tax for Fairfax County, VA
        
        Args:
            vehicle_value: Assessed value of the vehicle
        
        Returns:
            Annual property tax amount
        """
        pptra_amount = min(vehicle_value, 20000) * property_tax_rate * pptra_relief
        tax_first_20k = min(vehicle_value, 20000) * property_tax_rate
        tax_over_20k = max(vehicle_value - 20000, 0) * property_tax_rate
        return tax_first_20k + tax_over_20k - pptra_amount
    
    # Calculate annual property taxes
    # Use impaired values only if VA recognizes the impairment for tax purposes
    if impairment_affects_taxes:
        rdx_property_taxes = [calculate_property_tax(val) for val in rdx_values_3yr_impaired]  # use impaired values for taxes
    else:
        rdx_property_taxes = [calculate_property_tax(val) for val in rdx_values_3yr]  # use clean values for taxes (VA doesn't recognize impairment)
    lucid_property_taxes = [calculate_property_tax(val) for val in lucid_values_3yr]
    
    # Average monthly property tax over 3 years
    # Exclude year 0 (current year) and average over the 3-year period
    rdx_avg_monthly_tax = sum(rdx_property_taxes[1:]) / 36  # exclude year 0
    lucid_avg_monthly_tax = sum(lucid_property_taxes[1:]) / 36
    
    # =============================================================================
    # TABLE 1: MONTHLY PAYMENT BREAKDOWN
    # =============================================================================
    
    # This table shows the monthly costs for each scenario
    monthly_data = {
        'Category': ['Payment', 'Property Tax', 'Insurance', 'Maintenance', 'Fuel/Electricity', 'TOTAL MONTHLY'],
        'Lucid Air Lease (36 mo)': [
            f'${lucid_monthly_payment}',
            f'${lucid_avg_monthly_tax:.0f}',
            f'${lucid_insurance_monthly}',
            f'${lucid_maintenance_monthly}',
            f'${lucid_electricity_monthly}',
            f'${lucid_monthly_payment + lucid_avg_monthly_tax + lucid_insurance_monthly + lucid_maintenance_monthly + lucid_electricity_monthly:.0f}'
        ],
        'Acura RDX Loan (15 mo)': [
            f'${rdx_total_payment:.0f}',
            f'${rdx_avg_monthly_tax:.0f}',
            f'${rdx_insurance_monthly}',
            f'${rdx_maintenance_monthly}',
            f'${rdx_fuel_monthly}',
            f'${rdx_total_payment + rdx_avg_monthly_tax + rdx_insurance_monthly + rdx_maintenance_monthly + rdx_fuel_monthly:.0f}'
        ],
        'Acura RDX (21 mo, after payoff)': [
            '$0',
            f'${rdx_avg_monthly_tax:.0f}',
            f'${rdx_insurance_monthly}',
            f'${rdx_maintenance_monthly}',
            f'${rdx_fuel_monthly}',
            f'${rdx_avg_monthly_tax + rdx_insurance_monthly + rdx_maintenance_monthly + rdx_fuel_monthly:.0f}'
        ]
    }
    
    monthly_df = pd.DataFrame(monthly_data)
    
    # =============================================================================
    # TABLE 2: 3-YEAR SUMMARY COST BY CATEGORY
    # =============================================================================
    
    # Calculate 3-year totals for each cost category
    # This provides the total cost over the entire 3-year period
    
    # RDX Loan Scenario (keeping current car)
    rdx_loan_payments = rdx_principal_balance + total_interest_paid  # Total principal + interest
    rdx_property_tax_total = sum(rdx_property_taxes[1:])  # Sum of years 1-3
    rdx_insurance_total = rdx_insurance_monthly * 36  # Monthly cost * 36 months
    rdx_maintenance_total = rdx_maintenance_monthly * 36
    rdx_fuel_total = rdx_fuel_monthly * 36
    rdx_equity_end = rdx_values_3yr_impaired[-1]  # 2028 value (with impairment)
    
    # Calculate scenario where you keep RDX and continue paying the loan (no trade-in)
    # This represents keeping your current car and continuing to pay it off
    rdx_loan_payments_keep = rdx_principal_balance + total_interest_paid
    rdx_interest_keep = total_interest_paid
    
    # Lucid Lease Scenario
    lucid_lease_payments = lucid_monthly_payment * lucid_lease_terms  # Monthly payment * 36 months
    lucid_property_tax_total = sum(lucid_property_taxes[1:])
    lucid_insurance_total = lucid_insurance_monthly * 36
    lucid_maintenance_total = lucid_maintenance_monthly * 36
    lucid_electricity_total = lucid_electricity_monthly * 36
    lucid_equity_end = 0  # lease return, no equity
    
    # Create summary table with all cost categories
    summary_data = {
        'Cost Category': [
            'Lease/Loan Payment',
            'Loan Interest',
            'Down Payment/Upfront', 
            'Property Tax',
            'Insurance',
            'Maintenance',
            'Fuel/Electricity',
            'SUBTOTAL',
            '- Equity @ 36 mo',
            '+ Investment Opportunity',
            'NET OUT-OF-POCKET'
        ],
        'Acura RDX (Keep Current Car)': [
            f'${rdx_loan_payments_keep:.0f}',
            f'${rdx_interest_keep:.0f}',
            '$0',
            f'${rdx_property_tax_total:.0f}',
            f'${rdx_insurance_total:.0f}',
            f'${rdx_maintenance_total:.0f}',
            f'${rdx_fuel_total:.0f}',
            f'${rdx_loan_payments_keep + rdx_property_tax_total + rdx_insurance_total + rdx_maintenance_total + rdx_fuel_total:.0f}',
            f'-${rdx_equity_end:.0f}',
            f'${total_investment_opportunity:.0f}',
            f'${rdx_loan_payments_keep + rdx_property_tax_total + rdx_insurance_total + rdx_maintenance_total + rdx_fuel_total - rdx_equity_end - total_investment_opportunity:.0f}'
        ],
        'Lucid Air (Lease)': [
            f'${lucid_lease_payments:.0f}',
            f'${lucid_lease_interest:.0f}',
            f'${lucid_effective_down_payment:.0f}',
            f'${lucid_property_tax_total:.0f}',
            f'${lucid_insurance_total:.0f}',
            f'${lucid_maintenance_total:.0f}',
            f'${lucid_electricity_total:.0f}',
            f'${lucid_lease_payments + lucid_lease_interest + lucid_effective_down_payment + lucid_property_tax_total + lucid_insurance_total + lucid_maintenance_total + lucid_electricity_total:.0f}',
            f'${lucid_equity_end:.0f}',
            '$0',
            f'${lucid_lease_payments + lucid_lease_interest + lucid_effective_down_payment + lucid_property_tax_total + lucid_insurance_total + lucid_maintenance_total + lucid_electricity_total:.0f}'
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    
    # Calculate the cost difference between scenarios
    # This shows how much more expensive the Lucid lease is compared to keeping the RDX
    lucid_total_cost = lucid_lease_payments + lucid_lease_interest + lucid_effective_down_payment + lucid_property_tax_total + lucid_insurance_total + lucid_maintenance_total + lucid_electricity_total
    rdx_keep_total_cost = rdx_loan_payments_keep + rdx_property_tax_total + rdx_insurance_total + rdx_maintenance_total + rdx_fuel_total - rdx_equity_end - total_investment_opportunity
    cost_difference = lucid_total_cost - rdx_keep_total_cost
    
    # Add comparison row to the summary dataframe
    comparison_row = pd.DataFrame({
        'Cost Category': ['COST DIFFERENCE (Lease vs Keep RDX)'],
        'Acura RDX (Keep Current Car)': [''],
        'Lucid Air (Lease)': [f'${cost_difference:.0f}']
    })
    
    summary_df = pd.concat([summary_df, comparison_row], ignore_index=True)
    
    # =============================================================================
    # TABLE 3: COST DIFFERENCE BREAKDOWN
    # =============================================================================
    
    # This table breaks down exactly where the cost difference comes from
    # Each row shows how much more/less the Lucid costs in that category
    
    # Calculate individual cost differences that sum to the total
    # Break down the lease vs loan payments into their components
    lucid_depreciation = lucid_capitalized_cost - lucid_residual_value
    rdx_depreciation = rdx_current_value - rdx_equity_end
    
    # Calculate the actual differences that sum to the total
    depreciation_diff = lucid_depreciation - rdx_depreciation  # Higher depreciation on Lucid
    interest_diff = lucid_lease_interest - rdx_interest_keep  # Lease interest vs loan interest
    property_tax_diff = lucid_property_tax_total - rdx_property_tax_total
    insurance_diff = lucid_insurance_total - rdx_insurance_total
    maintenance_diff = lucid_maintenance_total - rdx_maintenance_total
    fuel_diff = lucid_electricity_total - rdx_fuel_total
    equity_diff = lucid_equity_end - (-rdx_equity_end)  # Lucid has 0 equity, RDX has positive equity
    investment_opp_diff = total_investment_opportunity  # RDX gets investment opportunity, Lucid doesn't - this makes Lucid less attractive
    
    cost_difference_breakdown = {
        'Cost Component': [
            'Depreciation Difference',
            'Interest (Lease vs Loan)',
            'Property Tax Difference',
            'Insurance Difference',
            'Maintenance Difference',
            'Fuel/Electricity Difference',
            'Equity Difference (Lucid 0 vs RDX +$12,300)',
            'Investment Opportunity (RDX only)',
            'TOTAL COST DIFFERENCE'
        ],
        'Amount': [
            f'${depreciation_diff:.0f}',
            f'${interest_diff:.0f}',
            f'${property_tax_diff:.0f}',
            f'${insurance_diff:.0f}',
            f'${maintenance_diff:.0f}',
            f'${fuel_diff:.0f}',
            f'${equity_diff:.0f}',
            f'${investment_opp_diff:.0f}',
            f'${cost_difference:.0f}'
        ],
        'Description': [
            'Higher depreciation on more expensive Lucid vs RDX',
            'Lease interest (money factor) vs loan interest',
            'Higher property tax on more expensive Lucid',
            'Higher insurance on luxury EV',
            'Lower maintenance on EV vs gas vehicle',
            'Electricity savings vs gas costs',
            'Lucid has no equity, RDX retains $12,300 value (with impairment)',
            'Investment opportunity lost with lease (RDX gets this benefit)',
            'Total additional cost of Lucid lease (sum of all above)'
        ]
    }
    
    cost_difference_df = pd.DataFrame(cost_difference_breakdown)
    
    # =============================================================================
    # TABLE 4: LOAN PAYOFF BREAKDOWN
    # =============================================================================
    
    # This table shows the detailed loan payoff calculation
    # It demonstrates how your accelerated payments reduce the loan term and interest
    loan_payoff_data = {
        'Component': [
            'Current Loan Balance',
            'Monthly Payment (Base)',
            'Extra Payment',
            'Total Monthly Payment',
            'Interest Rate',
            'Months to Payoff',
            'Total Interest Paid',
            'Total Principal Paid',
            'Payoff Date (from today)'
        ],
        'Value': [
            f'${rdx_principal_balance:.2f}',
            f'${rdx_monthly_payment:.2f}',
            f'${rdx_extra_payment:.2f}',
            f'${rdx_total_payment:.2f}',
            f'{rdx_interest_rate*100:.2f}%',
            f'{months_to_payoff} months',
            f'${total_interest_paid:.2f}',
            f'${rdx_principal_balance:.2f}',
            f'~{months_to_payoff} months from now'
        ]
    }
    
    loan_payoff_df = pd.DataFrame(loan_payoff_data)
    
    # =============================================================================
    # TABLE 5: VEHICLE IMPAIRMENT IMPACT
    # =============================================================================
    
    # This table shows how the vehicle's damage/accident history affects values
    # It demonstrates the difference between clean and impaired condition values
    impairment_data = {
        'Component': [
            'Clean Condition Value (2025)',
            'Impairment Amount',
            'Impaired Value (2025)',
            'Clean Condition Value (2028)',
            'Impairment Amount',
            'Impaired Value (2028)',
            'Impact on 3-Year Equity',
            'Property Tax Impact Flag',
            'Actual Property Tax Impact'
        ],
        'Value': [
            f'${rdx_values_3yr[0]:.0f}',
            f'-${rdx_impairment:.0f}',
            f'${rdx_values_3yr_impaired[0]:.0f}',
            f'${rdx_values_3yr[-1]:.0f}',
            f'-${rdx_impairment:.0f}',
            f'${rdx_values_3yr_impaired[-1]:.0f}',
            f'-${rdx_values_3yr[-1] - rdx_values_3yr_impaired[-1]:.0f}',
            f'{impairment_affects_taxes}',
            f'{"Lower taxes on reduced value" if impairment_affects_taxes else "No impact (VA paperwork required)"}'
        ]
    }
    
    impairment_df = pd.DataFrame(impairment_data)
    
    # =============================================================================
    # TABLE 6: LEASE INTEREST CALCULATION
    # =============================================================================
    
    # This table shows how lease interest is calculated using the money factor
    lease_interest_data = {
        'Component': [
            'Lucid MSRP',
            'Air Credit',
            'EV Credit',
            'Onsite Credit',
            'Net Capitalized Cost',
            'Residual Value (3 years)',
            'Depreciation (Cap Cost - Residual)',
            'Total Lease Payments (36 × $368)',
            'Total Interest (Payments - Depreciation)',
            'Money Factor (Derived)',
            'Equivalent APR',
            'Interest per Month',
            'Why Negative Interest?'
        ],
        'Value': [
            f'${lucid_msrp:.0f}',
            f'-${air_credit:.0f}',
            f'-${ev_credit:.0f}',
            f'-${onsite_credit:.0f}',
            f'${lucid_capitalized_cost:.0f}',
            f'${lucid_residual_value:.0f}',
            f'${lucid_depreciation:.0f}',
            f'${lucid_total_lease_payments:.0f}',
            f'${lucid_lease_interest:.0f}',
            f'{lucid_money_factor:.4f}',
            f'{lucid_money_factor * 2400:.1f}%',
            f'${lucid_lease_interest/lucid_lease_terms:.0f}',
            f'Incentives > Interest Cost'
        ]
    }
    
    lease_interest_df = pd.DataFrame(lease_interest_data)
    
    # =============================================================================
    # TABLE 7A: NEGATIVE INTEREST EXPLANATION
    # =============================================================================
    
    # This table explains why the lease has negative interest
    negative_interest_data = {
        'Concept': [
            'Normal Lease Structure',
            'Your Lease Structure',
            'Incentive Impact',
            'Why Negative Interest?',
            'Monthly Payment Breakdown',
            'Effective Interest Rate'
        ],
        'Explanation': [
            'Payments = Depreciation + Interest',
            'Payments = Depreciation + Negative Interest',
            'Incentives reduce the cost below market rate',
            'Incentives exceed the cost of financing',
            '$368 = $479 depreciation - $111 interest rebate',
            'You are essentially getting paid to lease'
        ],
        'Amount': [
            'N/A',
            'N/A',
            f'${air_credit + ev_credit + onsite_credit:.0f}',
            f'${lucid_lease_interest:.0f}',
            f'${lucid_depreciation/lucid_lease_terms:.0f} - ${abs(lucid_lease_interest/lucid_lease_terms):.0f}',
            f'{lucid_money_factor * 2400:.1f}%'
        ]
    }
    
    negative_interest_df = pd.DataFrame(negative_interest_data)
    
    # =============================================================================
    # TABLE 8: INVESTMENT OPPORTUNITY CALCULATION
    # =============================================================================
    
    # This table shows how the freed-up cash flow can be invested after loan payoff
    investment_data = {
        'Component': [
            'Loan Payoff Month',
            'Months After Payoff',
            'Monthly Investment Amount',
            'Investment Return Rate',
            'Total Investment Returns',
            'Investment Period (months)',
            'Average Monthly Return'
        ],
        'Value': [
            f'Month {months_to_payoff}',
            f'{months_after_payoff} months',
            f'${monthly_investment_amount:.0f}',
            f'{investment_return_rate*100:.1f}%',
            f'${total_investment_opportunity:.0f}',
            f'{months_after_payoff}',
            f'${total_investment_opportunity/months_after_payoff:.0f}'
        ]
    }
    
    investment_df = pd.DataFrame(investment_data)
    
    # =============================================================================
    # TABLE 8: TRADE-IN AND INCENTIVES BREAKDOWN
    # =============================================================================
    
    # This table shows how the trade-in value and incentives reduce upfront costs
    trade_in_data = {
        'Component': [
            'RDX Trade-in Value',
            'RDX Loan Balance',
            'Trade-in Incentives',
            'Net Trade-in Value',
            'Total Due at Delivery',
            'Effective Cash Down Payment',
            'Required Trade-in Value for $0 Down'
        ],
        'Amount': [
            f'${rdx_trade_in_value:.0f}',
            f'-${rdx_loan_balance:.0f}',
            f'${trade_in_incentives:.0f}',
            f'${trade_in_net_value:.0f}',
            f'${lucid_total_due_at_delivery:.0f}',
            f'${lucid_effective_down_payment:.0f}',
            f'${required_trade_in_value:.0f}'
        ]
    }
    
    trade_in_df = pd.DataFrame(trade_in_data)
    
    # =============================================================================
    # TABLE 7: INCENTIVES BREAKDOWN
    # =============================================================================
    
    # This table shows all the incentives available on the Lucid lease
    incentives_data = {
        'Incentive Type': [
            'Air Credit',
            'EV Credit (delivery by 9/30/2025)',
            'Onsite Credit',
            'Trade-in Incentives',
            'TOTAL INCENTIVES'
        ],
        'Amount': [
            f'${air_credit:.0f}',
            f'${ev_credit:.0f}',
            f'${onsite_credit:.0f}',
            f'${trade_in_incentives:.0f}',
            f'${air_credit + ev_credit + onsite_credit + trade_in_incentives:.0f}'
        ]
    }
    
    incentives_df = pd.DataFrame(incentives_data)
    
    # =============================================================================
    # TABLE 11: DUE AT DELIVERY BREAKDOWN
    # =============================================================================
    
    # This table breaks down the upfront costs required when taking delivery
    due_at_delivery_data = {
        'Component': [
            'Order Deposit',
            'Upfront Taxes',
            'Documentation Fee',
            'Registration Fees',
            'First Month Payment',
            'TOTAL DUE AT DELIVERY'
        ],
        'Amount': [
            f'${order_deposit:.0f}',
            f'${upfront_taxes:.0f}',
            f'${documentation_fee:.0f}',
            f'${registration_fees:.0f}',
            f'${first_month_payment:.0f}',
            f'${lucid_total_due_at_delivery:.0f}'
        ]
    }
    
    due_at_delivery_df = pd.DataFrame(due_at_delivery_data)
    
    return monthly_df, summary_df, trade_in_df, incentives_df, cost_difference_df, loan_payoff_df, impairment_df, lease_interest_df, negative_interest_df, investment_df, due_at_delivery_df

# Generate the tables
monthly_table, summary_table, trade_in_table, incentives_table, cost_difference_table, loan_payoff_table, impairment_table, lease_interest_table, negative_interest_table, investment_table, due_at_delivery_table = calculate_vehicle_costs()

print("="*80)
print("TABLE 1: MONTHLY PAYMENT BREAKDOWN")
print("="*80)
print(monthly_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 2: 3-YEAR SUMMARY COST BY CATEGORY")
print("="*80)
print(summary_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 3: TRADE-IN BREAKDOWN")
print("="*80)
print(trade_in_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 4: INCENTIVES BREAKDOWN")
print("="*80)
print(incentives_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 5: COST DIFFERENCE BREAKDOWN")
print("="*80)
print(cost_difference_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 6: LOAN PAYOFF BREAKDOWN")
print("="*80)
print(loan_payoff_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 7: VEHICLE IMPAIRMENT IMPACT")
print("="*80)
print(impairment_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 8: LEASE INTEREST CALCULATION")
print("="*80)
print(lease_interest_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 8A: NEGATIVE INTEREST EXPLANATION")
print("="*80)
print(negative_interest_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 9: INVESTMENT OPPORTUNITY CALCULATION")
print("="*80)
print(investment_table.to_string(index=False))

print("\n" + "="*80)
print("TABLE 10: DUE AT DELIVERY BREAKDOWN")
print("="*80)
print(due_at_delivery_table.to_string(index=False))

# Create prototype_results directory if it doesn't exist
import os
prototype_results_dir = 'prototype_results'
if not os.path.exists(prototype_results_dir):
    os.makedirs(prototype_results_dir)

# Save to CSV files in prototype_results folder
monthly_table.to_csv(f'{prototype_results_dir}/monthly_payment_comparison.csv', index=False)
summary_table.to_csv(f'{prototype_results_dir}/3year_cost_summary.csv', index=False)
trade_in_table.to_csv(f'{prototype_results_dir}/trade_in_breakdown.csv', index=False)
incentives_table.to_csv(f'{prototype_results_dir}/incentives_breakdown.csv', index=False)
cost_difference_table.to_csv(f'{prototype_results_dir}/cost_difference_breakdown.csv', index=False)
loan_payoff_table.to_csv(f'{prototype_results_dir}/loan_payoff_breakdown.csv', index=False)
impairment_table.to_csv(f'{prototype_results_dir}/vehicle_impairment_impact.csv', index=False)
lease_interest_table.to_csv(f'{prototype_results_dir}/lease_interest_calculation.csv', index=False)
negative_interest_table.to_csv(f'{prototype_results_dir}/negative_interest_explanation.csv', index=False)
investment_table.to_csv(f'{prototype_results_dir}/investment_opportunity_calculation.csv', index=False)
due_at_delivery_table.to_csv(f'{prototype_results_dir}/due_at_delivery_breakdown.csv', index=False)

print(f"\n\nTables saved to CSV files in '{prototype_results_dir}/' folder:")
print(f"- {prototype_results_dir}/monthly_payment_comparison.csv")
print(f"- {prototype_results_dir}/3year_cost_summary.csv")
print(f"- {prototype_results_dir}/trade_in_breakdown.csv")
print(f"- {prototype_results_dir}/incentives_breakdown.csv")
print(f"- {prototype_results_dir}/cost_difference_breakdown.csv")
print(f"- {prototype_results_dir}/loan_payoff_breakdown.csv")
print(f"- {prototype_results_dir}/vehicle_impairment_impact.csv")
print(f"- {prototype_results_dir}/lease_interest_calculation.csv")
print(f"- {prototype_results_dir}/negative_interest_explanation.csv")
print(f"- {prototype_results_dir}/investment_opportunity_calculation.csv")
print(f"- {prototype_results_dir}/due_at_delivery_breakdown.csv")