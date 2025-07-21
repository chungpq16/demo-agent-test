"""
Jira Agent that directly handles tool calls without LangGraph complexity.
"""

from typing import List, Dict, Any
# OpenAI support (commented for future use)
# from langchain_openai import ChatOpenAI

# Ollama support
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from jira_tools import JIRA_TOOLS, initialize_tools
from jira_client import JiraClient
import logging
import os
import json

logger = logging.getLogger(__name__)

class JiraAgent:
    """
    Jira agent that handles tool calls directly.
    """
    
    def __init__(self, jira_client: JiraClient = None):
        """Initialize the simple Jira agent."""
        logger.debug("Initializing JiraAgent...")
        
        # Initialize Jira client if not provided
        if jira_client is None:
            logger.debug("Creating new Jira client...")
            jira_client = JiraClient()
        
        # Initialize tools with the Jira client
        logger.debug("Initializing tools with Jira client...")
        initialize_tools(jira_client)
        
        # OpenAI Configuration (commented for future use)
        # openai_key = os.getenv("OPENAI_API_KEY")
        # if not openai_key:
        #     logger.error("OPENAI_API_KEY not found in environment variables")
        #     raise ValueError("OPENAI_API_KEY is required")
        # 
        # logger.debug(f"OpenAI API key found: {openai_key[:10]}...")
        # 
        # self.llm = ChatOpenAI(
        #     model="gpt-4o-mini",
        #     api_key=openai_key,
        #     temperature=0.1
        # )
        
        # Ollama Configuration
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        logger.debug(f"Using Ollama model: {ollama_model}")
        logger.debug(f"Ollama base URL: {ollama_base_url}")
        
        self.llm = ChatOllama(
            model=ollama_model,
            base_url=ollama_base_url,
            temperature=0.1
        )
        
        # Bind tools to the LLM
        logger.debug(f"Binding {len(JIRA_TOOLS)} tools to LLM")
        self.llm_with_tools = self.llm.bind_tools(JIRA_TOOLS)
        
        # Create tool map for easy access
        self.tools = {tool.name: tool for tool in JIRA_TOOLS}
        logger.debug(f"Available tools: {list(self.tools.keys())}")
        
        # Get project scope information for the system prompt
        project_scope = jira_client.get_current_project_scope()
        project_scope_info = f"\n\nIMPORTANT: All searches are automatically scoped to project '{project_scope}'. You don't need to add project filters to JQL queries as this is handled automatically." if project_scope else "\n\nNote: Searches span all accessible projects unless explicitly filtered."
        
        self.system_prompt = f"""You are a helpful AI assistant specialized in Jira issue management. You have access to tools that can:

1. Retrieve issues by status (get_issues_by_status)
2. Get all issues (get_all_issues)
3. Get detailed information about specific issues (get_issue_details)
4. Analyze all tickets for insights (get_all_issues_for_analysis)
5. Search issues using JQL queries (search_issues_by_jql)
6. Get project information (get_project_summary)

When users ask about Jira issues, use the appropriate tools to gather information and provide helpful, detailed responses.

Guidelines:
- For status queries like "show me to-do issues", use get_issues_by_status
- For general requests like "show me all issues", use get_all_issues
- For specific issue details like "tell me about PROJ-123", use get_issue_details
- For analysis requests like "analyze all tickets" or "give me insights", use get_all_issues_for_analysis
- For complex searches, use search_issues_by_jql with appropriate JQL queries
- Always provide context and explanations with your responses
- Format responses in a user-friendly way{project_scope_info}

If you need to search for issues but don't have a specific JQL query, you can use common patterns like:
- "assignee = 'username'" for user-specific issues
- "status in ('To Do', 'In Progress')" for multiple statuses
- "priority = 'High'" for priority-based searches
"""
        
        logger.info("Jira agent initialized successfully")
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and return agent response.
        
        Args:
            user_input: User's message/question
            
        Returns:
            Agent's response string
        """
        logger.debug(f"Processing user input: {user_input}")
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_input)
            ]
            
            logger.debug("Sending request to OpenAI...")
            # Get initial response from LLM
            response = self.llm_with_tools.invoke(messages)
            logger.debug(f"OpenAI response received: {type(response)}")
            
            # Check if there are tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"Tool calls requested: {len(response.tool_calls)} calls")
                
                # Execute tool calls
                tool_results = []
                for i, tool_call in enumerate(response.tool_calls):
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    logger.debug(f"Executing tool {i+1}/{len(response.tool_calls)}: {tool_name} with args: {tool_args}")
                    
                    if tool_name in self.tools:
                        try:
                            logger.debug(f"Invoking tool: {tool_name}")
                            tool_result = self.tools[tool_name].invoke(tool_args)
                            logger.debug(f"Tool {tool_name} result length: {len(str(tool_result))}")
                            tool_results.append(f"Tool {tool_name} result: {tool_result}")
                        except Exception as e:
                            logger.error(f"Error executing tool {tool_name}: {e}")
                            tool_results.append(f"Tool {tool_name} error: {str(e)}")
                    else:
                        logger.error(f"Unknown tool requested: {tool_name}")
                        tool_results.append(f"Tool {tool_name} error: Tool not found")
                
                logger.debug(f"All tools executed. Results count: {len(tool_results)}")
                
                # Create a follow-up prompt with tool results
                tool_results_text = "\n\n".join(tool_results)
                follow_up_prompt = f"""Based on the tool results below, please provide a comprehensive and user-friendly response to the user's question: "{user_input}"

Tool Results:
{tool_results_text}

Please format your response in a clear, helpful manner and provide insights or summaries as appropriate."""
                
                logger.debug("Sending follow-up request to OpenAI with tool results...")
                
                # Get final response
                final_messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=follow_up_prompt)
                ]
                
                final_response = self.llm.invoke(final_messages)
                logger.info(f"Final response generated successfully")
                return final_response.content
            
            else:
                # No tool calls needed, return direct response
                logger.info("No tool calls needed, returning direct response")
                return response.content
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}", exc_info=True)
            return f"Sorry, I encountered an error: {str(e)}"
    
    def chat_with_history(self, user_input: str, chat_history: List[Dict[str, str]]) -> str:
        """
        Process user input with conversation history.
        
        Args:
            user_input: User's current message
            chat_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}]
            
        Returns:
            Agent's response string
        """
        try:
            # Build message history
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add chat history
            for msg in chat_history[-10:]:  # Limit to last 10 messages
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add current user message
            messages.append(HumanMessage(content=user_input))
            
            # Get response from LLM
            response = self.llm_with_tools.invoke(messages)
            
            # Check if there are tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Execute tool calls
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    if tool_name in self.tools:
                        try:
                            tool_result = self.tools[tool_name].invoke(tool_args)
                            tool_results.append(f"Tool {tool_name} result: {tool_result}")
                        except Exception as e:
                            tool_results.append(f"Tool {tool_name} error: {str(e)}")
                
                # Create a follow-up prompt with tool results and context
                tool_results_text = "\n\n".join(tool_results)
                follow_up_prompt = f"""Based on our conversation and the tool results below, please provide a comprehensive and user-friendly response to the user's question: "{user_input}"

Tool Results:
{tool_results_text}

Please format your response in a clear, helpful manner and provide insights or summaries as appropriate."""
                
                # Get final response with full context
                final_messages = messages[:-1] + [HumanMessage(content=follow_up_prompt)]
                final_response = self.llm.invoke(final_messages)
                return final_response.content
            
            else:
                # No tool calls needed, return direct response
                return response.content
            
        except Exception as e:
            logger.error(f"Error processing user input with history: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
