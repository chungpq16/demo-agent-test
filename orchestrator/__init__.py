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
                "name": "get_jira_issues_advanced_filter",
                "description": "Get Jira issues with advanced filtering capabilities supporting multiple criteria, operators, and complex queries",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "array",
                            "description": "Array of filter objects to apply",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "field": {
                                        "type": "string",
                                        "description": "Field to filter by",
                                        "enum": ["status", "priority", "assignee", "reporter", "labels", "components", "summary", "description", "created", "updated", "issuetype", "fixVersion", "affectedVersion"]
                                    },
                                    "operator": {
                                        "type": "string",
                                        "description": "Operator to use for filtering",
                                        "enum": ["=", "!=", "IN", "NOT IN", "~", "!~", "IS EMPTY", "IS NOT EMPTY", ">", "<", ">=", "<="]
                                    },
                                    "values": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Values to filter by (array for IN/NOT IN operators, single value for others)"
                                    },
                                    "logic": {
                                        "type": "string",
                                        "description": "Logic operator to combine with next filter",
                                        "enum": ["AND", "OR"],
                                        "default": "AND"
                                    }
                                },
                                "required": ["field", "operator", "values"]
                            }
                        },
                        "text_search": {
                            "type": "string",
                            "description": "Text to search in summary and description fields"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Field to order results by",
                            "enum": ["created", "updated", "priority", "status", "assignee", "reporter", "key"],
                            "default": "created"
                        },
                        "order_direction": {
                            "type": "string",
                            "description": "Direction to order results",
                            "enum": ["ASC", "DESC"],
                            "default": "DESC"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return"
                        }
                    }
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
5. get_jira_issues_advanced_filter: Advanced filtering with multiple criteria, operators, and complex queries

**CRITICAL DECISION RULES:**

🗂️ **Use get_all_jira_issues when:**
- User wants ALL issues from the project without any filtering
- Examples: "Show me all jira issues", "Get all issues", "List all project issues"

📋 **Use get_jira_issues_by_status when:**
- User asks for issues by single status only (simple filter)
- Examples: "Show open issues", "Get completed tasks", "What's in progress?"

🔍 **Use search_jira_issues ONLY when:**
- User asks for simple text search within issue content
- Examples: "Find login problems", "Issues about authentication"

⚡ **Use get_jira_issues_advanced_filter for ALL COMPLEX queries:**
- Multiple criteria (priority AND status, labels AND assignee, etc.)
- Multiple values (multiple labels, assignees, components)
- Negation queries (NOT, doesn't have, exclude)
- Specific field filtering (priority, labels, components, assignee, etc.)

**Advanced Filter Examples:**

🏷️ **Labels:**
- "Get issues with label A, B, C" → filters: [{"field": "labels", "operator": "IN", "values": ["A", "B", "C"]}]
- "Issues that don't have labels A, B, C" → filters: [{"field": "labels", "operator": "NOT IN", "values": ["A", "B", "C"]}]

� **Assignees:**
- "Issues assigned to John, Jane, Bob" → filters: [{"field": "assignee", "operator": "IN", "values": ["John", "Jane", "Bob"]}]
- "Unassigned issues" → filters: [{"field": "assignee", "operator": "IS EMPTY", "values": []}]

⚡ **Priority:**
- "High or Critical priority issues" → filters: [{"field": "priority", "operator": "IN", "values": ["High", "Critical"]}]
- "Not low priority" → filters: [{"field": "priority", "operator": "!=", "values": ["Low"]}]

🎯 **Multiple Criteria:**
- "High priority open issues" → filters: [{"field": "priority", "operator": "=", "values": ["High"]}, {"field": "status", "operator": "=", "values": ["Open"]}]
- "Issues with label 'bug' assigned to John" → filters: [{"field": "labels", "operator": "IN", "values": ["bug"]}, {"field": "assignee", "operator": "=", "values": ["John"]}]

🔍 **Text + Filters:**
- "GenAI issues that are open" → filters: [{"field": "status", "operator": "=", "values": ["Open"]}], text_search: "GenAI"

**Operators Guide:**
- "=" : exact match
- "!=" : not equal
- "IN" : matches any of the values
- "NOT IN" : doesn't match any of the values  
- "~" : contains text
- "!~" : doesn't contain text
- "IS EMPTY" : field is empty/null
- "IS NOT EMPTY" : field has value

When users ask complex questions, analyze carefully and use get_jira_issues_advanced_filter with appropriate filters array.

Examples:
- "Show me all jira issues" → get_all_jira_issues
- "Get open issues" → get_jira_issues_by_status with status="Open"
- "Issues with labels A, B, C" → get_jira_issues_advanced_filter with filters=[{"field": "labels", "operator": "IN", "values": ["A", "B", "C"]}]
- "High priority issues assigned to John or Jane" → get_jira_issues_advanced_filter with filters=[{"field": "priority", "operator": "=", "values": ["High"]}, {"field": "assignee", "operator": "IN", "values": ["John", "Jane"]}]
- "Issues that don't have label 'old'" → get_jira_issues_advanced_filter with filters=[{"field": "labels", "operator": "NOT IN", "values": ["old"]}]

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
            
            elif function_name == "get_jira_issues_advanced_filter":
                return self._handle_advanced_filter(function_args)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
                
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Function arguments: {function_args}")
            
            # Log diagnostic information for Jira-related errors
            if function_name.startswith('get_jira') or function_name == 'search_jira_issues':
                try:
                    diagnostics = self.jira_client.diagnostic_check()
                    logger.error(f"Jira diagnostics: {diagnostics}")
                except Exception as diag_e:
                    logger.error(f"Failed to run diagnostics: {str(diag_e)}")
            
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "function": function_name
            }
    
    def _handle_advanced_filter(self, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle advanced filter requests with dynamic JQL generation.
        
        Args:
            function_args: Arguments from the LLM function call
            
        Returns:
            Function execution result
        """
        try:
            filters = function_args.get("filters", [])
            text_search = function_args.get("text_search")
            order_by = function_args.get("order_by", "created")
            order_direction = function_args.get("order_direction", "DESC")
            max_results = function_args.get("max_results", self._current_max_results)
            
            # Generate JQL query dynamically
            jql_query = self._generate_dynamic_jql(filters, text_search, order_by, order_direction)
            
            logger.debug(f"Generated dynamic JQL: {jql_query}")
            
            return {
                "success": True,
                "data": self.jira_client.search_issues(query=jql_query, max_results=max_results)
            }
            
        except Exception as e:
            logger.error(f"Error in advanced filter: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "function": "get_jira_issues_advanced_filter"
            }
    
    def _generate_dynamic_jql(self, filters: List[Dict], text_search: Optional[str], 
                             order_by: str, order_direction: str) -> str:
        """
        Generate JQL query dynamically based on filters.
        
        Args:
            filters: List of filter dictionaries
            text_search: Optional text search string
            order_by: Field to order by
            order_direction: Order direction (ASC/DESC)
            
        Returns:
            Generated JQL query string
        """
        project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
        jql_parts = [f"project = {project_key}"]
        
        # Process filters
        for i, filter_obj in enumerate(filters):
            field = filter_obj.get("field")
            operator = filter_obj.get("operator")
            values = filter_obj.get("values", [])
            logic = filter_obj.get("logic", "AND")
            
            # Generate filter condition
            condition = self._generate_filter_condition(field, operator, values)
            if condition:
                jql_parts.append(condition)
        
        # Add text search if provided
        if text_search:
            text_condition = f"(summary ~ '{text_search}' OR description ~ '{text_search}')"
            jql_parts.append(text_condition)
        
        # Combine all conditions with AND
        jql_query = " AND ".join(jql_parts)
        
        # Add ordering
        jql_query += f" ORDER BY {order_by} {order_direction}"
        
        return jql_query
    
    def _generate_filter_condition(self, field: str, operator: str, values: List[str]) -> str:
        """
        Generate a single filter condition for JQL.
        
        Args:
            field: Field name
            operator: Operator type
            values: Values to filter by
            
        Returns:
            JQL condition string
        """
        if not field or not operator:
            return ""
        
        # Handle field name mappings
        field_mappings = {
            "severity": "priority",
            "assignee": "assignee",
            "reporter": "reporter",
            "labels": "labels",
            "components": "component",
            "summary": "summary",
            "description": "description",
            "status": "status",
            "priority": "priority",
            "created": "created",
            "updated": "updated",
            "issuetype": "issuetype",
            "fixVersion": "fixVersion",
            "affectedVersion": "affectedVersion"
        }
        
        jql_field = field_mappings.get(field, field)
        
        # Handle different operators
        if operator == "=":
            if len(values) == 1:
                return f"{jql_field} = '{values[0]}'"
            else:
                # Multiple values with = should use IN
                values_str = ", ".join([f"'{v}'" for v in values])
                return f"{jql_field} IN ({values_str})"
                
        elif operator == "!=":
            if len(values) == 1:
                return f"{jql_field} != '{values[0]}'"
            else:
                # Multiple values with != should use NOT IN
                values_str = ", ".join([f"'{v}'" for v in values])
                return f"{jql_field} NOT IN ({values_str})"
                
        elif operator == "IN":
            if values:
                values_str = ", ".join([f"'{v}'" for v in values])
                return f"{jql_field} IN ({values_str})"
            return ""
            
        elif operator == "NOT IN":
            if values:
                values_str = ", ".join([f"'{v}'" for v in values])
                return f"{jql_field} NOT IN ({values_str})"
            return ""
            
        elif operator == "~":
            if values:
                return f"{jql_field} ~ '{values[0]}'"
            return ""
            
        elif operator == "!~":
            if values:
                return f"{jql_field} !~ '{values[0]}'"
            return ""
            
        elif operator == "IS EMPTY":
            return f"{jql_field} IS EMPTY"
            
        elif operator == "IS NOT EMPTY":
            return f"{jql_field} IS NOT EMPTY"
            
        elif operator in [">", "<", ">=", "<="]:
            if values:
                return f"{jql_field} {operator} '{values[0]}'"
            return ""
        
        return ""
    
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
