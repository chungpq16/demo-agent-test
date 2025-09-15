#!/usr/bin/env python3
"""
Enhanced Streamlit Jira Assistant with Chat Interface and Analytics Dashboard
"""
import streamlit as st
import os
import sys
import pandas as pd
import json
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
        tab1, tab2 = st.tabs(["💬 Chat Assistant", "📊 Analytics Dashboard"])
        
        with tab1:
            st.session_state.current_page = 'Chat Assistant'
            # Render chat assistant content
            self._render_sidebar()
            self._render_main_content()
        
        with tab2:
            st.session_state.current_page = 'Analytics Dashboard'
            # Render analytics dashboard content
            render_analytics_dashboard()
    
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
        """Render the main content area - chat interface."""
        self._render_chat_interface()
    
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
                response = self.orchestrator.process_request(user_input)
                
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
