import argparse
import json

def calculate_depreciation_schedule(start_value, percentages):
    """
    Calculates a depreciation schedule.
    """
    values = [start_value]
    current_value = start_value
    for p in percentages:
        current_value *= (1 - (p / 100))
        values.append(round(current_value))
    return values

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate a 3-year depreciation schedule.")
    parser.add_argument("--value", type=float, required=True, help="The starting value of the vehicle.")
    parser.add_argument("--percentages", type=float, nargs=3, required=True, help="Three annual depreciation percentages (e.g., 20 12 8).")
    args = parser.parse_args()

    schedule = calculate_depreciation_schedule(args.value, args.percentages)
    print(json.dumps(schedule))
