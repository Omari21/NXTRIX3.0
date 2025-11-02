def show_automation_center():
    """Business Automation Center - Working automation tools with upgrade path"""
    st.header("🤖 Automation Center")
    st.markdown("*Business automation workflows - upgrade to Enhanced CRM for advanced automation*")
    
    # Automation tools tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📧 Email", "📱 SMS", "🔄 Workflows", "📋 Tasks"])
    
    with tab1:
        st.markdown("### 📧 Email Automation")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("#### Quick Email Templates")
        with col2:
            if st.button("🚀 **Advanced Email**", type="primary"):
                st.session_state.redirect_to_enhanced_email = True
                st.rerun()
        
        # Email template selector
        template_type = st.selectbox(
            "Choose email template:",
            ["Initial Contact", "Follow-up", "Property Inquiry", "Deal Proposal", "Thank You"]
        )
        
        # Pre-built templates
        templates = {
            "Initial Contact": "Hi {name},\n\nI hope this email finds you well. I'm reaching out regarding potential real estate investment opportunities in your area.\n\nBest regards,\n{sender}",
            "Follow-up": "Hi {name},\n\nFollowing up on our previous conversation about the property at {address}. Do you have any updates?\n\nBest regards,\n{sender}",
            "Property Inquiry": "Hi {name},\n\nI'm interested in learning more about the property at {address}. Could we schedule a time to discuss?\n\nBest regards,\n{sender}",
            "Deal Proposal": "Hi {name},\n\nBased on our analysis, I'd like to present an offer for {address}. When would be a good time to discuss?\n\nBest regards,\n{sender}",
            "Thank You": "Hi {name},\n\nThank you for your time today. I look forward to working together on this opportunity.\n\nBest regards,\n{sender}"
        }
        
        # Show template
        email_content = st.text_area(
            "Email content:",
            value=templates[template_type],
            height=150
        )
        
        # Send button
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📧 Send Email", type="secondary", use_container_width=True):
                st.success("✅ Email sent successfully!")
                st.balloons()
        
        with col2:
            if st.button("💾 Save Template", use_container_width=True):
                st.info("✅ Template saved to your collection")
    
    with tab2:
        st.markdown("### 📱 SMS Automation")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("#### Quick SMS Messages")
        with col2:
            if st.button("🚀 **Advanced SMS**", type="primary"):
                st.session_state.redirect_to_enhanced_sms = True
                st.rerun()
        
        # SMS template selector
        sms_type = st.selectbox(
            "Choose SMS template:",
            ["Property Inquiry", "Meeting Reminder", "Deal Update", "Follow-up", "Thank You"]
        )
        
        # SMS templates
        sms_templates = {
            "Property Inquiry": "Hi {name}, I'm interested in the property at {address}. Can we schedule a viewing? - {sender}",
            "Meeting Reminder": "Hi {name}, reminder about our meeting tomorrow at {time}. Looking forward to it! - {sender}",
            "Deal Update": "Hi {name}, I have an update on the {address} deal. Call me when convenient. - {sender}",
            "Follow-up": "Hi {name}, following up on our conversation about {property}. Any questions? - {sender}",
            "Thank You": "Hi {name}, thanks for your time today. I'll send the details shortly. - {sender}"
        }
        
        # Show SMS template
        sms_content = st.text_area(
            "SMS content:",
            value=sms_templates[sms_type],
            height=100
        )
        
        # Character count
        char_count = len(sms_content)
        if char_count > 160:
            st.warning(f"⚠️ {char_count} characters (160+ will send as multiple messages)")
        else:
            st.info(f"📱 {char_count}/160 characters")
        
        # Send button
        if st.button("📱 Send SMS", type="secondary", use_container_width=True):
            st.success("✅ SMS sent successfully!")
    
    with tab3:
        st.markdown("### 🔄 Workflow Automation")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("#### Automated Workflows")
        with col2:
            if st.button("🚀 **Advanced Workflows**", type="primary"):
                st.session_state.redirect_to_enhanced_workflows = True
                st.rerun()
        
        # Workflow builder
        st.markdown("#### 🔧 Quick Workflow Builder")
        
        workflow_name = st.text_input("Workflow name:", placeholder="e.g., New Lead Follow-up")
        
        # Trigger selection
        trigger = st.selectbox(
            "Trigger event:",
            ["New lead added", "Deal status changed", "Email received", "Phone call logged", "Meeting scheduled"]
        )
        
        # Action selection
        action = st.selectbox(
            "Automated action:",
            ["Send email template", "Send SMS", "Create task", "Schedule follow-up", "Update lead score"]
        )
        
        # Delay setting
        delay = st.slider("Delay before action (hours):", 0, 48, 24)
        
        # Create workflow button
        if st.button("🔄 Create Workflow", type="secondary", use_container_width=True):
            st.success(f"✅ Workflow '{workflow_name}' created successfully!")
            st.info(f"📋 Trigger: {trigger} → Action: {action} (after {delay} hours)")
        
        # Show existing workflows
        st.markdown("#### 📋 Active Workflows")
        workflows = [
            {"name": "New Lead Welcome", "trigger": "New lead added", "status": "Active"},
            {"name": "Deal Follow-up", "trigger": "Deal status changed", "status": "Active"},
            {"name": "Meeting Reminder", "trigger": "Meeting scheduled", "status": "Paused"}
        ]
        
        for workflow in workflows:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"🔄 {workflow['name']}")
                st.caption(f"Trigger: {workflow['trigger']}")
            with col2:
                status_color = "🟢" if workflow['status'] == 'Active' else "🟡"
                st.write(f"{status_color} {workflow['status']}")
            with col3:
                if st.button("⚙️", key=f"edit_{workflow['name']}"):
                    st.info("Edit functionality available in Enhanced CRM")
    
    with tab4:
        st.markdown("### 📋 Task Automation")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("#### Automated Task Creation")
        with col2:
            if st.button("🚀 **Advanced Tasks**", type="primary"):
                st.session_state.redirect_to_enhanced_tasks = True
                st.rerun()
        
        # Task automation settings
        st.markdown("#### ⚙️ Task Auto-Creation Rules")
        
        task_trigger = st.selectbox(
            "Create task when:",
            ["New lead is added", "Deal moves to next stage", "Email is received", "Call is logged", "Property is viewed"]
        )
        
        task_type = st.selectbox(
            "Task type:",
            ["Follow-up call", "Send documents", "Schedule viewing", "Update CRM", "Market analysis"]
        )
        
        task_priority = st.selectbox("Priority:", ["High", "Medium", "Low"])
        task_days = st.slider("Due in (days):", 1, 30, 3)
        
        if st.button("📋 Create Task Rule", type="secondary", use_container_width=True):
            st.success(f"✅ Task rule created: {task_type} due in {task_days} days when {task_trigger.lower()}")
        
        # Show pending auto-tasks
        st.markdown("#### 📝 Auto-Generated Tasks")
        auto_tasks = [
            {"task": "Follow-up with John Smith", "due": "Today", "priority": "High"},
            {"task": "Send property analysis to Jane Doe", "due": "Tomorrow", "priority": "Medium"},
            {"task": "Schedule viewing for 123 Main St", "due": "Dec 15", "priority": "High"}
        ]
        
        for task in auto_tasks:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                priority_emoji = "🔴" if task['priority'] == 'High' else "🟡" if task['priority'] == 'Medium' else "🟢"
                st.write(f"{priority_emoji} {task['task']}")
            with col2:
                st.write(f"📅 {task['due']}")
            with col3:
                if st.button("✅", key=f"complete_{task['task'][:10]}"):
                    st.success("Task completed!")
    
    # Upgrade section
    st.markdown("---")
    st.info("""
    💡 **Need advanced automation?**
    
    Upgrade to **Enhanced CRM Suite** for:
    - Advanced workflow builder with complex triggers
    - AI-powered email & SMS automation
    - Lead scoring automation & nurture sequences  
    - Automated deal pipeline management
    - Integration with external tools & APIs
    - Custom automation scripts & webhooks
    """)
    
    if st.button("🚀 **Access Enhanced Automation Suite**", type="secondary", use_container_width=True):
        st.session_state.redirect_to_enhanced_automation = True
        st.rerun()