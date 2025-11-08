import argparse

def calculate_monthly_payment(principal, annual_rate, years):
    """
    Calculates the monthly payment for a loan.
    """
    if annual_rate == 0:
        monthly_payment = principal / (years * 12)
    else:
        monthly_interest_rate = (annual_rate / 100) / 12
        number_of_payments = years * 12
        monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / ((1 + monthly_interest_rate) ** number_of_payments - 1)
    return monthly_payment

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate monthly loan payments.")
    parser.add_argument("--principal", type=float, required=True, help="The total loan amount.")
    parser.add_argument("--rate", type=float, required=True, help="The annual interest rate (e.g., 6.26 for 6.26%).")
    parser.add_argument("--years", type=int, required=True, help="The loan term in years.")
    args = parser.parse_args()

    monthly_payment = calculate_monthly_payment(args.principal, args.rate, args.years)
    print(f"{monthly_payment:.2f}")
