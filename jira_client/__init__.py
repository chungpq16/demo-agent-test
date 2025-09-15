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
        
        if not all([jira_url, jira_username, jira_token, self.project_key]):
            raise ValueError("Missing required Jira environment variables")
        
        try:
            self.jira = Jira(
                url=jira_url,
                username=jira_username,
                password=jira_token,
                cloud=True  # Set to True for Jira Cloud
            )
            
            logger.debug(f"Jira client configured for: {jira_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Jira client: {str(e)}")
            raise Exception(f"Jira client initialization failed: {str(e)}")
    
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
            
            # Get issues using JQL
            issues = self.jira.jql(jql, limit=max_results)
            
            if not issues or 'issues' not in issues:
                logger.warning("No issues returned from Jira")
                return []
            
            # Format issues for consumption
            formatted_issues = []
            for issue in issues['issues']:
                formatted_issues.append(self._format_issue(issue))
            
            logger.info(f"Retrieved {len(formatted_issues)} issues")
            return formatted_issues
            
        except Exception as e:
            logger.error(f"Error fetching all issues: {str(e)}")
            raise Exception(f"Failed to fetch issues: {str(e)}")
    
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
            
            # Get issues using JQL
            issues = self.jira.jql(jql, limit=max_results)
            
            if not issues or 'issues' not in issues:
                logger.warning(f"No issues found with status: {status}")
                return []
            
            # Format issues for consumption
            formatted_issues = []
            for issue in issues['issues']:
                formatted_issues.append(self._format_issue(issue))
            
            logger.info(f"Retrieved {len(formatted_issues)} issues with status: {status}")
            return formatted_issues
            
        except Exception as e:
            logger.error(f"Error fetching issues by status: {str(e)}")
            raise Exception(f"Failed to fetch issues by status: {str(e)}")
    
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
            raise Exception(f"Failed to fetch issue details: {str(e)}")
    
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
            
            # Get issues using JQL
            issues = self.jira.jql(jql, limit=max_results)
            
            if not issues or 'issues' not in issues:
                logger.warning(f"No issues found for query: {query}")
                return []
            
            # Format issues for consumption
            formatted_issues = []
            for issue in issues['issues']:
                formatted_issues.append(self._format_issue(issue))
            
            logger.info(f"Found {len(formatted_issues)} issues for query: {query}")
            return formatted_issues
            
        except Exception as e:
            logger.error(f"Error searching issues: {str(e)}")
            raise Exception(f"Failed to search issues: {str(e)}")
    
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
    
    def health_check(self) -> bool:
        """
        Check if Jira client is healthy and can connect.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to get server info as a health check
            server_info = self.jira.server_info()
            logger.debug(f"Jira server info: {server_info}")
            return True
        except Exception as e:
            logger.error(f"Jira health check failed: {str(e)}")
            return False
