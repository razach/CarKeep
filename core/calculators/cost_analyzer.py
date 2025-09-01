#!/usr/bin/env python3
"""
CarKeep Cost Analyzer
Core module for analyzing vehicle costs and preparing data for display
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class CostBreakdown:
    """Structured cost breakdown for a scenario"""
    scenario_name: str
    description: str
    vehicle_name: str
    monthly_payment: float
    insurance_monthly: float
    maintenance_monthly: float
    fuel_monthly: float
    total_monthly: float
    vs_baseline: float  # Positive = cost increase, Negative = savings


@dataclass
class CostAnalysis:
    """Complete cost analysis results"""
    baseline: CostBreakdown
    scenarios: List[CostBreakdown]
    summary: Dict[str, Any]


class CostAnalyzer:
    """Analyzes vehicle costs and prepares data for display"""
    
    def __init__(self):
        # Default monthly costs (can be made configurable later)
        self.default_insurance = 100
        self.default_maintenance = 50
        self.default_fuel = 150
    
    def analyze_scenarios(self, scenarios_data: Dict[str, Any]) -> CostAnalysis:
        """
        Analyze all scenarios and prepare structured cost data
        
        Args:
            scenarios_data: Data from list_scenarios() function
            
        Returns:
            CostAnalysis object with structured data
        """
        if not scenarios_data:
            raise ValueError("No scenarios data provided")
        
        # Analyze baseline
        baseline = self._analyze_baseline(scenarios_data.get('baseline', {}))
        
        # Analyze alternative scenarios
        scenarios = []
        for scenario_name, scenario_data in scenarios_data.get('scenarios', {}).items():
            breakdown = self._analyze_scenario(scenario_name, scenario_data, baseline.total_monthly)
            scenarios.append(breakdown)
        
        # Sort scenarios by total monthly cost (lowest first)
        scenarios.sort(key=lambda x: x.total_monthly)
        
        # Prepare summary
        summary = self._prepare_summary(baseline, scenarios)
        
        return CostAnalysis(
            baseline=baseline,
            scenarios=scenarios,
            summary=summary
        )
    
    def _analyze_baseline(self, baseline_data: Dict[str, Any]) -> CostBreakdown:
        """Analyze baseline scenario costs"""
        vehicle_name = baseline_data.get('vehicle', {}).get('name', 'Current Vehicle')
        monthly_payment = baseline_data.get('current_loan', {}).get('monthly_payment', 0) or 0
        
        # For baseline, use default costs (could be made configurable)
        insurance_monthly = self.default_insurance
        maintenance_monthly = self.default_maintenance
        fuel_monthly = self.default_fuel
        
        total_monthly = monthly_payment + insurance_monthly + maintenance_monthly + fuel_monthly
        
        return CostBreakdown(
            scenario_name="baseline",
            description=baseline_data.get('description', 'Keep current vehicle'),
            vehicle_name=vehicle_name,
            monthly_payment=monthly_payment,
            insurance_monthly=insurance_monthly,
            maintenance_monthly=maintenance_monthly,
            fuel_monthly=fuel_monthly,
            total_monthly=total_monthly,
            vs_baseline=0  # Baseline has no difference from itself
        )
    
    def _analyze_scenario(self, scenario_name: str, scenario_data: Dict[str, Any], baseline_total: float) -> CostBreakdown:
        """Analyze a single alternative scenario"""
        description = scenario_data.get('description', 'New Vehicle')
        vehicle_name = scenario_data.get('scenario', {}).get('vehicle', {}).get('name', 'New Vehicle')
        monthly_payment = scenario_data.get('scenario', {}).get('financing', {}).get('monthly_payment', 0)
        
        # Get cost overrides if they exist, otherwise use defaults
        cost_overrides = scenario_data.get('cost_overrides', {})
        
        insurance_monthly = self._get_cost_override(
            cost_overrides, 'insurance_monthly', vehicle_name, self.default_insurance
        )
        maintenance_monthly = self._get_cost_override(
            cost_overrides, 'maintenance_monthly', vehicle_name, self.default_maintenance
        )
        fuel_monthly = self._get_cost_override(
            cost_overrides, 'fuel_monthly', vehicle_name, self.default_fuel
        )
        
        total_monthly = monthly_payment + insurance_monthly + maintenance_monthly + fuel_monthly
        vs_baseline = total_monthly - baseline_total
        
        return CostBreakdown(
            scenario_name=scenario_name,
            description=description,
            vehicle_name=vehicle_name,
            monthly_payment=monthly_payment,
            insurance_monthly=insurance_monthly,
            maintenance_monthly=maintenance_monthly,
            fuel_monthly=fuel_monthly,
            total_monthly=total_monthly,
            vs_baseline=vs_baseline
        )
    
    def _get_cost_override(self, cost_overrides: Dict, cost_type: str, vehicle_name: str, default: float) -> float:
        """Get cost override for a specific vehicle and cost type"""
        if cost_type in cost_overrides and vehicle_name in cost_overrides[cost_type]:
            return cost_overrides[cost_type][vehicle_name]
        return default
    
    def _prepare_summary(self, baseline: CostBreakdown, scenarios: List[CostBreakdown]) -> Dict[str, Any]:
        """Prepare summary statistics"""
        if not scenarios:
            return {
                'lowest_monthly_cost': 0,
                'lowest_scenario_name': 'No alternatives',
                'monthly_savings': 0,
                'total_scenarios': 0
            }
        
        # Find lowest cost scenario
        lowest_scenario = min(scenarios, key=lambda x: x.total_monthly)
        
        return {
            'lowest_monthly_cost': lowest_scenario.total_monthly,
            'lowest_scenario_name': lowest_scenario.description,
            'monthly_savings': baseline.total_monthly - lowest_scenario.total_monthly,
            'total_scenarios': len(scenarios)
        }


def analyze_scenarios_from_data(scenarios_data: Dict[str, Any]) -> CostAnalysis:
    """
    Convenience function to analyze scenarios from data
    
    Args:
        scenarios_data: Data from list_scenarios() function
        
    Returns:
        CostAnalysis object
    """
    analyzer = CostAnalyzer()
    return analyzer.analyze_scenarios(scenarios_data)
