"""
Streamlit application for Jira AI Chatbot.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src.core.chatbot import JiraChatbot
from src.utils.debug_utils import setup_logging
import logging

# Load environment variables
load_dotenv()

# Setup logging based on DEBUG environment variable
debug_mode = os.getenv("DEBUG", "false").lower() == "true"
setup_logging(debug=debug_mode)
logger = logging.getLogger(__name__)

# Configure logging
logger.info("Starting Jira AI Chatbot Streamlit application")

# Page configuration
st.set_page_config(
    page_title="Jira AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .system-message {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        font-style: italic;
    }
    
    .stTextInput > div > div > input {
        font-size: 1.1rem;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    
    /* Hide the sidebar completely */
    .css-1d391kg {
        display: none;
    }
    
    /* Remove white background from chat input */
    .stChatInput {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Clean up chat input styling */
    .stChatInput > div {
        background: transparent !important;
        border: none !important;
    }
    
    /* Main content full width */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_chatbot():
    """Initialize the chatbot and handle any errors."""
    logger.debug("Initializing chatbot...")
    try:
        if 'chatbot' not in st.session_state:
            with st.spinner("Initializing Jira AI Chatbot..."):
                logger.debug("Creating new chatbot instance...")
                st.session_state.chatbot = JiraChatbot()
                logger.info("Chatbot initialized successfully")
                st.success("✅ Chatbot initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}", exc_info=True)
        st.error(f"❌ Failed to initialize chatbot: {str(e)}")
        st.info("Please check your environment variables and Jira credentials.")
        
        # Show debug info in case of error
        if os.getenv("DEBUG", "false").lower() == "true":
            st.error("Debug mode is enabled. Check the debug log file: jira_chatbot_debug.log")
        
        return False

def display_chat_history():
    """Display the chat history."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Create a container for chat messages
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def handle_user_input():
    """Handle user input and generate response."""
    if prompt := st.chat_input("Ask me about Jira issues..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Check for system commands first
                    system_response = st.session_state.chatbot.handle_system_commands(prompt)
                    if system_response:
                        response = system_response
                    else:
                        response = st.session_state.chatbot.chat(prompt)
                    
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def main():
    """Main application function."""
    # Title
    st.markdown('<div class="main-header">🤖 Jira AI Chatbot</div>', unsafe_allow_html=True)
    
    # Show project scope if configured
    project_key = os.getenv("JIRA_PROJECT_KEY")
    if project_key:
        st.markdown(f"*🎯 Project-scoped to: **{project_key}***")
    else:
        st.markdown("*🌐 Searching across all accessible projects*")
    
    st.markdown("*Intelligent Jira issue management powered by Custom LLM Farm*")
    
    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize chatbot
    if not initialize_chatbot():
        st.stop()
    
    # Main chat area (full width)
    # Welcome message for new users
    if len(st.session_state.messages) == 0:
        with st.chat_message("assistant"):
            project_scope_msg = f"\n\n🎯 **Current scope**: {project_key}" if project_key else "\n\n🌐 **Current scope**: All accessible projects"
            welcome_msg = f"""
👋 **Welcome to Jira AI Chatbot!**

I'm here to help you manage and analyze your Jira issues. You can:

🔍 **Ask about specific issues:** "Tell me about issue PROJ-123"
📋 **List issues by status:** "Show me all To Do issues"
📊 **Get insights:** "Analyze all tickets"
🔎 **Search issues:** "Find high priority bugs"{project_scope_msg}

Type your question below to get started!
            """
            st.markdown(welcome_msg)
    
    # Display chat history
    display_chat_history()
    
    # Handle user input - this will automatically appear at the bottom
    handle_user_input()

if __name__ == "__main__":
    main()
