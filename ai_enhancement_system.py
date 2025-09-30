"""
NxTrix CRM - Phase 3B: AI Enhancement System
Advanced AI-powered features for intelligent deal analysis and automation
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import json
import openai
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass
import asyncio
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from textblob import TextBlob

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

@dataclass
class AIAnalysisResult:
    """Data class for AI analysis results"""
    analysis_type: str
    confidence_score: float
    recommendations: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    market_insights: Dict
    financial_analysis: Dict
    overall_score: int

class AIEnhancementSystem:
    """Advanced AI Enhancement System for NxTrix CRM"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.openai_client = None
        self.setup_openai()
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
    def setup_openai(self):
        """Setup OpenAI client"""
        try:
            # Get API key from Streamlit secrets or environment
            api_key = st.secrets.get("OPENAI_API_KEY") or st.session_state.get("openai_api_key")
            if api_key:
                openai.api_key = api_key
                self.openai_client = openai
            else:
                st.warning("⚠️ OpenAI API key not configured. AI features will be limited.")
        except Exception as e:
            st.error(f"Error setting up OpenAI: {e}")
    
    def get_database_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def analyze_deal_with_ai(self, deal_data: Dict) -> AIAnalysisResult:
        """Comprehensive AI analysis of a deal"""
        
        if not self.openai_client:
            return self._generate_mock_analysis(deal_data)
        
        try:
            # Prepare deal context for AI
            context = self._prepare_deal_context(deal_data)
            
            # Generate AI analysis
            analysis_prompt = f"""
            As an expert real estate investment analyst, analyze this deal comprehensively:
            
            {context}
            
            Provide analysis in the following JSON format:
            {{
                "overall_score": <1-100>,
                "confidence_score": <0.0-1.0>,
                "recommendations": ["recommendation1", "recommendation2", ...],
                "risk_factors": ["risk1", "risk2", ...],
                "opportunities": ["opportunity1", "opportunity2", ...],
                "market_insights": {{
                    "market_strength": "<weak/moderate/strong>",
                    "appreciation_potential": "<low/medium/high>",
                    "rental_demand": "<low/medium/high>",
                    "competition_level": "<low/medium/high>"
                }},
                "financial_analysis": {{
                    "roi_assessment": "<poor/fair/good/excellent>",
                    "cash_flow_potential": "<negative/break_even/positive/strong>",
                    "appreciation_outlook": "<declining/stable/growing/rapid>",
                    "risk_level": "<low/medium/high>"
                }}
            }}
            """
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert real estate investment analyst with 20+ years of experience."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            analysis_data = json.loads(ai_response)
            
            return AIAnalysisResult(
                analysis_type="comprehensive_ai_analysis",
                confidence_score=analysis_data["confidence_score"],
                recommendations=analysis_data["recommendations"],
                risk_factors=analysis_data["risk_factors"],
                opportunities=analysis_data["opportunities"],
                market_insights=analysis_data["market_insights"],
                financial_analysis=analysis_data["financial_analysis"],
                overall_score=analysis_data["overall_score"]
            )
            
        except Exception as e:
            st.error(f"AI Analysis Error: {e}")
            return self._generate_mock_analysis(deal_data)
    
    def _prepare_deal_context(self, deal_data: Dict) -> str:
        """Prepare deal data for AI analysis"""
        context = f"""
        Property Address: {deal_data.get('property_address', 'N/A')}
        Purchase Price: ${deal_data.get('purchase_price', 0):,.2f}
        After Repair Value (ARV): ${deal_data.get('after_repair_value', 0):,.2f}
        Repair Costs: ${deal_data.get('repair_costs', 0):,.2f}
        Monthly Rent: ${deal_data.get('monthly_rent', 0):,.2f}
        Monthly Expenses: ${deal_data.get('monthly_expenses', 0):,.2f}
        Deal Type: {deal_data.get('deal_type', 'N/A')}
        Current Status: {deal_data.get('status', 'N/A')}
        
        Financial Metrics:
        - ROI: {deal_data.get('roi', 0):.2f}%
        - Cap Rate: {deal_data.get('cap_rate', 0):.2f}%
        - Cash on Cash Return: {deal_data.get('cash_on_cash_return', 0):.2f}%
        - Profit Potential: ${deal_data.get('profit_potential', 0):,.2f}
        - Deal Score: {deal_data.get('deal_score', 0)}/100
        
        Additional Details:
        {json.dumps(deal_data.get('property_details', {}), indent=2)}
        """
        return context
    
    def _generate_mock_analysis(self, deal_data: Dict) -> AIAnalysisResult:
        """Generate mock analysis when AI is not available"""
        purchase_price = deal_data.get('purchase_price', 0)
        arv = deal_data.get('after_repair_value', 0)
        repair_costs = deal_data.get('repair_costs', 0)
        monthly_rent = deal_data.get('monthly_rent', 0)
        roi = deal_data.get('roi', 0)
        
        # Calculate basic metrics
        profit_margin = ((arv - purchase_price - repair_costs) / purchase_price * 100) if purchase_price > 0 else 0
        rent_to_price_ratio = (monthly_rent * 12 / purchase_price * 100) if purchase_price > 0 else 0
        
        # Generate score based on metrics
        score = min(100, max(0, (roi * 2 + profit_margin + rent_to_price_ratio) / 3))
        
        recommendations = []
        risk_factors = []
        opportunities = []
        
        if roi > 15:
            recommendations.append("Strong ROI indicates excellent investment potential")
        elif roi < 8:
            risk_factors.append("Low ROI may not justify investment risk")
        
        if profit_margin > 20:
            opportunities.append("High profit margin provides good cushion")
        elif profit_margin < 10:
            risk_factors.append("Thin profit margins increase risk")
        
        if rent_to_price_ratio > 1:
            recommendations.append("Good rent-to-price ratio supports cash flow")
        else:
            risk_factors.append("Low rent-to-price ratio may impact cash flow")
        
        return AIAnalysisResult(
            analysis_type="rule_based_analysis",
            confidence_score=0.75,
            recommendations=recommendations,
            risk_factors=risk_factors,
            opportunities=opportunities,
            market_insights={
                "market_strength": "moderate",
                "appreciation_potential": "medium",
                "rental_demand": "medium",
                "competition_level": "medium"
            },
            financial_analysis={
                "roi_assessment": "good" if roi > 12 else "fair",
                "cash_flow_potential": "positive" if monthly_rent > 0 else "unknown",
                "appreciation_outlook": "stable",
                "risk_level": "medium"
            },
            overall_score=int(score)
        )
    
    def natural_language_property_search(self, query: str) -> List[Dict]:
        """AI-powered natural language property search"""
        
        if not query.strip():
            return []
        
        try:
            # Get all properties from database
            conn = self.get_database_connection()
            properties_df = pd.read_sql_query("""
                SELECT * FROM deals 
                WHERE status != 'rejected'
                ORDER BY created_at DESC
            """, conn)
            conn.close()
            
            if properties_df.empty:
                return []
            
            # Process query with TextBlob for better understanding
            blob = TextBlob(query.lower())
            
            # Extract entities and intents
            search_criteria = self._extract_search_criteria(query.lower())
            
            # Filter properties based on criteria
            filtered_properties = self._filter_properties(properties_df, search_criteria)
            
            # Convert to list of dictionaries
            results = filtered_properties.head(10).to_dict('records')
            
            return results
            
        except Exception as e:
            st.error(f"Search Error: {e}")
            return []
    
    def _extract_search_criteria(self, query: str) -> Dict:
        """Extract search criteria from natural language query"""
        criteria = {
            'min_price': None,
            'max_price': None,
            'deal_type': None,
            'min_roi': None,
            'location': None,
            'keywords': []
        }
        
        # Price extraction
        price_patterns = [
            r'under \$?(\d+(?:,\d{3})*(?:k|000)?)',
            r'below \$?(\d+(?:,\d{3})*(?:k|000)?)',
            r'less than \$?(\d+(?:,\d{3})*(?:k|000)?)',
            r'above \$?(\d+(?:,\d{3})*(?:k|000)?)',
            r'over \$?(\d+(?:,\d{3})*(?:k|000)?)',
            r'more than \$?(\d+(?:,\d{3})*(?:k|000)?)',
            r'\$?(\d+(?:,\d{3})*(?:k|000)?)\s*-\s*\$?(\d+(?:,\d{3})*(?:k|000)?)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query)
            if match:
                if 'under' in query or 'below' in query or 'less than' in query:
                    criteria['max_price'] = self._parse_price(match.group(1))
                elif 'above' in query or 'over' in query or 'more than' in query:
                    criteria['min_price'] = self._parse_price(match.group(1))
                elif '-' in match.group(0):  # Range
                    criteria['min_price'] = self._parse_price(match.group(1))
                    criteria['max_price'] = self._parse_price(match.group(2))
        
        # Deal type extraction
        if any(word in query for word in ['flip', 'flipping', 'fix and flip']):
            criteria['deal_type'] = 'flip'
        elif any(word in query for word in ['rental', 'rent', 'cash flow']):
            criteria['deal_type'] = 'rental'
        elif any(word in query for word in ['wholesale', 'wholesaling']):
            criteria['deal_type'] = 'wholesale'
        elif any(word in query for word in ['brrrr', 'buy hold refinance']):
            criteria['deal_type'] = 'brrrr'
        
        # ROI extraction
        roi_match = re.search(r'(\d+)%?\s*roi', query)
        if roi_match:
            criteria['min_roi'] = float(roi_match.group(1))
        
        # Location extraction (basic)
        location_keywords = ['in', 'near', 'around', 'at']
        for keyword in location_keywords:
            if keyword in query:
                # Extract words after location keyword
                parts = query.split(keyword)
                if len(parts) > 1:
                    location_part = parts[1].strip().split()[0:3]  # Take first few words
                    criteria['location'] = ' '.join(location_part)
                    break
        
        return criteria
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        price_str = price_str.replace(',', '').replace('$', '')
        if price_str.endswith('k'):
            return float(price_str[:-1]) * 1000
        elif price_str.endswith('000'):
            return float(price_str)
        else:
            return float(price_str)
    
    def _filter_properties(self, df: pd.DataFrame, criteria: Dict) -> pd.DataFrame:
        """Filter properties based on extracted criteria"""
        filtered_df = df.copy()
        
        # Price filters
        if criteria['min_price']:
            filtered_df = filtered_df[filtered_df['purchase_price'] >= criteria['min_price']]
        if criteria['max_price']:
            filtered_df = filtered_df[filtered_df['purchase_price'] <= criteria['max_price']]
        
        # Deal type filter
        if criteria['deal_type']:
            filtered_df = filtered_df[filtered_df['deal_type'] == criteria['deal_type']]
        
        # ROI filter
        if criteria['min_roi']:
            filtered_df = filtered_df[filtered_df['roi'] >= criteria['min_roi']]
        
        # Location filter (basic string matching)
        if criteria['location']:
            location_mask = filtered_df['property_address'].str.contains(
                criteria['location'], case=False, na=False
            )
            filtered_df = filtered_df[location_mask]
        
        return filtered_df
    
    def generate_investment_recommendations(self, investor_profile: Dict) -> List[Dict]:
        """Generate AI-powered investment recommendations"""
        
        try:
            conn = self.get_database_connection()
            
            # Get all available deals
            deals_df = pd.read_sql_query("""
                SELECT * FROM deals 
                WHERE status = 'analyzing' OR status = 'approved'
                ORDER BY deal_score DESC, roi DESC
            """, conn)
            
            # Get investor criteria if available
            investor_criteria_df = pd.read_sql_query("""
                SELECT * FROM investor_criteria 
                WHERE active = 1
                ORDER BY created_date DESC
            """, conn)
            
            conn.close()
            
            if deals_df.empty:
                return []
            
            # Score and rank deals based on investor profile
            scored_deals = self._score_deals_for_investor(deals_df, investor_profile)
            
            # Generate recommendations
            recommendations = []
            for _, deal in scored_deals.head(5).iterrows():
                recommendation = {
                    'deal_id': deal['id'],
                    'property_address': deal['property_address'],
                    'recommendation_score': deal['recommendation_score'],
                    'purchase_price': deal['purchase_price'],
                    'roi': deal['roi'],
                    'deal_type': deal['deal_type'],
                    'reasons': self._generate_recommendation_reasons(deal, investor_profile),
                    'potential_concerns': self._generate_potential_concerns(deal)
                }
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            st.error(f"Error generating recommendations: {e}")
            return []
    
    def _score_deals_for_investor(self, deals_df: pd.DataFrame, investor_profile: Dict) -> pd.DataFrame:
        """Score deals based on investor profile"""
        scored_df = deals_df.copy()
        
        # Initialize recommendation score
        scored_df['recommendation_score'] = 0.0
        
        # Preferred deal types
        preferred_types = investor_profile.get('preferred_deal_types', [])
        if preferred_types:
            type_mask = scored_df['deal_type'].isin(preferred_types)
            scored_df.loc[type_mask, 'recommendation_score'] += 20
        
        # ROI preferences
        min_roi = investor_profile.get('min_roi', 0)
        scored_df.loc[scored_df['roi'] >= min_roi, 'recommendation_score'] += 15
        scored_df.loc[scored_df['roi'] >= min_roi * 1.5, 'recommendation_score'] += 10
        
        # Price range preferences
        min_price = investor_profile.get('min_price', 0)
        max_price = investor_profile.get('max_price', float('inf'))
        price_mask = (scored_df['purchase_price'] >= min_price) & (scored_df['purchase_price'] <= max_price)
        scored_df.loc[price_mask, 'recommendation_score'] += 15
        
        # Cash flow preferences
        min_cash_flow = investor_profile.get('min_cash_flow', 0)
        monthly_cash_flow = scored_df['monthly_rent'] - scored_df['monthly_expenses']
        scored_df.loc[monthly_cash_flow >= min_cash_flow, 'recommendation_score'] += 10
        
        # Deal score bonus
        scored_df['recommendation_score'] += scored_df['deal_score'] * 0.3
        
        # Sort by recommendation score
        return scored_df.sort_values('recommendation_score', ascending=False)
    
    def _generate_recommendation_reasons(self, deal: pd.Series, investor_profile: Dict) -> List[str]:
        """Generate reasons for recommendation"""
        reasons = []
        
        if deal['roi'] > investor_profile.get('min_roi', 10):
            reasons.append(f"Strong ROI of {deal['roi']:.1f}% exceeds your minimum requirement")
        
        if deal['deal_type'] in investor_profile.get('preferred_deal_types', []):
            reasons.append(f"Matches your preferred deal type: {deal['deal_type']}")
        
        if deal['deal_score'] > 75:
            reasons.append(f"High deal score of {deal['deal_score']}/100 indicates strong fundamentals")
        
        monthly_cash_flow = deal['monthly_rent'] - deal['monthly_expenses']
        if monthly_cash_flow > 0:
            reasons.append(f"Positive monthly cash flow of ${monthly_cash_flow:,.2f}")
        
        if deal['cap_rate'] > 8:
            reasons.append(f"Attractive cap rate of {deal['cap_rate']:.1f}%")
        
        return reasons[:3]  # Limit to top 3 reasons
    
    def _generate_potential_concerns(self, deal: pd.Series) -> List[str]:
        """Generate potential concerns for a deal"""
        concerns = []
        
        if deal['roi'] < 10:
            concerns.append("ROI below 10% may not justify risk")
        
        if deal['deal_score'] < 60:
            concerns.append("Lower deal score suggests potential issues")
        
        monthly_cash_flow = deal['monthly_rent'] - deal['monthly_expenses']
        if monthly_cash_flow < 0:
            concerns.append("Negative cash flow requires additional funding")
        
        if deal['repair_costs'] > deal['purchase_price'] * 0.3:
            concerns.append("High repair costs relative to purchase price")
        
        return concerns[:2]  # Limit to top 2 concerns
    
    def automated_deal_scoring(self, deal_data: Dict) -> Dict:
        """Advanced AI-powered deal scoring"""
        
        try:
            # Base metrics
            purchase_price = deal_data.get('purchase_price', 0)
            arv = deal_data.get('after_repair_value', 0)
            repair_costs = deal_data.get('repair_costs', 0)
            monthly_rent = deal_data.get('monthly_rent', 0)
            monthly_expenses = deal_data.get('monthly_expenses', 0)
            
            # Calculate advanced metrics
            metrics = self._calculate_advanced_metrics(deal_data)
            
            # AI scoring algorithm
            score_components = {
                'profitability_score': self._score_profitability(metrics),
                'cash_flow_score': self._score_cash_flow(metrics),
                'market_score': self._score_market_factors(metrics),
                'risk_score': self._score_risk_factors(metrics),
                'location_score': self._score_location_factors(deal_data)
            }
            
            # Weighted overall score
            weights = {
                'profitability_score': 0.3,
                'cash_flow_score': 0.25,
                'market_score': 0.2,
                'risk_score': 0.15,
                'location_score': 0.1
            }
            
            overall_score = sum(score_components[component] * weights[component] 
                              for component in score_components)
            
            return {
                'overall_score': min(100, max(0, overall_score)),
                'component_scores': score_components,
                'metrics': metrics,
                'grade': self._get_deal_grade(overall_score),
                'confidence': self._calculate_confidence(deal_data)
            }
            
        except Exception as e:
            st.error(f"Error in automated scoring: {e}")
            return {'overall_score': 0, 'component_scores': {}, 'metrics': {}, 'grade': 'F', 'confidence': 0}
    
    def _calculate_advanced_metrics(self, deal_data: Dict) -> Dict:
        """Calculate advanced financial metrics"""
        purchase_price = deal_data.get('purchase_price', 0)
        arv = deal_data.get('after_repair_value', 0)
        repair_costs = deal_data.get('repair_costs', 0)
        monthly_rent = deal_data.get('monthly_rent', 0)
        monthly_expenses = deal_data.get('monthly_expenses', 0)
        
        # Prevent division by zero
        if purchase_price == 0:
            return {}
        
        total_investment = purchase_price + repair_costs
        annual_rent = monthly_rent * 12
        annual_expenses = monthly_expenses * 12
        net_annual_income = annual_rent - annual_expenses
        
        metrics = {
            'total_investment': total_investment,
            'annual_rent': annual_rent,
            'annual_expenses': annual_expenses,
            'net_annual_income': net_annual_income,
            'monthly_cash_flow': monthly_rent - monthly_expenses,
            'profit_potential': arv - total_investment,
            'profit_margin': ((arv - total_investment) / total_investment * 100) if total_investment > 0 else 0,
            'cap_rate': (net_annual_income / total_investment * 100) if total_investment > 0 else 0,
            'cash_on_cash': (net_annual_income / total_investment * 100) if total_investment > 0 else 0,
            'rent_to_price_ratio': (monthly_rent / purchase_price * 100) if purchase_price > 0 else 0,
            'arv_ratio': (arv / total_investment) if total_investment > 0 else 0,
            'repair_ratio': (repair_costs / purchase_price * 100) if purchase_price > 0 else 0
        }
        
        return metrics
    
    def _score_profitability(self, metrics: Dict) -> float:
        """Score deal profitability (0-100)"""
        if not metrics:
            return 0
        
        profit_margin = metrics.get('profit_margin', 0)
        cap_rate = metrics.get('cap_rate', 0)
        arv_ratio = metrics.get('arv_ratio', 0)
        
        # Profitability scoring
        score = 0
        
        # Profit margin scoring (40% weight)
        if profit_margin >= 30:
            score += 40
        elif profit_margin >= 20:
            score += 30
        elif profit_margin >= 10:
            score += 20
        elif profit_margin > 0:
            score += 10
        
        # Cap rate scoring (35% weight)
        if cap_rate >= 12:
            score += 35
        elif cap_rate >= 8:
            score += 25
        elif cap_rate >= 6:
            score += 15
        elif cap_rate > 0:
            score += 10
        
        # ARV ratio scoring (25% weight)
        if arv_ratio >= 1.3:
            score += 25
        elif arv_ratio >= 1.2:
            score += 20
        elif arv_ratio >= 1.1:
            score += 15
        elif arv_ratio > 1.0:
            score += 10
        
        return min(100, score)
    
    def _score_cash_flow(self, metrics: Dict) -> float:
        """Score cash flow potential (0-100)"""
        if not metrics:
            return 0
        
        monthly_cash_flow = metrics.get('monthly_cash_flow', 0)
        rent_to_price_ratio = metrics.get('rent_to_price_ratio', 0)
        
        score = 0
        
        # Monthly cash flow scoring (70% weight)
        if monthly_cash_flow >= 500:
            score += 70
        elif monthly_cash_flow >= 300:
            score += 55
        elif monthly_cash_flow >= 100:
            score += 40
        elif monthly_cash_flow > 0:
            score += 25
        elif monthly_cash_flow >= -100:
            score += 10
        
        # Rent-to-price ratio scoring (30% weight)
        if rent_to_price_ratio >= 1.5:
            score += 30
        elif rent_to_price_ratio >= 1.0:
            score += 20
        elif rent_to_price_ratio >= 0.8:
            score += 15
        elif rent_to_price_ratio > 0:
            score += 10
        
        return min(100, score)
    
    def _score_market_factors(self, metrics: Dict) -> float:
        """Score market factors (0-100)"""
        # This would integrate with market data in a real implementation
        # For now, return a baseline score
        return 70
    
    def _score_risk_factors(self, metrics: Dict) -> float:
        """Score risk factors (0-100, higher = lower risk)"""
        if not metrics:
            return 50
        
        repair_ratio = metrics.get('repair_ratio', 0)
        monthly_cash_flow = metrics.get('monthly_cash_flow', 0)
        
        score = 100  # Start with perfect score, deduct for risks
        
        # High repair costs increase risk
        if repair_ratio > 50:
            score -= 40
        elif repair_ratio > 30:
            score -= 25
        elif repair_ratio > 20:
            score -= 15
        
        # Negative cash flow increases risk
        if monthly_cash_flow < -200:
            score -= 30
        elif monthly_cash_flow < 0:
            score -= 15
        
        return max(0, score)
    
    def _score_location_factors(self, deal_data: Dict) -> float:
        """Score location factors (0-100)"""
        # This would integrate with location data APIs in a real implementation
        # For now, return a baseline score based on available data
        return 75
    
    def _get_deal_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        elif score >= 45:
            return 'D+'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def _calculate_confidence(self, deal_data: Dict) -> float:
        """Calculate confidence level of analysis"""
        # Base confidence on data completeness
        required_fields = ['purchase_price', 'after_repair_value', 'repair_costs', 'monthly_rent']
        provided_fields = sum(1 for field in required_fields if deal_data.get(field, 0) > 0)
        
        base_confidence = provided_fields / len(required_fields)
        
        # Boost confidence if we have additional data
        if deal_data.get('property_details'):
            base_confidence += 0.1
        if deal_data.get('market_analysis'):
            base_confidence += 0.1
        
        return min(1.0, base_confidence)

def show_ai_enhancement_system():
    """Main function to display AI Enhancement System"""
    st.header("🤖 AI Enhancement System")
    st.subheader("Advanced AI-powered features for intelligent deal analysis")
    
    # Initialize AI system
    if 'ai_system' not in st.session_state:
        st.session_state.ai_system = AIEnhancementSystem()
    
    ai_system = st.session_state.ai_system
    
    # Sidebar for AI configuration
    with st.sidebar:
        st.subheader("🔧 AI Configuration")
        
        # OpenAI API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get("openai_api_key", ""),
            help="Enter your OpenAI API key for advanced AI features"
        )
        
        if api_key:
            st.session_state.openai_api_key = api_key
            ai_system.setup_openai()
            st.success("✅ AI Ready")
        else:
            st.warning("⚠️ Limited AI features without API key")
    
    # Main AI features tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Smart Deal Analysis",
        "🗣️ Natural Language Search", 
        "💡 Investment Recommendations",
        "📊 Advanced Scoring",
        "📋 AI Insights Dashboard"
    ])
    
    with tab1:
        show_smart_deal_analysis(ai_system)
    
    with tab2:
        show_natural_language_search(ai_system)
    
    with tab3:
        show_investment_recommendations(ai_system)
    
    with tab4:
        show_advanced_scoring(ai_system)
    
    with tab5:
        show_ai_insights_dashboard(ai_system)

def show_smart_deal_analysis(ai_system: AIEnhancementSystem):
    """Smart Deal Analysis tab"""
    st.subheader("🔍 Smart Deal Analysis")
    
    # Get available deals
    try:
        conn = ai_system.get_database_connection()
        deals_df = pd.read_sql_query("""
            SELECT id, property_address, purchase_price, deal_type, status 
            FROM deals 
            ORDER BY created_at DESC
        """, conn)
        conn.close()
        
        if not deals_df.empty:
            # Deal selection
            selected_deal_id = st.selectbox(
                "Select Deal for AI Analysis",
                options=deals_df['id'].tolist(),
                format_func=lambda x: f"{deals_df[deals_df['id']==x]['property_address'].iloc[0]} - ${deals_df[deals_df['id']==x]['purchase_price'].iloc[0]:,.0f}"
            )
            
            if st.button("🤖 Run AI Analysis", type="primary"):
                with st.spinner("Analyzing deal with AI..."):
                    # Get full deal data
                    conn = ai_system.get_database_connection()
                    deal_data = pd.read_sql_query(
                        "SELECT * FROM deals WHERE id = ?", 
                        conn, 
                        params=[selected_deal_id]
                    ).iloc[0].to_dict()
                    conn.close()
                    
                    # Run AI analysis
                    analysis_result = ai_system.analyze_deal_with_ai(deal_data)
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Overall Score", f"{analysis_result.overall_score}/100")
                    with col2:
                        st.metric("Confidence", f"{analysis_result.confidence_score:.0%}")
                    with col3:
                        st.metric("Analysis Type", analysis_result.analysis_type.replace('_', ' ').title())
                    
                    # Recommendations
                    if analysis_result.recommendations:
                        st.subheader("💡 Recommendations")
                        for rec in analysis_result.recommendations:
                            st.success(f"✅ {rec}")
                    
                    # Risk Factors
                    if analysis_result.risk_factors:
                        st.subheader("⚠️ Risk Factors")
                        for risk in analysis_result.risk_factors:
                            st.warning(f"⚠️ {risk}")
                    
                    # Opportunities
                    if analysis_result.opportunities:
                        st.subheader("🎯 Opportunities")
                        for opp in analysis_result.opportunities:
                            st.info(f"🎯 {opp}")
                    
                    # Market Insights
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📊 Market Insights")
                        for key, value in analysis_result.market_insights.items():
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                    
                    with col2:
                        st.subheader("💰 Financial Analysis")
                        for key, value in analysis_result.financial_analysis.items():
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            st.info("No deals available for analysis. Add some deals first!")
            
    except Exception as e:
        st.error(f"Error loading deals: {e}")

def show_natural_language_search(ai_system: AIEnhancementSystem):
    """Natural Language Search tab"""
    st.subheader("🗣️ Natural Language Property Search")
    st.write("Search for properties using natural language queries!")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.write("Try these example searches:")
        examples = [
            "Show me rental properties under $200k with good cash flow",
            "Find flips with over 15% ROI in good neighborhoods", 
            "Properties between $100k and $300k for BRRRR strategy",
            "High cap rate deals above 8% with low repair costs",
            "Wholesale deals under $150k with quick profit potential"
        ]
        for example in examples:
            if st.button(f"📝 {example}", key=f"example_{example[:20]}"):
                st.session_state.search_query = example
    
    # Search input
    search_query = st.text_input(
        "Enter your property search query:",
        value=st.session_state.get('search_query', ''),
        placeholder="e.g., 'Show me rental properties under $200k with good cash flow'"
    )
    
    if search_query:
        with st.spinner("Searching properties..."):
            results = ai_system.natural_language_property_search(search_query)
            
            if results:
                st.success(f"Found {len(results)} matching properties:")
                
                # Display results
                for i, property_data in enumerate(results):
                    with st.expander(f"🏠 {property_data['property_address']} - ${property_data['purchase_price']:,.0f}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Deal Type:** {property_data['deal_type']}")
                            st.write(f"**Status:** {property_data['status']}")
                            st.write(f"**Purchase Price:** ${property_data['purchase_price']:,.0f}")
                        
                        with col2:
                            st.write(f"**ARV:** ${property_data['after_repair_value']:,.0f}")
                            st.write(f"**Repair Costs:** ${property_data['repair_costs']:,.0f}")
                            st.write(f"**Monthly Rent:** ${property_data['monthly_rent']:,.0f}")
                        
                        with col3:
                            st.write(f"**ROI:** {property_data['roi']:.1f}%")
                            st.write(f"**Deal Score:** {property_data['deal_score']}/100")
                            st.write(f"**Cap Rate:** {property_data['cap_rate']:.1f}%")
                        
                        if st.button(f"View Details", key=f"details_{property_data['id']}"):
                            st.session_state.selected_deal_id = property_data['id']
                            st.experimental_rerun()
            else:
                st.info("No properties found matching your search criteria. Try adjusting your query.")

def show_investment_recommendations(ai_system: AIEnhancementSystem):
    """Investment Recommendations tab"""
    st.subheader("💡 AI Investment Recommendations")
    
    # Investor profile setup
    with st.expander("👤 Set Your Investment Profile"):
        col1, col2 = st.columns(2)
        
        with col1:
            min_roi = st.number_input("Minimum ROI (%)", min_value=0.0, max_value=50.0, value=12.0, step=0.5)
            min_price = st.number_input("Minimum Price ($)", min_value=0, value=50000, step=5000)
            max_price = st.number_input("Maximum Price ($)", min_value=0, value=300000, step=10000)
        
        with col2:
            min_cash_flow = st.number_input("Minimum Monthly Cash Flow ($)", min_value=-1000, value=200, step=50)
            preferred_types = st.multiselect(
                "Preferred Deal Types",
                ["flip", "rental", "wholesale", "brrrr"],
                default=["rental", "flip"]
            )
    
    investor_profile = {
        'min_roi': min_roi,
        'min_price': min_price,
        'max_price': max_price,
        'min_cash_flow': min_cash_flow,
        'preferred_deal_types': preferred_types
    }
    
    if st.button("🎯 Get AI Recommendations", type="primary"):
        with st.spinner("Generating personalized recommendations..."):
            recommendations = ai_system.generate_investment_recommendations(investor_profile)
            
            if recommendations:
                st.success(f"Found {len(recommendations)} recommended deals for you!")
                
                for i, rec in enumerate(recommendations):
                    with st.container():
                        st.divider()
                        
                        # Header with score
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.subheader(f"🏠 {rec['property_address']}")
                        with col2:
                            score_color = "green" if rec['recommendation_score'] > 70 else "orange" if rec['recommendation_score'] > 50 else "red"
                            st.markdown(f"<h3 style='color: {score_color}'>Score: {rec['recommendation_score']:.0f}/100</h3>", unsafe_allow_html=True)
                        
                        # Key metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Price", f"${rec['purchase_price']:,.0f}")
                        with col2:
                            st.metric("ROI", f"{rec['roi']:.1f}%")
                        with col3:
                            st.metric("Type", rec['deal_type'].title())
                        with col4:
                            st.button("View Deal", key=f"view_rec_{rec['deal_id']}")
                        
                        # Reasons and concerns
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Why We Recommend This:**")
                            for reason in rec['reasons']:
                                st.write(f"✅ {reason}")
                        
                        with col2:
                            if rec['potential_concerns']:
                                st.write("**Potential Concerns:**")
                                for concern in rec['potential_concerns']:
                                    st.write(f"⚠️ {concern}")
            else:
                st.info("No recommendations available based on your criteria. Try adjusting your preferences.")

def show_advanced_scoring(ai_system: AIEnhancementSystem):
    """Advanced Scoring tab"""
    st.subheader("📊 Advanced AI Deal Scoring")
    
    # Manual deal input for scoring
    with st.expander("📝 Enter Deal Details for Scoring"):
        col1, col2 = st.columns(2)
        
        with col1:
            address = st.text_input("Property Address")
            purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=150000)
            arv = st.number_input("After Repair Value ($)", min_value=0, value=200000)
            repair_costs = st.number_input("Repair Costs ($)", min_value=0, value=25000)
        
        with col2:
            monthly_rent = st.number_input("Monthly Rent ($)", min_value=0, value=1500)
            monthly_expenses = st.number_input("Monthly Expenses ($)", min_value=0, value=600)
            deal_type = st.selectbox("Deal Type", ["flip", "rental", "wholesale", "brrrr"])
        
        deal_data = {
            'property_address': address,
            'purchase_price': purchase_price,
            'after_repair_value': arv,
            'repair_costs': repair_costs,
            'monthly_rent': monthly_rent,
            'monthly_expenses': monthly_expenses,
            'deal_type': deal_type
        }
        
        if st.button("🎯 Score This Deal", type="primary"):
            with st.spinner("Calculating advanced scores..."):
                scoring_result = ai_system.automated_deal_scoring(deal_data)
                
                # Main score display
                col1, col2, col3 = st.columns(3)
                with col1:
                    score_color = "green" if scoring_result['overall_score'] > 75 else "orange" if scoring_result['overall_score'] > 50 else "red"
                    st.markdown(f"<h1 style='color: {score_color}; text-align: center'>{scoring_result['overall_score']:.0f}/100</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='text-align: center'>Grade: {scoring_result['grade']}</h3>", unsafe_allow_html=True)
                
                with col2:
                    st.metric("Confidence Level", f"{scoring_result['confidence']:.0%}")
                
                with col3:
                    # Component scores chart
                    if scoring_result['component_scores']:
                        fig = go.Figure(data=[
                            go.Bar(
                                x=list(scoring_result['component_scores'].keys()),
                                y=list(scoring_result['component_scores'].values()),
                                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                            )
                        ])
                        fig.update_layout(
                            title="Score Components",
                            xaxis_title="Component",
                            yaxis_title="Score",
                            height=300
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Detailed metrics
                if scoring_result['metrics']:
                    st.subheader("📊 Detailed Financial Metrics")
                    metrics_df = pd.DataFrame([scoring_result['metrics']]).T
                    metrics_df.columns = ['Value']
                    
                    # Format financial values
                    financial_fields = ['total_investment', 'annual_rent', 'annual_expenses', 'net_annual_income', 'monthly_cash_flow', 'profit_potential']
                    for field in financial_fields:
                        if field in metrics_df.index:
                            metrics_df.loc[field, 'Value'] = f"${metrics_df.loc[field, 'Value']:,.2f}"
                    
                    # Format percentage values
                    percentage_fields = ['profit_margin', 'cap_rate', 'cash_on_cash', 'rent_to_price_ratio', 'repair_ratio']
                    for field in percentage_fields:
                        if field in metrics_df.index:
                            metrics_df.loc[field, 'Value'] = f"{metrics_df.loc[field, 'Value']:.2f}%"
                    
                    st.dataframe(metrics_df, use_container_width=True)

def show_ai_insights_dashboard(ai_system: AIEnhancementSystem):
    """AI Insights Dashboard tab"""
    st.subheader("📋 AI Insights Dashboard")
    
    try:
        conn = ai_system.get_database_connection()
        
        # Get deals data
        deals_df = pd.read_sql_query("""
            SELECT * FROM deals 
            ORDER BY created_at DESC
        """, conn)
        
        conn.close()
        
        if not deals_df.empty:
            # Overall portfolio insights
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_roi = deals_df['roi'].mean()
                st.metric("Average ROI", f"{avg_roi:.1f}%")
            
            with col2:
                total_deals = len(deals_df)
                st.metric("Total Deals", total_deals)
            
            with col3:
                approved_deals = len(deals_df[deals_df['status'] == 'approved'])
                approval_rate = (approved_deals / total_deals * 100) if total_deals > 0 else 0
                st.metric("Approval Rate", f"{approval_rate:.1f}%")
            
            with col4:
                avg_score = deals_df['deal_score'].mean()
                st.metric("Average Deal Score", f"{avg_score:.0f}/100")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # ROI distribution
                fig = px.histogram(
                    deals_df, 
                    x='roi', 
                    title='ROI Distribution',
                    bins=20,
                    labels={'roi': 'ROI (%)', 'count': 'Number of Deals'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Deal types
                deal_type_counts = deals_df['deal_type'].value_counts()
                fig = px.pie(
                    values=deal_type_counts.values,
                    names=deal_type_counts.index,
                    title='Deal Types Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Top performing deals
            st.subheader("🏆 Top Performing Deals")
            top_deals = deals_df.nlargest(5, 'deal_score')[
                ['property_address', 'deal_type', 'purchase_price', 'roi', 'deal_score', 'status']
            ]
            st.dataframe(top_deals, use_container_width=True)
            
            # Deal status timeline
            if 'created_at' in deals_df.columns:
                deals_df['created_at'] = pd.to_datetime(deals_df['created_at'])
                deals_df['month'] = deals_df['created_at'].dt.to_period('M')
                
                monthly_deals = deals_df.groupby(['month', 'status']).size().unstack(fill_value=0)
                
                fig = go.Figure()
                for status in monthly_deals.columns:
                    fig.add_trace(go.Scatter(
                        x=monthly_deals.index.astype(str),
                        y=monthly_deals[status],
                        mode='lines+markers',
                        name=status.title()
                    ))
                
                fig.update_layout(
                    title='Deal Activity Timeline',
                    xaxis_title='Month',
                    yaxis_title='Number of Deals'
                )
                st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("No deal data available for insights. Add some deals to see AI-powered analytics!")
            
    except Exception as e:
        st.error(f"Error generating insights: {e}")

if __name__ == "__main__":
    show_ai_enhancement_system()