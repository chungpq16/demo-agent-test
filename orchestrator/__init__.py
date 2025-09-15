"""
Orchestrator Module
Implements prompt-based orchestration logic for Jira operations via LLM Farm.
"""
import json
import os
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
4. search_jira_issues: Search issues using text or JQL queries (for general content search)
5. get_jira_issues_by_label: Get issues filtered by SPECIFIC label names (when user mentions exact label)
6. get_jira_issues_by_severity: Get issues filtered by severity/priority (Critical, High, Medium, Low, etc.)

**CRITICAL DECISION RULES:**

🗂️ **Use get_all_jira_issues when:**
- User wants ALL issues from the project without any filtering
- Examples: "Show me all jira issues", "Get all issues", "List all project issues", "What issues do we have?"

🏷️ **Use get_jira_issues_by_label when:**
- User asks for issues with a SPECIFIC label name or mentions "labeled" "label"
- Examples: "Find issues labeled '2025'", "Show issues with label 'bug'", "Get all '2024' labeled issues"

⚡ **Use get_jira_issues_by_severity when:**
- User asks for issues with specific priority/severity levels
- Examples: "Show high priority issues", "Find critical bugs", "Get low severity issues"

📋 **Use get_jira_issues_by_status when:**
- User asks for issues by workflow status
- Examples: "Show open issues", "Get completed tasks", "What's in progress?"

🔍 **Use search_jira_issues ONLY when:**
- User asks for general content search or mentions topics/keywords (NOT labels or severity)
- User wants to search within issue content (summary/description)
- Examples: "Find login problems", "Issues about authentication", "Search for database errors"

💬 **For general questions, provide direct helpful responses without function calls:**
- Questions about Jira concepts, workflow advice, best practices
- "How do I create an issue?", "What's the difference between bug and story?"

**IMPORTANT: DO NOT use search_jira_issues for:**
- Getting all issues (use get_all_jira_issues)
- Label searches (use get_jira_issues_by_label)
- Severity searches (use get_jira_issues_by_severity)

When a user asks about Jira issues, analyze their request carefully and call the appropriate function.
After getting the results, provide a clear, human-readable summary of the information.

Examples:
- "Show me all jira issues" → get_all_jira_issues
- "Get all issues" → get_all_jira_issues
- "List all project issues" → get_all_jira_issues
- "Show me all open issues" → get_jira_issues_by_status with status="Open"
- "Get details for PROJ-123" → get_jira_issue_details with issue_key="PROJ-123"
- "Find issues labeled '2025'" → get_jira_issues_by_label with label="2025"
- "Find login problems" → search_jira_issues with query="login"
- "Issues about authentication" → search_jira_issues with query="authentication"
- "Find high priority issues" → get_jira_issues_by_severity with severity="High"
- "Issues with label 'urgent'" → get_jira_issues_by_label with label="urgent"

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
                
                # Check if the result contains Jira issues data
                if (function_result.get('success') and 
                    'data' in function_result and 
                    isinstance(function_result['data'], list) and 
                    len(function_result['data']) > 0 and 
                    isinstance(function_result['data'][0], dict) and
                    'key' in function_result['data'][0]):  # This indicates Jira issues
                    
                    # Generate summary and return structured data
                    summary_prompt = f"Based on the following Jira issues data, provide a brief 2-3 sentence summary of what was found: {json.dumps(function_result['data'][:3], indent=2)}"
                    
                    summary_response = self.llm_client.completion(
                        user_text=summary_prompt,
                        system_prompt="You are a helpful assistant. Provide only a brief summary of the Jira issues found, focusing on count, types, and key insights. Keep it concise and professional."
                    )
                    
                    # Return structured response for chat interface
                    logger.info("Request processed successfully with structured Jira issues response")
                    return {
                        'type': 'jira_issues',
                        'summary': summary_response.strip(),
                        'issues': function_result['data']
                    }
                
                # Standard function result handling for non-issues responses
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
                project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
                jql_query = f"project = {project_key} AND labels = {label} ORDER BY created DESC"
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=jql_query, max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_severity":
                severity = function_args["severity"]
                max_results = function_args.get("max_results", 50)
                # Create JQL query to search by priority (severity)
                project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
                jql_query = f"project = {project_key} AND priority = {severity} ORDER BY created DESC"
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=jql_query, max_results=max_results)
                }
            
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
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
