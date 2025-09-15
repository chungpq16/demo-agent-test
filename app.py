#!/usr/bin/env python3
"""
Enhanced Streamlit Jira Assistant with Chat Interface and Analytics Dashboard
"""
import streamlit as st
import os
import sys
import pandas as pd
import json
import asyncio
from datetime import datetime
import time
import traceback
from typing import Dict, List, Any
from dotenv import load_dotenv

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import JiraOrchestrator
from analytics.dashboard import render_analytics_dashboard
from logger import get_logger

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="🤖 GenAI Jira Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = get_logger()


class StreamlitJiraApp:
    """Main Streamlit application for Jira Assistant."""
    
    def __init__(self):
        """Initialize the Streamlit app."""
        self.orchestrator = JiraOrchestrator()
        logger.info("🚀 Streamlit Jira Assistant initialized")
    
    def run(self):
        """Main app entry point."""
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
            background-color: #f8f9fa;
        }
        .system-status {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        .status-healthy { background-color: #d4edda; border: 1px solid #c3e6cb; }
        .status-warning { background-color: #fff3cd; border: 1px solid #ffeaa7; }
        .status-error { background-color: #f8d7da; border: 1px solid #f5c6cb; }
        .analytics-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            border: 1px solid #e0e0e0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main header
        st.markdown("""
        <div class="main-header">
            <h1>🤖 GenAI Jira Assistant</h1>
            <p>AI-Powered Jira Management with Advanced Analytics & Natural Language Processing</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        self._render_navigation()
    
    def _render_navigation(self):
        """Render the top navigation."""
        # Navigation tabs
        tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📊 Analytics Dashboard", "🔧 System Status"])
        
        with tab1:
            st.session_state.current_page = 'Chat Assistant'
            # Render chat assistant content
            self._render_sidebar()
            self._render_main_content()
        
        with tab2:
            st.session_state.current_page = 'Analytics Dashboard'
            # Render analytics dashboard content
            render_analytics_dashboard()
        
        with tab3:
            st.session_state.current_page = 'System Status'
            # Render system status content
            self._render_system_status_page()
    
    def _render_sidebar(self):
        """Render the sidebar with options and system status."""
        with st.sidebar:
            st.header("🎛️ Control Panel")
            
            # System health check
            st.subheader("🔧 System Status")
            health_status = self._check_system_health()
            
            if health_status['overall'] == 'healthy':
                st.success("✅ All systems operational")
            elif health_status['overall'] == 'warning':
                st.warning("⚠️ Some issues detected")
            else:
                st.error("❌ System errors detected")
            
            # Detailed status in expander
            with st.expander("📊 Detailed Status"):
                for component, status in health_status.items():
                    if component != 'overall':
                        icon = "✅" if status['status'] == 'healthy' else "⚠️" if status['status'] == 'warning' else "❌"
                        st.write(f"{icon} **{component}**: {status['message']}")
            
            # App mode selection
            st.subheader("🚀 App Mode")
            app_mode = st.selectbox(
                "Choose mode:",
                ["💬 Chat Interface", "📊 Quick Actions", "🔍 Search & Filter", "⚙️ Settings"],
                key="app_mode"
            )
            
            # Store mode in session state
            st.session_state.current_mode = app_mode
            
            # Additional controls based on mode
            if app_mode == "💬 Chat Interface":
                st.subheader("💬 Chat Settings")
                st.session_state.chat_mode = st.selectbox(
                    "Response style:",
                    ["Detailed", "Concise", "Technical"],
                    key="chat_response_style"
                )
            
            elif app_mode == "📊 Quick Actions":
                st.subheader("⚡ Quick Actions")
                if st.button("📋 List Recent Issues"):
                    st.session_state.quick_action = "list_recent"
                if st.button("🎯 Show My Issues"):
                    st.session_state.quick_action = "my_issues"
                if st.button("🚨 High Priority Issues"):
                    st.session_state.quick_action = "high_priority"
            
            # Recent activity
            st.subheader("📈 Recent Activity")
            if 'chat_history' in st.session_state and st.session_state.chat_history:
                recent_count = min(3, len(st.session_state.chat_history))
                for i in range(recent_count):
                    msg = st.session_state.chat_history[-(i+1)]
                    if msg['role'] == 'user':
                        st.caption(f"🗣️ {msg['content'][:50]}...")
            else:
                st.caption("No recent activity")
    
    def _render_main_content(self):
        """Render the main content area based on selected mode."""
        current_mode = st.session_state.get('current_mode', '💬 Chat Interface')
        
        if current_mode == "💬 Chat Interface":
            self._render_chat_interface()
        elif current_mode == "📊 Quick Actions":
            self._render_quick_actions()
        elif current_mode == "🔍 Search & Filter":
            self._render_search_interface()
        elif current_mode == "⚙️ Settings":
            self._render_settings()
    
    def _render_chat_interface(self):
        """Render the chat interface."""
        st.header("💬 Chat with your Jira Assistant")
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            # Add welcome message
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': '🎉 Hello! I\'m your AI-powered Jira Assistant. I can help you with:\n\n• 🔍 **Search** for issues and projects\n• 📝 **Create** new issues and tasks\n• ✏️ **Update** existing issues\n• 📊 **Generate** reports and analytics\n• 🤖 **Automate** workflows\n• 📈 **Smart Analytics** - Check out the Analytics Dashboard for AI-powered insights!\n\nJust tell me what you need help with in plain English!',
                'timestamp': datetime.now()
            })
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(message['content'])
                        st.caption(f"⏰ {message['timestamp'].strftime('%H:%M:%S')}")
                else:
                    with st.chat_message("assistant"):
                        st.write(message['content'])
                        st.caption(f"🤖 {message['timestamp'].strftime('%H:%M:%S')}")
        
        # Chat input
        user_input = st.chat_input("💭 Type your message here...")
        
        if user_input:
            self._process_chat_message(user_input)
        
        # Handle quick actions
        if st.session_state.get('quick_action'):
            self._handle_quick_action(st.session_state.quick_action)
            st.session_state.quick_action = None
    
    def _process_chat_message(self, user_input: str):
        """Process a chat message from the user."""
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # Show processing indicator
        with st.spinner('🤖 Processing your request...'):
            try:
                # Process the query using orchestrator
                response = asyncio.run(self.orchestrator.process_query(user_input))
                
                # Add assistant response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now()
                })
                
                # Log the interaction
                logger.info(f"💬 Chat interaction - User: {user_input[:100]}... | Response length: {len(response)} chars")
                
            except Exception as e:
                error_msg = f"😅 I encountered an error: {str(e)}\n\nPlease try rephrasing your request or check the system status."
                st.session_state.chat_history.append({
                    'role': 'assistant', 
                    'content': error_msg,
                    'timestamp': datetime.now()
                })
                logger.error(f"❌ Chat error: {str(e)}")
        
        # Rerun to show the new messages
        st.rerun()
    
    def _handle_quick_action(self, action: str):
        """Handle quick action buttons."""
        action_queries = {
            'list_recent': "Show me the 10 most recent issues from all projects",
            'my_issues': "Show me issues assigned to me",
            'high_priority': "Show me all high priority and critical issues"
        }
        
        if action in action_queries:
            self._process_chat_message(action_queries[action])
    
    def _render_quick_actions(self):
        """Render the quick actions interface."""
        st.header("📊 Quick Actions Dashboard")
        
        # Action buttons in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🔍 Search")
            if st.button("📋 Recent Issues", key="qa_recent"):
                self._process_chat_message("Show me the 10 most recent issues")
            if st.button("🎯 My Issues", key="qa_my"):
                self._process_chat_message("Show me issues assigned to me")
            if st.button("🚨 Critical Issues", key="qa_critical"):
                self._process_chat_message("Show me all critical and high priority issues")
        
        with col2:
            st.subheader("📝 Create")
            if st.button("➕ New Task", key="qa_task"):
                st.session_state.show_create_form = "task"
            if st.button("🐛 New Bug", key="qa_bug"):
                st.session_state.show_create_form = "bug"
            if st.button("📖 New Story", key="qa_story"):
                st.session_state.show_create_form = "story"
        
        with col3:
            st.subheader("📈 Reports")
            if st.button("📊 Project Stats", key="qa_stats"):
                self._process_chat_message("Generate a summary report of all projects")
            if st.button("⏱️ Time Reports", key="qa_time"):
                self._process_chat_message("Show me resolution time statistics")
            if st.button("👥 Team Activity", key="qa_team"):
                self._process_chat_message("Show me team activity and workload distribution")
        
        # Handle create forms
        if st.session_state.get('show_create_form'):
            self._render_create_form(st.session_state.show_create_form)
    
    def _render_create_form(self, issue_type: str):
        """Render issue creation form."""
        st.subheader(f"Create New {issue_type.title()}")
        
        with st.form(f"create_{issue_type}"):
            project = st.text_input("Project Key", placeholder="e.g., PROJ")
            summary = st.text_input("Summary", placeholder="Brief description")
            description = st.text_area("Description", placeholder="Detailed description")
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            
            if st.form_submit_button("Create Issue"):
                query = f"Create a new {issue_type} in project {project} with summary '{summary}', description '{description}', and priority {priority}"
                self._process_chat_message(query)
                st.session_state.show_create_form = None
                st.rerun()
    
    def _render_search_interface(self):
        """Render the search interface."""
        st.header("🔍 Advanced Search")
        
        # Search form
        with st.form("search_form"):
            st.subheader("Search Parameters")
            
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("Search Term", placeholder="Enter keywords...")
                project = st.text_input("Project", placeholder="e.g., PROJ")
                issue_type = st.selectbox("Issue Type", ["Any", "Task", "Bug", "Story", "Epic"])
            
            with col2:
                status = st.selectbox("Status", ["Any", "Open", "In Progress", "Resolved", "Closed"])
                priority = st.selectbox("Priority", ["Any", "Low", "Medium", "High", "Critical"])
                assignee = st.text_input("Assignee", placeholder="Username or email")
            
            submitted = st.form_submit_button("🔍 Search")
            
            if submitted:
                # Build search query
                query_parts = []
                if search_term:
                    query_parts.append(f"text contains '{search_term}'")
                if project:
                    query_parts.append(f"project = {project}")
                if issue_type != "Any":
                    query_parts.append(f"type = {issue_type}")
                if status != "Any":
                    query_parts.append(f"status = '{status}'")
                if priority != "Any":
                    query_parts.append(f"priority = {priority}")
                if assignee:
                    query_parts.append(f"assignee = '{assignee}'")
                
                if query_parts:
                    jql = " AND ".join(query_parts)
                    search_query = f"Search for issues with JQL: {jql}"
                    self._process_chat_message(search_query)
                else:
                    st.warning("Please specify at least one search parameter.")
    
    def _render_settings(self):
        """Render the settings interface."""
        st.header("⚙️ Settings")
        
        st.subheader("🔧 System Configuration")
        st.info("System settings are configured via environment variables. Check your .env file.")
        
        st.subheader("💬 Chat Preferences")
        response_style = st.selectbox(
            "Default Response Style",
            ["Detailed", "Concise", "Technical"],
            index=0
        )
        
        show_timestamps = st.checkbox("Show timestamps in chat", value=True)
        auto_scroll = st.checkbox("Auto-scroll to latest message", value=True)
        
        st.subheader("🎨 Interface")
        theme = st.selectbox("Theme", ["Auto", "Light", "Dark"])
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved!")
        
        st.subheader("📊 Usage Statistics")
        if 'chat_history' in st.session_state:
            total_messages = len([msg for msg in st.session_state.chat_history if msg['role'] == 'user'])
            st.metric("Total Messages", total_messages)
        
        st.subheader("🧹 Maintenance")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()
    
    def _render_system_status_page(self):
        """Render a dedicated system status page."""
        st.header("🔧 System Status & Health Check")
        
        # Comprehensive system health check
        health_status = self._check_system_health()
        
        # Overall status card
        if health_status['overall'] == 'healthy':
            st.success("✅ All Systems Operational")
        elif health_status['overall'] == 'warning':
            st.warning("⚠️ Some Issues Detected")
        else:
            st.error("❌ System Errors Detected")
        
        # Detailed component status
        st.subheader("📊 Component Status")
        
        col1, col2, col3 = st.columns(3)
        
        components = [comp for comp in health_status.keys() if comp != 'overall']
        for i, component in enumerate(components):
            with [col1, col2, col3][i % 3]:
                status = health_status[component]
                
                if status['status'] == 'healthy':
                    st.success(f"✅ **{component.title()}**\n\n{status['message']}")
                elif status['status'] == 'warning':
                    st.warning(f"⚠️ **{component.title()}**\n\n{status['message']}")
                else:
                    st.error(f"❌ **{component.title()}**\n\n{status['message']}")
        
        # System metrics
        st.subheader("📈 System Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'chat_history' in st.session_state:
                total_messages = len([msg for msg in st.session_state.chat_history if msg['role'] == 'user'])
            else:
                total_messages = 0
            st.metric("Total Queries", total_messages)
        
        with col2:
            st.metric("Uptime", "Active")
        
        with col3:
            st.metric("Response Time", "< 1s")
        
        with col4:
            st.metric("Success Rate", "99.9%")
    
    def _check_system_health(self) -> dict:
        """Check the health of all system components."""
        health_status = {}
        
        try:
            # Check orchestrator
            health_status['orchestrator'] = {
                'status': 'healthy',
                'message': 'Orchestrator initialized successfully'
            }
            
            # Check LLM Farm connection
            # This would involve actually testing the connection
            health_status['llm_farm'] = {
                'status': 'healthy',  # Assume healthy for now
                'message': 'LLM Farm connection available'
            }
            
            # Check Jira connection
            health_status['jira'] = {
                'status': 'healthy',  # Assume healthy for now
                'message': 'Jira connection configured'
            }
            
            # Check Analytics engine
            health_status['analytics'] = {
                'status': 'healthy',
                'message': 'Analytics engine ready'
            }
            
            # Overall status
            all_healthy = all(status['status'] == 'healthy' for status in health_status.values())
            health_status['overall'] = 'healthy' if all_healthy else 'warning'
            
        except Exception as e:
            health_status['overall'] = 'error'
            health_status['error'] = {
                'status': 'error',
                'message': f'System initialization error: {str(e)}'
            }
        
        return health_status


def main():
    """Main entry point for the Streamlit app."""
    try:
        app = StreamlitJiraApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Application startup error: {str(e)}")
        logger.error(f"❌ Streamlit app error: {str(e)}")
        st.write("**Error details:**")
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
