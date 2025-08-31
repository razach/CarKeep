#!/usr/bin/env python3
"""
Example usage of the CarKeep vehicle cost comparison tool.
This demonstrates how to use the generalized system for different vehicle comparisons.
"""

from main import VehicleCostCalculator, VehicleConfig, LoanConfig, LeaseConfig, TradeInConfig


def example_comparison():
    """Example of comparing Acura RDX vs Lucid Air using prototype values."""
    
    # Initialize calculator for Virginia
    calculator = VehicleCostCalculator(state="VA")
    
    # Vehicle configurations (from prototype)
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
    
    # Loan configuration (from prototype)
    loan_config = LoanConfig(
        principal_balance=9909.95,
        monthly_payment=564.10,
        extra_payment=85.90,
        interest_rate=4.39 / 100
    )
    
    # Lease configuration (from prototype)
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
    
    # Trade-in configuration (from prototype)
    trade_in_config = TradeInConfig(
        trade_in_value=18000,
        loan_balance=9909.95,
        incentives=2000
    )
    
    # Run comparison
    results = calculator.run_comparison(
        rdx_config, lucid_config, loan_config, lease_config, trade_in_config
    )
    
    return results


def example_custom_costs():
    """Example with custom cost configurations for different state."""
    
    # Create calculator with custom cost configuration for Texas
    calculator = VehicleCostCalculator(state="TX")
    
    # Override default costs for specific vehicles (Texas rates)
    calculator.cost_config.insurance_monthly.update({
        "Acura RDX": 120,  # Higher insurance in TX
        "Lucid Air": 200   # Higher insurance in TX
    })
    
    calculator.cost_config.maintenance_monthly.update({
        "Acura RDX": 50,   # Slightly higher maintenance
        "Lucid Air": 35    # Slightly higher maintenance
    })
    
    calculator.cost_config.fuel_monthly.update({
        "Acura RDX": 150,  # Different fuel prices in TX
        "Lucid Air": 45    # Different electricity rates in TX
    })
    
    # Vehicle configurations (same as prototype but with different costs)
    rdx_config = VehicleConfig(
        name="Acura RDX",
        msrp=0,
        current_value=21000,
        values_3yr=[21000, 18900, 17000, 15300],
        impairment=3000,
        impairment_affects_taxes=False
    )
    
    lucid_config = VehicleConfig(
        name="Lucid Air",
        msrp=72800,
        current_value=0,
        values_3yr=[71400, 55100, 41500, 31059]
    )
    
    # Loan configuration (same as prototype)
    loan_config = LoanConfig(
        principal_balance=9909.95,
        monthly_payment=564.10,
        extra_payment=85.90,
        interest_rate=4.39 / 100
    )
    
    # Lease configuration (same as prototype)
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
    
    # Trade-in configuration (same as prototype)
    trade_in_config = TradeInConfig(
        trade_in_value=18000,
        loan_balance=9909.95,
        incentives=2000
    )
    
    # Run comparison
    results = calculator.run_comparison(
        rdx_config, lucid_config, loan_config, lease_config, trade_in_config
    )
    
    return results


if __name__ == "__main__":
    print("CarKeep Example Usage")
    print("=" * 50)
    
    # Run example comparison
    print("\n1. Basic Comparison (Acura RDX vs Lucid Air - VA)")
    print("-" * 50)
    results1 = example_comparison()
    
    for table_name, df in results1.items():
        print(f"\n{table_name.upper().replace('_', ' ')} TABLE")
        print(df.to_string(index=False))
    
    print("\n" + "=" * 50)
    print("2. Custom Cost Comparison (Acura RDX vs Lucid Air - TX)")
    print("-" * 50)
    results2 = example_custom_costs()
    
    for table_name, df in results2.items():
        print(f"\n{table_name.upper().replace('_', ' ')} TABLE")
        print(df.to_string(index=False))
    
    print("\nExample usage complete!")
    print("Both examples use the same vehicle configurations but different cost assumptions.")
    print("You can now easily create different vehicle comparisons by changing the configurations.")
