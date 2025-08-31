#!/usr/bin/env python3
"""
Main entry point for the CarKeep application.
Generalized vehicle cost comparison tool.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VehicleConfig:
    """Configuration for a vehicle in the comparison."""
    name: str
    msrp: float
    current_value: float
    values_3yr: List[float]
    impairment: float = 0
    impairment_affects_taxes: bool = False


@dataclass
class LoanConfig:
    """Configuration for loan terms."""
    principal_balance: float
    monthly_payment: float
    extra_payment: float
    interest_rate: float


@dataclass
class LeaseConfig:
    """Configuration for lease terms."""
    monthly_payment: float
    lease_terms: int
    msrp: float
    incentives: Dict[str, float]
    residual_value: Optional[float] = None


@dataclass
class TradeInConfig:
    """Configuration for trade-in terms."""
    trade_in_value: float
    loan_balance: float
    incentives: float


@dataclass
class CostConfig:
    """Configuration for various cost parameters."""
    property_tax_rate: float
    pptra_relief: float
    insurance_monthly: Dict[str, float]
    maintenance_monthly: Dict[str, float]
    fuel_monthly: Dict[str, float]
    investment_return_rate: float


class VehicleCostCalculator:
    """Main calculator class for vehicle cost comparisons."""
    
    def __init__(self, state: str = "VA"):
        self.state = state
        self.cost_config = self._get_default_cost_config()
    
    def _get_default_cost_config(self) -> CostConfig:
        """Get default cost configuration for VA."""
        return CostConfig(
            property_tax_rate=4.57 / 100,  # $4.57 per $100 of assessed value
            pptra_relief=0.51,  # 51% relief on first $20k
            insurance_monthly={"Acura RDX": 100, "Lucid Air": 176},
            maintenance_monthly={"Acura RDX": 47, "Lucid Air": 33},
            fuel_monthly={"Acura RDX": 167, "Lucid Air": 42},
            investment_return_rate=0.06
        )
    
    def calculate_property_tax(self, vehicle_value: float) -> float:
        """Calculate property tax for Fairfax County, VA."""
        pptra_amount = min(vehicle_value, 20000) * self.cost_config.property_tax_rate * self.cost_config.pptra_relief
        tax_first_20k = min(vehicle_value, 20000) * self.cost_config.property_tax_rate
        tax_over_20k = max(vehicle_value - 20000, 0) * self.cost_config.property_tax_rate
        return tax_first_20k + tax_over_20k - pptra_amount
    
    def calculate_loan_payoff(self, principal: float, monthly_payment: float, interest_rate: float, max_months: int = 36) -> Tuple[int, float, float]:
        """Calculate loan payoff with accelerated payments."""
        remaining_balance = principal
        total_interest = 0
        months = 0
        
        while remaining_balance > 0 and months < max_months:
            monthly_interest = remaining_balance * (interest_rate / 12)
            principal_payment = monthly_payment - monthly_interest
            
            if principal_payment > remaining_balance:
                principal_payment = remaining_balance
                monthly_interest = 0
            
            remaining_balance -= principal_payment
            total_interest += monthly_interest
            months += 1
        
        return months, total_interest, remaining_balance
    
    def calculate_lease_components(self, lease_config: LeaseConfig) -> Dict[str, float]:
        """Calculate lease components from monthly payment."""
        capitalized_cost = lease_config.msrp - sum(lease_config.incentives.values())
        total_lease_payments = lease_config.monthly_payment * lease_config.lease_terms
        
        # Derive residual value from monthly payment
        residual_value = lease_config.msrp * 0.60  # Initial guess
        
        for iteration in range(10):
            depreciation = capitalized_cost - residual_value
            lease_interest = total_lease_payments - depreciation
            money_factor = lease_interest / ((capitalized_cost + residual_value) * lease_config.lease_terms)
            calculated_monthly = (depreciation / lease_config.lease_terms) + ((capitalized_cost + residual_value) * money_factor / 2)
            
            if abs(calculated_monthly - lease_config.monthly_payment) < 1:
                break
                
            if calculated_monthly > lease_config.monthly_payment:
                residual_value += 100
            else:
                residual_value -= 100
        
        depreciation = capitalized_cost - residual_value
        lease_interest = total_lease_payments - depreciation
        money_factor = lease_interest / ((capitalized_cost + residual_value) * lease_config.lease_terms)
        
        return {
            'capitalized_cost': capitalized_cost,
            'residual_value': residual_value,
            'depreciation': depreciation,
            'lease_interest': lease_interest,
            'money_factor': money_factor,
            'total_payments': total_lease_payments
        }
    
    def calculate_investment_opportunity(self, months_to_payoff: int, monthly_payment: float, 
                                       investment_rate: float, total_period: int = 36) -> float:
        """Calculate investment opportunity after loan payoff."""
        months_after_payoff = total_period - months_to_payoff
        total_opportunity = 0
        
        for month in range(months_after_payoff):
            months_invested = months_after_payoff - month
            monthly_return = monthly_payment * (investment_rate / 12) * months_invested
            total_opportunity += monthly_return
        
        return total_opportunity
    
    def create_monthly_payment_table(self, vehicle1_config: VehicleConfig, vehicle2_config: VehicleConfig,
                                   loan_config: LoanConfig, lease_config: LeaseConfig) -> pd.DataFrame:
        """Create monthly payment breakdown table."""
        # Calculate loan payoff
        months_to_payoff, _, _ = self.calculate_loan_payoff(
            loan_config.principal_balance, 
            loan_config.monthly_payment + loan_config.extra_payment, 
            loan_config.interest_rate
        )
        
        # Calculate property taxes
        vehicle1_taxes = [self.calculate_property_tax(val) for val in vehicle1_config.values_3yr]
        vehicle2_taxes = [self.calculate_property_tax(val) for val in vehicle2_config.values_3yr]
        
        vehicle1_avg_monthly_tax = sum(vehicle1_taxes[1:]) / 36
        vehicle2_avg_monthly_tax = sum(vehicle2_taxes[1:]) / 36
        
        monthly_data = {
            'Category': ['Payment', 'Property Tax', 'Insurance', 'Maintenance', 'Fuel/Electricity', 'TOTAL MONTHLY'],
            f'{vehicle2_config.name} Lease (36 mo)': [
                f'${lease_config.monthly_payment}',
                f'${vehicle2_avg_monthly_tax:.0f}',
                f'${self.cost_config.insurance_monthly.get(vehicle2_config.name, 0)}',
                f'${self.cost_config.maintenance_monthly.get(vehicle2_config.name, 0)}',
                f'${self.cost_config.fuel_monthly.get(vehicle2_config.name, 0)}',
                f'${lease_config.monthly_payment + vehicle2_avg_monthly_tax + self.cost_config.insurance_monthly.get(vehicle2_config.name, 0) + self.cost_config.maintenance_monthly.get(vehicle2_config.name, 0) + self.cost_config.fuel_monthly.get(vehicle2_config.name, 0):.0f}'
            ],
            f'{vehicle1_config.name} Loan ({months_to_payoff} mo)': [
                f'${loan_config.monthly_payment + loan_config.extra_payment:.0f}',
                f'${vehicle1_avg_monthly_tax:.0f}',
                f'${self.cost_config.insurance_monthly.get(vehicle1_config.name, 0)}',
                f'${self.cost_config.maintenance_monthly.get(vehicle1_config.name, 0)}',
                f'${self.cost_config.fuel_monthly.get(vehicle1_config.name, 0)}',
                f'${loan_config.monthly_payment + loan_config.extra_payment + vehicle1_avg_monthly_tax + self.cost_config.insurance_monthly.get(vehicle1_config.name, 0) + self.cost_config.maintenance_monthly.get(vehicle1_config.name, 0) + self.cost_config.fuel_monthly.get(vehicle1_config.name, 0):.0f}'
            ],
            f'{vehicle1_config.name} (after payoff)': [
                '$0',
                f'${vehicle1_avg_monthly_tax:.0f}',
                f'${self.cost_config.insurance_monthly.get(vehicle1_config.name, 0)}',
                f'${self.cost_config.maintenance_monthly.get(vehicle1_config.name, 0)}',
                f'${self.cost_config.fuel_monthly.get(vehicle1_config.name, 0)}',
                f'${vehicle1_avg_monthly_tax + self.cost_config.insurance_monthly.get(vehicle1_config.name, 0) + self.cost_config.maintenance_monthly.get(vehicle1_config.name, 0) + self.cost_config.fuel_monthly.get(vehicle1_config.name, 0):.0f}'
            ]
        }
        
        return pd.DataFrame(monthly_data)
    
    def create_summary_table(self, vehicle1_config: VehicleConfig, vehicle2_config: VehicleConfig,
                           loan_config: LoanConfig, lease_config: LeaseConfig, 
                           trade_in_config: TradeInConfig) -> pd.DataFrame:
        """Create 3-year summary cost table."""
        # Calculate loan payoff
        months_to_payoff, total_interest_paid, _ = self.calculate_loan_payoff(
            loan_config.principal_balance, 
            loan_config.monthly_payment + loan_config.extra_payment, 
            loan_config.interest_rate
        )
        
        # Calculate investment opportunity
        investment_opportunity = self.calculate_investment_opportunity(
            months_to_payoff, 
            loan_config.monthly_payment + loan_config.extra_payment, 
            self.cost_config.investment_return_rate
        )
        
        # Calculate lease components
        lease_components = self.calculate_lease_components(lease_config)
        
        # Calculate property taxes
        vehicle1_taxes = [self.calculate_property_tax(val) for val in vehicle1_config.values_3yr]
        vehicle2_taxes = [self.calculate_property_tax(val) for val in vehicle2_config.values_3yr]
        
        vehicle1_property_tax_total = sum(vehicle1_taxes[1:])
        vehicle2_property_tax_total = sum(vehicle2_taxes[1:])
        
        # Calculate 3-year totals
        vehicle1_loan_payments = loan_config.principal_balance + total_interest_paid
        vehicle1_insurance_total = self.cost_config.insurance_monthly.get(vehicle1_config.name, 0) * 36
        vehicle1_maintenance_total = self.cost_config.maintenance_monthly.get(vehicle1_config.name, 0) * 36
        vehicle1_fuel_total = self.cost_config.fuel_monthly.get(vehicle1_config.name, 0) * 36
        vehicle1_equity_end = vehicle1_config.values_3yr[-1] - vehicle1_config.impairment
        
        vehicle2_lease_payments = lease_config.monthly_payment * lease_config.lease_terms
        vehicle2_insurance_total = self.cost_config.insurance_monthly.get(vehicle2_config.name, 0) * 36
        vehicle2_maintenance_total = self.cost_config.maintenance_monthly.get(vehicle2_config.name, 0) * 36
        vehicle2_fuel_total = self.cost_config.fuel_monthly.get(vehicle2_config.name, 0) * 36
        
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
            f'{vehicle1_config.name} (Keep Current Car)': [
                f'${vehicle1_loan_payments:.0f}',
                f'${total_interest_paid:.0f}',
                '$0',
                f'${vehicle1_property_tax_total:.0f}',
                f'${vehicle1_insurance_total:.0f}',
                f'${vehicle1_maintenance_total:.0f}',
                f'${vehicle1_fuel_total:.0f}',
                f'${vehicle1_loan_payments + vehicle1_property_tax_total + vehicle1_insurance_total + vehicle1_maintenance_total + vehicle1_fuel_total:.0f}',
                f'-${vehicle1_equity_end:.0f}',
                f'${investment_opportunity:.0f}',
                f'${vehicle1_loan_payments + vehicle1_property_tax_total + vehicle1_insurance_total + vehicle1_maintenance_total + vehicle1_fuel_total - vehicle1_equity_end - investment_opportunity:.0f}'
            ],
            f'{vehicle2_config.name} (Lease)': [
                f'${vehicle2_lease_payments:.0f}',
                f'${lease_components["lease_interest"]:.0f}',
                '$0',
                f'${vehicle2_property_tax_total:.0f}',
                f'${vehicle2_insurance_total:.0f}',
                f'${vehicle2_maintenance_total:.0f}',
                f'${vehicle2_fuel_total:.0f}',
                f'${vehicle2_lease_payments + lease_components["lease_interest"] + vehicle2_property_tax_total + vehicle2_insurance_total + vehicle2_maintenance_total + vehicle2_fuel_total:.0f}',
                '$0',
                '$0',
                f'${vehicle2_lease_payments + lease_components["lease_interest"] + vehicle2_property_tax_total + vehicle2_insurance_total + vehicle2_maintenance_total + vehicle2_fuel_total:.0f}'
            ]
        }
        
        return pd.DataFrame(summary_data)
    
    def create_cost_difference_table(self, vehicle1_config: VehicleConfig, vehicle2_config: VehicleConfig,
                                   loan_config: LoanConfig, lease_config: LeaseConfig) -> pd.DataFrame:
        """Create cost difference breakdown table."""
        # Calculate loan payoff
        months_to_payoff, total_interest_paid, _ = self.calculate_loan_payoff(
            loan_config.principal_balance, 
            loan_config.monthly_payment + loan_config.extra_payment, 
            loan_config.interest_rate
        )
        
        # Calculate investment opportunity
        investment_opportunity = self.calculate_investment_opportunity(
            months_to_payoff, 
            loan_config.monthly_payment + loan_config.extra_payment, 
            self.cost_config.investment_return_rate
        )
        
        # Calculate lease components
        lease_components = self.calculate_lease_components(lease_config)
        
        # Calculate property taxes
        vehicle1_taxes = [self.calculate_property_tax(val) for val in vehicle1_config.values_3yr]
        vehicle2_taxes = [self.calculate_property_tax(val) for val in vehicle2_config.values_3yr]
        
        vehicle1_property_tax_total = sum(vehicle1_taxes[1:])
        vehicle2_property_tax_total = sum(vehicle2_taxes[1:])
        
        # Calculate differences
        depreciation_diff = lease_components['depreciation'] - (vehicle1_config.current_value - (vehicle1_config.values_3yr[-1] - vehicle1_config.impairment))
        interest_diff = lease_components['lease_interest'] - total_interest_paid
        property_tax_diff = vehicle2_property_tax_total - vehicle1_property_tax_total
        insurance_diff = (self.cost_config.insurance_monthly.get(vehicle2_config.name, 0) - self.cost_config.insurance_monthly.get(vehicle1_config.name, 0)) * 36
        maintenance_diff = (self.cost_config.maintenance_monthly.get(vehicle2_config.name, 0) - self.cost_config.maintenance_monthly.get(vehicle1_config.name, 0)) * 36
        fuel_diff = (self.cost_config.fuel_monthly.get(vehicle2_config.name, 0) - self.cost_config.fuel_monthly.get(vehicle1_config.name, 0)) * 36
        equity_diff = 0 - (vehicle1_config.values_3yr[-1] - vehicle1_config.impairment)
        investment_opp_diff = 0 - investment_opportunity
        
        # Calculate 3-year totals for cost difference calculation
        vehicle1_loan_payments = loan_config.principal_balance + total_interest_paid
        vehicle1_insurance_total = self.cost_config.insurance_monthly.get(vehicle1_config.name, 0) * 36
        vehicle1_maintenance_total = self.cost_config.maintenance_monthly.get(vehicle1_config.name, 0) * 36
        vehicle1_fuel_total = self.cost_config.fuel_monthly.get(vehicle1_config.name, 0) * 36
        vehicle1_equity_end = vehicle1_config.values_3yr[-1] - vehicle1_config.impairment
        
        vehicle2_lease_payments = lease_config.monthly_payment * lease_config.lease_terms
        vehicle2_insurance_total = self.cost_config.insurance_monthly.get(vehicle2_config.name, 0) * 36
        vehicle2_maintenance_total = self.cost_config.maintenance_monthly.get(vehicle2_config.name, 0) * 36
        vehicle2_fuel_total = self.cost_config.fuel_monthly.get(vehicle2_config.name, 0) * 36
        
        # Calculate total costs the same way as prototype
        vehicle1_total_cost = vehicle1_loan_payments + vehicle1_property_tax_total + vehicle1_insurance_total + vehicle1_maintenance_total + vehicle1_fuel_total - vehicle1_equity_end - investment_opportunity
        vehicle2_total_cost = vehicle2_lease_payments + lease_components["lease_interest"] + vehicle2_property_tax_total + vehicle2_insurance_total + vehicle2_maintenance_total + vehicle2_fuel_total
        total_cost_difference = vehicle2_total_cost - vehicle1_total_cost
        
        cost_difference_data = {
            'Cost Component': [
                'Depreciation Difference',
                'Interest (Lease vs Loan)',
                'Property Tax Difference',
                'Insurance Difference',
                'Maintenance Difference',
                'Fuel/Electricity Difference',
                f'Equity Difference ({vehicle2_config.name} 0 vs {vehicle1_config.name} +${vehicle1_config.values_3yr[-1] - vehicle1_config.impairment:.0f})',
                'Investment Opportunity (Keep car only)',
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
                f'${total_cost_difference:.0f}'
            ],
            'Description': [
                f'Higher depreciation on more expensive {vehicle2_config.name} vs {vehicle1_config.name}',
                'Lease interest (money factor) vs loan interest',
                f'Higher property tax on more expensive {vehicle2_config.name}',
                f'Higher insurance on luxury EV',
                'Lower maintenance on EV vs gas vehicle',
                'Electricity savings vs gas costs',
                f'{vehicle2_config.name} has no equity, {vehicle1_config.name} retains ${vehicle1_config.values_3yr[-1] - vehicle1_config.impairment:.0f} value',
                'Investment opportunity lost with lease (Keep car gets this benefit)',
                'Total additional cost of lease (sum of all above)'
            ]
        }
        
        return pd.DataFrame(cost_difference_data)
    
    def run_comparison(self, vehicle1_config: VehicleConfig, vehicle2_config: VehicleConfig,
                      loan_config: LoanConfig, lease_config: LeaseConfig, 
                      trade_in_config: TradeInConfig) -> Dict[str, pd.DataFrame]:
        """Run the complete vehicle cost comparison."""
        results = {}
        
        # Generate all tables
        results['monthly_payment'] = self.create_monthly_payment_table(
            vehicle1_config, vehicle2_config, loan_config, lease_config
        )
        
        results['summary'] = self.create_summary_table(
            vehicle1_config, vehicle2_config, loan_config, lease_config, trade_in_config
        )
        
        results['cost_difference'] = self.create_cost_difference_table(
            vehicle1_config, vehicle2_config, loan_config, lease_config
        )
        
        return results


def create_sample_comparison() -> Dict[str, pd.DataFrame]:
    """Create a sample comparison using the original prototype data."""
    calculator = VehicleCostCalculator(state="VA")
    
    # Vehicle configurations
    rdx_config = VehicleConfig(
        name="Acura RDX",
        msrp=0,  # Not used for current vehicle
        current_value=21000,
        values_3yr=[21000, 18900, 17000, 15300],
        impairment=3000,
        impairment_affects_taxes=False
    )
    
    lucid_config = VehicleConfig(
        name="Lucid Air",
        msrp=72800,
        current_value=0,  # Not used for lease
        values_3yr=[71400, 55100, 41500, 31059]
    )
    
    # Loan configuration
    loan_config = LoanConfig(
        principal_balance=9909.95,
        monthly_payment=564.10,
        extra_payment=85.90,
        interest_rate=4.39 / 100
    )
    
    # Lease configuration
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
    
    # Trade-in configuration
    trade_in_config = TradeInConfig(
        trade_in_value=18000,
        loan_balance=9909.95,
        incentives=2000
    )
    
    return calculator.run_comparison(rdx_config, lucid_config, loan_config, lease_config, trade_in_config)


def main():
    """Main function that runs when the script is executed."""
    print("CarKeep Vehicle Cost Comparison Tool")
    print("=" * 50)
    
    # Run sample comparison
    results = create_sample_comparison()
    
    # Display results
    for table_name, df in results.items():
        print(f"\n{table_name.upper().replace('_', ' ')} TABLE")
        print("=" * 50)
        print(df.to_string(index=False))
        print()
    
    # Save to CSV files
    for table_name, df in results.items():
        filename = f"{table_name}_comparison.csv"
        df.to_csv(filename, index=False)
        print(f"Saved {filename}")
    
    print("\nAnalysis complete! CSV files have been generated for further processing and visualization.")


if __name__ == "__main__":
    main()
