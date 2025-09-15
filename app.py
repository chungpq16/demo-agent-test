#!/usr/bin/env python3
"""
Streamlit UI for GenAI Jira Assistant
Web interface for interacting with Jira through natural language prompts.
"""
import streamlit as st
import os
import sys
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import JiraOrchestrator
from logger import get_logger

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="GenAI Jira Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = get_logger()


class StreamlitJiraApp:
    """Streamlit application for Jira GenAI Assistant."""
    
    def __init__(self):
        """Initialize the Streamlit app."""
        self.init_session_state()
        self.orchestrator = self.get_orchestrator()
    
    def init_session_state(self):
        """Initialize Streamlit session state."""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'orchestrator_initialized' not in st.session_state:
            st.session_state.orchestrator_initialized = False
        if 'health_status' not in st.session_state:
            st.session_state.health_status = {}
    
    @st.cache_resource
    def get_orchestrator(_self):
        """Get or create orchestrator instance (cached)."""
        try:
            orchestrator = JiraOrchestrator()
            st.session_state.orchestrator_initialized = True
            logger.info("Orchestrator initialized successfully for Streamlit")
            return orchestrator
        except Exception as e:
            st.session_state.orchestrator_initialized = False
            logger.error(f"Failed to initialize orchestrator: {str(e)}")
            st.error(f"❌ Failed to initialize: {str(e)}")
            return None
    
    def render_sidebar(self):
        """Render the sidebar with configuration and status."""
        with st.sidebar:
            st.title("🤖 GenAI Jira Assistant")
            st.markdown("---")
            
            # Health Status Section
            st.subheader("🏥 System Status")
            
            if st.button("🔄 Check Health", use_container_width=True):
                with st.spinner("Checking system health..."):
                    if self.orchestrator:
                        st.session_state.health_status = self.orchestrator.health_check()
                    else:
                        st.session_state.health_status = {
                            "llm_farm": False,
                            "jira": False,
                            "overall": False
                        }
            
            # Display health status
            if st.session_state.health_status:
                for component, status in st.session_state.health_status.items():
                    if component == "overall":
                        continue
                    emoji = "✅" if status else "❌"
                    st.write(f"{emoji} **{component.replace('_', ' ').title()}**: {'Healthy' if status else 'Unhealthy'}")
                
                overall_status = st.session_state.health_status.get("overall", False)
                if overall_status:
                    st.success("🟢 All systems operational")
                else:
                    st.error("🔴 System issues detected")
            
            st.markdown("---")
            
            # Configuration Status
            st.subheader("⚙️ Configuration")
            
            required_vars = [
                'API_KEY', 'LLM_FARM_URL', 
                'JIRA_URL', 'JIRA_USERNAME', 'JIRA_TOKEN', 'JIRA_PROJECT'
            ]
            
            config_ok = True
            for var in required_vars:
                value = os.getenv(var)
                if value:
                    st.write(f"✅ {var}")
                else:
                    st.write(f"❌ {var}")
                    config_ok = False
            
            if config_ok:
                st.success("🟢 Configuration complete")
            else:
                st.error("🔴 Missing configuration")
                st.info("💡 Please update your .env file")
            
            st.markdown("---")
            
            # Quick Actions
            st.subheader("🚀 Quick Actions")
            
            quick_queries = [
                "Show me all open issues",
                "What issues are in progress?",
                "Get all completed issues",
                "Find high priority issues",
                "Show me recent issues"
            ]
            
            for query in quick_queries:
                if st.button(query, key=f"quick_{hash(query)}", use_container_width=True):
                    self.process_query(query)
            
            st.markdown("---")
            
            # Clear Chat
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    def render_main_chat(self):
        """Render the main chat interface."""
        st.title("💬 Chat with Your Jira Assistant")
        
        # Display initialization status
        if not st.session_state.orchestrator_initialized:
            st.error("❌ System not initialized. Please check your configuration and try refreshing the page.")
            return
        
        # Chat history container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                        st.caption(f"🕒 {message['timestamp']}")
                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])
                        st.caption(f"🕒 {message['timestamp']}")
                        
                        # If the response contains structured data, display it
                        if "data" in message:
                            self.render_structured_data(message["data"])
        
        # Chat input
        user_input = st.chat_input("Ask me about your Jira issues... (e.g., 'Show me all open issues')")
        
        if user_input:
            self.process_query(user_input)
    
    def process_query(self, user_input: str):
        """Process user query and update chat history."""
        if not self.orchestrator:
            st.error("❌ System not available. Please check configuration.")
            return
        
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        # Process the query
        with st.spinner("🔄 Processing your request..."):
            try:
                response = self.orchestrator.process_request(user_input)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
            except Exception as e:
                error_msg = f"❌ Error processing request: {str(e)}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                logger.error(f"Error in Streamlit query processing: {str(e)}")
        
        st.rerun()
    
    def render_structured_data(self, data: Any):
        """Render structured data (like Jira issues) in a nice format."""
        try:
            if isinstance(data, list) and len(data) > 0:
                # Convert to DataFrame for better display
                df = pd.DataFrame(data)
                
                # Customize columns for better display
                if 'key' in df.columns:
                    df = df[['key', 'summary', 'status', 'assignee', 'priority', 'created']]
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show summary stats
                if len(data) > 1:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Issues", len(data))
                    
                    if 'status' in df.columns:
                        status_counts = df['status'].value_counts()
                        with col2:
                            st.metric("Most Common Status", status_counts.index[0])
                        with col3:
                            st.metric("Count", status_counts.iloc[0])
                        
                        # Status distribution chart
                        if len(status_counts) > 1:
                            st.subheader("📊 Status Distribution")
                            st.bar_chart(status_counts)
            
            elif isinstance(data, dict):
                # Display single issue details
                st.subheader("📋 Issue Details")
                
                # Key information in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Key:** {data.get('key', 'N/A')}")
                    st.write(f"**Status:** {data.get('status', 'N/A')}")
                    st.write(f"**Priority:** {data.get('priority', 'N/A')}")
                    st.write(f"**Issue Type:** {data.get('issue_type', 'N/A')}")
                
                with col2:
                    st.write(f"**Assignee:** {data.get('assignee', 'Unassigned')}")
                    st.write(f"**Reporter:** {data.get('reporter', 'N/A')}")
                    st.write(f"**Created:** {data.get('created', 'N/A')}")
                    st.write(f"**Updated:** {data.get('updated', 'N/A')}")
                
                # Summary and description
                if data.get('summary'):
                    st.write(f"**Summary:** {data['summary']}")
                
                if data.get('description'):
                    st.write("**Description:**")
                    st.write(data['description'])
                
                # URL link
                if data.get('url'):
                    st.link_button("🔗 View in Jira", data['url'])
        
        except Exception as e:
            logger.error(f"Error rendering structured data: {str(e)}")
            st.write("📄 Raw data:")
            st.json(data)
    
    def render_help_tab(self):
        """Render the help tab."""
        st.title("❓ Help & Examples")
        
        st.markdown("""
        ## 🚀 Getting Started
        
        Welcome to the GenAI Jira Assistant! You can interact with your Jira project using natural language.
        
        ### 📋 What You Can Do
        
        #### Get Issues
        - "Show me all issues"
        - "Get all open issues"  
        - "What issues are in progress?"
        - "Show me completed tasks"
        
        #### Search Issues
        - "Find issues about login"
        - "Search for bug reports"
        - "Issues related to authentication"
        - "Show me high priority issues"
        
        #### Issue Details
        - "Get details for PROJ-123"
        - "Tell me about issue PROJ-456"
        - "What's the status of PROJ-789?"
        
        ### 💡 Tips
        - Use natural language - no need for specific commands
        - You can ask follow-up questions
        - Issue keys (like PROJ-123) give you detailed information
        - The assistant understands various status names
        
        ### 🔧 Quick Actions
        Use the sidebar for common queries or check system health.
        
        ### 🆘 Troubleshooting
        
        If you encounter issues:
        1. Check the **System Status** in the sidebar
        2. Ensure all configuration items show ✅
        3. Try the **Check Health** button
        4. Verify your .env file has all required values
        
        ### 🔒 Security
        All credentials are stored securely in environment variables.
        No sensitive information is displayed in the interface.
        """)
    
    def run(self):
        """Run the Streamlit application."""
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2 = st.tabs(["💬 Chat", "❓ Help"])
        
        with tab1:
            self.render_main_chat()
        
        with tab2:
            self.render_help_tab()


def main():
    """Main function to run the Streamlit app."""
    app = StreamlitJiraApp()
    app.run()


if __name__ == "__main__":
    main()
