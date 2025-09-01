"""
CarKeep Core Module
Main entry point for core functionality
"""

from .calculators.vehicle_cost_calculator import (
    VehicleCostCalculator,
    StateTaxConfig,
    StateTaxRegistry
)

from .calculators.car_keep_runner import run_comparison_from_json
from .calculators.run_scenarios import list_scenarios, run_scenario

# Re-export main classes for backward compatibility
__all__ = [
    'VehicleCostCalculator',
    'StateTaxConfig', 
    'StateTaxRegistry',
    'run_comparison_from_json',
    'list_scenarios',
    'run_scenario'
]
