"""
Advanced Financial Modeling Module for NXTRIX CRM
Provides sophisticated financial analysis including:
- 10-year cash flow projections
- Monte Carlo simulations
- Sensitivity analysis
- Exit strategy comparisons
- Advanced financial metrics (IRR, NPV)
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import random

class AdvancedFinancialModeling:
    def __init__(self):
        self.scenarios = ['Conservative', 'Base Case', 'Optimistic']
        self.projection_years = 10
        
    def generate_cash_flow_projections(self, deal_data: Dict) -> Dict:
        """Generate detailed 10-year cash flow projections with multiple scenarios"""
        
        # Extract deal parameters
        purchase_price = deal_data.get('purchase_price', 0)
        monthly_rent = deal_data.get('monthly_rent', 0)
        annual_expenses = self._calculate_annual_expenses(deal_data)
        
        projections = {}
        
        for scenario in self.scenarios:
            # Scenario multipliers
            multipliers = {
                'Conservative': {'rent_growth': 0.02, 'expense_growth': 0.04, 'vacancy': 0.08},
                'Base Case': {'rent_growth': 0.03, 'expense_growth': 0.03, 'vacancy': 0.05},
                'Optimistic': {'rent_growth': 0.05, 'expense_growth': 0.025, 'vacancy': 0.03}
            }
            
            scenario_data = []
            current_rent = monthly_rent * 12
            current_expenses = annual_expenses
            
            for year in range(1, self.projection_years + 1):
                # Apply growth rates
                annual_rent = current_rent * (1 - multipliers[scenario]['vacancy'])
                net_operating_income = annual_rent - current_expenses
                
                # Calculate debt service (assuming 80% LTV, 6% rate, 30-year amortization)
                loan_amount = purchase_price * 0.8
                annual_debt_service = loan_amount * 0.072  # Simplified calculation
                
                cash_flow = net_operating_income - annual_debt_service
                
                # Calculate cumulative metrics
                property_value = purchase_price * (1.03 ** year)  # 3% appreciation
                loan_balance = loan_amount * ((1.06 ** 30) - (1.06 ** year)) / ((1.06 ** 30) - 1)
                equity = property_value - loan_balance
                
                scenario_data.append({
                    'year': year,
                    'gross_rent': annual_rent,
                    'operating_expenses': current_expenses,
                    'noi': net_operating_income,
                    'debt_service': annual_debt_service,
                    'cash_flow': cash_flow,
                    'property_value': property_value,
                    'loan_balance': loan_balance,
                    'equity': equity,
                    'total_return': equity + (cash_flow * year)
                })
                
                # Update for next year
                current_rent *= (1 + multipliers[scenario]['rent_growth'])
                current_expenses *= (1 + multipliers[scenario]['expense_growth'])
            
            projections[scenario] = pd.DataFrame(scenario_data)
        
        return projections
    
    def monte_carlo_simulation(self, deal_data: Dict, num_simulations: int = 1000) -> Dict:
        """Run Monte Carlo simulation for risk analysis"""
        
        results = []
        
        for _ in range(num_simulations):
            # Random variables with normal distributions
            rent_growth = np.random.normal(0.03, 0.02)  # 3% ± 2%
            expense_growth = np.random.normal(0.03, 0.015)  # 3% ± 1.5%
            vacancy_rate = np.random.normal(0.05, 0.02)  # 5% ± 2%
            appreciation = np.random.normal(0.03, 0.02)  # 3% ± 2%
            interest_rate = np.random.normal(0.06, 0.01)  # 6% ± 1%
            
            # Ensure reasonable bounds
            rent_growth = max(-0.05, min(0.15, rent_growth))
            expense_growth = max(0, min(0.10, expense_growth))
            vacancy_rate = max(0, min(0.20, vacancy_rate))
            appreciation = max(-0.10, min(0.20, appreciation))
            interest_rate = max(0.03, min(0.12, interest_rate))
            
            # Calculate 10-year returns
            total_cash_flow = 0
            purchase_price = deal_data.get('purchase_price', 0)
            monthly_rent = deal_data.get('monthly_rent', 0)
            annual_expenses = self._calculate_annual_expenses(deal_data)
            
            current_rent = monthly_rent * 12
            current_expenses = annual_expenses
            
            for year in range(1, 11):
                annual_rent = current_rent * (1 - vacancy_rate)
                noi = annual_rent - current_expenses
                loan_amount = purchase_price * 0.8
                debt_service = loan_amount * (interest_rate + 0.012)  # Interest + principal
                cash_flow = noi - debt_service
                total_cash_flow += cash_flow
                
                current_rent *= (1 + rent_growth)
                current_expenses *= (1 + expense_growth)
            
            # Final property value and equity
            final_value = purchase_price * ((1 + appreciation) ** 10)
            remaining_loan = loan_amount * 0.7  # Approximate after 10 years
            final_equity = final_value - remaining_loan
            
            total_return = total_cash_flow + final_equity - (purchase_price * 0.2)  # Minus down payment
            roi = (total_return / (purchase_price * 0.2)) * 100
            
            results.append({
                'total_return': total_return,
                'roi': roi,
                'final_value': final_value,
                'total_cash_flow': total_cash_flow
            })
        
        df = pd.DataFrame(results)
        
        return {
            'results': df,
            'statistics': {
                'mean_roi': df['roi'].mean(),
                'median_roi': df['roi'].median(),
                'std_roi': df['roi'].std(),
                'percentile_5': df['roi'].quantile(0.05),
                'percentile_95': df['roi'].quantile(0.95),
                'probability_positive': (df['roi'] > 0).mean() * 100,
                'probability_target': (df['roi'] > 15).mean() * 100  # Prob of >15% ROI
            }
        }
    
    def sensitivity_analysis(self, deal_data: Dict) -> Dict:
        """Analyze sensitivity of returns to key variables"""
        
        base_metrics = self._calculate_base_metrics(deal_data)
        base_roi = base_metrics['roi']
        
        variables = {
            'Purchase Price': {'range': [-20, -10, 0, 10, 20], 'base': deal_data.get('purchase_price', 0)},
            'Monthly Rent': {'range': [-20, -10, 0, 10, 20], 'base': deal_data.get('monthly_rent', 0)},
            'Repair Costs': {'range': [-50, -25, 0, 25, 50], 'base': deal_data.get('repair_costs', 0)},
            'Vacancy Rate': {'range': [-2, -1, 0, 1, 2], 'base': 5},
            'Interest Rate': {'range': [-2, -1, 0, 1, 2], 'base': 6}
        }
        
        sensitivity_results = {}
        
        for var_name, var_data in variables.items():
            results = []
            
            for change in var_data['range']:
                modified_deal = deal_data.copy()
                
                if var_name == 'Purchase Price':
                    modified_deal['purchase_price'] = var_data['base'] * (1 + change/100)
                elif var_name == 'Monthly Rent':
                    modified_deal['monthly_rent'] = var_data['base'] * (1 + change/100)
                elif var_name == 'Repair Costs':
                    modified_deal['repair_costs'] = var_data['base'] * (1 + change/100)
                
                # Calculate new ROI
                new_metrics = self._calculate_base_metrics(modified_deal)
                roi_change = new_metrics['roi'] - base_roi
                
                results.append({
                    'change_percent': change,
                    'roi_impact': roi_change,
                    'new_roi': new_metrics['roi']
                })
            
            sensitivity_results[var_name] = results
        
        return sensitivity_results
    
    def exit_strategy_analysis(self, deal_data: Dict) -> Dict:
        """Compare different exit strategies: Hold, Flip, BRRRR"""
        
        purchase_price = deal_data.get('purchase_price', 0)
        arv = deal_data.get('arv', 0)
        repair_costs = deal_data.get('repair_costs', 0)
        monthly_rent = deal_data.get('monthly_rent', 0)
        
        strategies = {}
        
        # Strategy 1: Quick Flip
        flip_costs = purchase_price * 0.08  # 8% selling costs
        flip_profit = arv - purchase_price - repair_costs - flip_costs
        flip_roi = (flip_profit / purchase_price) * 100 if purchase_price > 0 else 0
        flip_timeline = 6  # months
        
        strategies['Flip'] = {
            'profit': flip_profit,
            'roi': flip_roi,
            'timeline_months': flip_timeline,
            'annual_roi': flip_roi * (12 / flip_timeline),
            'risk_level': 'Medium',
            'capital_required': purchase_price + repair_costs
        }
        
        # Strategy 2: Buy & Hold (5 years)
        hold_years = 5
        annual_noi = (monthly_rent * 12) - self._calculate_annual_expenses(deal_data)
        total_cash_flow = annual_noi * hold_years
        appreciation = arv * (1.03 ** hold_years) - arv  # 3% annual appreciation
        selling_costs = arv * (1.03 ** hold_years) * 0.06
        hold_profit = total_cash_flow + appreciation - selling_costs
        hold_roi = (hold_profit / purchase_price) * 100 if purchase_price > 0 else 0
        
        strategies['Hold'] = {
            'profit': hold_profit,
            'roi': hold_roi,
            'timeline_months': hold_years * 12,
            'annual_roi': hold_roi / hold_years,
            'risk_level': 'Low',
            'capital_required': purchase_price + repair_costs
        }
        
        # Strategy 3: BRRRR (Buy, Rehab, Rent, Refinance, Repeat)
        brrrr_refi_value = arv * 0.75  # 75% LTV refinance
        brrrr_capital_recovered = brrrr_refi_value - (purchase_price + repair_costs)
        brrrr_annual_cash_flow = annual_noi - (brrrr_refi_value * 0.06)  # 6% interest
        brrrr_5year_cash_flow = brrrr_annual_cash_flow * 5
        brrrr_equity = arv * (1.03 ** 5) - brrrr_refi_value
        brrrr_profit = brrrr_5year_cash_flow + brrrr_equity + brrrr_capital_recovered
        brrrr_effective_investment = max(0, purchase_price + repair_costs - brrrr_capital_recovered)
        brrrr_roi = (brrrr_profit / brrrr_effective_investment) * 100 if brrrr_effective_investment > 0 else float('inf')
        
        strategies['BRRRR'] = {
            'profit': brrrr_profit,
            'roi': brrrr_roi if brrrr_roi != float('inf') else 999,
            'timeline_months': 60,
            'annual_roi': brrrr_roi / 5 if brrrr_roi != float('inf') else 199,
            'risk_level': 'High',
            'capital_required': brrrr_effective_investment,
            'capital_recovered': brrrr_capital_recovered
        }
        
        return strategies
    
    def calculate_advanced_metrics(self, deal_data: Dict, projections: Dict) -> Dict:
        """Calculate IRR, NPV, and other advanced financial metrics"""
        
        purchase_price = deal_data.get('purchase_price', 0)
        down_payment = purchase_price * 0.2
        
        metrics = {}
        
        for scenario, df in projections.items():
            cash_flows = [-down_payment] + df['cash_flow'].tolist()
            
            # Add final sale proceeds
            final_value = df.iloc[-1]['property_value']
            loan_balance = df.iloc[-1]['loan_balance']
            selling_costs = final_value * 0.06
            final_proceeds = final_value - loan_balance - selling_costs
            cash_flows[-1] += final_proceeds
            
            # Calculate IRR using numpy
            irr = self._calculate_irr(cash_flows)
            
            # Calculate NPV at 10% discount rate
            npv = self._calculate_npv(cash_flows, 0.10)
            
            # Calculate total return and ROI
            total_invested = down_payment
            total_return = sum(cash_flows[1:])  # Exclude initial investment
            roi = (total_return / total_invested) * 100 if total_invested > 0 else 0
            
            metrics[scenario] = {
                'irr': irr * 100,  # Convert to percentage
                'npv': npv,
                'total_return': total_return,
                'roi': roi,
                'cash_on_cash': df['cash_flow'].mean() / down_payment * 100,
                'debt_coverage_ratio': df['noi'].mean() / df['debt_service'].mean()
            }
        
        return metrics
    
    def _calculate_annual_expenses(self, deal_data: Dict) -> float:
        """Calculate total annual operating expenses"""
        return (
            deal_data.get('annual_taxes', 0) +
            deal_data.get('insurance', 0) +
            deal_data.get('hoa_fees', 0) +
            deal_data.get('monthly_rent', 0) * 12 * 0.1  # 10% for maintenance/management
        )
    
    def _calculate_base_metrics(self, deal_data: Dict) -> Dict:
        """Calculate basic financial metrics for sensitivity analysis"""
        purchase_price = deal_data.get('purchase_price', 0)
        monthly_rent = deal_data.get('monthly_rent', 0)
        annual_expenses = self._calculate_annual_expenses(deal_data)
        
        annual_noi = (monthly_rent * 12) - annual_expenses
        cap_rate = (annual_noi / purchase_price) * 100 if purchase_price > 0 else 0
        
        # Simple ROI calculation
        down_payment = purchase_price * 0.2
        annual_debt_service = (purchase_price * 0.8) * 0.072
        annual_cash_flow = annual_noi - annual_debt_service
        cash_on_cash = (annual_cash_flow / down_payment) * 100 if down_payment > 0 else 0
        
        return {
            'roi': cash_on_cash,
            'cap_rate': cap_rate,
            'noi': annual_noi
        }
    
    def _calculate_irr(self, cash_flows: List[float]) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson method"""
        try:
            # Simple IRR calculation using numpy's approximation
            return np.irr(cash_flows) if hasattr(np, 'irr') else self._irr_approximation(cash_flows)
        except:
            return self._irr_approximation(cash_flows)
    
    def _irr_approximation(self, cash_flows: List[float]) -> float:
        """Approximation method for IRR calculation"""
        try:
            # Newton-Raphson method approximation
            rate = 0.1  # Initial guess
            for _ in range(100):  # Max iterations
                npv = sum([cf / (1 + rate) ** i for i, cf in enumerate(cash_flows)])
                derivative = sum([-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows)])
                
                if abs(derivative) < 1e-10:
                    break
                    
                new_rate = rate - npv / derivative
                
                if abs(new_rate - rate) < 1e-10:
                    break
                    
                rate = new_rate
            
            return rate
        except:
            return 0.10  # Default to 10% if calculation fails
    
    def _calculate_npv(self, cash_flows: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value"""
        return sum([cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows)])


# Visualization functions for the financial modeling
def create_cash_flow_chart(projections: Dict) -> go.Figure:
    """Create interactive cash flow projections chart"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Annual Cash Flow', 'Property Value Growth', 'Cumulative Returns', 'NOI vs Debt Service'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = {'Conservative': '#ff7f0e', 'Base Case': '#1f77b4', 'Optimistic': '#2ca02c'}
    
    for scenario, df in projections.items():
        color = colors[scenario]
        
        # Cash flow chart
        fig.add_trace(
            go.Scatter(x=df['year'], y=df['cash_flow'], name=f'{scenario} Cash Flow',
                      line=dict(color=color), mode='lines+markers'),
            row=1, col=1
        )
        
        # Property value chart
        fig.add_trace(
            go.Scatter(x=df['year'], y=df['property_value'], name=f'{scenario} Value',
                      line=dict(color=color, dash='dash'), mode='lines'),
            row=1, col=2
        )
        
        # Cumulative returns
        fig.add_trace(
            go.Scatter(x=df['year'], y=df['total_return'], name=f'{scenario} Total Return',
                      line=dict(color=color, dash='dot'), mode='lines'),
            row=2, col=1
        )
        
        # NOI vs Debt Service (Base Case only to avoid clutter)
        if scenario == 'Base Case':
            fig.add_trace(
                go.Scatter(x=df['year'], y=df['noi'], name='NOI',
                          line=dict(color='green'), mode='lines'),
                row=2, col=2
            )
            fig.add_trace(
                go.Scatter(x=df['year'], y=df['debt_service'], name='Debt Service',
                          line=dict(color='red'), mode='lines'),
                row=2, col=2
            )
    
    fig.update_layout(
        height=600,
        title_text="Advanced Financial Projections",
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_monte_carlo_chart(simulation_results: Dict) -> go.Figure:
    """Create Monte Carlo simulation visualization"""
    
    df = simulation_results['results']
    stats = simulation_results['statistics']
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('ROI Distribution', 'Risk Analysis'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # ROI histogram
    fig.add_trace(
        go.Histogram(x=df['roi'], nbinsx=50, name='ROI Distribution',
                    marker_color='rgba(55, 128, 191, 0.7)'),
        row=1, col=1
    )
    
    # Add percentile lines
    fig.add_vline(x=stats['percentile_5'], line_dash="dash", line_color="red",
                  annotation_text=f"5th Percentile: {stats['percentile_5']:.1f}%",
                  row=1, col=1)
    fig.add_vline(x=stats['median_roi'], line_dash="dash", line_color="green",
                  annotation_text=f"Median: {stats['median_roi']:.1f}%",
                  row=1, col=1)
    fig.add_vline(x=stats['percentile_95'], line_dash="dash", line_color="blue",
                  annotation_text=f"95th Percentile: {stats['percentile_95']:.1f}%",
                  row=1, col=1)
    
    # Risk metrics
    risk_data = [
        ['Probability of Profit', stats['probability_positive']],
        ['Probability of 15%+ ROI', stats['probability_target']],
        ['Mean ROI', stats['mean_roi']],
        ['Standard Deviation', stats['std_roi']]
    ]
    
    fig.add_trace(
        go.Bar(x=[item[0] for item in risk_data[:2]], 
               y=[item[1] for item in risk_data[:2]],
               name='Probabilities (%)',
               marker_color='rgba(255, 127, 14, 0.7)'),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        title_text="Monte Carlo Risk Analysis",
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_sensitivity_chart(sensitivity_results: Dict) -> go.Figure:
    """Create sensitivity analysis tornado chart"""
    
    fig = go.Figure()
    
    variables = []
    impacts = []
    
    for var_name, results in sensitivity_results.items():
        # Find the impact of a 10% change (or closest)
        for result in results:
            if abs(result['change_percent'] - 10) < 1:
                variables.append(var_name)
                impacts.append(abs(result['roi_impact']))
                break
    
    # Sort by impact magnitude
    sorted_data = sorted(zip(variables, impacts), key=lambda x: x[1], reverse=True)
    variables, impacts = zip(*sorted_data)
    
    fig.add_trace(go.Bar(
        y=variables,
        x=impacts,
        orientation='h',
        marker_color='rgba(55, 128, 191, 0.7)',
        name='ROI Impact'
    ))
    
    fig.update_layout(
        title="Sensitivity Analysis - Impact on ROI",
        xaxis_title="ROI Impact (% points for 10% variable change)",
        yaxis_title="Variables",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_exit_strategy_chart(strategies: Dict) -> go.Figure:
    """Create exit strategy comparison chart"""
    
    strategy_names = list(strategies.keys())
    annual_rois = [strategies[name]['annual_roi'] for name in strategy_names]
    profits = [strategies[name]['profit'] for name in strategy_names]
    timelines = [strategies[name]['timeline_months'] for name in strategy_names]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Annual ROI Comparison', 'Profit vs Timeline'),
        specs=[[{"secondary_y": False}, {"secondary_y": True}]]
    )
    
    # Annual ROI comparison
    fig.add_trace(
        go.Bar(x=strategy_names, y=annual_rois, name='Annual ROI (%)',
               marker_color=['#ff7f0e', '#1f77b4', '#2ca02c']),
        row=1, col=1
    )
    
    # Profit vs Timeline scatter
    fig.add_trace(
        go.Scatter(x=timelines, y=profits, mode='markers+text',
                  text=strategy_names, textposition="top center",
                  marker=dict(size=[50, 75, 100], color=['#ff7f0e', '#1f77b4', '#2ca02c']),
                  name='Strategies'),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        title_text="Exit Strategy Analysis",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(title_text="Timeline (Months)", row=1, col=2)
    fig.update_yaxes(title_text="Total Profit ($)", row=1, col=2)
    
    return fig