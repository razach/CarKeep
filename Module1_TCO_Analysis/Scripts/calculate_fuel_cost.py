"""
calculate_fuel_cost.py
Standalone fuel cost comparison: gas vehicle vs. EV.
Reads inputs from scenarios/fuel_inputs.json and prints a JSON result.

Usage:
    python3 Scripts/calculate_fuel_cost.py
    python3 Scripts/calculate_fuel_cost.py --miles 10000
"""

import argparse
import json
import os
from datetime import date, datetime


def load_inputs(inputs_path: str) -> dict:
    with open(inputs_path, "r") as f:
        return json.load(f)


def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def calculate_mileage_summary(readings: list) -> dict:
    """Compute miles/year stats from a list of {date, miles} odometer readings."""
    sorted_readings = sorted(readings, key=lambda r: r["date"])
    periods = []
    for i in range(1, len(sorted_readings)):
        start = sorted_readings[i - 1]
        end = sorted_readings[i]
        start_date = parse_date(start["date"])
        end_date = parse_date(end["date"])
        days = (end_date - start_date).days
        miles = end["miles"] - start["miles"]
        annualized = round(miles / days * 365) if days > 0 else 0
        periods.append({
            "from": start["date"],
            "to": end["date"],
            "miles_driven": miles,
            "days": days,
            "annualized_miles_per_year": annualized,
        })

    # Full span
    first = sorted_readings[0]
    last = sorted_readings[-1]
    total_days = (parse_date(last["date"]) - parse_date(first["date"])).days
    total_miles = last["miles"] - first["miles"]
    overall_annual = round(total_miles / total_days * 365) if total_days > 0 else 0

    return {
        "periods": periods,
        "overall_annualized_miles_per_year": overall_annual,
        "total_miles_driven": total_miles,
        "tracking_start": first["date"],
        "tracking_end": last["date"],
        "current_odometer": last["miles"],
    }


def calculate_fuel_costs(inputs: dict, annual_miles: int) -> dict:
    elec = inputs["electricity"]
    odom = inputs["odometer"]
    gas_v = inputs["gas_vehicle"]
    ev_v = inputs["ev_vehicle"]

    # --- Electricity rate ---
    rate_per_kwh = elec["rate_per_kwh"]

    # Blended charging rate: mix of home and public DC fast charge
    blended_rate = (
        ev_v["home_charging_fraction"] * rate_per_kwh
        + (1 - ev_v["home_charging_fraction"]) * ev_v["public_charging_rate_per_kwh"]
    )

    # --- Gas vehicle ---
    gallons_per_year = annual_miles / gas_v["mpg_combined"]
    rdx_annual_cost = gallons_per_year * gas_v["gas_price_per_gallon"]

    # --- EV ---
    kwh_per_year = annual_miles * ev_v["kwh_per_mile_epa"]
    ev_annual_cost = kwh_per_year * blended_rate

    # --- Savings ---
    annual_savings = rdx_annual_cost - ev_annual_cost
    savings_pct = (annual_savings / rdx_annual_cost * 100) if rdx_annual_cost > 0 else 0

    # --- Cost per mile ---
    rdx_cost_per_mile = rdx_annual_cost / annual_miles if annual_miles > 0 else 0
    ev_cost_per_mile = ev_annual_cost / annual_miles if annual_miles > 0 else 0

    # --- Mileage summary ---
    mileage_summary = calculate_mileage_summary(odom["readings"])

    return {
        "inputs_used": {
            "annual_miles": annual_miles,
            "electricity_rate_per_kwh": round(rate_per_kwh, 4),
            "blended_ev_charging_rate_per_kwh": round(blended_rate, 4),
            "gas_price_per_gallon": gas_v["gas_price_per_gallon"],
            "gas_price_source": gas_v.get("gas_price_source", ""),
            "rdx_mpg_combined": gas_v["mpg_combined"],
            "ev_kwh_per_mile_epa": ev_v["kwh_per_mile_epa"],
        },
        "gas_vehicle": {
            "name": gas_v["name"],
            "gallons_per_year": round(gallons_per_year, 1),
            "annual_cost": round(rdx_annual_cost, 2),
            "monthly_cost": round(rdx_annual_cost / 12, 2),
            "cost_per_mile": round(rdx_cost_per_mile, 4),
        },
        "ev_vehicle": {
            "name": ev_v["name"],
            "kwh_per_year": round(kwh_per_year, 1),
            "annual_cost": round(ev_annual_cost, 2),
            "monthly_cost": round(ev_annual_cost / 12, 2),
            "cost_per_mile": round(ev_cost_per_mile, 4),
        },
        "comparison": {
            "annual_savings": round(annual_savings, 2),
            "monthly_savings": round(annual_savings / 12, 2),
            "ev_fuel_cost_reduction_pct": round(savings_pct, 1),
        },
        "mileage_summary": mileage_summary,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate annual fuel cost: gas vehicle vs. EV."
    )
    parser.add_argument(
        "--miles",
        type=int,
        default=None,
        help="Override annual miles (default: uses projected_annual_miles from fuel_inputs.json)",
    )
    parser.add_argument(
        "--inputs",
        type=str,
        default=None,
        help="Path to fuel_inputs.json (default: auto-detected relative to this script)",
    )
    args = parser.parse_args()

    # Locate inputs file relative to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    default_inputs_path = os.path.join(project_root, "scenarios", "fuel_inputs.json")
    inputs_path = args.inputs if args.inputs else default_inputs_path

    inputs = load_inputs(inputs_path)

    annual_miles = args.miles if args.miles is not None else inputs["odometer"]["projected_annual_miles"]

    result = calculate_fuel_costs(inputs, annual_miles)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
