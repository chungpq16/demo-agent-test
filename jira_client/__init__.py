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
        
        # Load configurable limits
        self.default_limit = int(os.getenv('JIRA_DEFAULT_LIMIT', '10'))
        self.max_results = int(os.getenv('JIRA_MAX_RESULTS', '50'))
        
        logger.info(f"Jira client initialized successfully with default_limit={self.default_limit}, max_results={self.max_results}")
    
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
            max_results: Maximum number of results to return (uses JIRA_DEFAULT_LIMIT if None)
            
        Returns:
            List of issue dictionaries
        """
        if max_results is None:
            max_results = self.default_limit
            
        try:
            jql = f"project = {self.project_key} ORDER BY created DESC"
            
            logger.debug(f"Fetching all issues with JQL: {jql}")
            
            issues = self.jira.jql(jql, limit=max_results)
            
            result = []
            for issue in issues['issues']:
                issue_data = self._format_issue(issue)
                result.append(issue_data)
            
            logger.info(f"Retrieved {len(result)} issues from project {self.project_key}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching all issues: {str(e)}")
            raise Exception(f"Failed to fetch all issues: {str(e)}")
    
    def get_issues_by_status(self, status: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Get issues filtered by status.
        
        Args:
            status: Status to filter by (e.g., 'Open', 'In Progress', 'Done')
            max_results: Maximum number of results to return (uses JIRA_DEFAULT_LIMIT if None)
            
        Returns:
            List of issue dictionaries
        """
        if max_results is None:
            max_results = self.default_limit
            
        try:
            # Map common status names
            status_mapping = {
                'open': 'Open',
                'in-progress': 'In Progress',
                'done': 'Done',
                'closed': 'Closed',
                'resolved': 'Resolved'
            }
            
            mapped_status = status_mapping.get(status.lower(), status)
            jql = f'project = {self.project_key} AND status = "{mapped_status}" ORDER BY created DESC'
            
            logger.debug(f"Fetching issues by status with JQL: {jql}")
            
            issues = self.jira.jql(jql, limit=max_results)
            
            result = []
            for issue in issues['issues']:
                issue_data = self._format_issue(issue)
                result.append(issue_data)
            
            logger.info(f"Retrieved {len(result)} issues with status '{mapped_status}'")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching issues by status '{status}': {str(e)}")
            raise Exception(f"Failed to fetch issues by status: {str(e)}")
    
    def get_issue_details(self, issue_key: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific issue.
        
        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')
            
        Returns:
            Detailed issue information
        """
        try:
            logger.debug(f"Fetching details for issue: {issue_key}")
            
            issue = self.jira.issue(issue_key)
            issue_data = self._format_issue_detailed(issue)
            
            logger.info(f"Retrieved detailed information for issue {issue_key}")
            return issue_data
            
        except Exception as e:
            logger.error(f"Error fetching issue details for '{issue_key}': {str(e)}")
            raise Exception(f"Failed to fetch issue details: {str(e)}")
    
    def _format_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format issue data for consistent output.
        
        Args:
            issue: Raw issue data from Jira API
            
        Returns:
            Formatted issue data
        """
        fields = issue.get('fields', {})
        
        return {
            'key': issue.get('key'),
            'summary': fields.get('summary'),
            'status': fields.get('status', {}).get('name'),
            'priority': fields.get('priority', {}).get('name'),
            'assignee': fields.get('assignee', {}).get('displayName') if fields.get('assignee') else None,
            'reporter': fields.get('reporter', {}).get('displayName') if fields.get('reporter') else None,
            'created': fields.get('created'),
            'updated': fields.get('updated'),
            'issue_type': fields.get('issuetype', {}).get('name'),
            'url': f"{os.getenv('JIRA_URL')}/browse/{issue.get('key')}"
        }
    
    def _format_issue_detailed(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format detailed issue data.
        
        Args:
            issue: Raw issue data from Jira API
            
        Returns:
            Detailed formatted issue data
        """
        fields = issue.get('fields', {})
        basic_info = self._format_issue(issue)
        
        # Add detailed fields
        basic_info.update({
            'description': fields.get('description'),
            'labels': fields.get('labels', []),
            'components': [comp.get('name') for comp in fields.get('components', [])],
            'fix_versions': [ver.get('name') for ver in fields.get('fixVersions', [])],
            'resolution': fields.get('resolution', {}).get('name') if fields.get('resolution') else None,
            'environment': fields.get('environment'),
            'due_date': fields.get('duedate')
        })
        
        return basic_info
    
    def health_check(self) -> bool:
        """
        Check if Jira is accessible and credentials are valid.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to fetch user info as a simple health check
            user_info = self.jira.myself()
            logger.info(f"Jira health check passed for user: {user_info.get('displayName')}")
            return True
        except Exception as e:
            logger.error(f"Jira health check failed: {str(e)}")
            return False
    
    def search_issues(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Search issues using JQL or text search.
        
        Args:
            query: Search query (JQL or text)
            max_results: Maximum number of results (uses JIRA_MAX_RESULTS if None)
            
        Returns:
            List of matching issues
        """
        if max_results is None:
            max_results = self.max_results
            
        try:
            # If query contains JQL syntax, use it directly, otherwise search in summary and description
            if any(keyword in query.upper() for keyword in ['AND', 'OR', 'ORDER BY', 'PROJECT']):
                jql = query
            else:
                jql = f'project = {self.project_key} AND (summary ~ "{query}" OR description ~ "{query}") ORDER BY created DESC'
            
            logger.debug(f"Searching issues with JQL: {jql}")
            
            issues = self.jira.jql(jql, limit=max_results)
            
            result = []
            for issue in issues['issues']:
                issue_data = self._format_issue(issue)
                result.append(issue_data)
            
            logger.info(f"Found {len(result)} issues matching query")
            return result
            
        except Exception as e:
            logger.error(f"Error searching issues: {str(e)}")
            raise Exception(f"Failed to search issues: {str(e)}")
