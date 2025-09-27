"""
Enhanced Financial Modeling for NXTRIX Advanced Analytics
Comprehensive financial analysis, ROI forecasting, and market trend modeling
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class FinancingType(Enum):
    """Property financing options"""
    CASH = "Cash Purchase"
    CONVENTIONAL = "Conventional Loan"
    FHA = "FHA Loan"
    VA = "VA Loan"
    PORTFOLIO = "Portfolio Loan"
    HARD_MONEY = "Hard Money"
    PRIVATE_MONEY = "Private Money"
    SELLER_FINANCING = "Seller Financing"

class ExitStrategy(Enum):
    """Property exit strategies"""
    BUY_HOLD = "Buy & Hold"
    FLIP = "Fix & Flip"
    WHOLESALE = "Wholesale"
    BRRRR = "BRRRR Strategy"
    RENT_TO_OWN = "Rent-to-Own"
    COMMERCIAL_CONVERSION = "Commercial Conversion"

@dataclass
class FinancialModel:
    """Comprehensive financial model for real estate deals"""
    property_address: str
    purchase_price: float
    estimated_arv: float
    rehab_costs: float
    holding_costs: float
    acquisition_costs: float
    financing_type: FinancingType
    down_payment_percent: float
    interest_rate: float
    loan_term_years: int
    monthly_rent: float
    vacancy_rate: float
    property_management_rate: float
    maintenance_reserve: float
    capex_reserve: float
    insurance_monthly: float
    property_taxes_monthly: float
    hoa_fees: float
    exit_strategy: ExitStrategy
    hold_period_years: float

class EnhancedFinancialModeling:
    """Enhanced financial modeling and forecasting engine"""
    
    def __init__(self):
        self.inflation_rate = 0.03  # 3% annual inflation
        self.market_appreciation = 0.05  # 5% annual appreciation
        self.rent_growth = 0.03  # 3% annual rent growth
    
    def calculate_comprehensive_roi(self, model: FinancialModel) -> Dict[str, Any]:
        """Calculate comprehensive ROI analysis"""
        
        # Basic calculations
        total_investment = self._calculate_total_investment(model)
        loan_amount = self._calculate_loan_amount(model)
        monthly_payment = self._calculate_monthly_payment(model, loan_amount)
        net_monthly_cash_flow = self._calculate_monthly_cash_flow(model, monthly_payment)
        
        # ROI Metrics
        cash_on_cash_return = (net_monthly_cash_flow * 12) / total_investment * 100
        cap_rate = (model.monthly_rent * 12 - self._calculate_annual_expenses(model)) / model.purchase_price * 100
        
        # Rule calculations
        one_percent_rule = (model.monthly_rent / model.purchase_price) * 100
        two_percent_rule = (model.monthly_rent / model.purchase_price) * 100
        fifty_percent_rule_net = model.monthly_rent * 0.5 - monthly_payment
        
        # Advanced metrics
        debt_service_coverage = (model.monthly_rent * (1 - model.vacancy_rate)) / monthly_payment if monthly_payment > 0 else float('inf')
        loan_to_value = loan_amount / model.purchase_price * 100
        
        # Exit strategy analysis
        exit_analysis = self._calculate_exit_strategy_returns(model)
        
        # Risk assessment
        risk_score = self._calculate_risk_score(model)
        
        return {
            'total_investment': total_investment,
            'loan_amount': loan_amount,
            'monthly_payment': monthly_payment,
            'net_monthly_cash_flow': net_monthly_cash_flow,
            'annual_cash_flow': net_monthly_cash_flow * 12,
            'cash_on_cash_return': cash_on_cash_return,
            'cap_rate': cap_rate,
            'one_percent_rule': one_percent_rule,
            'two_percent_rule': two_percent_rule,
            'fifty_percent_rule_net': fifty_percent_rule_net,
            'debt_service_coverage': debt_service_coverage,
            'loan_to_value': loan_to_value,
            'risk_score': risk_score,
            'exit_analysis': exit_analysis,
            'investment_grade': self._get_investment_grade(cash_on_cash_return, cap_rate, risk_score)
        }
    
    def _calculate_total_investment(self, model: FinancialModel) -> float:
        """Calculate total cash investment required"""
        down_payment = model.purchase_price * (model.down_payment_percent / 100)
        return down_payment + model.rehab_costs + model.acquisition_costs + model.holding_costs
    
    def _calculate_loan_amount(self, model: FinancialModel) -> float:
        """Calculate loan amount"""
        if model.financing_type == FinancingType.CASH:
            return 0
        return model.purchase_price * (1 - model.down_payment_percent / 100)
    
    def _calculate_monthly_payment(self, model: FinancialModel, loan_amount: float) -> float:
        """Calculate monthly mortgage payment"""
        if loan_amount == 0:
            return 0
        
        monthly_rate = model.interest_rate / 100 / 12
        num_payments = model.loan_term_years * 12
        
        if monthly_rate == 0:
            return loan_amount / num_payments
        
        return loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    def _calculate_monthly_cash_flow(self, model: FinancialModel, monthly_payment: float) -> float:
        """Calculate net monthly cash flow"""
        gross_monthly_income = model.monthly_rent * (1 - model.vacancy_rate / 100)
        
        monthly_expenses = (
            monthly_payment +
            model.insurance_monthly +
            model.property_taxes_monthly +
            model.hoa_fees +
            (model.monthly_rent * model.property_management_rate / 100) +
            (model.monthly_rent * model.maintenance_reserve / 100) +
            (model.monthly_rent * model.capex_reserve / 100)
        )
        
        return gross_monthly_income - monthly_expenses
    
    def _calculate_annual_expenses(self, model: FinancialModel) -> float:
        """Calculate annual operating expenses (excluding debt service)"""
        return (
            model.insurance_monthly * 12 +
            model.property_taxes_monthly * 12 +
            model.hoa_fees * 12 +
            (model.monthly_rent * 12 * model.property_management_rate / 100) +
            (model.monthly_rent * 12 * model.maintenance_reserve / 100) +
            (model.monthly_rent * 12 * model.capex_reserve / 100) +
            (model.monthly_rent * 12 * model.vacancy_rate / 100)
        )
    
    def _calculate_exit_strategy_returns(self, model: FinancialModel) -> Dict[str, float]:
        """Calculate returns based on exit strategy"""
        
        if model.exit_strategy == ExitStrategy.BUY_HOLD:
            return self._calculate_buy_hold_returns(model)
        elif model.exit_strategy == ExitStrategy.FLIP:
            return self._calculate_flip_returns(model)
        elif model.exit_strategy == ExitStrategy.BRRRR:
            return self._calculate_brrrr_returns(model)
        else:
            return self._calculate_generic_exit_returns(model)
    
    def _calculate_buy_hold_returns(self, model: FinancialModel) -> Dict[str, float]:
        """Calculate buy and hold strategy returns"""
        
        # Future property value with appreciation
        future_value = model.estimated_arv * (1 + self.market_appreciation) ** model.hold_period_years
        
        # Total cash flow over hold period (with rent growth)
        total_cash_flow = 0
        monthly_cash_flow = self._calculate_monthly_cash_flow(
            model, 
            self._calculate_monthly_payment(model, self._calculate_loan_amount(model))
        )
        
        for year in range(int(model.hold_period_years)):
            annual_cash_flow = monthly_cash_flow * 12 * (1 + self.rent_growth) ** year
            total_cash_flow += annual_cash_flow
        
        # Equity build-up (simplified)
        loan_amount = self._calculate_loan_amount(model)
        remaining_balance = loan_amount * 0.85  # Approximate remaining balance
        equity_buildup = loan_amount - remaining_balance
        
        # Total return
        total_investment = self._calculate_total_investment(model)
        net_proceeds = future_value - remaining_balance - (future_value * 0.08)  # 8% selling costs
        total_return = total_cash_flow + equity_buildup + (net_proceeds - total_investment)
        
        return {
            'strategy': 'Buy & Hold',
            'future_property_value': future_value,
            'total_cash_flow': total_cash_flow,
            'equity_buildup': equity_buildup,
            'net_proceeds': net_proceeds,
            'total_return': total_return,
            'annualized_return': (total_return / total_investment) / model.hold_period_years * 100
        }
    
    def _calculate_flip_returns(self, model: FinancialModel) -> Dict[str, float]:
        """Calculate fix and flip returns"""
        
        total_investment = model.purchase_price + model.rehab_costs + model.acquisition_costs + model.holding_costs
        gross_proceeds = model.estimated_arv
        selling_costs = gross_proceeds * 0.08  # 8% selling costs
        net_proceeds = gross_proceeds - selling_costs
        profit = net_proceeds - total_investment
        
        return {
            'strategy': 'Fix & Flip',
            'total_investment': total_investment,
            'gross_proceeds': gross_proceeds,
            'selling_costs': selling_costs,
            'net_proceeds': net_proceeds,
            'profit': profit,
            'roi_percentage': (profit / total_investment) * 100 if total_investment > 0 else 0
        }
    
    def _calculate_brrrr_returns(self, model: FinancialModel) -> Dict[str, float]:
        """Calculate BRRRR strategy returns"""
        
        # Initial investment
        initial_investment = model.purchase_price + model.rehab_costs + model.acquisition_costs
        
        # Refinance analysis (75% LTV on ARV)
        refinance_amount = model.estimated_arv * 0.75
        cash_recovered = refinance_amount - initial_investment
        remaining_investment = max(0, initial_investment - refinance_amount)
        
        # Infinite return potential
        monthly_cash_flow = self._calculate_monthly_cash_flow(model, refinance_amount * 0.004)  # Approximate payment
        
        return {
            'strategy': 'BRRRR',
            'initial_investment': initial_investment,
            'refinance_amount': refinance_amount,
            'cash_recovered': cash_recovered,
            'remaining_investment': remaining_investment,
            'monthly_cash_flow': monthly_cash_flow,
            'cash_on_cash_return': (monthly_cash_flow * 12 / remaining_investment * 100) if remaining_investment > 0 else float('inf')
        }
    
    def _calculate_generic_exit_returns(self, model: FinancialModel) -> Dict[str, float]:
        """Calculate generic exit strategy returns"""
        
        total_investment = self._calculate_total_investment(model)
        
        return {
            'strategy': model.exit_strategy.value,
            'total_investment': total_investment,
            'estimated_return': total_investment * 0.15,  # 15% estimated return
            'roi_percentage': 15.0
        }
    
    def _calculate_risk_score(self, model: FinancialModel) -> float:
        """Calculate investment risk score (0-100, lower is better)"""
        
        risk_score = 50  # Base risk score
        
        # Financing risk
        if model.financing_type == FinancingType.HARD_MONEY:
            risk_score += 15
        elif model.financing_type == FinancingType.CASH:
            risk_score -= 10
        
        # LTV risk
        ltv = (1 - model.down_payment_percent / 100) * 100
        if ltv > 80:
            risk_score += 10
        elif ltv < 70:
            risk_score -= 5
        
        # Cash flow risk
        monthly_payment = self._calculate_monthly_payment(model, self._calculate_loan_amount(model))
        net_cash_flow = self._calculate_monthly_cash_flow(model, monthly_payment)
        if net_cash_flow < 0:
            risk_score += 25
        elif net_cash_flow > 300:
            risk_score -= 10
        
        # Market risk
        if model.purchase_price > model.estimated_arv * 0.9:
            risk_score += 20
        
        # Vacancy risk
        if model.vacancy_rate > 10:
            risk_score += 10
        
        return max(0, min(100, risk_score))
    
    def _get_investment_grade(self, cash_on_cash: float, cap_rate: float, risk_score: float) -> str:
        """Determine investment grade"""
        
        if cash_on_cash >= 12 and cap_rate >= 8 and risk_score <= 30:
            return "A+ Excellent"
        elif cash_on_cash >= 10 and cap_rate >= 7 and risk_score <= 40:
            return "A Good"
        elif cash_on_cash >= 8 and cap_rate >= 6 and risk_score <= 50:
            return "B+ Fair"
        elif cash_on_cash >= 6 and cap_rate >= 5 and risk_score <= 60:
            return "B Acceptable"
        elif cash_on_cash >= 4 and cap_rate >= 4 and risk_score <= 70:
            return "C- Below Average"
        else:
            return "D Poor"
    
    def create_cash_flow_projection(self, model: FinancialModel, years: int = 10) -> pd.DataFrame:
        """Create detailed cash flow projection"""
        
        projections = []
        monthly_payment = self._calculate_monthly_payment(model, self._calculate_loan_amount(model))
        base_cash_flow = self._calculate_monthly_cash_flow(model, monthly_payment)
        
        for year in range(1, years + 1):
            # Account for rent growth and inflation
            adjusted_rent = model.monthly_rent * (1 + self.rent_growth) ** year
            adjusted_expenses = (
                model.insurance_monthly * (1 + self.inflation_rate) ** year +
                model.property_taxes_monthly * (1 + self.inflation_rate) ** year +
                model.hoa_fees * (1 + self.inflation_rate) ** year
            )
            
            annual_cash_flow = (base_cash_flow * (1 + self.rent_growth) ** year) * 12
            property_value = model.estimated_arv * (1 + self.market_appreciation) ** year
            
            projections.append({
                'Year': year,
                'Property Value': property_value,
                'Monthly Rent': adjusted_rent,
                'Annual Cash Flow': annual_cash_flow,
                'Cumulative Cash Flow': sum([p['Annual Cash Flow'] for p in projections]) + annual_cash_flow
            })
        
        return pd.DataFrame(projections)
    
    def create_sensitivity_analysis(self, model: FinancialModel) -> Dict[str, Any]:
        """Perform sensitivity analysis on key variables"""
        
        base_roi = self.calculate_comprehensive_roi(model)
        base_cash_flow = base_roi['net_monthly_cash_flow']
        
        # Variable ranges
        rent_variations = [-20, -10, 0, 10, 20]  # % changes
        vacancy_variations = [2, 5, 8, 12, 15]  # % vacancy rates
        interest_variations = [3.5, 4.5, 5.5, 6.5, 7.5]  # % interest rates
        
        sensitivity_data = {
            'rent_sensitivity': [],
            'vacancy_sensitivity': [],
            'interest_sensitivity': []
        }
        
        # Rent sensitivity
        for rent_change in rent_variations:
            modified_model = model
            modified_model.monthly_rent = model.monthly_rent * (1 + rent_change / 100)
            roi = self.calculate_comprehensive_roi(modified_model)
            sensitivity_data['rent_sensitivity'].append({
                'change': rent_change,
                'cash_flow': roi['net_monthly_cash_flow'],
                'roi': roi['cash_on_cash_return']
            })
        
        # Vacancy sensitivity
        for vacancy in vacancy_variations:
            modified_model = model
            modified_model.vacancy_rate = vacancy
            roi = self.calculate_comprehensive_roi(modified_model)
            sensitivity_data['vacancy_sensitivity'].append({
                'vacancy_rate': vacancy,
                'cash_flow': roi['net_monthly_cash_flow'],
                'roi': roi['cash_on_cash_return']
            })
        
        # Interest rate sensitivity
        for rate in interest_variations:
            modified_model = model
            modified_model.interest_rate = rate
            roi = self.calculate_comprehensive_roi(modified_model)
            sensitivity_data['interest_sensitivity'].append({
                'interest_rate': rate,
                'cash_flow': roi['net_monthly_cash_flow'],
                'roi': roi['cash_on_cash_return']
            })
        
        return sensitivity_data

def show_enhanced_financial_modeling():
    """Display enhanced financial modeling interface"""
    
    st.header("💰 Enhanced Financial Modeling")
    st.markdown("*Comprehensive financial analysis and ROI forecasting*")
    
    # Financial modeling form
    with st.form("financial_model"):
        st.subheader("🏠 Property & Deal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            property_address = st.text_input("Property Address", value="123 Investment St, City, ST")
            purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=200000)
            estimated_arv = st.number_input("Estimated ARV ($)", min_value=0, value=250000)
            rehab_costs = st.number_input("Rehab Costs ($)", min_value=0, value=25000)
            holding_costs = st.number_input("Holding Costs ($)", min_value=0, value=5000)
            acquisition_costs = st.number_input("Acquisition Costs ($)", min_value=0, value=8000)
        
        with col2:
            financing_type = st.selectbox("Financing Type", [f.value for f in FinancingType])
            down_payment_percent = st.slider("Down Payment (%)", 0, 100, 25)
            interest_rate = st.slider("Interest Rate (%)", 0.0, 12.0, 5.5, 0.1)
            loan_term_years = st.selectbox("Loan Term (Years)", [15, 20, 25, 30], index=3)
            exit_strategy = st.selectbox("Exit Strategy", [e.value for e in ExitStrategy])
            hold_period_years = st.slider("Hold Period (Years)", 1, 30, 5)
        
        st.subheader("🏠 Property Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_rent = st.number_input("Monthly Rent ($)", min_value=0, value=2000)
            vacancy_rate = st.slider("Vacancy Rate (%)", 0.0, 20.0, 5.0, 0.5)
            property_management_rate = st.slider("Property Management (%)", 0.0, 15.0, 8.0, 0.5)
            maintenance_reserve = st.slider("Maintenance Reserve (%)", 0.0, 10.0, 5.0, 0.5)
        
        with col2:
            capex_reserve = st.slider("CapEx Reserve (%)", 0.0, 10.0, 5.0, 0.5)
            insurance_monthly = st.number_input("Monthly Insurance ($)", min_value=0, value=150)
            property_taxes_monthly = st.number_input("Monthly Property Taxes ($)", min_value=0, value=300)
            hoa_fees = st.number_input("HOA Fees ($)", min_value=0, value=0)
        
        submitted = st.form_submit_button("📊 Generate Financial Analysis", type="primary")
    
    if submitted:
        # Create financial model
        model = FinancialModel(
            property_address=property_address,
            purchase_price=purchase_price,
            estimated_arv=estimated_arv,
            rehab_costs=rehab_costs,
            holding_costs=holding_costs,
            acquisition_costs=acquisition_costs,
            financing_type=FinancingType(financing_type),
            down_payment_percent=down_payment_percent,
            interest_rate=interest_rate,
            loan_term_years=loan_term_years,
            monthly_rent=monthly_rent,
            vacancy_rate=vacancy_rate,
            property_management_rate=property_management_rate,
            maintenance_reserve=maintenance_reserve,
            capex_reserve=capex_reserve,
            insurance_monthly=insurance_monthly,
            property_taxes_monthly=property_taxes_monthly,
            hoa_fees=hoa_fees,
            exit_strategy=ExitStrategy(exit_strategy),
            hold_period_years=hold_period_years
        )
        
        # Generate analysis
        modeling = EnhancedFinancialModeling()
        roi_analysis = modeling.calculate_comprehensive_roi(model)
        
        # Display results
        st.markdown("---")
        st.subheader("📊 Financial Analysis Results")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Investment", f"${roi_analysis['total_investment']:,.0f}")
            st.metric("Monthly Cash Flow", f"${roi_analysis['net_monthly_cash_flow']:,.0f}")
        
        with col2:
            st.metric("Cash-on-Cash Return", f"{roi_analysis['cash_on_cash_return']:.1f}%")
            st.metric("Cap Rate", f"{roi_analysis['cap_rate']:.1f}%")
        
        with col3:
            st.metric("1% Rule", f"{roi_analysis['one_percent_rule']:.2f}%")
            st.metric("Debt Service Coverage", f"{roi_analysis['debt_service_coverage']:.2f}x")
        
        with col4:
            st.metric("Investment Grade", roi_analysis['investment_grade'])
            st.metric("Risk Score", f"{roi_analysis['risk_score']:.0f}/100")
        
        # Exit strategy analysis
        st.subheader("🎯 Exit Strategy Analysis")
        exit_analysis = roi_analysis['exit_analysis']
        
        if exit_analysis['strategy'] == 'Buy & Hold':
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Future Property Value:** ${exit_analysis['future_property_value']:,.0f}")
                st.write(f"**Total Cash Flow:** ${exit_analysis['total_cash_flow']:,.0f}")
                st.write(f"**Equity Buildup:** ${exit_analysis['equity_buildup']:,.0f}")
            with col2:
                st.write(f"**Net Proceeds:** ${exit_analysis['net_proceeds']:,.0f}")
                st.write(f"**Total Return:** ${exit_analysis['total_return']:,.0f}")
                st.write(f"**Annualized Return:** {exit_analysis['annualized_return']:.1f}%")
        
        # Cash flow projection
        st.subheader("📈 10-Year Cash Flow Projection")
        projection_df = modeling.create_cash_flow_projection(model)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=projection_df['Year'],
            y=projection_df['Annual Cash Flow'],
            mode='lines+markers',
            name='Annual Cash Flow',
            line=dict(color='green')
        ))
        
        fig.update_layout(
            title="Annual Cash Flow Projection",
            xaxis_title="Year",
            yaxis_title="Cash Flow ($)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Sensitivity analysis
        st.subheader("🎯 Sensitivity Analysis")
        sensitivity = modeling.create_sensitivity_analysis(model)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Rent Sensitivity**")
            rent_data = sensitivity['rent_sensitivity']
            for item in rent_data:
                st.write(f"{item['change']:+d}%: ${item['cash_flow']:,.0f}")
        
        with col2:
            st.markdown("**Vacancy Sensitivity**")
            vacancy_data = sensitivity['vacancy_sensitivity']
            for item in vacancy_data:
                st.write(f"{item['vacancy_rate']:.0f}%: ${item['cash_flow']:,.0f}")
        
        with col3:
            st.markdown("**Interest Rate Sensitivity**")
            interest_data = sensitivity['interest_sensitivity']
            for item in interest_data:
                st.write(f"{item['interest_rate']:.1f}%: ${item['cash_flow']:,.0f}")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Enhanced Financial Modeling",
        page_icon="💰",
        layout="wide"
    )
    
    show_enhanced_financial_modeling()