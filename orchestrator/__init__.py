"""
Orchestrator Module
Implements prompt-based orchestration logic for Jira operations via LLM Farm.
"""
import json
import re
from typing import Dict, List, Any, Optional
from llm_farm_client import LLMFarmClient
from jira_client import JiraClient
from logger import get_logger

logger = get_logger()


class JiraOrchestrator:
    """Orchestrates Jira operations through natural language prompts."""
    
    def __init__(self):
        """Initialize orchestrator with LLM Farm and Jira clients."""
        self.llm_client = LLMFarmClient()
        self.jira_client = JiraClient()
        
        # Define available Jira functions for LLM
        self.jira_functions = self._define_jira_functions()
        
        logger.info("Jira Orchestrator initialized successfully")
    
    def _define_jira_functions(self) -> List[Dict]:
        """
        Define available Jira functions for function calling.
        
        Returns:
            List of function definitions
        """
        return [
            {
                "name": "get_all_jira_issues",
                "description": "Get all Jira issues from the project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 50
                        }
                    }
                }
            },
            {
                "name": "get_jira_issues_by_status",
                "description": "Get Jira issues filtered by status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Status to filter by (e.g., 'Open', 'In Progress', 'Done')",
                            "enum": ["Open", "In Progress", "Done", "Closed", "Resolved"]
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 50
                        }
                    },
                    "required": ["status"]
                }
            },
            {
                "name": "get_jira_issue_details",
                "description": "Get detailed information for a specific Jira issue",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "Jira issue key (e.g., 'PROJ-123')"
                        }
                    },
                    "required": ["issue_key"]
                }
            },
            {
                "name": "search_jira_issues",
                "description": "Search Jira issues using text query or JQL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query text or JQL"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 50
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_jira_issues_by_label",
                "description": "Get Jira issues filtered by label",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Label to filter by (e.g., 'frontend', 'backend', 'bug', 'feature')"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 50
                        }
                    },
                    "required": ["label"]
                }
            },
            {
                "name": "get_jira_issues_by_severity",
                "description": "Get Jira issues filtered by severity/priority",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "description": "Severity/priority to filter by",
                            "enum": ["Critical", "High", "Medium", "Low", "Blocker", "Major", "Minor", "Trivial"]
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return", 
                            "default": 50
                        }
                    },
                    "required": ["severity"]
                }
            }
        ]
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for Jira operations.
        
        Returns:
            System prompt string
        """
        return """You are a Jira assistant that helps users interact with their Jira project through natural language.

You have access to the following Jira operations:
1. get_all_jira_issues: Get all issues from the project
2. get_jira_issues_by_status: Get issues filtered by status (Open, In Progress, Done, Closed, Resolved)
3. get_jira_issue_details: Get detailed information for a specific issue by key
4. search_jira_issues: Search issues using text or JQL queries
5. get_jira_issues_by_label: Get issues filtered by label (e.g., frontend, backend, bug, feature)
6. get_jira_issues_by_severity: Get issues filtered by severity/priority (Critical, High, Medium, Low, etc.)

When a user asks about Jira issues, analyze their request and call the appropriate function.
After getting the results, provide a clear, human-readable summary of the information.

Examples:
- "Show me all open issues" → use get_jira_issues_by_status with status="Open"
- "Get details for PROJ-123" → use get_jira_issue_details with issue_key="PROJ-123"
- "Find issues related to login" → use search_jira_issues with query="login"
- "What issues are in progress?" → use get_jira_issues_by_status with status="In Progress"
- "Show me all frontend issues" → use get_jira_issues_by_label with label="frontend"
- "Find high priority issues" → use get_jira_issues_by_severity with severity="High"

Always provide helpful, clear responses based on the Jira data returned."""
    
    def process_request(self, user_input: str) -> str:
        """
        Process user request and orchestrate appropriate Jira operations.
        
        Args:
            user_input: User's natural language request
            
        Returns:
            Response string with results
        """
        try:
            logger.debug(f"Processing user request: {user_input}")
            
            # Get completion with function calling
            system_prompt = self._get_system_prompt()
            
            response = self.llm_client.completion_with_functions(
                user_text=user_input,
                system_prompt=system_prompt,
                functions=self.jira_functions,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            # Check if LLM wants to call a function
            if hasattr(message, 'function_call') and message.function_call:
                function_result = self._execute_function_call(message.function_call)
                
                # Get final response from LLM with function results
                follow_up_prompt = f"The function returned: {json.dumps(function_result, indent=2)}\n\nPlease provide a clear, human-readable summary of this information for the user."
                
                final_response = self.llm_client.completion(
                    user_text=follow_up_prompt,
                    system_prompt="You are a helpful assistant that summarizes Jira data in a clear, readable format."
                )
                
                logger.info("Request processed successfully with function call")
                return final_response
            else:
                # No function call needed, return direct response
                logger.info("Request processed successfully without function call")
                return message.content
                
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(error_msg)
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def _execute_function_call(self, function_call) -> Dict[str, Any]:
        """
        Execute the function call requested by LLM.
        
        Args:
            function_call: Function call object from LLM response
            
        Returns:
            Function execution result
        """
        function_name = function_call.name
        function_args = json.loads(function_call.arguments)
        
        logger.debug(f"Executing function: {function_name} with args: {function_args}")
        
        try:
            if function_name == "get_all_jira_issues":
                max_results = function_args.get("max_results", 50)
                return {
                    "success": True,
                    "data": self.jira_client.get_all_issues(max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_status":
                status = function_args["status"]
                max_results = function_args.get("max_results", 50)
                return {
                    "success": True,
                    "data": self.jira_client.get_issues_by_status(status=status, max_results=max_results)
                }
            
            elif function_name == "get_jira_issue_details":
                issue_key = function_args["issue_key"]
                return {
                    "success": True,
                    "data": self.jira_client.get_issue_details(issue_key=issue_key)
                }
            
            elif function_name == "search_jira_issues":
                query = function_args["query"]
                max_results = function_args.get("max_results", 50)
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=query, max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_label":
                label = function_args["label"]
                max_results = function_args.get("max_results", 50)
                # Create JQL query to search by label
                jql_query = f"labels = {label}"
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=jql_query, max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_severity":
                severity = function_args["severity"]
                max_results = function_args.get("max_results", 50)
                # Create JQL query to search by priority (severity)
                jql_query = f"priority = {severity}"
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=jql_query, max_results=max_results)
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
                
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, bool]:
        """
        Check health of all components.
        
        Returns:
            Health status of LLM Farm and Jira clients
        """
        logger.info("Performing health check")
        
        llm_healthy = self.llm_client.health_check()
        jira_healthy = self.jira_client.health_check()
        
        return {
            "llm_farm": llm_healthy,
            "jira": jira_healthy,
            "overall": llm_healthy and jira_healthy
        }
    
    def get_help(self) -> str:
        """
        Get help information about available operations.
        
        Returns:
            Help text
        """
        help_text = """
🤖 Jira GenAI Assistant Help

I can help you with the following Jira operations:

📋 **Get Issues:**
- "Show me all issues"
- "Get all open issues"
- "What issues are in progress?"
- "Show me completed issues"

🔍 **Search Issues:**
- "Find issues about login"
- "Search for bug reports"
- "Issues related to authentication"

📊 **Issue Details:**
- "Get details for PROJ-123"
- "Tell me about issue PROJ-456"

💡 **Tips:**
- You can ask in natural language
- I understand various status names (Open, In Progress, Done, etc.)
- I can search in both titles and descriptions
- Use specific issue keys (like PROJ-123) for detailed information

Just ask me anything about your Jira issues! 🚀
        """
        
        return help_text.strip()
