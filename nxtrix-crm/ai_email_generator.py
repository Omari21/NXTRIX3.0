"""
AI Email Template Generation System for NXTRIX CRM
Uses existing OpenAI GPT-4 integration to generate personalized emails
"""

import streamlit as st
import openai
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import sqlite3

class EmailType(Enum):
    DEAL_ANNOUNCEMENT = "deal_announcement"
    INVESTOR_OUTREACH = "investor_outreach"
    FOLLOW_UP = "follow_up"
    MARKET_UPDATE = "market_update"
    DEAL_UPDATE = "deal_update"
    THANK_YOU = "thank_you"
    MEETING_REQUEST = "meeting_request"
    URGENT_OPPORTUNITY = "urgent_opportunity"

class EmailTone(Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    URGENT = "urgent"
    CASUAL = "casual"
    FORMAL = "formal"
    PERSUASIVE = "persuasive"

@dataclass
class EmailTemplate:
    """AI-generated email template structure"""
    id: str
    subject: str
    content: str
    email_type: EmailType
    tone: EmailTone
    generated_at: datetime
    personalization_data: Dict[str, Any]
    estimated_engagement: str

class AIEmailGenerator:
    """AI-powered email template generation system"""
    
    def __init__(self, db_path: str = "crm_data.db"):
        self.db_path = db_path
        self.init_database()
        
        # Initialize OpenAI if available
        try:
            if hasattr(st, 'secrets') and 'OPENAI' in st.secrets:
                openai.api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
                self.openai_available = True
            else:
                self.openai_available = False
        except:
            self.openai_available = False
    
    def init_database(self):
        """Initialize AI email templates database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_email_templates (
                    id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    content TEXT NOT NULL,
                    email_type TEXT NOT NULL,
                    tone TEXT NOT NULL,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    personalization_data TEXT,
                    estimated_engagement TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_generation_history (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    email_type TEXT NOT NULL,
                    tone TEXT NOT NULL,
                    context_data TEXT,
                    generated_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error initializing AI email database: {e}")
    
    def generate_email_template(self, email_type: EmailType, tone: EmailTone,
                               context_data: Dict[str, Any], 
                               recipient_data: Dict[str, Any] = None) -> EmailTemplate:
        """Generate AI-powered email template"""
        
        if not self.openai_available:
            return self._generate_fallback_template(email_type, tone, context_data)
        
        try:
            # Build the AI prompt
            prompt = self._build_ai_prompt(email_type, tone, context_data, recipient_data)
            
            # Generate with OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            # Parse the response
            ai_response = response.choices[0].message.content
            subject, content = self._parse_ai_response(ai_response)
            
            # Create template object
            template = EmailTemplate(
                id=f"ai_email_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                subject=subject,
                content=content,
                email_type=email_type,
                tone=tone,
                generated_at=datetime.now(),
                personalization_data=context_data,
                estimated_engagement=self._estimate_engagement(subject, content)
            )
            
            # Save to database
            self._save_template(template)
            
            return template
            
        except Exception as e:
            st.error(f"Error generating AI email: {e}")
            return self._generate_fallback_template(email_type, tone, context_data)
    
    def _build_ai_prompt(self, email_type: EmailType, tone: EmailTone,
                        context_data: Dict[str, Any], 
                        recipient_data: Dict[str, Any] = None) -> str:
        """Build comprehensive AI prompt for email generation"""
        
        # Base prompt structure
        base_prompt = f"""Generate a {tone.value} email for {email_type.value.replace('_', ' ')} purpose.

EMAIL REQUIREMENTS:
- Tone: {tone.value}
- Purpose: {email_type.value.replace('_', ' ').title()}
- Length: 150-300 words
- Include clear call-to-action
- Professional real estate context

CONTEXT DATA:
"""
        
        # Add context data
        for key, value in context_data.items():
            if value and str(value).strip():
                base_prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        # Add recipient data if available
        if recipient_data:
            base_prompt += "\nRECIPIENT INFO:\n"
            for key, value in recipient_data.items():
                if value and str(value).strip():
                    base_prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        # Add specific instructions based on email type
        specific_instructions = {
            EmailType.DEAL_ANNOUNCEMENT: "Focus on investment opportunity, include key metrics, create urgency without being pushy.",
            EmailType.INVESTOR_OUTREACH: "Professional introduction, highlight mutual benefits, request meeting or call.",
            EmailType.FOLLOW_UP: "Reference previous interaction, provide value, gentle persistence.",
            EmailType.MARKET_UPDATE: "Share market insights, position as expert, educational approach.",
            EmailType.DEAL_UPDATE: "Update on deal progress, maintain investor confidence, next steps clear.",
            EmailType.THANK_YOU: "Express genuine gratitude, strengthen relationship, open door for future.",
            EmailType.MEETING_REQUEST: "Clear meeting purpose, time-efficient, value proposition obvious.",
            EmailType.URGENT_OPPORTUNITY: "Time sensitivity clear, compelling opportunity, immediate action needed."
        }
        
        base_prompt += f"\nSPECIFIC FOCUS: {specific_instructions.get(email_type, 'Professional real estate communication.')}\n"
        
        base_prompt += """
OUTPUT FORMAT:
Return as JSON with exactly these keys:
{
    "subject": "Email subject line (compelling, 50-60 characters)",
    "content": "Full email body (150-300 words, include greeting and signature placeholders)"
}

Make the email unique, engaging, and personalized to the provided context."""
        
        return base_prompt
    
    def _parse_ai_response(self, ai_response: str) -> tuple:
        """Parse AI response to extract subject and content"""
        try:
            # Try to parse as JSON first
            if ai_response.strip().startswith('{'):
                data = json.loads(ai_response)
                return data.get('subject', 'AI Generated Email'), data.get('content', ai_response)
            
            # Fallback: try to extract subject line
            lines = ai_response.split('\n')
            subject = "AI Generated Email"
            content = ai_response
            
            for line in lines:
                if 'subject:' in line.lower():
                    subject = line.split(':', 1)[1].strip().strip('"')
                    break
            
            return subject, content
            
        except:
            return "AI Generated Email", ai_response
    
    def _estimate_engagement(self, subject: str, content: str) -> str:
        """Estimate email engagement potential"""
        score = 0
        
        # Subject line factors
        if len(subject) >= 40 and len(subject) <= 60:
            score += 20
        if any(word in subject.lower() for word in ['opportunity', 'urgent', 'exclusive', 'roi']):
            score += 15
        if '?' in subject or any(word in subject.lower() for word in ['how', 'what', 'why', 'when']):
            score += 10
        
        # Content factors
        if len(content.split()) >= 100 and len(content.split()) <= 300:
            score += 20
        if content.count('?') >= 1:
            score += 10
        if any(word in content.lower() for word in ['call', 'meeting', 'discuss', 'schedule']):
            score += 15
        if content.lower().count('you') >= 3:
            score += 10
        
        if score >= 70:
            return "High"
        elif score >= 50:
            return "Medium"
        else:
            return "Low"
    
    def _generate_fallback_template(self, email_type: EmailType, tone: EmailTone,
                                  context_data: Dict[str, Any]) -> EmailTemplate:
        """Generate fallback template when AI is unavailable"""
        
        fallback_templates = {
            EmailType.DEAL_ANNOUNCEMENT: {
                "subject": "Exclusive Investment Opportunity - {property_type} Deal",
                "content": """Dear {recipient_name},

I hope this email finds you well. I'm excited to share an exclusive investment opportunity that aligns with your investment criteria.

Property Details:
- Location: {address}
- Property Type: {property_type}
- Investment Amount: ${purchase_price:,}
- Projected ROI: {roi}%

This deal offers excellent potential in a growing market. I'd love to discuss the details with you and answer any questions you might have.

Would you be available for a brief call this week to explore this opportunity?

Best regards,
[Your Name]"""
            },
            EmailType.INVESTOR_OUTREACH: {
                "subject": "Partnership Opportunity - Real Estate Investment",
                "content": """Dear {recipient_name},

I hope you're doing well. I'm reaching out because I believe we could have a mutually beneficial partnership in real estate investing.

I specialize in identifying high-value investment opportunities and would love to discuss how we might work together to maximize your investment returns.

Some areas I focus on:
- Fix and flip opportunities
- Buy and hold properties  
- Commercial real estate
- Market analysis and due diligence

Would you be interested in a brief conversation to explore potential collaboration?

Looking forward to hearing from you.

Best regards,
[Your Name]"""
            }
        }
        
        template_data = fallback_templates.get(email_type, {
            "subject": f"{email_type.value.replace('_', ' ').title()}",
            "content": "Professional email content would be generated here based on your specific requirements."
        })
        
        return EmailTemplate(
            id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            subject=template_data["subject"],
            content=template_data["content"],
            email_type=email_type,
            tone=tone,
            generated_at=datetime.now(),
            personalization_data=context_data,
            estimated_engagement="Medium"
        )
    
    def _save_template(self, template: EmailTemplate):
        """Save generated template to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_email_templates 
                (id, subject, content, email_type, tone, generated_at, 
                 personalization_data, estimated_engagement)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                template.id,
                template.subject,
                template.content,
                template.email_type.value,
                template.tone.value,
                template.generated_at.isoformat(),
                json.dumps(template.personalization_data),
                template.estimated_engagement
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error saving AI template: {e}")
    
    def get_recent_templates(self, limit: int = 10) -> List[EmailTemplate]:
        """Get recently generated templates"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ai_email_templates 
                ORDER BY generated_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            templates = []
            
            for row in rows:
                template = EmailTemplate(
                    id=row[0],
                    subject=row[1],
                    content=row[2],
                    email_type=EmailType(row[3]),
                    tone=EmailTone(row[4]),
                    generated_at=datetime.fromisoformat(row[5]),
                    personalization_data=json.loads(row[6]) if row[6] else {},
                    estimated_engagement=row[7]
                )
                templates.append(template)
            
            conn.close()
            return templates
            
        except Exception as e:
            st.error(f"Error retrieving templates: {e}")
            return []
    
    def generate_multiple_variations(self, email_type: EmailType, tone: EmailTone,
                                   context_data: Dict[str, Any], 
                                   count: int = 3) -> List[EmailTemplate]:
        """Generate multiple email variations for A/B testing"""
        variations = []
        
        for i in range(count):
            # Slight prompt variation for diversity
            context_copy = context_data.copy()
            context_copy['variation'] = f"variation_{i+1}"
            
            template = self.generate_email_template(email_type, tone, context_copy)
            variations.append(template)
        
        return variations

def show_ai_email_generator():
    """Show AI email generator interface"""
    st.header("🤖 AI Email Template Generator")
    st.write("Generate personalized, professional emails using AI based on your deals and contacts.")
    
    # Check tier access
    user_tier = st.session_state.get('user_tier', 'solo')
    if user_tier == 'solo':
        st.warning("🔒 AI Email Template Generation is available for Team and Business plans.")
        st.info("Upgrade to Team plan to unlock AI-powered email creation!")
        return
    
    # Initialize AI generator
    if 'ai_email_generator' not in st.session_state:
        st.session_state.ai_email_generator = AIEmailGenerator()
    
    generator = st.session_state.ai_email_generator
    
    # Main interface tabs
    tab1, tab2, tab3 = st.tabs([
        "🎯 Generate New Email",
        "📚 Template Library", 
        "📊 Email Analytics"
    ])
    
    with tab1:
        show_email_generation_interface(generator)
    
    with tab2:
        show_template_library(generator)
    
    with tab3:
        show_email_analytics(generator)

def show_email_generation_interface(generator: AIEmailGenerator):
    """Show email generation interface"""
    st.subheader("🎯 Generate AI Email Template")
    
    with st.form("ai_email_generation"):
        col1, col2 = st.columns(2)
        
        with col1:
            email_type = st.selectbox("Email Type", [
                ("Deal Announcement", EmailType.DEAL_ANNOUNCEMENT),
                ("Investor Outreach", EmailType.INVESTOR_OUTREACH),
                ("Follow Up", EmailType.FOLLOW_UP),
                ("Market Update", EmailType.MARKET_UPDATE),
                ("Deal Update", EmailType.DEAL_UPDATE),
                ("Thank You", EmailType.THANK_YOU),
                ("Meeting Request", EmailType.MEETING_REQUEST),
                ("Urgent Opportunity", EmailType.URGENT_OPPORTUNITY)
            ], format_func=lambda x: x[0])[1]
            
            tone = st.selectbox("Email Tone", [
                ("Professional", EmailTone.PROFESSIONAL),
                ("Friendly", EmailTone.FRIENDLY),
                ("Urgent", EmailTone.URGENT),
                ("Casual", EmailTone.CASUAL),
                ("Formal", EmailTone.FORMAL),
                ("Persuasive", EmailTone.PERSUASIVE)
            ], format_func=lambda x: x[0])[1]
        
        with col2:
            generate_variations = st.checkbox("Generate multiple variations", value=False)
            variation_count = 3
            if generate_variations:
                variation_count = st.slider("Number of variations", 2, 5, 3)
        
        # Context data inputs
        st.markdown("### 📋 Email Context")
        
        col1, col2 = st.columns(2)
        with col1:
            recipient_name = st.text_input("Recipient Name", placeholder="John Smith")
            company_name = st.text_input("Company/Organization", placeholder="ABC Investments")
            
        with col2:
            property_type = st.text_input("Property Type", placeholder="Single Family Home")
            location = st.text_input("Location", placeholder="Dallas, TX")
        
        col1, col2 = st.columns(2)
        with col1:
            purchase_price = st.number_input("Purchase Price ($)", value=0, step=1000)
            roi = st.number_input("Expected ROI (%)", value=0.0, step=0.1)
        
        with col2:
            additional_context = st.text_area("Additional Context", 
                placeholder="Any specific details to mention...", height=100)
        
        generate_button = st.form_submit_button("🤖 Generate AI Email", type="primary")
        
        if generate_button:
            # Prepare context data
            context_data = {
                "recipient_name": recipient_name or "Valued Investor",
                "company_name": company_name,
                "property_type": property_type,
                "location": location,
                "purchase_price": purchase_price,
                "roi": roi,
                "additional_context": additional_context
            }
            
            # Remove empty values
            context_data = {k: v for k, v in context_data.items() if v}
            
            with st.spinner("🤖 AI is generating your personalized email..."):
                if generate_variations:
                    templates = generator.generate_multiple_variations(
                        email_type, tone, context_data, variation_count
                    )
                    
                    st.success(f"✅ Generated {len(templates)} email variations!")
                    
                    for i, template in enumerate(templates, 1):
                        with st.expander(f"📧 Variation {i} - Engagement: {template.estimated_engagement}"):
                            st.markdown(f"**Subject:** {template.subject}")
                            st.markdown("**Content:**")
                            st.text_area("", template.content, height=200, key=f"var_{i}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"📋 Copy Variation {i}", key=f"copy_var_{i}"):
                                    st.session_state[f'email_subject'] = template.subject
                                    st.session_state[f'email_content'] = template.content
                                    st.success("Copied to clipboard!")
                            
                            with col2:
                                st.caption(f"Generated: {template.generated_at.strftime('%m/%d/%Y %H:%M')}")
                else:
                    template = generator.generate_email_template(email_type, tone, context_data)
                    
                    st.success("✅ AI email generated successfully!")
                    
                    st.markdown(f"**Subject:** {template.subject}")
                    st.markdown("**Content:**")
                    st.text_area("Generated Email", template.content, height=250)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Engagement Potential", template.estimated_engagement)
                    with col2:
                        st.metric("Email Type", template.email_type.value.replace('_', ' ').title())
                    with col3:
                        st.metric("Tone", template.tone.value.title())
                    
                    if st.button("📋 Use This Email"):
                        st.session_state['email_subject'] = template.subject
                        st.session_state['email_content'] = template.content
                        st.success("Email ready to use in Communication Center!")

def show_template_library(generator: AIEmailGenerator):
    """Show template library"""
    st.subheader("📚 AI Generated Template Library")
    
    templates = generator.get_recent_templates(20)
    
    if templates:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            email_type_filter = st.selectbox("Filter by Type", 
                ["All"] + [t.value.replace('_', ' ').title() for t in EmailType])
        with col2:
            tone_filter = st.selectbox("Filter by Tone",
                ["All"] + [t.value.title() for t in EmailTone])
        with col3:
            engagement_filter = st.selectbox("Filter by Engagement",
                ["All", "High", "Medium", "Low"])
        
        # Filter templates
        filtered_templates = templates
        if email_type_filter != "All":
            filtered_templates = [t for t in filtered_templates 
                                if t.email_type.value.replace('_', ' ').title() == email_type_filter]
        if tone_filter != "All":
            filtered_templates = [t for t in filtered_templates 
                                if t.tone.value.title() == tone_filter]
        if engagement_filter != "All":
            filtered_templates = [t for t in filtered_templates 
                                if t.estimated_engagement == engagement_filter]
        
        st.write(f"Showing {len(filtered_templates)} templates")
        
        # Display templates
        for template in filtered_templates:
            with st.expander(f"📧 {template.subject} - {template.estimated_engagement} Engagement"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"Type: {template.email_type.value.replace('_', ' ').title()}")
                with col2:
                    st.caption(f"Tone: {template.tone.value.title()}")
                with col3:
                    st.caption(f"Generated: {template.generated_at.strftime('%m/%d/%Y %H:%M')}")
                
                st.text_area("Content", template.content, height=150, key=f"lib_{template.id}")
                
                if st.button("📋 Use This Template", key=f"use_{template.id}"):
                    st.session_state['email_subject'] = template.subject
                    st.session_state['email_content'] = template.content
                    st.success("Template ready to use!")
    else:
        st.info("📭 No templates generated yet. Create your first AI email template!")

def show_email_analytics(generator: AIEmailGenerator):
    """Show email generation analytics"""
    st.subheader("📊 Email Generation Analytics")
    
    templates = generator.get_recent_templates(50)
    
    if templates:
        import pandas as pd
        import plotly.express as px
        
        # Prepare data
        df_data = []
        for template in templates:
            df_data.append({
                'type': template.email_type.value.replace('_', ' ').title(),
                'tone': template.tone.value.title(),
                'engagement': template.estimated_engagement,
                'date': template.generated_at.date(),
                'subject_length': len(template.subject),
                'content_length': len(template.content)
            })
        
        df = pd.DataFrame(df_data)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Templates", len(templates))
        with col2:
            high_engagement = len([t for t in templates if t.estimated_engagement == "High"])
            st.metric("High Engagement", high_engagement)
        with col3:
            most_common_type = df['type'].mode().iloc[0] if not df.empty else "N/A"
            st.metric("Most Used Type", most_common_type)
        with col4:
            avg_subject_length = df['subject_length'].mean() if not df.empty else 0
            st.metric("Avg Subject Length", f"{avg_subject_length:.0f}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Email types distribution
            type_counts = df['type'].value_counts()
            fig_types = px.pie(values=type_counts.values, names=type_counts.index,
                             title="Email Types Distribution")
            st.plotly_chart(fig_types, use_container_width=True)
        
        with col2:
            # Engagement levels
            engagement_counts = df['engagement'].value_counts()
            fig_engagement = px.bar(x=engagement_counts.index, y=engagement_counts.values,
                                  title="Engagement Levels")
            st.plotly_chart(fig_engagement, use_container_width=True)
        
        # Generation timeline
        if len(df) > 1:
            timeline_data = df.groupby('date').size().reset_index(name='count')
            fig_timeline = px.line(timeline_data, x='date', y='count',
                                 title="Email Generation Timeline")
            st.plotly_chart(fig_timeline, use_container_width=True)
        
    else:
        st.info("📊 Generate some emails to see analytics!")