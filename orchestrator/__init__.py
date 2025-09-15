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
        
        # Initialize current max results with environment default
        self._current_max_results = int(os.getenv('JIRA_MAX_RESULTS', '50'))
        
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
                            "description": "Maximum number of results to return (will use configured limit if not specified)"
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
                            "description": "Maximum number of results to return (will use configured limit if not specified)"
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
                            "description": "Maximum number of results to return (will use configured limit if not specified)"
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
                            "description": "Maximum number of results to return (will use configured limit if not specified)"
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
                            "description": "Maximum number of results to return (will use configured limit if not specified)"
                        }
                    },
                    "required": ["severity"]
                }
            },
            {
                "name": "get_jira_issues_by_text_and_status",
                "description": "Get Jira issues that contain specific text/keywords in title or description AND have a specific status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text_query": {
                            "type": "string",
                            "description": "Text to search for in issue title or description (e.g., 'GenAI', 'authentication', 'login')"
                        },
                        "status": {
                            "type": "string",
                            "description": "Status to filter by",
                            "enum": ["Open", "In Progress", "Done", "Closed", "Resolved", "TO-DO", "To Do"]
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (will use configured limit if not specified)"
                        }
                    },
                    "required": ["text_query", "status"]
                }
            },
            {
                "name": "get_jira_issues_by_priority_and_status",
                "description": "Get Jira issues filtered by both priority/severity AND status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "priority": {
                            "type": "string",
                            "description": "Priority/severity to filter by",
                            "enum": ["Critical", "High", "Medium", "Low", "Blocker", "Major", "Minor", "Trivial"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Status to filter by",
                            "enum": ["Open", "In Progress", "Done", "Closed", "Resolved", "TO-DO", "To Do"]
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (will use configured limit if not specified)"
                        }
                    },
                    "required": ["priority", "status"]
                }
            },
            {
                "name": "get_jira_issues_by_label_and_status",
                "description": "Get Jira issues filtered by both label AND status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Label to filter by (e.g., 'Exam', 'frontend', 'backend', 'bug')"
                        },
                        "status": {
                            "type": "string",
                            "description": "Status to filter by",
                            "enum": ["Open", "In Progress", "Done", "Closed", "Resolved", "TO-DO", "To Do"]
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (will use configured limit if not specified)"
                        }
                    },
                    "required": ["label", "status"]
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
7. get_jira_issues_by_text_and_status: Get issues containing specific text AND having specific status
8. get_jira_issues_by_priority_and_status: Get issues with specific priority AND status
9. get_jira_issues_by_label_and_status: Get issues with specific label AND status

**CRITICAL DECISION RULES:**

🗂️ **Use get_all_jira_issues when:**
- User wants ALL issues from the project without any filtering
- Examples: "Show me all jira issues", "Get all issues", "List all project issues", "What issues do we have?"

🏷️ **Use get_jira_issues_by_label when:**
- User asks for issues with a SPECIFIC label name or mentions "labeled" "label" (single filter only)
- Examples: "Find issues labeled '2025'", "Show issues with label 'bug'", "Get all '2024' labeled issues"

⚡ **Use get_jira_issues_by_severity when:**
- User asks for issues with specific priority/severity levels (single filter only)
- Examples: "Show high priority issues", "Find critical bugs", "Get low severity issues"

📋 **Use get_jira_issues_by_status when:**
- User asks for issues by workflow status (single filter only)
- Examples: "Show open issues", "Get completed tasks", "What's in progress?"

🔍 **Use search_jira_issues ONLY when:**
- User asks for general content search or mentions topics/keywords (NOT labels or severity)
- User wants to search within issue content (summary/description) with simple text
- Examples: "Find login problems", "Issues about authentication", "Search for database errors"

🎯 **Use COMBINATION functions for multi-criteria queries:**

📝 **Use get_jira_issues_by_text_and_status when:**
- User wants issues containing specific text/keywords AND having specific status
- Examples: "List all jira issues relate to GenAI and in Open Status", "Find authentication issues that are open"

⚡📋 **Use get_jira_issues_by_priority_and_status when:**
- User wants issues with specific priority AND status
- Examples: "List all jira issues in critical priority and in TO-DO Status", "Show high priority open issues"

🏷️📋 **Use get_jira_issues_by_label_and_status when:**
- User wants issues with specific label AND status  
- Examples: "List all jira issues with label 'Exam' and in Open Status", "Show bug labeled issues that are closed"

💬 **For general questions, provide direct helpful responses without function calls:**
- Questions about Jira concepts, workflow advice, best practices
- "How do I create an issue?", "What's the difference between bug and story?"

**IMPORTANT: Choose the RIGHT function based on the query complexity:**
- Single filter → Use specific single-filter function
- Multiple filters → Use appropriate combination function
- General text search → Use search_jira_issues (NOT for labels or priority)

When a user asks about Jira issues, analyze their request carefully and call the appropriate function.
After getting the results, provide a clear, human-readable summary of the information.

Examples:
- "Show me all jira issues" → get_all_jira_issues
- "List all jira issues relate to GenAI and in Open Status" → get_jira_issues_by_text_and_status with text_query="GenAI" and status="Open"
- "List all jira issues in critical priority and in TO-DO Status" → get_jira_issues_by_priority_and_status with priority="Critical" and status="TO-DO"
- "List all jira issues with label 'Exam' and in Open Status" → get_jira_issues_by_label_and_status with label="Exam" and status="Open"
- "Show me all open issues" → get_jira_issues_by_status with status="Open"
- "Get details for PROJ-123" → get_jira_issue_details with issue_key="PROJ-123"
- "Find issues labeled '2025'" → get_jira_issues_by_label with label="2025"
- "Find high priority issues" → get_jira_issues_by_severity with severity="High"

Always provide helpful, clear responses based on the Jira data returned."""
    
    def process_request(self, user_input: str, max_results: int = None) -> str:
        """
        Process user request and orchestrate appropriate Jira operations.
        
        Args:
            user_input: User's natural language request
            max_results: Maximum number of results to return (from UI config)
            
        Returns:
            Response string with results or structured data
        """
        try:
            logger.debug(f"Processing user request: {user_input}")
            
            # Use provided max_results or fall back to environment default
            if max_results is None:
                max_results = int(os.getenv('JIRA_MAX_RESULTS', '50'))
            
            # Store max_results for use in function calls
            self._current_max_results = max_results
            
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
                    
                    # Generate summary based on ALL issues, not just first 3
                    issues_data = function_result['data']
                    
                    # Create comprehensive summary data for all issues
                    total_count = len(issues_data)
                    status_counts = {}
                    priority_counts = {}
                    assignee_counts = {}
                    
                    for issue in issues_data:
                        # Count by status
                        status = issue.get('status', 'Unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                        
                        # Count by priority
                        priority = issue.get('priority', 'Unknown')
                        priority_counts[priority] = priority_counts.get(priority, 0) + 1
                        
                        # Count by assignee
                        assignee = issue.get('assignee', 'Unassigned')
                        assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
                    
                    # Create summary with complete statistics
                    summary_data = {
                        'total_issues': total_count,
                        'status_breakdown': status_counts,
                        'priority_breakdown': priority_counts,
                        'assignee_breakdown': assignee_counts,
                        'recent_issues': issues_data[:5]  # Show first 5 as examples
                    }
                    
                    summary_prompt = f"Based on the following complete Jira issues statistics, provide a comprehensive 2-3 sentence summary: {json.dumps(summary_data, indent=2)}"
                    
                    summary_response = self.llm_client.completion(
                        user_text=summary_prompt,
                        system_prompt="You are a helpful assistant. Provide a comprehensive summary of ALL the Jira issues found, including total count, status distribution, priority levels, and key insights. Be thorough and professional."
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
                max_results = function_args.get("max_results", self._current_max_results)
                return {
                    "success": True,
                    "data": self.jira_client.get_all_issues(max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_status":
                status = function_args["status"]
                max_results = function_args.get("max_results", self._current_max_results)
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
                max_results = function_args.get("max_results", self._current_max_results)
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=query, max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_label":
                label = function_args["label"]
                max_results = function_args.get("max_results", self._current_max_results)
                # Create JQL query to search by label
                project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
                jql_query = f"project = {project_key} AND labels = {label} ORDER BY created DESC"
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=jql_query, max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_severity":
                severity = function_args["severity"]
                max_results = function_args.get("max_results", self._current_max_results)
                # Create JQL query to search by priority (severity)
                project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
                jql_query = f"project = {project_key} AND priority = {severity} ORDER BY created DESC"
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=jql_query, max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_text_and_status":
                text_query = function_args["text_query"]
                status = function_args["status"]
                max_results = function_args.get("max_results", self._current_max_results)
                
                # Normalize status name
                status_mapping = {
                    'to-do': 'TO-DO',
                    'todo': 'TO-DO', 
                    'to do': 'To Do'
                }
                normalized_status = status_mapping.get(status.lower(), status)
                
                # Create JQL query to search by text content AND status
                project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
                jql_query = f"project = {project_key} AND (summary ~ '{text_query}' OR description ~ '{text_query}') AND status = '{normalized_status}' ORDER BY created DESC"
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=jql_query, max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_priority_and_status":
                priority = function_args["priority"]
                status = function_args["status"]
                max_results = function_args.get("max_results", self._current_max_results)
                
                # Normalize status name
                status_mapping = {
                    'to-do': 'TO-DO',
                    'todo': 'TO-DO',
                    'to do': 'To Do'
                }
                normalized_status = status_mapping.get(status.lower(), status)
                
                # Create JQL query to search by priority AND status
                project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
                jql_query = f"project = {project_key} AND priority = {priority} AND status = '{normalized_status}' ORDER BY created DESC"
                return {
                    "success": True,
                    "data": self.jira_client.search_issues(query=jql_query, max_results=max_results)
                }
            
            elif function_name == "get_jira_issues_by_label_and_status":
                label = function_args["label"]
                status = function_args["status"]
                max_results = function_args.get("max_results", self._current_max_results)
                
                # Normalize status name
                status_mapping = {
                    'to-do': 'TO-DO',
                    'todo': 'TO-DO',
                    'to do': 'To Do'
                }
                normalized_status = status_mapping.get(status.lower(), status)
                
                # Create JQL query to search by label AND status
                project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
                jql_query = f"project = {project_key} AND labels = {label} AND status = '{normalized_status}' ORDER BY created DESC"
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
