"""
Example Implementation: Applying Subscription Tier Restrictions to Deal Tracker Module
Demonstrates how to gate features and track usage for SaaS enforcement
"""

import streamlit as st
from subscription_manager import (
    SubscriptionManager, 
    require_subscription, 
    track_usage,
    BulkOperationContext
)
from feature_access_control import (
    require_feature,
    require_tier, 
    track_feature_usage,
    access_control
)
from typing import List, Dict, Any

class ProtectedDealTracker:
    """Deal Tracker with subscription tier enforcement"""
    
    def __init__(self):
        self.sub_manager = SubscriptionManager()
        
    @require_feature("deal_tracker")
    @track_feature_usage("deals_per_month")
    def create_deal(self, deal_data: Dict[str, Any]) -> bool:
        """Create a new deal with usage tracking"""
        try:
            # Validate user has access and hasn't exceeded limits
            user_id = st.session_state.get('user_id')
            if not user_id:
                st.error("Authentication required")
                return False
            
            # Check usage limits before creation
            has_access, current, limit = access_control.check_usage_limit("deals_per_month", user_id)
            
            if not has_access:
                st.error(f"Deal creation limit reached: {current}/{limit} for this billing cycle")
                access_control.show_upgrade_prompt("deal_tracker")
                return False
            
            # Create the deal (your existing logic here)
            deal_id = self._save_deal_to_database(deal_data)
            
            if deal_id:
                st.success(f"✅ Deal created successfully! ({current + 1}/{limit if limit != -1 else '∞'} deals this month)")
                return True
            else:
                st.error("Failed to create deal")
                return False
                
        except Exception as e:
            st.error(f"Error creating deal: {e}")
            return False
    
    @require_feature("deal_tracker")
    def view_deals(self) -> List[Dict[str, Any]]:
        """View deals (no usage limit for viewing)"""
        try:
            return self._get_deals_from_database()
        except Exception as e:
            st.error(f"Error loading deals: {e}")
            return []
    
    @require_feature("advanced_analytics")
    def generate_deal_report(self, deal_ids: List[str]) -> bool:
        """Generate advanced deal report (Pro+ feature)"""
        user_id = st.session_state.get('user_id')
        
        # Use bulk operation context for multiple deals
        try:
            with BulkOperationContext(user_id, "document_generations_per_month", len(deal_ids)):
                # Generate report logic here
                report_data = self._generate_report_data(deal_ids)
                
                st.success(f"✅ Generated report for {len(deal_ids)} deals")
                return True
                
        except Exception as e:
            st.error(f"Report generation failed: {e}")
            return False
    
    @require_tier("enterprise")
    def bulk_import_deals(self, deals_data: List[Dict]) -> bool:
        """Bulk import deals (Enterprise only)"""
        user_id = st.session_state.get('user_id')
        
        try:
            with BulkOperationContext(user_id, "deals_per_month", len(deals_data)):
                # Bulk import logic
                imported_count = 0
                
                for deal_data in deals_data:
                    if self._save_deal_to_database(deal_data):
                        imported_count += 1
                
                st.success(f"✅ Imported {imported_count}/{len(deals_data)} deals")
                return True
                
        except Exception as e:
            st.error(f"Bulk import failed: {e}")
            return False
    
    def _save_deal_to_database(self, deal_data: Dict[str, Any]) -> str:
        """Save deal to database (mock implementation)"""
        # Your actual database save logic here
        import uuid
        return str(uuid.uuid4())
    
    def _get_deals_from_database(self) -> List[Dict[str, Any]]:
        """Get deals from database (mock implementation)"""
        # Your actual database query logic here
        return [
            {"id": "1", "title": "Sample Deal 1", "value": 100000},
            {"id": "2", "title": "Sample Deal 2", "value": 150000}
        ]
    
    def _generate_report_data(self, deal_ids: List[str]) -> Dict[str, Any]:
        """Generate report data (mock implementation)"""
        return {"deals": len(deal_ids), "total_value": 250000}

def show_protected_deal_interface():
    """Demo interface showing subscription-gated deal features"""
    st.title("🏠 Deal Tracker - Subscription Protected")
    
    # Initialize protected deal tracker
    deal_tracker = ProtectedDealTracker()
    
    # Show current user's subscription status
    user_id = st.session_state.get('user_id', 'demo_user_001')
    subscription = deal_tracker.sub_manager.get_user_subscription(user_id)
    
    if subscription:
        st.info(f"👤 Current Plan: **{subscription.tier.value.title()}** | Status: **{subscription.status.title()}**")
    
    # Demo different feature tiers
    tab1, tab2, tab3, tab4 = st.tabs([
        "🆓 Basic Features", 
        "💎 Pro Features", 
        "👑 Enterprise Features",
        "📊 Usage Dashboard"
    ])
    
    with tab1:
        st.subheader("Basic Deal Management (All Tiers)")
        
        # Create deal form (with usage tracking)
        with st.form("create_deal_form"):
            st.write("**Create New Deal**")
            
            deal_title = st.text_input("Deal Title")
            deal_value = st.number_input("Deal Value ($)", min_value=0, value=100000)
            property_type = st.selectbox("Property Type", ["Single Family", "Multi-Family", "Commercial"])
            
            submitted = st.form_submit_button("Create Deal")
            
            if submitted and deal_title:
                deal_data = {
                    "title": deal_title,
                    "value": deal_value,
                    "property_type": property_type,
                    "created_at": st.session_state.get('current_time', '2025-09-16')
                }
                
                deal_tracker.create_deal(deal_data)
        
        # View deals (no restrictions)
        st.write("**Current Deals**")
        deals = deal_tracker.view_deals()
        
        if deals:
            deals_df = pd.DataFrame(deals)
            st.dataframe(deals_df, use_container_width=True)
        else:
            st.info("No deals found")
    
    with tab2:
        st.subheader("Professional Features (Pro & Enterprise)")
        
        # Advanced reporting (Pro+ feature)
        st.write("**Advanced Deal Reports**")
        
        if st.button("Generate Advanced Report"):
            deal_ids = ["deal_1", "deal_2", "deal_3"]  # Mock deal IDs
            deal_tracker.generate_deal_report(deal_ids)
        
        # AI-powered insights (Pro+ feature)
        st.write("**AI Deal Analysis**")
        
        @require_feature("ai_deal_analysis")
        @track_feature_usage("ai_queries_per_month")
        def analyze_deal_with_ai():
            st.success("🤖 AI analysis complete! Deal score: 8.5/10")
            st.write("**Key Insights:**")
            st.write("• Strong cash flow potential")
            st.write("• Below market purchase price")
            st.write("• Growing neighborhood")
        
        if st.button("Run AI Analysis"):
            analyze_deal_with_ai()
    
    with tab3:
        st.subheader("Enterprise Features (Enterprise Only)")
        
        # Bulk operations (Enterprise only)
        st.write("**Bulk Deal Import**")
        
        if st.button("Import 100 Sample Deals"):
            sample_deals = [
                {"title": f"Bulk Deal {i}", "value": 100000 + i * 1000}
                for i in range(100)
            ]
            deal_tracker.bulk_import_deals(sample_deals)
        
        # API access (Enterprise only)
        st.write("**API Access**")
        
        @require_feature("api_access")
        def show_api_keys():
            st.code("""
            API Endpoint: https://api.nxtrix.com/v1/deals
            API Key: nxtrix_ent_abc123...
            Rate Limit: Unlimited
            """)
        
        if st.button("Show API Keys"):
            show_api_keys()
    
    with tab4:
        st.subheader("📊 Usage Analytics")
        
        # Show usage dashboard
        from subscription_dashboard import subscription_dashboard
        subscription_dashboard.show_user_subscription_widget(user_id)
        
        # Feature access matrix
        st.write("**Feature Access Matrix**")
        
        features = [
            ("Create Deals", "deal_tracker", "deals_per_month"),
            ("AI Analysis", "ai_deal_analysis", "ai_queries_per_month"),
            ("Advanced Reports", "advanced_reports", None),
            ("Bulk Import", "bulk_operations", None),
            ("API Access", "api_access", "api_calls_per_month")
        ]
        
        access_data = []
        for feature_name, feature_key, usage_type in features:
            has_access = access_control.check_feature_access(feature_key, user_id)
            
            if usage_type and has_access:
                has_usage, current, limit = access_control.check_usage_limit(feature_key, user_id)
                usage_info = f"{current}/{limit if limit != -1 else '∞'}"
            else:
                usage_info = "N/A"
            
            access_data.append({
                "Feature": feature_name,
                "Access": "✅" if has_access else "❌",
                "Usage": usage_info
            })
        
        access_df = pd.DataFrame(access_data)
        st.table(access_df)

def show_subscription_enforcement_demo():
    """Complete demo of subscription enforcement"""
    st.title("🔐 Subscription Tier Enforcement Demo")
    
    st.markdown("""
    This demo shows how the NxTrix CRM enforces subscription tiers:
    
    - **🆓 Free Tier**: 5 deals/month, basic features only
    - **💎 Pro Tier**: 50 deals/month, AI features, advanced analytics
    - **👑 Enterprise**: Unlimited usage, all features, API access
    """)
    
    # User tier selector for demo
    st.sidebar.subheader("Demo Controls")
    demo_tier = st.sidebar.selectbox(
        "Simulate User Tier",
        ["free", "pro", "enterprise"]
    )
    
    # Set demo user subscription
    if 'demo_tier' not in st.session_state or st.session_state.demo_tier != demo_tier:
        st.session_state.demo_tier = demo_tier
        st.session_state.user_id = f"demo_{demo_tier}_user"
        st.rerun()
    
    # Show the protected interface
    show_protected_deal_interface()

if __name__ == "__main__":
    import pandas as pd
    show_subscription_enforcement_demo()