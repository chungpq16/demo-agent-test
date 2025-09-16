"""
Jira Client Module
Handles Jira API interactions using atlassian-python-api SDK.
"""
import os
from typing import List, Dict, Optional, Any
from atlassian import Jira
from dotenv import load_dotenv
from logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger()


class JiraClient:
    """Client for interacting with Jira API."""
    
    def __init__(self):
        """Initialize Jira client with configuration from environment."""
        self._setup_client()
        
        # Load configurable limits - using single consolidated parameter
        self.max_results = int(os.getenv('JIRA_MAX_RESULTS', '50'))
        
        logger.info(f"Jira client initialized successfully with max_results={self.max_results}")
    
    def _setup_client(self):
        """Setup Jira client with authentication."""
        jira_url = os.getenv('JIRA_URL')
        jira_username = os.getenv('JIRA_USERNAME')
        jira_token = os.getenv('JIRA_TOKEN')
        self.project_key = os.getenv('JIRA_PROJECT')
        
        logger.debug(f"Setting up Jira client with URL: {jira_url}")
        logger.debug(f"Username: {jira_username}")
        logger.debug(f"Project key: {self.project_key}")
        logger.debug(f"Token provided: {'Yes' if jira_token else 'No'}")
        
        if not all([jira_url, jira_username, jira_token, self.project_key]):
            missing = []
            if not jira_url: missing.append('JIRA_URL')
            if not jira_username: missing.append('JIRA_USERNAME')
            if not jira_token: missing.append('JIRA_TOKEN')
            if not self.project_key: missing.append('JIRA_PROJECT')
            
            error_msg = f"Missing required Jira environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            self.jira = Jira(
                url=jira_url,
                username=jira_username,
                password=jira_token,
                cloud=True  # Set to True for Jira Cloud
            )
            
            logger.debug(f"Jira client configured for: {jira_url}")
            
            # Test the connection by trying to get current user info
            try:
                current_user = self.jira.myself()
                logger.info(f"Successfully connected to Jira. Connected as: {current_user.get('displayName', 'Unknown')}")
            except Exception as test_e:
                logger.warning(f"Jira client created but connection test failed: {str(test_e)}")
                logger.warning("This might indicate authentication issues or network problems")
            
        except Exception as e:
            logger.error(f"Failed to initialize Jira client: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"URL: {jira_url}")
            logger.error(f"Username: {jira_username}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Jira client initialization failed: {str(e)} - Check credentials and network connectivity")
    
    def get_all_issues(self, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Get all issues from the configured project.
        
        Args:
            max_results: Maximum number of results to return (uses JIRA_MAX_RESULTS if None)
            
        Returns:
            List of issue dictionaries
        """
        if max_results is None:
            max_results = self.max_results
            
        try:
            jql = f"project = {self.project_key} ORDER BY created DESC"
            
            logger.debug(f"Fetching all issues with JQL: {jql}")
            logger.debug(f"Using max_results limit: {max_results}")
            
            # Use custom JQL method with proper endpoint and fields
            response = self._execute_jql(jql, max_results)
            
            if not response or 'issues' not in response:
                logger.warning("No issues returned from Jira")
                return []
            
            # Format issues for consumption
            formatted_issues = []
            for issue in response['issues']:
                formatted_issues.append(self._format_issue(issue))
            
            logger.info(f"Retrieved {len(formatted_issues)} issues")
            return formatted_issues
            
        except Exception as e:
            logger.error(f"Error fetching all issues: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"JQL used: {jql}")
            logger.error(f"Project key: {self.project_key}")
            logger.error(f"Max results: {max_results}")
            # Log more details about the Jira connection
            logger.error(f"Jira URL: {os.getenv('JIRA_URL')}")
            logger.error(f"Jira Username: {os.getenv('JIRA_USERNAME')}")
            
            # Enhanced HTTP error logging
            if hasattr(e, 'response'):
                logger.error(f"HTTP Status Code: {e.response.status_code}")
                logger.error(f"HTTP Response Headers: {dict(e.response.headers)}")
                try:
                    logger.error(f"HTTP Response Body: {e.response.text}")
                except:
                    logger.error("Could not read HTTP response body")
            
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to fetch issues: {str(e)} - Check logs for more details")
    
    def get_issues_by_status(self, status: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Get issues filtered by status.
        
        Args:
            status: Status to filter by (e.g., 'Open', 'In Progress', 'Done')
            max_results: Maximum number of results to return (uses JIRA_MAX_RESULTS if None)
            
        Returns:
            List of issue dictionaries
        """
        if max_results is None:
            max_results = self.max_results
            
        try:
            # Map common status names
            status_mapping = {
                'open': 'Open',
                'in progress': 'In Progress',
                'done': 'Done',
                'closed': 'Closed',
                'resolved': 'Resolved'
            }
            
            # Normalize status name
            normalized_status = status_mapping.get(status.lower(), status)
            
            jql = f"project = {self.project_key} AND status = '{normalized_status}' ORDER BY created DESC"
            
            logger.debug(f"Fetching issues by status with JQL: {jql}")
            
            # Use custom JQL method with proper endpoint and fields
            response = self._execute_jql(jql, max_results)
            
            if not response or 'issues' not in response:
                logger.warning(f"No issues found with status: {status}")
                return []
            
            # Format issues for consumption
            formatted_issues = []
            for issue in response['issues']:
                formatted_issues.append(self._format_issue(issue))
            
            logger.info(f"Retrieved {len(formatted_issues)} issues with status: {status}")
            return formatted_issues
            
        except Exception as e:
            logger.error(f"Error fetching issues by status: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"JQL used: {jql}")
            logger.error(f"Status filter: {status} -> {normalized_status}")
            
            # Enhanced HTTP error logging
            if hasattr(e, 'response'):
                logger.error(f"HTTP Status Code: {e.response.status_code}")
                logger.error(f"HTTP Response Headers: {dict(e.response.headers)}")
                try:
                    logger.error(f"HTTP Response Body: {e.response.text}")
                except:
                    logger.error("Could not read HTTP response body")
            
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to fetch issues by status: {str(e)} - Check logs for more details")
    
    def get_issue_details(self, issue_key: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific issue.
        
        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')
            
        Returns:
            Issue details dictionary
        """
        try:
            logger.debug(f"Fetching issue details for: {issue_key}")
            
            # Get issue details
            issue = self.jira.issue(issue_key)
            
            if not issue:
                logger.warning(f"Issue not found: {issue_key}")
                return {}
            
            # Format issue for consumption
            formatted_issue = self._format_issue(issue, detailed=True)
            
            logger.info(f"Retrieved details for issue: {issue_key}")
            return formatted_issue
            
        except Exception as e:
            logger.error(f"Error fetching issue details: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Issue key requested: {issue_key}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to fetch issue details: {str(e)} - Check logs for more details")
    
    def search_issues(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Search issues using text query or JQL.
        
        Args:
            query: Search query (text or JQL)
            max_results: Maximum number of results to return (uses JIRA_MAX_RESULTS if None)
            
        Returns:
            List of matching issue dictionaries
        """
        if max_results is None:
            max_results = self.max_results
            
        try:
            # Check if query is already JQL (contains JQL keywords)
            jql_keywords = ['project', 'status', 'assignee', 'reporter', 'labels', 'priority', 'created', 'updated', 'AND', 'OR', 'ORDER BY']
            is_jql = any(keyword.lower() in query.lower() for keyword in jql_keywords)
            
            if is_jql:
                # Use query as-is (JQL)
                jql = query
            else:
                # Convert text to JQL search
                jql = f"project = {self.project_key} AND (summary ~ '{query}' OR description ~ '{query}') ORDER BY created DESC"
            
            logger.debug(f"Searching issues with JQL: {jql}")
            
            # Use custom JQL method with proper endpoint and fields
            response = self._execute_jql(jql, max_results)
            
            if not response or 'issues' not in response:
                logger.warning(f"No issues found for query: {query}")
                return []
            
            # Format issues for consumption
            formatted_issues = []
            for issue in response['issues']:
                formatted_issues.append(self._format_issue(issue))
            
            logger.info(f"Found {len(formatted_issues)} issues for query: {query}")
            return formatted_issues
            
        except Exception as e:
            logger.error(f"Error searching issues: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Original query: {query}")
            logger.error(f"JQL used: {jql}")
            logger.error(f"Is JQL: {is_jql}")
            
            # Enhanced HTTP error logging
            if hasattr(e, 'response'):
                logger.error(f"HTTP Status Code: {e.response.status_code}")
                logger.error(f"HTTP Response Headers: {dict(e.response.headers)}")
                try:
                    logger.error(f"HTTP Response Body: {e.response.text}")
                except:
                    logger.error("Could not read HTTP response body")
            
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to search issues: {str(e)} - Check logs for more details")
    
    def _format_issue(self, issue: Dict, detailed: bool = False) -> Dict[str, Any]:
        """
        Format a Jira issue for consistent consumption.
        
        Args:
            issue: Raw issue data from Jira API
            detailed: Whether to include detailed information
            
        Returns:
            Formatted issue dictionary
        """
        try:
            fields = issue.get('fields', {})
            
            # Base formatting
            formatted = {
                'key': issue.get('key', 'Unknown'),
                'id': issue.get('id', 'Unknown'),
                'summary': fields.get('summary', 'No summary'),
                'status': fields.get('status', {}).get('name', 'Unknown'),
                'priority': fields.get('priority', {}).get('name', 'Unknown'),
                'assignee': self._get_user_display_name(fields.get('assignee')),
                'reporter': self._get_user_display_name(fields.get('reporter')),
                'created': fields.get('created', 'Unknown'),
                'updated': fields.get('updated', 'Unknown'),
                'url': f"{os.getenv('JIRA_URL')}/browse/{issue.get('key', '')}"
            }
            
            # Add labels if present
            labels = fields.get('labels', [])
            if labels:
                formatted['labels'] = labels
            
            # Add detailed information if requested
            if detailed:
                formatted.update({
                    'description': fields.get('description', 'No description'),
                    'issue_type': fields.get('issuetype', {}).get('name', 'Unknown'),
                    'project': fields.get('project', {}).get('name', 'Unknown'),
                    'project_key': fields.get('project', {}).get('key', 'Unknown')
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting issue: {str(e)}")
            return {
                'key': issue.get('key', 'Unknown'),
                'error': f"Failed to format issue: {str(e)}"
            }
    
    def _get_user_display_name(self, user_field: Optional[Dict]) -> str:
        """
        Extract display name from user field.
        
        Args:
            user_field: User field from Jira API
            
        Returns:
            User display name or 'Unassigned'
        """
        if not user_field:
            return 'Unassigned'
        
        return user_field.get('displayName') or user_field.get('name') or 'Unknown User'
    
    def _execute_jql(self, jql: str, max_results: int = None, fields: str = None) -> Dict[str, Any]:
        """
        Execute JQL query using the correct API endpoint with proper field specification.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            fields: Comma-separated field list (required by company guidelines)
            
        Returns:
            Jira API response dictionary
        """
        import time
        
        if max_results is None:
            max_results = self.max_results
        
        # Default fields as required by company guidelines to avoid load-intensive queries
        if fields is None:
            fields = "summary,status,priority,assignee,reporter,created,updated,labels,issuetype,project"
        
        try:
            # Use the correct API endpoint as per company guidelines
            url = "/rest/api/2/search"
            
            params = {
                'jql': jql,
                'maxResults': max_results,
                'fields': fields
            }
            
            logger.debug(f"Executing JQL with correct endpoint: {url}")
            logger.debug(f"Parameters: {params}")
            
            # Add small delay to avoid high-frequency queries as per guidelines
            time.sleep(0.5)
            
            # Use direct GET request to correct endpoint
            response = self.jira.get(url, params=params)
            
            logger.debug(f"JQL query successful. Response type: {type(response)}")
            return response
            
        except Exception as e:
            logger.error(f"JQL execution failed: {str(e)}")
            logger.error(f"JQL: {jql}")
            logger.error(f"URL: {url}")
            logger.error(f"Params: {params}")
            
            # Enhanced HTTP error logging
            if hasattr(e, 'response'):
                logger.error(f"HTTP Status Code: {e.response.status_code}")
                logger.error(f"HTTP Response Headers: {dict(e.response.headers)}")
                try:
                    logger.error(f"HTTP Response Body: {e.response.text}")
                except:
                    logger.error("Could not read HTTP response body")
            
            raise e
    
    def health_check(self) -> bool:
        """
        Check if Jira client is healthy and can connect.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            logger.info("Starting Jira health check...")
            
            # Try to get current user info as a health check
            current_user = self.jira.myself()
            logger.info(f"✅ Jira health check passed. Connected as: {current_user.get('displayName', 'Unknown')}")
            
            # Test a simple JQL query to ensure we can query issues
            test_jql = f"project = {self.project_key}"
            logger.debug(f"Testing JQL query: {test_jql}")
            
            test_result = self._execute_jql(test_jql, max_results=1)
            logger.info(f"✅ JQL test query successful. Response type: {type(test_result)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Jira health check failed: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Project key tested: {self.project_key}")
            
            # Try to provide more specific error information
            if "401" in str(e) or "Unauthorized" in str(e):
                logger.error("🔑 Authentication failed - check JIRA_USERNAME and JIRA_TOKEN")
            elif "403" in str(e) or "Forbidden" in str(e):
                logger.error("🚫 Access forbidden - check user permissions for project")
            elif "404" in str(e) or "Not Found" in str(e):
                logger.error("📍 Resource not found - check JIRA_URL and JIRA_PROJECT")
            elif "timeout" in str(e).lower() or "connection" in str(e).lower():
                logger.error("🌐 Network connectivity issue - check JIRA_URL and network access")
            
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def diagnostic_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive diagnostic check and return detailed results.
        
        Returns:
            Dictionary with diagnostic information
        """
        diagnostics = {
            'config_check': {},
            'connection_check': {},
            'project_check': {},
            'permissions_check': {},
            'overall_status': 'unknown'
        }
        
        # Check configuration
        try:
            jira_url = os.getenv('JIRA_URL')
            jira_username = os.getenv('JIRA_USERNAME') 
            jira_token = os.getenv('JIRA_TOKEN')
            project_key = os.getenv('JIRA_PROJECT')
            
            diagnostics['config_check'] = {
                'jira_url': '✅ Set' if jira_url else '❌ Missing',
                'jira_username': '✅ Set' if jira_username else '❌ Missing',
                'jira_token': '✅ Set' if jira_token else '❌ Missing',
                'project_key': '✅ Set' if project_key else '❌ Missing',
                'url_value': jira_url if jira_url else 'Not set',
                'username_value': jira_username if jira_username else 'Not set',
                'project_value': project_key if project_key else 'Not set'
            }
        except Exception as e:
            diagnostics['config_check']['error'] = str(e)
        
        # Test connection
        try:
            current_user = self.jira.myself()
            diagnostics['connection_check'] = {
                'status': '✅ Connected',
                'connected_user': current_user.get('displayName', 'Unknown'),
                'user_account_id': current_user.get('accountId', 'Unknown')
            }
        except Exception as e:
            diagnostics['connection_check'] = {
                'status': '❌ Connection failed',
                'error': str(e),
                'error_type': type(e).__name__
            }
        
        # Test project access
        try:
            project_info = self.jira.project(self.project_key)
            diagnostics['project_check'] = {
                'status': '✅ Project accessible',
                'project_name': project_info.get('name', 'Unknown'),
                'project_type': project_info.get('projectTypeKey', 'Unknown')
            }
        except Exception as e:
            error_details = {
                'status': '❌ Cannot access project',
                'error': str(e),
                'error_type': type(e).__name__,
                'project_key': self.project_key
            }
            
            if hasattr(e, 'response'):
                error_details.update({
                    'http_status': e.response.status_code,
                    'http_reason': e.response.reason if hasattr(e.response, 'reason') else 'Unknown'
                })
            
            diagnostics['project_check'] = error_details
        
        # Test permissions
        try:
            test_jql = f"project = {self.project_key}"
            result = self._execute_jql(test_jql, max_results=1)
            diagnostics['permissions_check'] = {
                'status': '✅ Can query project',
                'test_jql': test_jql,
                'issues_found': len(result.get('issues', [])) if result else 0
            }
        except Exception as e:
            error_details = {
                'status': '❌ Cannot query project',
                'error': str(e),
                'error_type': type(e).__name__,
                'test_jql': f"project = {self.project_key}"
            }
            
            # Enhanced HTTP error logging for diagnostics
            if hasattr(e, 'response'):
                error_details.update({
                    'http_status': e.response.status_code,
                    'http_reason': e.response.reason if hasattr(e.response, 'reason') else 'Unknown'
                })
                try:
                    error_details['http_body'] = e.response.text[:500]  # First 500 chars
                except:
                    error_details['http_body'] = 'Could not read response body'
            
            diagnostics['permissions_check'] = error_details
        
        # Determine overall status
        config_ok = all('✅' in str(v) for v in diagnostics['config_check'].values() if isinstance(v, str))
        connection_ok = '✅' in diagnostics['connection_check'].get('status', '')
        project_ok = '✅' in diagnostics['project_check'].get('status', '')
        permissions_ok = '✅' in diagnostics['permissions_check'].get('status', '')
        
        if config_ok and connection_ok and project_ok and permissions_ok:
            diagnostics['overall_status'] = '✅ All systems operational'
        elif not config_ok:
            diagnostics['overall_status'] = '❌ Configuration incomplete'
        elif not connection_ok:
            diagnostics['overall_status'] = '❌ Connection failed'
        elif not project_ok:
            diagnostics['overall_status'] = '❌ Project inaccessible'
        elif not permissions_ok:
            diagnostics['overall_status'] = '❌ Permission denied'
        else:
            diagnostics['overall_status'] = '⚠️ Partial functionality'
        
        return diagnostics
