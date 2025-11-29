"""
Advanced Analytics and AI Engine for NXTRIX CRM
Implements machine learning, predictive analytics, and intelligent insights
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
import pickle
import os
from dataclasses import dataclass

@dataclass
class MarketPrediction:
    property_type: str
    location: str
    predicted_price: float
    confidence_score: float
    market_trend: str
    risk_factors: List[str]
    opportunities: List[str]

@dataclass
class DealScore:
    overall_score: int
    financial_score: int
    market_score: int
    risk_score: int
    breakdown: Dict[str, float]
    recommendations: List[str]

class AdvancedAnalyticsEngine:
    """Advanced AI-powered analytics engine"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_metadata = {}
        self.load_or_train_models()
    
    def load_or_train_models(self):
        """Load existing models or train new ones"""
        model_files = [
            'price_prediction_model.pkl',
            'ai_score_model.pkl',
            'market_trend_model.pkl'
        ]
        
        models_exist = all(os.path.exists(f'models/{f}') for f in model_files)
        
        if not models_exist:
            self.train_models()
        else:
            self.load_models()
    
    def train_models(self):
        """Train ML models on historical data"""
        st.info("🤖 Training AI models... This may take a moment.")
        os.makedirs('models', exist_ok=True)
        
        # Generate synthetic training data (in production, use real data)
        training_data = self._generate_training_data()
        
        # Train price prediction model
        self._train_price_prediction_model(training_data)
        
        # Train AI scoring model
        self._train_ai_scoring_model(training_data)
        
        # Train market trend model
        self._train_market_trend_model(training_data)
        
        st.success("✅ AI models trained successfully!")
    
    def _generate_training_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """Generate synthetic training data for model training"""
        np.random.seed(42)
        
        property_types = ['Single Family', 'Multi-Family', 'Condo', 'Townhouse', 'Commercial']
        locations = ['Downtown', 'Suburbs', 'Urban', 'Rural', 'Waterfront']
        conditions = ['Excellent', 'Good', 'Fair', 'Poor']
        
        data = []
        for _ in range(n_samples):
            property_type = np.random.choice(property_types)
            location = np.random.choice(locations)
            condition = np.random.choice(conditions)
            
            # Base price influenced by property type and location
            base_price = {
                'Single Family': 300000,
                'Multi-Family': 500000,
                'Condo': 250000,
                'Townhouse': 350000,
                'Commercial': 800000
            }[property_type]
            
            location_multiplier = {
                'Downtown': 1.3,
                'Suburbs': 1.0,
                'Urban': 1.2,
                'Rural': 0.8,
                'Waterfront': 1.5
            }[location]
            
            condition_multiplier = {
                'Excellent': 1.1,
                'Good': 1.0,
                'Fair': 0.9,
                'Poor': 0.7
            }[condition]
            
            bedrooms = np.random.randint(1, 6)
            bathrooms = np.random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4])
            square_feet = np.random.randint(800, 4000)
            year_built = np.random.randint(1950, 2024)
            
            # Calculate price with some noise
            price = base_price * location_multiplier * condition_multiplier
            price += (bedrooms * 25000) + (bathrooms * 15000) + (square_feet * 50)
            price += np.random.normal(0, 50000)  # Add noise
            price = max(price, 50000)  # Minimum price
            
            # Calculate AI score based on various factors
            roi_potential = np.random.normal(15, 5)  # 15% average ROI
            market_strength = np.random.uniform(0.5, 1.0)
            condition_score = {'Excellent': 95, 'Good': 80, 'Fair': 65, 'Poor': 40}[condition]
            location_score = {'Downtown': 90, 'Suburbs': 75, 'Urban': 85, 'Rural': 60, 'Waterfront': 95}[location]
            
            ai_score = (roi_potential * 2) + (market_strength * 30) + (condition_score * 0.3) + (location_score * 0.2)
            ai_score = np.clip(ai_score, 0, 100)
            
            # Market trend
            trend_prob = np.random.random()
            market_trend = 'Rising' if trend_prob > 0.6 else 'Stable' if trend_prob > 0.3 else 'Declining'
            
            data.append({
                'property_type': property_type,
                'location': location,
                'condition': condition,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'square_feet': square_feet,
                'year_built': year_built,
                'price': price,
                'ai_score': ai_score,
                'market_trend': market_trend,
                'roi_potential': roi_potential
            })
        
        return pd.DataFrame(data)
    
    def _train_price_prediction_model(self, data: pd.DataFrame):
        """Train price prediction model"""
        # Prepare features
        features = ['bedrooms', 'bathrooms', 'square_feet', 'year_built']
        categorical_features = ['property_type', 'location', 'condition']
        
        X = data[features].copy()
        
        # Encode categorical variables
        for feature in categorical_features:
            le = LabelEncoder()
            X[f'{feature}_encoded'] = le.fit_transform(data[feature])
            self.encoders[f'price_{feature}'] = le
        
        # Scale numerical features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['price_prediction'] = scaler
        
        y = data['price']
        
        # Train model
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        # Calculate performance metrics
        y_pred = model.predict(X_scaled)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        self.models['price_prediction'] = model
        self.model_metadata['price_prediction'] = {
            'mae': mae,
            'r2_score': r2,
            'features': list(X.columns),
            'trained_at': datetime.now()
        }
        
        # Save model
        with open('models/price_prediction_model.pkl', 'wb') as f:
            pickle.dump({
                'model': model,
                'scaler': scaler,
                'encoders': {k: v for k, v in self.encoders.items() if k.startswith('price_')},
                'metadata': self.model_metadata['price_prediction']
            }, f)
    
    def _train_ai_scoring_model(self, data: pd.DataFrame):
        """Train AI scoring model"""
        features = ['bedrooms', 'bathrooms', 'square_feet', 'year_built', 'price', 'roi_potential']
        categorical_features = ['property_type', 'location', 'condition']
        
        X = data[features].copy()
        
        # Encode categorical variables
        for feature in categorical_features:
            if f'score_{feature}' not in self.encoders:
                le = LabelEncoder()
                self.encoders[f'score_{feature}'] = le
            else:
                le = self.encoders[f'score_{feature}']
            X[f'{feature}_encoded'] = le.fit_transform(data[feature])
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['ai_scoring'] = scaler
        
        y = data['ai_score']
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        self.models['ai_scoring'] = model
        
        # Save model
        with open('models/ai_score_model.pkl', 'wb') as f:
            pickle.dump({
                'model': model,
                'scaler': scaler,
                'encoders': {k: v for k, v in self.encoders.items() if k.startswith('score_')},
                'features': list(X.columns)
            }, f)
    
    def _train_market_trend_model(self, data: pd.DataFrame):
        """Train market trend prediction model"""
        from sklearn.ensemble import RandomForestClassifier
        
        features = ['price', 'ai_score', 'roi_potential', 'year_built']
        categorical_features = ['property_type', 'location']
        
        X = data[features].copy()
        
        # Encode categorical variables
        for feature in categorical_features:
            if f'trend_{feature}' not in self.encoders:
                le = LabelEncoder()
                self.encoders[f'trend_{feature}'] = le
            else:
                le = self.encoders[f'trend_{feature}']
            X[f'{feature}_encoded'] = le.fit_transform(data[feature])
        
        # Encode target variable
        le_target = LabelEncoder()
        y = le_target.fit_transform(data['market_trend'])
        self.encoders['market_trend_target'] = le_target
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['market_trend'] = scaler
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        self.models['market_trend'] = model
        
        # Save model
        with open('models/market_trend_model.pkl', 'wb') as f:
            pickle.dump({
                'model': model,
                'scaler': scaler,
                'encoders': {k: v for k, v in self.encoders.items() if k.startswith('trend_')},
                'target_encoder': le_target,
                'features': list(X.columns)
            }, f)
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            # Load price prediction model
            with open('models/price_prediction_model.pkl', 'rb') as f:
                price_data = pickle.load(f)
                self.models['price_prediction'] = price_data['model']
                self.scalers['price_prediction'] = price_data['scaler']
                self.encoders.update(price_data['encoders'])
                self.model_metadata['price_prediction'] = price_data['metadata']
            
            # Load AI scoring model
            with open('models/ai_score_model.pkl', 'rb') as f:
                score_data = pickle.load(f)
                self.models['ai_scoring'] = score_data['model']
                self.scalers['ai_scoring'] = score_data['scaler']
                self.encoders.update(score_data['encoders'])
            
            # Load market trend model
            with open('models/market_trend_model.pkl', 'rb') as f:
                trend_data = pickle.load(f)
                self.models['market_trend'] = trend_data['model']
                self.scalers['market_trend'] = trend_data['scaler']
                self.encoders.update(trend_data['encoders'])
                self.encoders['market_trend_target'] = trend_data['target_encoder']
        
        except Exception as e:
            st.error(f"Error loading models: {e}")
            self.train_models()
    
    def predict_property_price(self, property_data: Dict[str, Any]) -> MarketPrediction:
        """Predict property price using ML model"""
        try:
            model = self.models['price_prediction']
            scaler = self.scalers['price_prediction']
            
            # Prepare features
            features = pd.DataFrame([{
                'bedrooms': property_data.get('bedrooms', 3),
                'bathrooms': property_data.get('bathrooms', 2),
                'square_feet': property_data.get('square_feet', 1500),
                'year_built': property_data.get('year_built', 2000),
                'property_type_encoded': self.encoders['price_property_type'].transform([property_data.get('property_type', 'Single Family')])[0],
                'location_encoded': self.encoders['price_location'].transform([property_data.get('location', 'Suburbs')])[0],
                'condition_encoded': self.encoders['price_condition'].transform([property_data.get('condition', 'Good')])[0]
            }])
            
            # Scale features
            features_scaled = scaler.transform(features)
            
            # Make prediction
            predicted_price = model.predict(features_scaled)[0]
            
            # Calculate confidence score based on model performance
            confidence = max(0.6, min(0.95, self.model_metadata['price_prediction']['r2_score']))
            
            # Determine market trend
            trend = self.predict_market_trend(property_data)
            
            # Generate insights
            risk_factors = self._identify_risk_factors(property_data, predicted_price)
            opportunities = self._identify_opportunities(property_data, predicted_price)
            
            return MarketPrediction(
                property_type=property_data.get('property_type', 'Single Family'),
                location=property_data.get('location', 'Suburbs'),
                predicted_price=predicted_price,
                confidence_score=confidence,
                market_trend=trend,
                risk_factors=risk_factors,
                opportunities=opportunities
            )
        
        except Exception as e:
            st.error(f"Error predicting price: {e}")
            return None
    
    def calculate_advanced_ai_score(self, deal_data: Dict[str, Any]) -> DealScore:
        """Calculate advanced AI score with detailed breakdown"""
        try:
            model = self.models['ai_scoring']
            scaler = self.scalers['ai_scoring']
            
            # Prepare features
            features = pd.DataFrame([{
                'bedrooms': deal_data.get('bedrooms', 3),
                'bathrooms': deal_data.get('bathrooms', 2),
                'square_feet': deal_data.get('square_feet', 1500),
                'year_built': deal_data.get('year_built', 2000),
                'price': deal_data.get('purchase_price', 200000),
                'roi_potential': self._calculate_roi_potential(deal_data),
                'property_type_encoded': self.encoders['score_property_type'].transform([deal_data.get('property_type', 'Single Family')])[0],
                'location_encoded': self.encoders['score_location'].transform([deal_data.get('location', 'Suburbs')])[0],
                'condition_encoded': self.encoders['score_condition'].transform([deal_data.get('condition', 'Good')])[0]
            }])
            
            # Scale features
            features_scaled = scaler.transform(features)
            
            # Make prediction
            overall_score = int(model.predict(features_scaled)[0])
            
            # Calculate component scores
            financial_score = self._calculate_financial_score(deal_data)
            market_score = self._calculate_market_score(deal_data)
            risk_score = self._calculate_risk_score(deal_data)
            
            # Detailed breakdown
            breakdown = {
                'Financial Performance': financial_score,
                'Market Conditions': market_score,
                'Risk Assessment': risk_score,
                'Property Condition': self._score_property_condition(deal_data.get('condition', 'Good')),
                'Location Quality': self._score_location(deal_data.get('location', 'Suburbs'))
            }
            
            # Generate recommendations
            recommendations = self._generate_deal_recommendations(deal_data, overall_score, breakdown)
            
            return DealScore(
                overall_score=overall_score,
                financial_score=financial_score,
                market_score=market_score,
                risk_score=risk_score,
                breakdown=breakdown,
                recommendations=recommendations
            )
        
        except Exception as e:
            st.error(f"Error calculating AI score: {e}")
            return None
    
    def predict_market_trend(self, property_data: Dict[str, Any]) -> str:
        """Predict market trend for property"""
        try:
            model = self.models['market_trend']
            scaler = self.scalers['market_trend']
            encoder = self.encoders['market_trend_target']
            
            # Prepare features
            features = pd.DataFrame([{
                'price': property_data.get('purchase_price', 200000),
                'ai_score': property_data.get('ai_score', 75),
                'roi_potential': self._calculate_roi_potential(property_data),
                'year_built': property_data.get('year_built', 2000),
                'property_type_encoded': self.encoders['trend_property_type'].transform([property_data.get('property_type', 'Single Family')])[0],
                'location_encoded': self.encoders['trend_location'].transform([property_data.get('location', 'Suburbs')])[0]
            }])
            
            # Scale features
            features_scaled = scaler.transform(features)
            
            # Make prediction
            trend_encoded = model.predict(features_scaled)[0]
            trend = encoder.inverse_transform([trend_encoded])[0]
            
            return trend
        
        except Exception as e:
            return 'Stable'  # Default fallback
    
    def _calculate_roi_potential(self, deal_data: Dict[str, Any]) -> float:
        """Calculate ROI potential"""
        purchase_price = deal_data.get('purchase_price', 200000)
        monthly_rent = deal_data.get('monthly_rent', 1500)
        repair_costs = deal_data.get('repair_costs', 10000)
        
        annual_rent = monthly_rent * 12
        total_investment = purchase_price + repair_costs
        
        if total_investment > 0:
            return (annual_rent / total_investment) * 100
        return 0
    
    def _calculate_financial_score(self, deal_data: Dict[str, Any]) -> int:
        """Calculate financial component score"""
        roi = self._calculate_roi_potential(deal_data)
        
        # Score based on ROI potential
        if roi >= 15:
            return 95
        elif roi >= 12:
            return 85
        elif roi >= 10:
            return 75
        elif roi >= 8:
            return 65
        else:
            return 50
    
    def _calculate_market_score(self, deal_data: Dict[str, Any]) -> int:
        """Calculate market component score"""
        location = deal_data.get('location', 'Suburbs')
        property_type = deal_data.get('property_type', 'Single Family')
        
        location_scores = {
            'Downtown': 90,
            'Urban': 85,
            'Waterfront': 95,
            'Suburbs': 75,
            'Rural': 60
        }
        
        type_scores = {
            'Single Family': 80,
            'Multi-Family': 85,
            'Commercial': 75,
            'Condo': 70,
            'Townhouse': 75
        }
        
        return int((location_scores.get(location, 75) + type_scores.get(property_type, 75)) / 2)
    
    def _calculate_risk_score(self, deal_data: Dict[str, Any]) -> int:
        """Calculate risk component score (higher = lower risk)"""
        condition = deal_data.get('condition', 'Good')
        year_built = deal_data.get('year_built', 2000)
        current_year = datetime.now().year
        
        condition_scores = {
            'Excellent': 95,
            'Good': 80,
            'Fair': 60,
            'Poor': 30
        }
        
        # Age factor
        age = current_year - year_built
        age_score = max(40, 100 - (age * 0.5))
        
        return int((condition_scores.get(condition, 80) + age_score) / 2)
    
    def _score_property_condition(self, condition: str) -> float:
        """Score property condition"""
        scores = {'Excellent': 95, 'Good': 80, 'Fair': 65, 'Poor': 40}
        return scores.get(condition, 75)
    
    def _score_location(self, location: str) -> float:
        """Score location quality"""
        scores = {'Downtown': 90, 'Urban': 85, 'Waterfront': 95, 'Suburbs': 75, 'Rural': 60}
        return scores.get(location, 75)
    
    def _identify_risk_factors(self, property_data: Dict[str, Any], predicted_price: float) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Age-related risks
        year_built = property_data.get('year_built', 2000)
        current_year = datetime.now().year
        age = current_year - year_built
        
        if age > 40:
            risks.append("Property age may require significant maintenance")
        
        # Market risks
        if property_data.get('condition') == 'Poor':
            risks.append("Poor condition increases renovation costs")
        
        # Financial risks
        purchase_price = property_data.get('purchase_price', 200000)
        if purchase_price > predicted_price * 1.1:
            risks.append("Purchase price above market prediction")
        
        return risks
    
    def _identify_opportunities(self, property_data: Dict[str, Any], predicted_price: float) -> List[str]:
        """Identify potential opportunities"""
        opportunities = []
        
        # Price opportunities
        purchase_price = property_data.get('purchase_price', 200000)
        if purchase_price < predicted_price * 0.9:
            opportunities.append("Below-market purchase price")
        
        # Location opportunities
        if property_data.get('location') in ['Downtown', 'Waterfront']:
            opportunities.append("Prime location with appreciation potential")
        
        # Condition opportunities
        if property_data.get('condition') == 'Fair':
            opportunities.append("Value-add renovation opportunity")
        
        return opportunities
    
    def _generate_deal_recommendations(self, deal_data: Dict[str, Any], overall_score: int, breakdown: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if overall_score >= 85:
            recommendations.append("✅ Excellent deal - proceed with confidence")
        elif overall_score >= 70:
            recommendations.append("👍 Good deal with solid fundamentals")
        elif overall_score >= 60:
            recommendations.append("⚠️ Average deal - negotiate better terms")
        else:
            recommendations.append("❌ Below-average deal - consider passing")
        
        # Specific recommendations based on component scores
        if breakdown['Financial Performance'] < 70:
            recommendations.append("💰 Negotiate purchase price or rental rates")
        
        if breakdown['Risk Assessment'] < 70:
            recommendations.append("🔍 Conduct thorough property inspection")
        
        if breakdown['Market Conditions'] < 70:
            recommendations.append("📊 Research local market trends carefully")
        
        return recommendations

# Global analytics engine
@st.cache_resource
def get_analytics_engine():
    """Get or create analytics engine instance"""
    return AdvancedAnalyticsEngine()

def show_advanced_analytics_dashboard():
    """Show advanced analytics dashboard"""
    st.subheader("🤖 Advanced AI Analytics")
    
    engine = get_analytics_engine()
    
    # Model performance metrics
    with st.expander("📊 Model Performance"):
        if 'price_prediction' in engine.model_metadata:
            metadata = engine.model_metadata['price_prediction']
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Price Model R²", f"{metadata['r2_score']:.3f}")
            with col2:
                st.metric("Mean Absolute Error", f"${metadata['mae']:,.0f}")
            with col3:
                st.metric("Last Trained", metadata['trained_at'].strftime('%Y-%m-%d'))
    
    # Interactive prediction tool
    st.subheader("🔮 Property Price Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        property_type = st.selectbox("Property Type", ['Single Family', 'Multi-Family', 'Condo', 'Townhouse', 'Commercial'])
        location = st.selectbox("Location", ['Downtown', 'Suburbs', 'Urban', 'Rural', 'Waterfront'])
        condition = st.selectbox("Condition", ['Excellent', 'Good', 'Fair', 'Poor'])
        
    with col2:
        bedrooms = st.number_input("Bedrooms", 1, 10, 3)
        bathrooms = st.number_input("Bathrooms", 1.0, 8.0, 2.0, 0.5)
        square_feet = st.number_input("Square Feet", 500, 8000, 1500)
        year_built = st.number_input("Year Built", 1900, 2024, 2000)
    
    if st.button("🔮 Predict Price", type="primary"):
        property_data = {
            'property_type': property_type,
            'location': location,
            'condition': condition,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'square_feet': square_feet,
            'year_built': year_built
        }
        
        prediction = engine.predict_property_price(property_data)
        
        if prediction:
            st.success(f"🎯 Predicted Price: **${prediction.predicted_price:,.0f}**")
            st.info(f"📊 Confidence: **{prediction.confidence_score:.1%}**")
            st.info(f"📈 Market Trend: **{prediction.market_trend}**")
            
            if prediction.opportunities:
                st.markdown("**🚀 Opportunities:**")
                for opp in prediction.opportunities:
                    st.write(f"• {opp}")
            
            if prediction.risk_factors:
                st.markdown("**⚠️ Risk Factors:**")
                for risk in prediction.risk_factors:
                    st.write(f"• {risk}")

# Additional utility functions for enhanced analytics
def create_advanced_market_analysis():
    """Create advanced market analysis charts"""
    # This would integrate with real market data APIs
    pass

def generate_predictive_insights():
    """Generate predictive market insights"""
    # This would use external market data and news APIs
    pass