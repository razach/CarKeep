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
class DetailedCostAnalysis:
    """Detailed 3-year cost analysis for a scenario vs baseline"""
    scenario_name: str
    description: str
    vehicle_name: str
    
    # 3-Year Total Costs
    lease_loan_payment: float
    loan_interest: float
    down_payment: float
    property_tax: float
    insurance: float
    maintenance: float
    fuel_electricity: float
    subtotal: float
    
    # Equity and Investment
    equity_36mo: float
    investment_opportunity: float
    net_out_of_pocket: float
    
    # Monthly Evolution
    monthly_evolution: Dict[str, float]  # Current, After payoff, etc.


@dataclass
class CostAnalysis:
    """Complete cost analysis results"""
    baseline: CostBreakdown
    scenarios: List[CostBreakdown]
    detailed_analysis: List[DetailedCostAnalysis]
    summary: Dict[str, Any]


class CostAnalyzer:
    """Analyzes vehicle costs and prepares data for display"""
    
    def __init__(self):
        # Default monthly costs (can be made configurable later)
        self.default_insurance = 100
        self.default_maintenance = 50
        self.default_fuel = 150
        
        # Analysis period (36 months = 3 years)
        self.analysis_period = 36
    
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
        detailed_analysis = []
        
        for scenario_name, scenario_data in scenarios_data.get('scenarios', {}).items():
            # Basic monthly breakdown
            breakdown = self._analyze_scenario(scenario_name, scenario_data, baseline.total_monthly)
            scenarios.append(breakdown)
            
            # Detailed 3-year analysis
            detailed = self._analyze_detailed_costs(scenario_name, scenario_data, scenarios_data.get('baseline', {}))
            detailed_analysis.append(detailed)
        
        # Sort scenarios by total monthly cost (lowest first)
        scenarios.sort(key=lambda x: x.total_monthly)
        
        # Sort detailed analysis to match scenarios order
        detailed_analysis.sort(key=lambda x: scenarios.index(next(s for s in scenarios if s.scenario_name == x.scenario_name)))
        
        # Prepare summary
        summary = self._prepare_summary(baseline, scenarios, detailed_analysis)
        
        return CostAnalysis(
            baseline=baseline,
            scenarios=scenarios,
            detailed_analysis=detailed_analysis,
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
    
    def _analyze_detailed_costs(self, scenario_name: str, scenario_data: Dict[str, Any], baseline_data: Dict[str, Any]) -> DetailedCostAnalysis:
        """Analyze detailed 3-year costs for a scenario vs baseline"""
        description = scenario_data.get('description', 'New Vehicle')
        vehicle_name = scenario_data.get('scenario', {}).get('vehicle', {}).get('name', 'New Vehicle')
        
        # Get financing details
        financing = scenario_data.get('scenario', {}).get('financing', {})
        monthly_payment = financing.get('monthly_payment', 0)
        loan_term = financing.get('loan_term', 36)
        
        # Calculate 3-year totals
        lease_loan_payment = monthly_payment * min(loan_term, self.analysis_period)
        loan_interest = self._estimate_loan_interest(scenario_data, baseline_data)
        down_payment = 0  # Could be made configurable
        
        # Get cost overrides for 3-year totals
        cost_overrides = scenario_data.get('cost_overrides', {})
        insurance = self._get_cost_override(cost_overrides, 'insurance_monthly', vehicle_name, self.default_insurance) * self.analysis_period
        maintenance = self._get_cost_override(cost_overrides, 'maintenance_monthly', vehicle_name, self.default_maintenance) * self.analysis_period
        fuel_electricity = self._get_cost_override(cost_overrides, 'fuel_monthly', vehicle_name, self.default_fuel) * self.analysis_period
        
        # Property tax (simplified - could be enhanced with state tax logic)
        property_tax = self._estimate_property_tax(scenario_data, baseline_data)
        
        # Calculate subtotal
        subtotal = lease_loan_payment + loan_interest + down_payment + property_tax + insurance + maintenance + fuel_electricity
        
        # Equity analysis
        equity_36mo = self._estimate_equity_36mo(scenario_data, baseline_data)
        investment_opportunity = self._estimate_investment_opportunity(scenario_data, baseline_data)
        
        # Net out-of-pocket
        net_out_of_pocket = subtotal - equity_36mo + investment_opportunity
        
        # Monthly evolution
        monthly_evolution = self._calculate_monthly_evolution(scenario_data, baseline_data)
        
        return DetailedCostAnalysis(
            scenario_name=scenario_name,
            description=description,
            vehicle_name=vehicle_name,
            lease_loan_payment=lease_loan_payment,
            loan_interest=loan_interest,
            down_payment=down_payment,
            property_tax=property_tax,
            insurance=insurance,
            maintenance=maintenance,
            fuel_electricity=fuel_electricity,
            subtotal=subtotal,
            equity_36mo=equity_36mo,
            investment_opportunity=investment_opportunity,
            net_out_of_pocket=net_out_of_pocket,
            monthly_evolution=monthly_evolution
        )
    
    def _estimate_loan_interest(self, scenario_data: Dict[str, Any], baseline_data: Dict[str, Any]) -> float:
        """Estimate loan interest for 3 years"""
        # Simplified estimation - could be enhanced with actual loan calculations
        financing = scenario_data.get('scenario', {}).get('financing', {})
        if 'interest_rate' in financing:
            principal = financing.get('principal_balance', 0)
            rate = financing.get('interest_rate', 0.05)
            return principal * rate * (self.analysis_period / 12)
        return 0
    
    def _estimate_property_tax(self, scenario_data: Dict[str, Any], baseline_data: Dict[str, Any]) -> float:
        """Estimate property tax difference for 3 years"""
        # Simplified estimation - could be enhanced with state tax logic
        scenario_vehicle = scenario_data.get('scenario', {}).get('vehicle', {})
        baseline_vehicle = baseline_data.get('vehicle', {})
        
        scenario_msrp = scenario_vehicle.get('msrp', 0)
        baseline_value = baseline_vehicle.get('current_value', 0)
        
        # Assume 4% annual property tax rate (could be made configurable)
        annual_tax_rate = 0.04
        scenario_tax = scenario_msrp * annual_tax_rate * 3
        baseline_tax = baseline_value * annual_tax_rate * 3
        
        return scenario_tax - baseline_tax
    
    def _estimate_equity_36mo(self, scenario_data: Dict[str, Any], baseline_data: Dict[str, Any]) -> float:
        """Estimate equity at 36 months"""
        # Simplified estimation - could be enhanced with depreciation models
        scenario_vehicle = scenario_data.get('scenario', {}).get('vehicle', {})
        baseline_vehicle = baseline_data.get('vehicle', {})
        
        # Use 3-year values if available
        if 'values_3yr' in scenario_vehicle and len(scenario_vehicle['values_3yr']) > 3:
            scenario_equity = scenario_vehicle['values_3yr'][3]
        else:
            scenario_equity = scenario_vehicle.get('msrp', 0) * 0.6  # Assume 40% depreciation
        
        if 'values_3yr' in baseline_vehicle and len(baseline_vehicle['values_3yr']) > 3:
            baseline_equity = baseline_vehicle['values_3yr'][3]
        else:
            baseline_equity = baseline_vehicle.get('current_value', 0) * 0.7  # Assume 30% depreciation
        
        return scenario_equity - baseline_equity
    
    def _estimate_investment_opportunity(self, scenario_data: Dict[str, Any], baseline_data: Dict[str, Any]) -> float:
        """Estimate investment opportunity cost"""
        # Simplified estimation - assume 6% annual return on saved money
        # This represents the opportunity cost of spending money on a new vehicle
        annual_return = 0.06
        
        # Calculate how much more the new vehicle costs per year
        monthly_diff = scenario_data.get('scenario', {}).get('financing', {}).get('monthly_payment', 0)
        baseline_monthly = baseline_data.get('current_loan', {}).get('monthly_payment', 0)
        annual_diff = (monthly_diff - baseline_monthly) * 12
        
        # Investment opportunity is what you could earn on that money
        return annual_diff * annual_return * 3
    
    def _calculate_monthly_evolution(self, scenario_data: Dict[str, Any], baseline_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate how monthly costs evolve over time"""
        financing = scenario_data.get('scenario', {}).get('financing', {})
        monthly_payment = financing.get('monthly_payment', 0)
        
        # Get cost overrides
        cost_overrides = scenario_data.get('cost_overrides', {})
        vehicle_name = scenario_data.get('scenario', {}).get('vehicle', {}).get('name', 'New Vehicle')
        
        insurance = self._get_cost_override(cost_overrides, 'insurance_monthly', vehicle_name, self.default_insurance)
        maintenance = self._get_cost_override(cost_overrides, 'maintenance_monthly', vehicle_name, self.default_maintenance)
        fuel = self._get_cost_override(cost_overrides, 'fuel_monthly', vehicle_name, self.default_fuel)
        
        # Property tax (monthly)
        property_tax_monthly = self._estimate_property_tax(scenario_data, baseline_data) / self.analysis_period
        
        return {
            'payment': monthly_payment,
            'property_tax': property_tax_monthly,
            'insurance': insurance,
            'maintenance': maintenance,
            'fuel_electricity': fuel,
            'total': monthly_payment + property_tax_monthly + insurance + maintenance + fuel
        }
    
    def _get_cost_override(self, cost_overrides: Dict, cost_type: str, vehicle_name: str, default: float) -> float:
        """Get cost override for a specific vehicle and cost type"""
        if cost_type in cost_overrides and vehicle_name in cost_overrides[cost_type]:
            return cost_overrides[cost_type][vehicle_name]
        return default
    
    def _prepare_summary(self, baseline: CostBreakdown, scenarios: List[CostBreakdown], detailed_analysis: List[DetailedCostAnalysis]) -> Dict[str, Any]:
        """Prepare summary statistics"""
        if not scenarios:
            return {
                'lowest_monthly_cost': 0,
                'lowest_scenario_name': 'No alternatives',
                'monthly_savings': 0,
                'total_scenarios': 0,
                'best_net_cost': 0,
                'best_scenario_name': 'No alternatives'
            }
        
        # Find lowest monthly cost scenario
        lowest_scenario = min(scenarios, key=lambda x: x.total_monthly)
        
        # Find best net cost scenario (lowest net out-of-pocket)
        if detailed_analysis:
            best_net_scenario = min(detailed_analysis, key=lambda x: x.net_out_of_pocket)
            best_net_cost = best_net_scenario.net_out_of_pocket
            best_scenario_name = best_net_scenario.description
        else:
            best_net_cost = 0
            best_scenario_name = 'No alternatives'
        
        return {
            'lowest_monthly_cost': lowest_scenario.total_monthly,
            'lowest_scenario_name': lowest_scenario.description,
            'monthly_savings': baseline.total_monthly - lowest_scenario.total_monthly,
            'total_scenarios': len(scenarios),
            'best_net_cost': best_net_cost,
            'best_scenario_name': best_scenario_name
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
