"""
Voice AI System for NXTRIX 3.0
Advanced voice commands, AI chat assistant, and speech-to-text simulation
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time

class VoiceAISystem:
    def __init__(self):
        self.voice_commands = {
            "show me my top deals": self.get_top_deals,
            "what's my revenue": self.get_revenue_stats,
            "how many contacts do I have": self.get_contact_count,
            "show pipeline": self.show_pipeline,
            "create new deal": self.create_deal_form,
            "send email campaign": self.start_email_campaign,
            "generate report": self.generate_report,
            "show analytics": self.show_analytics_dashboard,
            "what's trending": self.show_market_trends,
            "schedule follow up": self.schedule_followup
        }
        
        self.ai_responses = {
            "greeting": [
                "Hello! I'm your NXTRIX AI assistant. How can I help you today?",
                "Hi there! Ready to boost your real estate business?",
                "Welcome back! What would you like to accomplish today?"
            ],
            "help": [
                "I can help you with deals, contacts, analytics, and much more. Try saying 'show me my top deals' or 'what's my revenue'.",
                "Here are some things I can do: manage your pipeline, generate reports, send campaigns, and provide insights.",
                "You can ask me about your deals, revenue, contacts, or ask me to perform actions like creating deals or sending emails."
            ],
            "unknown": [
                "I'm not sure I understand that command. Could you try rephrasing?",
                "I didn't catch that. Try commands like 'show pipeline' or 'what's my revenue'.",
                "Can you clarify what you'd like me to help you with?"
            ]
        }
    
    def render_voice_command_interface(self):
        """Render the voice command interface"""
        st.markdown("### 🎤 Voice AI Commands")
        
        # Voice AI Demo Interface
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            text-align: center;
        ">
            <div style="font-size: 48px; margin-bottom: 16px;">🎤</div>
            <h3 style="color: #ffffff; margin-bottom: 16px;">Voice AI Demo Mode</h3>
            <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 24px;">
                Experience the future of CRM with voice commands!<br>
                <small>Full speech recognition available in mobile app</small>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo Voice Commands
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Try These Commands:")
            command_buttons = [
                ("Show me my top deals", "💼"),
                ("What's my revenue?", "💰"),
                ("How many contacts do I have?", "👥"),
                ("Show pipeline", "📊"),
                ("Generate report", "📋")
            ]
            
            for command, icon in command_buttons:
                if st.button(f"{icon} {command}", key=f"voice_cmd_{command}", use_container_width=True):
                    self.process_voice_command(command.lower())
        
        with col2:
            st.markdown("#### 🤖 AI Actions:")
            action_buttons = [
                ("Create new deal", "➕"),
                ("Send email campaign", "📧"),
                ("Schedule follow up", "📅"),
                ("Show analytics", "📈"),
                ("Market trends", "📊")
            ]
            
            for action, icon in action_buttons:
                if st.button(f"{icon} {action}", key=f"voice_action_{action}", use_container_width=True):
                    self.process_voice_command(action.lower())
        
        # Voice simulation
        if st.button("🎙️ Start Voice Simulation", type="primary", use_container_width=True):
            self.simulate_voice_interaction()
        
        # Recent voice commands
        if 'voice_history' in st.session_state and st.session_state.voice_history:
            st.markdown("#### 📝 Recent Commands:")
            for cmd in st.session_state.voice_history[-3:]:
                st.markdown(f"• {cmd}")
    
    def process_voice_command(self, command: str):
        """Process voice command and execute corresponding action"""
        # Store command in history
        if 'voice_history' not in st.session_state:
            st.session_state.voice_history = []
        
        st.session_state.voice_history.append(command)
        
        # Find matching command
        for cmd_key, cmd_func in self.voice_commands.items():
            if cmd_key in command.lower():
                result = cmd_func()
                st.success(f"✅ Executed: {command}")
                return result
        
        # No matching command found
        st.warning(f"🤔 Command not recognized: {command}")
        st.info("Try commands like: 'show me my top deals', 'what's my revenue', or 'show pipeline'")
    
    def simulate_voice_interaction(self):
        """Simulate realistic voice interaction"""
        st.markdown("### 🎙️ Voice Interaction Simulation")
        
        # Create conversation flow
        conversation = [
            {"type": "user", "text": "Show me my top deals", "time": "now"},
            {"type": "ai", "text": "Here are your top 5 deals by value:", "time": "1s"},
            {"type": "system", "text": "Displaying deals dashboard...", "time": "2s"},
            {"type": "user", "text": "What's the status of ABC Corp deal?", "time": "5s"},
            {"type": "ai", "text": "ABC Corp deal is in negotiation phase, valued at $85,000. Last activity was 2 days ago.", "time": "6s"},
            {"type": "user", "text": "Schedule follow up for tomorrow", "time": "10s"},
            {"type": "ai", "text": "Follow-up scheduled for tomorrow at 10 AM. I'll send you a reminder.", "time": "11s"}
        ]
        
        # Display conversation with animation
        for i, msg in enumerate(conversation):
            time.sleep(0.5)  # Simulate real-time conversation
            
            if msg["type"] == "user":
                st.markdown(f"""
                <div style="
                    background: rgba(99, 102, 241, 0.2);
                    border-left: 4px solid #6366f1;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 8px 0;
                    text-align: right;
                ">
                    <strong>👤 You:</strong> {msg['text']}
                    <br><small style="opacity: 0.7;">{msg['time']}</small>
                </div>
                """, unsafe_allow_html=True)
                
            elif msg["type"] == "ai":
                st.markdown(f"""
                <div style="
                    background: rgba(16, 185, 129, 0.2);
                    border-left: 4px solid #10b981;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 8px 0;
                ">
                    <strong>🤖 NXTRIX AI:</strong> {msg['text']}
                    <br><small style="opacity: 0.7;">{msg['time']}</small>
                </div>
                """, unsafe_allow_html=True)
                
            else:  # system
                st.markdown(f"""
                <div style="
                    background: rgba(139, 92, 246, 0.2);
                    border-left: 4px solid #8b5cf6;
                    border-radius: 8px;
                    padding: 8px 12px;
                    margin: 4px 0;
                    text-align: center;
                    font-style: italic;
                ">
                    {msg['text']}
                </div>
                """, unsafe_allow_html=True)
            
            st.rerun()
    
    def get_top_deals(self):
        """Get top deals by value"""
        deals = [
            {"name": "ABC Corp Acquisition", "value": "$125,000", "stage": "Negotiation", "probability": "85%"},
            {"name": "Downtown Office Complex", "value": "$95,000", "stage": "Proposal", "probability": "70%"},
            {"name": "Residential Development", "value": "$78,000", "stage": "Qualified", "probability": "60%"},
            {"name": "Tech Startup HQ", "value": "$65,000", "stage": "Negotiation", "probability": "90%"},
            {"name": "Retail Space Lease", "value": "$45,000", "stage": "Proposal", "probability": "50%"}
        ]
        
        st.markdown("#### 💼 Top 5 Deals by Value")
        for deal in deals:
            st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0;
            ">
                <strong>{deal['name']}</strong> - {deal['value']}<br>
                <small>Stage: {deal['stage']} | Probability: {deal['probability']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        return deals
    
    def get_revenue_stats(self):
        """Get revenue statistics"""
        stats = {
            "total_revenue": "$456,789",
            "monthly_revenue": "$45,230",
            "growth_rate": "+12.5%",
            "closed_deals": 23
        }
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", stats["total_revenue"])
        with col2:
            st.metric("This Month", stats["monthly_revenue"], stats["growth_rate"])
        with col3:
            st.metric("Closed Deals", stats["closed_deals"])
        with col4:
            st.metric("Avg Deal Size", "$19,860")
        
        return stats
    
    def get_contact_count(self):
        """Get contact statistics"""
        st.markdown("#### 👥 Contact Overview")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Contacts", "1,247", "+23")
        with col2:
            st.metric("Active Leads", "89", "+12")
        with col3:
            st.metric("This Week", "34", "+8")
        
        return {"total": 1247, "leads": 89, "new_this_week": 34}
    
    def show_pipeline(self):
        """Show pipeline visualization"""
        st.markdown("#### 📊 Sales Pipeline")
        
        pipeline_data = {
            "Lead": 15,
            "Qualified": 12,
            "Proposal": 8,
            "Negotiation": 5,
            "Closed Won": 3
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            for stage, count in pipeline_data.items():
                st.markdown(f"**{stage}:** {count} deals")
        
        with col2:
            st.bar_chart(pipeline_data)
        
        return pipeline_data
    
    def create_deal_form(self):
        """Show deal creation form"""
        st.markdown("#### ➕ Create New Deal")
        st.info("Voice command recognized! Deal creation form would open here.")
        return {"action": "create_deal_form"}
    
    def start_email_campaign(self):
        """Start email campaign"""
        st.markdown("#### 📧 Email Campaign")
        st.success("Voice command processed! Email campaign builder would launch here.")
        return {"action": "email_campaign"}
    
    def generate_report(self):
        """Generate business report"""
        st.markdown("#### 📋 Generating Report...")
        
        with st.spinner("Creating your business report..."):
            time.sleep(2)
        
        st.success("✅ Monthly business report generated!")
        st.info("Report includes: Revenue analysis, Deal pipeline, Contact growth, Performance metrics")
        
        return {"action": "report_generated"}
    
    def show_analytics_dashboard(self):
        """Show analytics dashboard"""
        st.markdown("#### 📈 Analytics Dashboard")
        
        # Sample analytics data
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Key Metrics:**")
            st.metric("Conversion Rate", "23.4%", "+2.1%")
            st.metric("Deal Velocity", "32 days", "-3 days")
            
        with col2:
            st.markdown("**Performance:**")
            st.metric("Lead Score Avg", "78.5", "+5.2")
            st.metric("Follow-up Rate", "94%", "+1%")
        
        return {"action": "analytics_displayed"}
    
    def show_market_trends(self):
        """Show market trends"""
        st.markdown("#### 📊 Market Trends")
        
        trends = [
            "🏠 Residential market up 3.2% this quarter",
            "🏢 Commercial real estate showing strong growth",
            "📈 Interest rates stable, buyer confidence high",
            "🌆 Urban properties in high demand",
            "💡 Tech sector driving office space needs"
        ]
        
        for trend in trends:
            st.markdown(f"• {trend}")
        
        return {"trends": trends}
    
    def schedule_followup(self):
        """Schedule follow up"""
        st.markdown("#### 📅 Schedule Follow-up")
        st.success("Voice scheduling activated! Calendar integration would open here.")
        return {"action": "schedule_followup"}

class AIChatbot:
    def __init__(self):
        self.conversation_history = []
        self.ai_personality = "professional_assistant"
        
    def render_chat_interface(self):
        """Render AI chat interface"""
        st.markdown("### 🤖 AI Assistant Chat")
        
        # Chat container
        chat_container = st.container()
        
        # Initialize chat history
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = [
                {"role": "assistant", "content": "Hello! I'm your NXTRIX AI assistant. How can I help you today?"}
            ]
        
        # Display chat messages
        for message in st.session_state.chat_messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="
                    background: rgba(99, 102, 241, 0.2);
                    border-left: 4px solid #6366f1;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 8px 0;
                    text-align: right;
                ">
                    <strong>👤 You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: rgba(16, 185, 129, 0.2);
                    border-left: 4px solid #10b981;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 8px 0;
                ">
                    <strong>🤖 AI:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Type your message...", key="chat_input", placeholder="Ask me anything about your business!")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Send", use_container_width=True, type="primary"):
                if user_input:
                    self.process_chat_message(user_input)
        
        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.chat_messages = [
                    {"role": "assistant", "content": "Hello! I'm your NXTRIX AI assistant. How can I help you today?"}
                ]
                st.rerun()
        
        # Quick actions
        st.markdown("#### 🚀 Quick Actions:")
        quick_actions = [
            "Show my performance this month",
            "What deals need attention?",
            "Generate lead report",
            "Schedule team meeting"
        ]
        
        cols = st.columns(2)
        for i, action in enumerate(quick_actions):
            with cols[i % 2]:
                if st.button(action, key=f"quick_{i}", use_container_width=True):
                    self.process_chat_message(action)
    
    def process_chat_message(self, message: str):
        """Process chat message and generate AI response"""
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": message})
        
        # Generate AI response
        response = self.generate_ai_response(message)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    def generate_ai_response(self, message: str) -> str:
        """Generate intelligent AI response"""
        message_lower = message.lower()
        
        # Business insights responses
        if any(word in message_lower for word in ["performance", "metrics", "stats"]):
            return "Based on your recent activity, you're performing well! Your deal conversion rate is up 12% this month, and you have 5 high-priority deals in negotiation. Would you like me to show you detailed analytics?"
        
        elif any(word in message_lower for word in ["deals", "pipeline", "opportunities"]):
            return "You currently have 23 active deals in your pipeline worth $487,000 total. 3 deals need immediate attention - ABC Corp (negotiation), Tech Startup (proposal review), and Downtown Office (follow-up required). Shall I prioritize these for you?"
        
        elif any(word in message_lower for word in ["leads", "contacts", "prospects"]):
            return "You have 89 active leads, with 12 new contacts added this week. Your lead scoring shows 15 high-quality prospects ready for outreach. I can help you craft personalized messages for top leads. Would you like me to start?"
        
        elif any(word in message_lower for word in ["report", "analysis", "summary"]):
            return "I can generate several reports for you: Revenue Analysis, Deal Pipeline Summary, Contact Growth Report, or Custom Performance Report. Which would be most valuable right now?"
        
        elif any(word in message_lower for word in ["email", "campaign", "marketing"]):
            return "Your last email campaign had an 87% open rate and 34% click rate - excellent performance! I can help you create a new campaign, segment your audience, or analyze campaign results. What would you like to focus on?"
        
        elif any(word in message_lower for word in ["schedule", "calendar", "meeting"]):
            return "I can help you schedule follow-ups, set reminders, or coordinate meetings. You have 3 pending follow-ups and 2 meetings scheduled for tomorrow. Would you like me to show your upcoming schedule?"
        
        elif any(word in message_lower for word in ["help", "what can you do"]):
            return "I can help you with: 📊 Analytics & Reports, 💼 Deal Management, 👥 Contact Insights, 📧 Email Campaigns, 📅 Scheduling, 🎯 Lead Scoring, 📈 Performance Tracking, and much more! What specific area interests you?"
        
        elif any(word in message_lower for word in ["thank", "thanks", "good", "great"]):
            return "You're welcome! I'm here to help you succeed. Is there anything else you'd like me to assist with today?"
        
        else:
            return f"I understand you're asking about {message}. Let me help you with that! I can provide insights on your deals, contacts, performance metrics, or help you take action. Could you be more specific about what you'd like me to do?"

# Global instances
voice_system = VoiceAISystem()
chatbot = AIChatbot()