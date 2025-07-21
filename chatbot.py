"""
Main Chatbot class integrating all components for Jira issue management.
"""

from jira_agent import JiraAgent
from jira_client import JiraClient
from debug_utils import setup_logging, get_debug_info
import logging
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging based on DEBUG environment variable
debug_mode = os.getenv("DEBUG", "false").lower() == "true"
setup_logging(debug=debug_mode)

logger = logging.getLogger(__name__)

class JiraChatbot:
    """
    Main chatbot class that orchestrates Jira issue management using simplified agent.
    """
    
    def __init__(self):
        """Initialize the Jira chatbot."""
        logger.debug("Initializing JiraChatbot...")
        
        try:
            logger.debug("Starting Jira client initialization...")
            # Initialize Jira client first
            self.jira_client = JiraClient()
            logger.debug("Jira client initialized successfully")
            
            logger.debug("Starting agent initialization...")
            # Initialize the agent with shared Jira client
            self.agent = JiraAgent(jira_client=self.jira_client)
            logger.debug("Agent initialized successfully")
            
            # Chat history storage
            self.chat_history: List[Dict[str, str]] = []
            
            logger.info("Jira chatbot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Jira chatbot: {e}", exc_info=True)
            raise
    
    def chat(self, user_input: str, use_history: bool = True) -> str:
        """
        Process user input and return chatbot response.
        
        Args:
            user_input: User's message/question
            use_history: Whether to use conversation history
            
        Returns:
            Chatbot's response string
        """
        logger.debug(f"Processing chat input: {user_input[:100]}...")
        
        try:
            if use_history and self.chat_history:
                logger.debug(f"Using chat history with {len(self.chat_history)} previous messages")
                response = self.agent.chat_with_history(user_input, self.chat_history)
            else:
                logger.debug("Using fresh conversation (no history)")
                response = self.agent.chat(user_input)
            
            # Update chat history
            if use_history:
                self.chat_history.append({"role": "user", "content": user_input})
                self.chat_history.append({"role": "assistant", "content": response})
                
                # Keep history limited to last 20 messages (10 exchanges)
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
                    logger.debug("Chat history trimmed to 20 messages")
            
            logger.info(f"Chat response generated successfully (length: {len(response)})")
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = []
        logger.info("Chat history cleared")
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the current chat history."""
        return self.chat_history.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information and health check.
        
        Returns:
            Dictionary containing system status
        """
        try:
            # Test Jira connection
            projects = self.jira_client.get_project_info()
            project_scope = self.jira_client.get_current_project_scope()
            
            info = {
                "status": "healthy",
                "jira_connection": "connected",
                "accessible_projects": len(projects),
                "project_scope": project_scope if project_scope else "All projects",
                "is_project_scoped": self.jira_client.is_project_scoped(),
                "chat_history_length": len(self.chat_history),
                "agent_initialized": self.agent is not None,
                "available_tools": [
                    "get_issues_by_status",
                    "get_issue_details", 
                    "get_all_issues",
                    "get_all_issues_for_analysis",
                    "search_issues_by_jql",
                    "get_project_summary"
                ]
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {
                "status": "error",
                "error": str(e),
                "chat_history_length": len(self.chat_history),
                "agent_initialized": self.agent is not None
            }
    
    def get_help_message(self) -> str:
        """
        Get help message with available commands and examples.
        
        Returns:
            Help message string
        """
        help_text = """
🤖 **Jira AI Chatbot Help**

I can help you manage and analyze Jira issues. Here's what I can do:

**📋 Issue Retrieval:**
- "Show me all To Do issues"
- "List issues with status 'In Progress'"
- "Get all Done tickets"

**🔍 Issue Details:**
- "Tell me about issue PROJ-123"
- "Show details for ticket ABC-456"
- "What's the status of TASK-789?"

**📊 Analysis & Insights:**
- "Analyze all tickets"
- "Give me insights about current issues"
- "What are the common themes in our backlog?"
- "Show me issue distribution by status"

**🔎 Advanced Search:**
- "Find issues assigned to John Doe"
- "Search for high priority bugs"
- "Show me issues created this week"

**📁 Project Information:**
- "What projects do I have access to?"
- "Show me project summary"

**💡 Tips:**
- You can ask in natural language - I'll understand!
- I remember our conversation, so you can ask follow-up questions
- For specific issues, use the exact issue key (e.g., PROJ-123)

**🔧 System Commands:**
- "Help" or "What can you do?" - Show this help message
- "Clear history" - Clear our conversation history
- "System status" - Check system health

Feel free to ask me anything about your Jira issues! 🚀
        """
        return help_text.strip()
    
    def handle_system_commands(self, user_input: str) -> Optional[str]:
        """
        Handle system-level commands.
        
        Args:
            user_input: User's input
            
        Returns:
            System response if it's a system command, None otherwise
        """
        input_lower = user_input.lower().strip()
        
        if input_lower in ["help", "what can you do", "what can you do?", "commands"]:
            return self.get_help_message()
        
        elif input_lower in ["clear history", "clear chat", "reset"]:
            self.clear_history()
            return "✅ Chat history has been cleared. Starting fresh!"
        
        elif input_lower in ["system status", "status", "health check"]:
            info = self.get_system_info()
            if info["status"] == "healthy":
                return f"""✅ **System Status: Healthy**

🔗 Jira Connection: Connected
📁 Accessible Projects: {info['accessible_projects']}
💬 Chat History: {info['chat_history_length']} messages
🤖 Agent Status: Initialized
🔧 Available Tools: {len(info['available_tools'])}

Ready to help with your Jira issues! 🚀"""
            else:
                return f"❌ **System Status: Error**\n\nError: {info.get('error', 'Unknown error')}"
        
        elif input_lower in ["debug info", "debug", "system debug"]:
            debug_info = get_debug_info()
            return f"""🔧 **Debug Information**

**System:**
- Platform: {debug_info['system']['platform']}
- Python: {debug_info['system']['python_version']}
- Working Directory: {debug_info['system']['working_directory']}

**Configuration:**
- Debug Mode: {debug_info['configuration']['debug_mode']}
- OpenAI Model: {debug_info['configuration']['openai_model']}
- Max Chat History: {debug_info['configuration']['max_chat_history']}

**Environment Variables:**
- JIRA_SERVER_URL: {'✅' if debug_info['environment_variables']['JIRA_SERVER_URL'] else '❌'}
- JIRA_USERNAME: {'✅' if debug_info['environment_variables']['JIRA_USERNAME'] else '❌'}
- JIRA_API_TOKEN: {'✅' if debug_info['environment_variables']['JIRA_API_TOKEN'] else '❌'}
- OPENAI_API_KEY: {'✅' if debug_info['environment_variables']['OPENAI_API_KEY'] else '❌'}

**Validation:**
- Configuration Valid: {'✅' if debug_info['configuration']['validation']['is_valid'] else '❌'}
- Missing Fields: {debug_info['configuration']['validation']['missing'] if debug_info['configuration']['validation']['missing'] else 'None'}

Debug log file: jira_chatbot_debug.log"""
        
        return None
