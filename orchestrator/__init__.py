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
        
        # Cache for storing retrieved issues to avoid repeated API calls
        self.cached_issues = None
        self.cached_issues_type = None  # Track what type of issues are cached
        
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
                "name": "show_more_issues",
                "description": "Show more issues from the previously retrieved data without calling Jira API again",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_index": {
                            "type": "integer",
                            "description": "Starting index for the next batch of issues",
                            "default": 5
                        },
                        "batch_size": {
                            "type": "integer", 
                            "description": "Number of issues to show in this batch",
                            "default": 5
                        }
                    }
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
7. show_more_issues: Show more issues from previously retrieved data (when user asks for "show more", "next", "more issues")

**CRITICAL DECISION RULES:**

🗂️ **Use get_all_jira_issues when:**
- User wants ALL issues from the project without any filtering
- Examples: "Show me all jira issues", "Get all issues", "List all project issues", "What issues do we have?"

🔄 **Use show_more_issues when:**
- User asks to see more issues after initial results were shown
- Examples: "show more", "show more issues", "next", "more", "show remaining issues"

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
- "Show more" or "more issues" → show_more_issues
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
                
                # Special handling for get_all_jira_issues with categorized summary
                if (hasattr(message.function_call, 'name') and 
                    message.function_call.name == 'get_all_jira_issues' and 
                    function_result.get('success') and 
                    'summary' in function_result):
                    
                    summary = function_result['summary']
                    follow_up_prompt = f"""Based on the following Jira issues analysis, provide a clear, simple summary:

ANALYSIS DATA:
- Total Issues: {summary['total_issues']}
- Status Breakdown: {summary['status_breakdown']}
- Displayed Issues: {summary['displayed_issues']}
- Has More: {summary['has_more']}
- Remaining Count: {summary.get('remaining_count', 0)}

Please format this as:
1. 📊 Total count: "Found X issues total"
2. 📋 Status breakdown with emojis (✅ Done, � In Progress, 🆕 Open, etc.)
3. Show the displayed issues (title, key, status, assignee)
4. If has_more is True, mention "Say 'show more' to see the remaining X issues"

Keep it clean and simple - just overview + status + first batch + show more option."""
                
                # Special handling for show_more_issues
                elif (hasattr(message.function_call, 'name') and 
                      message.function_call.name == 'show_more_issues' and 
                      function_result.get('success')):
                    
                    batch_info = function_result.get('batch_info', {})
                    follow_up_prompt = f"""Show the next batch of issues:

BATCH DATA:
- Issues: {function_result['data']}
- Showing: {batch_info.get('start_index', 0) + 1} to {batch_info.get('end_index', 0)}
- Total Available: {batch_info.get('total_cached', 0)}
- Has More: {batch_info.get('has_more', False)}
- Source: {batch_info.get('cached_type', 'unknown')}

Format as:
📋 Showing issues X-Y of Z:
[List the issues with key, title, status, assignee]

If has more: "Say 'show more' to see additional issues"
If no more: "That's all the issues from this query"
"""
                
                else:
                    # Standard function result handling
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
                issues_data = self.jira_client.get_all_issues(max_results=max_results)
                
                # Cache the data for "show more" functionality
                self.cached_issues = issues_data
                self.cached_issues_type = "all_issues"
                
                # Generate simplified summary
                categorized_summary = self._generate_categorized_summary(issues_data)
                
                return {
                    "success": True,
                    "data": issues_data,
                    "summary": categorized_summary
                }
            
            elif function_name == "get_jira_issues_by_status":
                status = function_args["status"]
                max_results = function_args.get("max_results", 50)
                issues_data = self.jira_client.get_issues_by_status(status=status, max_results=max_results)
                
                # Cache the data for "show more" functionality
                self.cached_issues = issues_data
                self.cached_issues_type = f"status_{status}"
                
                return {
                    "success": True,
                    "data": issues_data
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
                issues_data = self.jira_client.search_issues(query=query, max_results=max_results)
                
                # Cache the data for "show more" functionality
                self.cached_issues = issues_data
                self.cached_issues_type = f"search_{query[:20]}"
                
                return {
                    "success": True,
                    "data": issues_data
                }
            
            elif function_name == "get_jira_issues_by_label":
                label = function_args["label"]
                max_results = function_args.get("max_results", 50)
                # Create JQL query to search by label
                project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
                jql_query = f"project = {project_key} AND labels = {label} ORDER BY created DESC"
                issues_data = self.jira_client.search_issues(query=jql_query, max_results=max_results)
                
                # Cache the data for "show more" functionality
                self.cached_issues = issues_data
                self.cached_issues_type = f"label_{label}"
                
                return {
                    "success": True,
                    "data": issues_data
                }
            
            elif function_name == "get_jira_issues_by_severity":
                severity = function_args["severity"]
                max_results = function_args.get("max_results", 50)
                # Create JQL query to search by priority (severity)
                project_key = os.getenv('JIRA_PROJECT', 'PROJECT')
                jql_query = f"project = {project_key} AND priority = {severity} ORDER BY created DESC"
                issues_data = self.jira_client.search_issues(query=jql_query, max_results=max_results)
                
                # Cache the data for "show more" functionality
                self.cached_issues = issues_data
                self.cached_issues_type = f"severity_{severity}"
                
                return {
                    "success": True,
                    "data": issues_data
                }
            
            elif function_name == "show_more_issues":
                start_index = function_args.get("start_index", 5)
                batch_size = function_args.get("batch_size", 5)
                
                logger.debug(f"show_more_issues requested - start_index: {start_index}, batch_size: {batch_size}")
                logger.debug(f"Cache status - has cached_issues: {self.cached_issues is not None}, cached_type: {self.cached_issues_type}")
                
                if not self.cached_issues:
                    return {
                        "success": False,
                        "error": "No cached issues available. Please retrieve issues first by asking for 'all issues', 'open issues', or any specific search.",
                        "cache_status": {
                            "has_cache": False,
                            "cached_type": self.cached_issues_type
                        }
                    }
                
                if len(self.cached_issues) <= start_index:
                    return {
                        "success": False,
                        "error": f"No more issues to show. Total cached issues: {len(self.cached_issues)}, requested start: {start_index}",
                        "cache_status": {
                            "total_cached": len(self.cached_issues),
                            "requested_start": start_index,
                            "cached_type": self.cached_issues_type
                        }
                    }
                
                end_index = start_index + batch_size
                batch_issues = self.cached_issues[start_index:end_index]
                has_more = end_index < len(self.cached_issues)
                
                logger.info(f"Returning batch of {len(batch_issues)} issues from cache ({start_index+1}-{min(end_index, len(self.cached_issues))} of {len(self.cached_issues)})")
                
                return {
                    "success": True,
                    "data": batch_issues,
                    "batch_info": {
                        "start_index": start_index,
                        "end_index": min(end_index, len(self.cached_issues)),
                        "total_cached": len(self.cached_issues),
                        "has_more": has_more,
                        "cached_type": self.cached_issues_type,
                        "batch_size": len(batch_issues)
                    }
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
    
    def _generate_categorized_summary(self, issues_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate simple categorized summary with status breakdown only.
        
        Args:
            issues_data: List of formatted issue data
            
        Returns:
            Dictionary containing simplified summary
        """
        if not issues_data:
            return {
                "total_issues": 0,
                "status_breakdown": {},
                "displayed_issues": [],
                "has_more": False
            }
        
        # Count by status only
        status_counts = {}
        for issue in issues_data:
            status = issue.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Show first 5 issues
        displayed_issues = issues_data[:5]
        has_more = len(issues_data) > 5
        
        summary = {
            "total_issues": len(issues_data),
            "status_breakdown": dict(sorted(status_counts.items(), key=lambda x: x[1], reverse=True)),
            "displayed_issues": displayed_issues,
            "has_more": has_more,
            "remaining_count": len(issues_data) - 5 if has_more else 0
        }
        
        return summary
    
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
