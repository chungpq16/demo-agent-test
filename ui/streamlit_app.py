"""
Streamlit UI for GenAI Jira Assistant
Web interface for interacting with Jira through natural language prompts.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys
from typing import Dict, List, Any, Optional

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import JiraOrchestrator
from logger import get_logger

# Configure Streamlit page
st.set_page_config(
    page_title="GenAI Jira Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = get_logger()

class StreamlitUI:
    """Streamlit UI for GenAI Jira Assistant."""
    
    def __init__(self):
        """Initialize the Streamlit UI."""
        self.init_session_state()
        
    def init_session_state(self):
        """Initialize Streamlit session state."""
        if 'orchestrator' not in st.session_state:
            st.session_state.orchestrator = None
            st.session_state.initialized = False
            st.session_state.chat_history = []
            st.session_state.health_status = {}
    
    def initialize_app(self) -> bool:
        """Initialize the application components."""
        if st.session_state.initialized and st.session_state.orchestrator:
            return True
        
        try:
            with st.spinner("Initializing GenAI Jira Assistant..."):
                st.session_state.orchestrator = JiraOrchestrator()
                st.session_state.health_status = st.session_state.orchestrator.health_check()
                st.session_state.initialized = True
                logger.info("Streamlit app initialized successfully")
                return True
                
        except Exception as e:
            st.error(f"❌ Failed to initialize application: {str(e)}")
            logger.error(f"Failed to initialize Streamlit app: {str(e)}")
            return False
    
    def render_sidebar(self):
        """Render the sidebar with navigation and status."""
        st.sidebar.title("🤖 GenAI Jira Assistant")
        
        # Navigation
        page = st.sidebar.selectbox(
            "Navigate to:",
            ["💬 Chat Interface", "📊 Dashboard", "🔧 Settings", "📋 Help"]
        )
        
        # Health status
        st.sidebar.subheader("🏥 System Health")
        if st.session_state.get('health_status'):
            for component, status in st.session_state.health_status.items():
                if component != 'overall':
                    emoji = "✅" if status else "❌"
                    st.sidebar.text(f"{emoji} {component.replace('_', ' ').title()}")
        
        # Refresh health status button
        if st.sidebar.button("🔄 Refresh Health"):
            if st.session_state.orchestrator:
                st.session_state.health_status = st.session_state.orchestrator.health_check()
                st.rerun()
        
        # Quick stats
        if st.session_state.orchestrator:
            st.sidebar.subheader("📈 Quick Stats")
            try:
                # Get recent issues for stats
                recent_issues = st.session_state.orchestrator.jira_client.get_all_issues(max_results=100)
                if recent_issues:
                    st.sidebar.metric("Total Issues", len(recent_issues))
                    
                    # Status distribution
                    status_counts = {}
                    for issue in recent_issues:
                        status = issue.get('status', 'Unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    for status, count in list(status_counts.items())[:3]:
                        st.sidebar.metric(status, count)
            except Exception as e:
                st.sidebar.error("Could not load stats")
        
        return page
    
    def render_chat_interface(self):
        """Render the main chat interface."""
        st.title("💬 Chat with Your Jira Assistant")
        
        # Chat history
        if st.session_state.chat_history:
            st.subheader("Chat History")
            for i, (user_msg, bot_response) in enumerate(st.session_state.chat_history[-5:]):  # Show last 5
                with st.container():
                    st.markdown(f"**You:** {user_msg}")
                    st.markdown(f"**Assistant:** {bot_response}")
                    st.divider()
        
        # Input area
        st.subheader("Ask about your Jira issues")
        
        # Quick action buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📋 All Issues"):
                self.process_query("Show me all issues")
        with col2:
            if st.button("🔓 Open Issues"):
                self.process_query("Show me all open issues")
        with col3:
            if st.button("⚡ In Progress"):
                self.process_query("What issues are in progress?")
        with col4:
            if st.button("✅ Done"):
                self.process_query("Show me completed issues")
        
        # Text input
        user_input = st.text_area(
            "Type your question here...",
            placeholder="e.g., 'Show me all high priority bugs' or 'Get details for PROJ-123'",
            height=100
        )
        
        col1, col2, col3 = st.columns([1, 1, 8])
        with col1:
            if st.button("🚀 Send", type="primary") and user_input.strip():
                self.process_query(user_input)
        
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.chat_history = []
                st.rerun()
    
    def process_query(self, query: str):
        """Process user query and display response."""
        if not st.session_state.orchestrator:
            st.error("❌ Application not initialized properly")
            return
        
        try:
            with st.spinner("Processing your request..."):
                response = st.session_state.orchestrator.process_request(query)
                
                # Add to chat history
                st.session_state.chat_history.append((query, response))
                
                # Display response
                st.success("✅ Response received!")
                st.markdown(f"**Your question:** {query}")
                st.markdown(f"**Response:** {response}")
                
                # Auto-scroll to bottom
                st.rerun()
                
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            st.error(f"❌ {error_msg}")
            logger.error(error_msg)
    
    def render_dashboard(self):
        """Render the dashboard with Jira analytics."""
        st.title("📊 Jira Dashboard")
        
        if not st.session_state.orchestrator:
            st.warning("⚠️ Application not initialized")
            return
        
        try:
            # Get issues for dashboard
            with st.spinner("Loading dashboard data..."):
                all_issues = st.session_state.orchestrator.jira_client.get_all_issues(max_results=200)
            
            if not all_issues:
                st.info("📝 No issues found or unable to load data")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(all_issues)
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Issues", len(df))
            
            with col2:
                open_issues = len(df[df['status'].isin(['Open', 'To Do', 'New'])])
                st.metric("Open Issues", open_issues)
            
            with col3:
                in_progress = len(df[df['status'].isin(['In Progress', 'In Review'])])
                st.metric("In Progress", in_progress)
            
            with col4:
                done_issues = len(df[df['status'].isin(['Done', 'Closed', 'Resolved'])])
                st.metric("Completed", done_issues)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Status distribution
                st.subheader("📈 Status Distribution")
                status_counts = df['status'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Issues by Status"
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                # Priority distribution
                st.subheader("⚡ Priority Distribution")
                if 'priority' in df.columns and not df['priority'].isna().all():
                    priority_counts = df['priority'].value_counts()
                    fig_priority = px.bar(
                        x=priority_counts.index,
                        y=priority_counts.values,
                        title="Issues by Priority"
                    )
                    st.plotly_chart(fig_priority, use_container_width=True)
                else:
                    st.info("Priority data not available")
            
            # Issue type distribution
            if 'issue_type' in df.columns:
                st.subheader("🏷️ Issue Types")
                type_counts = df['issue_type'].value_counts()
                fig_types = px.bar(
                    x=type_counts.index,
                    y=type_counts.values,
                    title="Issues by Type"
                )
                st.plotly_chart(fig_types, use_container_width=True)
            
            # Recent issues table
            st.subheader("📋 Recent Issues")
            display_df = df[['key', 'summary', 'status', 'priority', 'assignee', 'created']].head(10)
            st.dataframe(display_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error loading dashboard: {str(e)}")
            logger.error(f"Dashboard error: {str(e)}")
    
    def render_settings(self):
        """Render the settings page."""
        st.title("🔧 Settings")
        
        # Environment status
        st.subheader("🌍 Environment Configuration")
        
        env_vars = [
            'API_KEY', 'LLM_FARM_URL', 'JIRA_URL', 
            'JIRA_USERNAME', 'JIRA_TOKEN', 'JIRA_PROJECT'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                if 'KEY' in var or 'TOKEN' in var:
                    display_value = '*' * 20  # Hide sensitive values
                else:
                    display_value = value
                st.success(f"✅ {var}: {display_value}")
            else:
                st.error(f"❌ {var}: Not set")
        
        # Application settings
        st.subheader("⚙️ Application Settings")
        
        # Log level
        current_log_level = os.getenv('LOG_LEVEL', 'INFO')
        new_log_level = st.selectbox(
            "Log Level",
            ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            index=['DEBUG', 'INFO', 'WARNING', 'ERROR'].index(current_log_level)
        )
        
        if new_log_level != current_log_level:
            st.info(f"Log level will be changed to {new_log_level} on next restart")
        
        # Connection test
        st.subheader("🔍 Connection Test")
        if st.button("Test Connections"):
            if st.session_state.orchestrator:
                health = st.session_state.orchestrator.health_check()
                for component, status in health.items():
                    if status:
                        st.success(f"✅ {component}: Connected")
                    else:
                        st.error(f"❌ {component}: Failed")
            else:
                st.error("❌ Application not initialized")
    
    def render_help(self):
        """Render the help page."""
        st.title("📋 Help & Documentation")
        
        st.markdown("""
        ## 🤖 How to Use the GenAI Jira Assistant
        
        ### 💬 Chat Interface
        Use natural language to interact with your Jira issues:
        
        **Examples:**
        - "Show me all open issues"
        - "Get details for PROJ-123" 
        - "Find issues about login problems"
        - "What high priority bugs do we have?"
        - "Show me issues assigned to John"
        
        ### 📊 Dashboard
        View visual analytics of your Jira data:
        - Issue status distribution
        - Priority breakdown
        - Issue type analysis
        - Recent issues table
        
        ### 🔧 Settings
        Check configuration and test connections:
        - Environment variable status
        - Connection health checks
        - Application settings
        
        ## 💡 Tips
        
        1. **Be Specific**: The more specific your query, the better the results
        2. **Use Issue Keys**: Reference specific issues using their keys (e.g., PROJ-123)
        3. **Natural Language**: Ask questions as you would to a human colleague
        4. **Try Different Phrasings**: If one query doesn't work, try rephrasing
        
        ## 🚀 Quick Actions
        
        Use the quick action buttons for common tasks:
        - 📋 All Issues
        - 🔓 Open Issues  
        - ⚡ In Progress
        - ✅ Done
        
        ## ❓ Common Queries
        
        | What you want | Example query |
        |---------------|---------------|
        | All issues | "Show me all issues" |
        | Open issues | "Get all open issues" |
        | Specific issue | "Tell me about PROJ-123" |
        | Search by text | "Find issues about authentication" |
        | By assignee | "Issues assigned to me" |
        | By status | "What's in progress?" |
        | By priority | "High priority issues" |
        
        ## 🆘 Troubleshooting
        
        If you encounter issues:
        
        1. **Check Health Status** in the sidebar
        2. **Verify Settings** in the Settings page
        3. **Clear Chat History** if responses seem outdated
        4. **Restart the application** if problems persist
        
        ## 📞 Support
        
        For technical support or feature requests, please contact your system administrator.
        """)
    
    def run(self):
        """Run the Streamlit application."""
        # Initialize app
        if not self.initialize_app():
            st.stop()
        
        # Render sidebar and get current page
        page = self.render_sidebar()
        
        # Render the selected page
        if page == "💬 Chat Interface":
            self.render_chat_interface()
        elif page == "📊 Dashboard":
            self.render_dashboard()
        elif page == "🔧 Settings":
            self.render_settings()
        elif page == "📋 Help":
            self.render_help()


def main():
    """Main function to run the Streamlit app."""
    try:
        # Custom CSS
        st.markdown("""
        <style>
        .main {
            padding-top: 2rem;
        }
        .stAlert {
            margin-top: 1rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #e6e9ef;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize and run the app
        app = StreamlitUI()
        app.run()
        
    except Exception as e:
        st.error(f"❌ Critical Error: {str(e)}")
        st.stop()


if __name__ == "__main__":
    main()
