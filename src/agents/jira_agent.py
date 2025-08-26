"""
Jira Agent that uses custom LLM farm API with prompt-based tool orchestration.
"""

from typing import List, Dict, Any
import json
import logging
import re
from src.tools.jira_tools import JIRA_TOOLS, initialize_tools
from src.clients.jira_client import JiraClient
from src.llm.custom_llm_client import create_llm_client

logger = logging.getLogger(__name__)

class JiraAgent:
    """
    Jira agent that uses custom LLM farm API with prompt-based tool calling.
    Since the API doesn't support automatic tool choice, we use prompt engineering
    to guide the LLM in deciding when and how to use tools.
    """
    
    def __init__(self, jira_client: JiraClient = None):
        """Initialize the Jira agent with custom LLM client."""
        logger.debug("Initializing JiraAgent with custom LLM...")
        
        # Initialize Jira client if not provided
        if jira_client is None:
            logger.debug("Creating new Jira client...")
            self.jira_client = JiraClient()
        else:
            self.jira_client = jira_client
        
        # Initialize tools with the Jira client
        logger.debug("Initializing tools...")
        initialize_tools(self.jira_client)
        self.tools = JIRA_TOOLS
        
        # Initialize custom LLM client
        logger.debug("Initializing custom LLM client...")
        self.llm_client = create_llm_client()
        
        # Create tool descriptions for prompts
        self.tool_descriptions = self._create_tool_descriptions()
        
        logger.info("JiraAgent initialized successfully with custom LLM")
    
    def _create_tool_descriptions(self) -> str:
        """Create a formatted description of available tools for prompts."""
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt that guides tool usage."""
        return f"""You are a Jira AI assistant that helps users manage and analyze Jira issues. 

Available Tools:
{self.tool_descriptions}

Instructions:
1. When a user asks about Jira issues, determine if you need to use tools to get information
2. If you need to use a tool, respond with: TOOL_CALL: tool_name(param1="value1", param2="value2")
3. If you can answer directly without tools, provide a helpful response
4. Always be helpful and provide detailed information when available

Examples:
- User: "Show me all To Do issues" → TOOL_CALL: get_issues_by_status(status="To Do")
- User: "Tell me about PROJ-123" → TOOL_CALL: get_issue_details(issue_key="PROJ-123")
- User: "Hello" → Direct response without tools

Be conversational and helpful while efficiently using tools when needed."""
    
    def _parse_tool_call(self, response: str) -> tuple[str, Dict[str, Any], bool]:
        """
        Parse tool call from LLM response.
        
        Returns:
            (tool_name, parameters, is_tool_call)
        """
        # Look for tool call pattern: TOOL_CALL: tool_name(param1="value1", param2="value2")
        tool_call_pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        match = re.search(tool_call_pattern, response)
        
        if not match:
            return "", {}, False
        
        tool_name = match.group(1)
        params_str = match.group(2)
        
        # Parse parameters
        parameters = {}
        if params_str.strip():
            # Simple parameter parsing (handles basic cases)
            param_pattern = r'(\w+)="([^"]*)"'
            for param_match in re.finditer(param_pattern, params_str):
                key = param_match.group(1)
                value = param_match.group(2)
                parameters[key] = value
        
        logger.debug(f"Parsed tool call: {tool_name} with parameters: {parameters}")
        return tool_name, parameters, True
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool with given parameters."""
        # Find the tool
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            logger.debug(f"Executing tool: {tool_name} with parameters: {parameters}")
            result = tool.invoke(parameters)
            logger.debug(f"Tool result: {str(result)[:200]}...")
            return str(result)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing tool {tool_name}: {str(e)}"
    
    def chat(self, user_input: str) -> str:
        """
        Process user input with custom LLM and tool orchestration.
        
        Args:
            user_input: User's message/question
            
        Returns:
            Agent's response string
        """
        logger.debug(f"Processing user input: {user_input[:100]}...")
        
        try:
            # Create messages for the LLM
            messages = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": user_input}
            ]
            
            # Get LLM response
            logger.debug("Calling custom LLM...")
            response = self.llm_client.chat_completion(messages)
            llm_response = self.llm_client.extract_content(response)
            
            logger.debug(f"LLM response: {llm_response}")
            
            # Check if LLM wants to use a tool
            tool_name, parameters, is_tool_call = self._parse_tool_call(llm_response)
            
            if is_tool_call:
                # Execute the tool
                tool_result = self._execute_tool(tool_name, parameters)
                
                # Get final response from LLM with tool result
                final_messages = [
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": llm_response},
                    {"role": "user", "content": f"Tool result from {tool_name}: {tool_result}\n\nPlease provide a helpful response based on this information."}
                ]
                
                final_response = self.llm_client.chat_completion(final_messages)
                final_content = self.llm_client.extract_content(final_response)
                
                logger.info("Tool-based response generated successfully")
                return final_content
            else:
                # Direct response without tools
                logger.info("Direct response generated successfully")
                return llm_response
            
        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def chat_with_history(self, user_input: str, chat_history: List[Dict[str, str]]) -> str:
        """
        Process user input with conversation history.
        
        Args:
            user_input: User's current message
            chat_history: Previous conversation history
            
        Returns:
            Agent's response string
        """
        logger.debug(f"Processing input with history: {len(chat_history)} previous messages")
        
        try:
            # Build messages with history
            messages = [{"role": "system", "content": self._create_system_prompt()}]
            
            # Add chat history (limit to last 10 exchanges to avoid token limits)
            recent_history = chat_history[-20:] if len(chat_history) > 20 else chat_history
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Get LLM response
            logger.debug("Calling custom LLM with history...")
            response = self.llm_client.chat_completion(messages)
            llm_response = self.llm_client.extract_content(response)
            
            # Check if LLM wants to use a tool
            tool_name, parameters, is_tool_call = self._parse_tool_call(llm_response)
            
            if is_tool_call:
                # Execute the tool
                tool_result = self._execute_tool(tool_name, parameters)
                
                # Get final response with tool result
                messages.append({"role": "assistant", "content": llm_response})
                messages.append({
                    "role": "user", 
                    "content": f"Tool result from {tool_name}: {tool_result}\n\nPlease provide a helpful response based on this information."
                })
                
                final_response = self.llm_client.chat_completion(messages)
                final_content = self.llm_client.extract_content(final_response)
                
                logger.info("Tool-based response with history generated successfully")
                return final_content
            else:
                logger.info("Direct response with history generated successfully")
                return llm_response
            
        except Exception as e:
            logger.error(f"Error in chat with history: {e}", exc_info=True)
            return f"I apologize, but I encountered an error: {str(e)}"
