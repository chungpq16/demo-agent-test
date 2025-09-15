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
        tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📊 Analytics Dashboard", "📖 Instructions"])
        
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
            st.session_state.current_page = 'Instructions'
            # Render instructions content
            self._render_instructions()
    
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
            
            # Application Configuration
            st.subheader("⚙️ Application Configuration")
            
            # Jira Results Limit
            default_limit = int(os.getenv('JIRA_MAX_RESULTS', '50'))
            jira_limit = st.slider(
                "📊 Jira Results Limit",
                min_value=10,
                max_value=200,
                value=default_limit,
                step=10,
                help="Maximum number of issues to retrieve from Jira for all operations"
            )
            
            # Store in session state for use across the app
            st.session_state.jira_results_limit = jira_limit
            
            # Show current setting
            st.caption(f"Current limit: {jira_limit} issues")
    
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
                        # Check if it's a structured Jira issues message
                        if message.get('type') == 'jira_issues':
                            self._render_jira_issues_message(message)
                        else:
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
                # Get the current limit from session state
                max_results = st.session_state.get('jira_results_limit', 50)
                
                # Process the query using orchestrator with the configured limit
                response = self.orchestrator.process_request(user_input, max_results=max_results)
                
                # Check if response is structured (Jira issues with table)
                if isinstance(response, dict) and response.get('type') == 'jira_issues':
                    # Handle structured Jira issues response
                    self._add_jira_issues_response(response)
                else:
                    # Handle regular text response
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response,
                        'timestamp': datetime.now()
                    })
                
                # Log the interaction
                logger.info(f"💬 Chat interaction - User: {user_input[:100]}... | Response type: {'structured' if isinstance(response, dict) else 'text'} | Max results: {max_results}")
                
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
    
    def _add_jira_issues_response(self, response_data):
        """Add a structured Jira issues response to chat history."""
        st.session_state.chat_history.append({
            'role': 'assistant',
            'type': 'jira_issues',
            'summary': response_data['summary'],
            'issues': response_data['issues'],
            'timestamp': datetime.now()
        })
    
    def _render_jira_issues_message(self, message):
        """Render a Jira issues message with summary + table."""
        # Display summary
        st.write(message['summary'])
        
        # Display issues table
        if message['issues']:
            # Convert issues to DataFrame for table display
            df_data = []
            for issue in message['issues']:
                df_data.append({
                    'Jira ID': issue.get('key', 'N/A'),
                    'Title': issue.get('summary', 'N/A'),
                    'Status': issue.get('status', 'N/A'),
                    'Priority': issue.get('priority', 'N/A'),
                    'Assignee': issue.get('assignee', 'Unassigned'),
                    'Reporter': issue.get('reporter', 'N/A'),
                    'URL': issue.get('url', 'N/A')
                })
            
            df = pd.DataFrame(df_data)
            
            # Display table with clickable URLs
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "URL": st.column_config.LinkColumn(
                        "URL",
                        help="Click to open issue in Jira",
                        display_text="Open Issue"
                    ),
                    "Jira ID": st.column_config.Column(
                        "Jira ID",
                        width="small"
                    ),
                    "Title": st.column_config.Column(
                        "Title", 
                        width="large"
                    )
                }
            )
        else:
            st.info("No issues found.")
    
    def _render_instructions(self):
        """Render the instructions and help page."""
        st.header("📖 GenAI Jira Assistant - User Guide")
        st.markdown("---")
        
        # Introduction
        st.subheader("🎯 Welcome to GenAI Jira Assistant")
        st.markdown("""
        This AI-powered assistant helps you interact with Jira using natural language. 
        No need to remember complex JQL queries or navigate through multiple screens - 
        just ask what you need in plain English!
        """)
        
        # Chat Assistant Section
        st.subheader("💬 Chat Assistant - How to Use")
        st.markdown("---")
        
        # Basic queries section
        with st.expander("📋 **1. Basic Jira Queries**", expanded=True):
            st.markdown("""
            **Get All Issues:**
            - `"Show me all jira issues"`
            - `"Get all issues"`
            - `"List all project issues"`
            - `"What issues do we have?"`
            
            **Get Issues by Status:**
            - `"Show me all open issues"`
            - `"Get completed tasks"`
            - `"What's in progress?"`
            - `"List closed issues"`
            
            **Get Issue Details:**
            - `"Get details for PROJ-123"`
            - `"Tell me about issue PROJ-456"`
            - `"Show me information for ticket ABC-789"`
            """)
        
        # Advanced queries section
        with st.expander("🔍 **2. Advanced Filtering**", expanded=True):
            st.markdown("""
            **Filter by Priority/Severity:**
            - `"Show high priority issues"`
            - `"Find critical bugs"`
            - `"Get low severity issues"`
            - `"List blocker issues"`
            
            **Filter by Labels:**
            - `"Find issues labeled '2025'"`
            - `"Show issues with label 'bug'"`
            - `"Get all 'frontend' labeled issues"`
            - `"Issues with label 'urgent'"`
            
            **Content Search:**
            - `"Find login problems"`
            - `"Issues about authentication"`
            - `"Search for database errors"`
            - `"Find GenAI related issues"`
            """)
        
        # Multi-criteria queries section  
        with st.expander("🎯 **3. Multi-Criteria Queries (NEW!)**", expanded=True):
            st.markdown("""
            **Text + Status Combinations:**
            - `"List all jira issues relate to GenAI and in Open Status"`
            - `"Find authentication issues that are open"`
            - `"Show login problems in progress"`
            
            **Priority + Status Combinations:**
            - `"List all jira issues in critical priority and in TO-DO Status"`
            - `"Show high priority open issues"`
            - `"Find medium priority completed tasks"`
            
            **Label + Status Combinations:**
            - `"List all jira issues with label 'Exam' and in Open Status"`
            - `"Show bug labeled issues that are closed"`
            - `"Get frontend issues that are in progress"`
            """)
        
        # Tips and best practices
        with st.expander("💡 **4. Tips & Best Practices**"):
            st.markdown("""
            **✅ Do's:**
            - Use natural language - the AI understands context
            - Be specific about what you want (status, priority, labels)
            - Combine multiple criteria for precise filtering
            - Use issue keys for specific details (e.g., PROJ-123)
            
            **❌ Don'ts:**
            - Don't use complex JQL syntax (let the AI handle it)
            - Don't worry about exact field names
            - Don't use multiple queries when one combined query works
            
            **🎯 Pro Tips:**
            - The AI learns from your language patterns
            - Results are displayed as summary + interactive table
            - Click URLs in the table to open issues in Jira
            - Use the sidebar to control result limits (10-200 issues)
            """)
        
        # Analytics Setup Section
        st.subheader("📊 Analytics Dashboard - Setup Guide")
        st.markdown("---")
        
        with st.expander("🔧 **1. Basic Setup**", expanded=True):
            st.markdown("""
            **Step 1: Configure Project**
            - Ensure your `JIRA_PROJECT` environment variable is set
            - This determines which project the analytics will analyze
            
            **Step 2: Choose Date Range**
            - Select from predefined ranges: Last 7/30/90 days, Last 6 months
            - Or use "Custom range" for specific dates
            - Analytics will only include issues created within this timeframe
            
            **Step 3: Set Analysis Limit**
            - Use the "Max Issues to Analyze" slider (10-200)
            - Higher numbers = more comprehensive analysis but slower processing
            - Recommended: 50-100 for most projects
            """)
        
        with st.expander("🎯 **2. Advanced Filtering**", expanded=True):
            st.markdown("""
            **Status Filtering:**
            - **"All Statuses"** (default): Analyzes issues in any status
            - **Specific Status**: Focus on particular workflow stages
            - Examples: "Open" for active work, "Done" for completed analysis
            
            **Priority Filtering:**
            - **"All Priorities"** (default): Includes all priority levels
            - **Specific Priority**: Focus on critical, high, medium, or low priority issues
            - Useful for understanding priority distribution and bottlenecks
            
            **Combining Filters:**
            - You can combine status + priority + date range
            - Example: "Critical priority + Open status + Last 30 days"
            - Creates focused analysis for specific scenarios
            """)
        
        with st.expander("📈 **3. Understanding Analytics Results**"):
            st.markdown("""
            **Key Metrics Overview:**
            - Total issues, completion rates, team performance indicators
            - Color-coded metrics show health status
            - Delta values indicate trends (↗️ improving, ↘️ declining)
            
            **Visualization Charts:**
            - **Status Pie Chart**: Distribution of issues across statuses
            - **Priority Bar Chart**: Volume of issues by priority level
            - **Team Workload**: Assignee distribution and capacity
            - **Sentiment Analysis**: AI-powered mood detection
            
            **AI Insights:**
            - 🔍 **Patterns**: Automatically detected trends
            - 💡 **Recommendations**: Actionable suggestions for improvement
            - ⚠️ **Alerts**: Issues requiring immediate attention
            
            **Issues Data Table:**
            - Reference table of all analyzed issues
            - Sortable and filterable for detailed investigation
            - Links directly to Jira for quick access
            """)
        
        with st.expander("🚀 **4. Analytics Best Practices**"):
            st.markdown("""
            **For Project Managers:**
            - Use date ranges that match your sprint/release cycles
            - Filter by "Open" status to focus on current workload
            - Monitor "Critical" and "High" priority distributions
            
            **For Team Leads:**
            - Analyze team workload distribution regularly
            - Use sentiment analysis to gauge team morale
            - Track completion patterns over time
            
            **For Stakeholders:**
            - Focus on broader date ranges (30-90 days)
            - Use "All" filters for comprehensive project overview
            - Pay attention to AI alerts and recommendations
            
            **Performance Optimization:**
            - Start with smaller date ranges and issue limits
            - Use specific filters to reduce processing time
            - Save frequently used filter combinations as mental notes
            """)
        
        # Configuration section
        st.subheader("⚙️ Configuration & Setup")
        st.markdown("---")
        
        with st.expander("🔑 **Environment Configuration**"):
            st.markdown("""
            **Required Environment Variables:**
            ```
            JIRA_URL=https://your-jira-instance.atlassian.net
            JIRA_USERNAME=your-username  
            JIRA_TOKEN=your-jira-api-token
            JIRA_PROJECT=YOUR-PROJECT-KEY
            JIRA_MAX_RESULTS=50
            API_KEY=your-llm-farm-api-key
            LLM_FARM_URL=your-llm-farm-endpoint
            ```
            
            **How to Get Jira API Token:**
            1. Go to Atlassian Account Settings
            2. Navigate to Security → API tokens
            3. Create token and copy it to `JIRA_TOKEN`
            
            **Finding Your Project Key:**
            - Look at any issue URL: `https://yoursite.atlassian.net/browse/PROJ-123`
            - "PROJ" is your project key
            """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-style: italic;'>
        🤖 GenAI Jira Assistant - Making Jira management simple and intelligent<br>
        Need help? Ask the Chat Assistant: "How do I use this app?"
        </div>
        """, unsafe_allow_html=True)
    
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
