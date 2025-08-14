"""
AI Agent for Infrastructure Monitoring Demo
Uses LangGraph for agent orchestration and tool routing
"""
import os
import json
import requests
import streamlit as st
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import logging

# Configure logging for console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # This outputs to console
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ================================
# INFRASTRUCTURE MONITORING TOOLS (LangChain Tools)
# ================================

@tool
def check_infrastructure() -> str:
    """Check system infrastructure status including CPU, memory, disk usage and uptime"""
    logger.info("🔧 Tool called: check_infrastructure() - Checking system infrastructure...")
    try:
        response = requests.get("http://localhost:5000/infrastructure", timeout=5)
        result = json.dumps({
            "endpoint": "/infrastructure",
            "status_code": response.status_code,
            "response": response.json()
        })
        logger.info(f"✅ Infrastructure check completed with status {response.status_code}")
        return result
    except Exception as e:
        error_result = json.dumps({
            "endpoint": "/infrastructure", 
            "error": f"Failed to connect: {str(e)}"
        })
        logger.error(f"❌ Infrastructure check failed: {str(e)}")
        return error_result

@tool
def check_network() -> str:
    """Check network connectivity, DNS resolution, latency and bandwidth availability"""
    logger.info("🔧 Tool called: check_network() - Checking network connectivity...")
    try:
        response = requests.get("http://localhost:5000/network", timeout=5)
        result = json.dumps({
            "endpoint": "/network",
            "status_code": response.status_code,
            "response": response.json()
        })
        logger.info(f"✅ Network check completed with status {response.status_code}")
        return result
    except Exception as e:
        error_result = json.dumps({
            "endpoint": "/network",
            "error": f"Failed to connect: {str(e)}"
        })
        logger.error(f"❌ Network check failed: {str(e)}")
        return error_result

@tool
def check_certificate() -> str:
    """Check SSL certificate status, expiry dates and certificate health"""
    logger.info("🔧 Tool called: check_certificate() - Checking SSL certificates...")
    try:
        response = requests.get("http://localhost:5000/certificate", timeout=5)
        result = json.dumps({
            "endpoint": "/certificate",
            "status_code": response.status_code,
            "response": response.json()
        })
        logger.info(f"✅ Certificate check completed with status {response.status_code}")
        return result
    except Exception as e:
        error_result = json.dumps({
            "endpoint": "/certificate",
            "error": f"Failed to connect: {str(e)}"
        })
        logger.error(f"❌ Certificate check failed: {str(e)}")
        return error_result

@tool
def check_deployment() -> str:
    """Check deployment status, recent deployments and any deployment failures"""
    logger.info("🔧 Tool called: check_deployment() - Checking deployment status...")
    try:
        response = requests.get("http://localhost:5000/deployment", timeout=5)
        result = json.dumps({
            "endpoint": "/deployment",
            "status_code": response.status_code,
            "response": response.json()
        })
        logger.info(f"✅ Deployment check completed with status {response.status_code}")
        return result
    except Exception as e:
        error_result = json.dumps({
            "endpoint": "/deployment",
            "error": f"Failed to connect: {str(e)}"
        })
        logger.error(f"❌ Deployment check failed: {str(e)}")
        return error_result

# Create tools list for LangGraph
tools = [
    check_infrastructure,
    check_network, 
    check_certificate,
    check_deployment
]

# ================================
# STREAMLIT UI WITH LANGGRAPH AGENT
# ================================

def main():
    """Main Streamlit application for AI Infrastructure Agent"""
    import streamlit as st
    
    # Page configuration
    st.set_page_config(
        page_title="AI Infrastructure Agent", 
        page_icon="🤖",
        layout="wide"
    )
    
    # Title
    st.title("🤖 AI Infrastructure Monitoring Agent")
    st.markdown("*Intelligent agent for infrastructure monitoring and system diagnostics powered by LangGraph*")
    
    # Initialize LangGraph agent
    def create_agent():
        # Initialize the language model
        model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create the react agent (simplified without memory for compatibility)
        agent_executor = create_react_agent(model, tools)
        
        return agent_executor
    
    # Get the agent
    agent_executor = create_agent()
        
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about infrastructure monitoring..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response using LangGraph agent
        with st.chat_message("assistant"):
            try:
                # Create a placeholder for response
                message_placeholder = st.empty()
                
                # Log the agent execution start
                logger.info(f"🚀 Starting agent execution for prompt: '{prompt[:100]}...'")
                logger.info(f"📝 User message: {prompt}")
                
                # Execute the agent with the user's input (simplified approach)
                result = agent_executor.invoke({"messages": [{"role": "user", "content": prompt}]})
                
                # Log the result
                logger.info(f"✅ Agent execution completed successfully")
                logger.info(f"📤 Result type: {type(result)}")
                logger.info(f"📤 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                if isinstance(result, dict) and "messages" in result:
                    logger.info(f"📨 Number of messages in result: {len(result['messages'])}")
                    if result["messages"]:
                        last_msg = result["messages"][-1]
                        logger.info(f"📨 Last message type: {type(last_msg)}")
                        if hasattr(last_msg, 'content'):
                            logger.info(f"📨 Last message content preview: {str(last_msg.content)[:200]}...")
                
                # Extract the response
                if "messages" in result and result["messages"]:
                    # Get the last message from the agent
                    last_message = result["messages"][-1]
                    if hasattr(last_message, 'content'):
                        full_response = last_message.content
                    else:
                        full_response = str(last_message)
                else:
                    full_response = str(result)
                
                logger.info(f"💬 Final response length: {len(full_response)} characters")
                
                # Display the response
                message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                logger.error(f"❌ Agent execution failed: {str(e)}")
                logger.error(f"❌ Exception type: {type(e)}")
                error_message = f"❌ **Error:** {str(e)}"
                st.error(error_message)
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

if __name__ == "__main__":
    main()
