"""
Jira Client for handling API interactions with Atlassian Jira.
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from atlassian import Jira
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class JiraClient:
    """
    A client class for interacting with Jira API.
    """
    
    def __init__(self):
        """Initialize Jira client with environment variables."""
        self.server_url = os.getenv("JIRA_SERVER_URL")
        self.username = os.getenv("JIRA_USERNAME")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.project_key = os.getenv("JIRA_PROJECT_KEY")  # Optional project scoping
        
        if not all([self.server_url, self.username, self.api_token]):
            raise ValueError("Missing required Jira credentials in environment variables")
        
        self.jira = Jira(
            url=self.server_url,
            username=self.username,
            password=self.api_token
        )
        
        # Log project scoping status
        if self.project_key:
            logger.info(f"Jira client initialized successfully with project scope: {self.project_key}")
        else:
            logger.info("Jira client initialized successfully (all projects)")
    
    def _build_project_scoped_jql(self, base_jql: str) -> str:
        """
        Add project scoping to JQL if JIRA_PROJECT_KEY is set.
        
        Args:
            base_jql: Base JQL query
            
        Returns:
            Project-scoped JQL query
        """
        if not self.project_key:
            logger.debug(f"No project scoping - returning original JQL: {base_jql}")
            return base_jql
        
        # If base_jql is empty, just add project filter
        if not base_jql:
            result = f'project = "{self.project_key}"'
            logger.debug(f"Empty base JQL - project filter only: {result}")
            return result
        
        # If base_jql only contains ORDER BY, add project filter before it
        if base_jql.strip().startswith("ORDER BY"):
            result = f'project = "{self.project_key}" {base_jql}'
            logger.debug(f"ORDER BY only - added project filter: {result}")
            return result
        
        # If base_jql contains ORDER BY, separate conditions from ordering
        if "ORDER BY" in base_jql:
            parts = base_jql.split("ORDER BY", 1)
            conditions = parts[0].strip()
            ordering = f"ORDER BY {parts[1].strip()}"
            result = f'project = "{self.project_key}" AND ({conditions}) {ordering}'
            logger.debug(f"Complex JQL with ORDER BY - scoped: {base_jql} -> {result}")
            return result
        
        # If base_jql has only conditions (no ORDER BY), add project filter with AND
        result = f'project = "{self.project_key}" AND ({base_jql})'
        logger.debug(f"Simple conditions - scoped: {base_jql} -> {result}")
        return result
    
    def get_issues_by_status(self, status: str, limit: int = 100) -> pd.DataFrame:
        """
        Retrieve issues by status.
        
        Args:
            status: Issue status (e.g., 'To Do', 'In Progress', 'Done')
            limit: Maximum number of issues to retrieve         
        Returns:
            DataFrame containing issue data
        """
        try:
            base_jql = f'status = "{status}" ORDER BY created DESC'
            jql = self._build_project_scoped_jql(base_jql)
            result = self.jira.jql(jql, limit=limit)
            
            if not result.get('issues'):
                project_info = f" in project {self.project_key}" if self.project_key else ""
                logger.warning(f"No issues found with status: {status}{project_info}")
                return pd.DataFrame()
            
            issues_data = []
            for issue in result['issues']:
                issue_data = self._extract_issue_data(issue)
                issues_data.append(issue_data)
            
            df = pd.DataFrame(issues_data)
            project_info = f" in project {self.project_key}" if self.project_key else ""
            logger.info(f"Retrieved {len(df)} issues with status: {status}{project_info}")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving issues by status {status}: {e}")
            raise
    
    def get_all_issues(self, limit: int = 100) -> pd.DataFrame:
        """
        Retrieve all issues accessible to the user.
        
        Args:
            limit: Maximum number of issues to retrieve
            
        Returns:
            DataFrame containing issue data
        """
        try:
            base_jql = "ORDER BY created DESC"
            jql = self._build_project_scoped_jql(base_jql)
            result = self.jira.jql(jql, limit=limit)
            
            if not result.get('issues'):
                project_info = f" in project {self.project_key}" if self.project_key else ""
                logger.warning(f"No issues found{project_info}")
                return pd.DataFrame()
            
            issues_data = []
            for issue in result['issues']:
                issue_data = self._extract_issue_data(issue)
                issues_data.append(issue_data)
            
            df = pd.DataFrame(issues_data)
            project_info = f" in project {self.project_key}" if self.project_key else ""
            logger.info(f"Retrieved {len(df)} total issues{project_info}")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving all issues: {e}")
            raise
    
    def get_issue_details(self, issue_key: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific issue.
        
        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')
        Returns:
            Dictionary containing detailed issue information
        """
        try:
            issue = self.jira.issue(issue_key)
            
            # Get comments
            comments = []
            if 'comment' in issue['fields'] and issue['fields']['comment']['comments']:
                for comment in issue['fields']['comment']['comments']:
                    comments.append({
                        'author': comment['author']['displayName'],
                        'created': comment['created'],
                        'body': comment['body']
                    })
            
            # Extract detailed information
            details = {
                'key': issue['key'],
                'summary': issue['fields'].get('summary', ''),
                'description': issue['fields'].get('description', ''),
                'status': issue['fields']['status']['name'],
                'assignee': issue['fields']['assignee']['displayName'] if issue['fields'].get('assignee') else 'Unassigned',
                'reporter': issue['fields']['reporter']['displayName'] if issue['fields'].get('reporter') else 'Unknown',
                'created': issue['fields'].get('created', ''),
                'updated': issue['fields'].get('updated', ''),
                'priority': issue['fields']['priority']['name'] if issue['fields'].get('priority') else 'None',
                'issue_type': issue['fields']['issuetype']['name'],
                'labels': issue['fields'].get('labels', []),
                'components': [comp['name'] for comp in issue['fields'].get('components', [])],
                'comments': comments,
                'comment_count': len(comments)
            }
            
            logger.info(f"Retrieved details for issue: {issue_key}")
            return details
            
        except Exception as e:
            logger.error(f"Error retrieving issue details for {issue_key}: {e}")
            raise
    
    def search_issues(self, jql: str, limit: int = 50) -> pd.DataFrame:
        """
        Search issues using JQL (Jira Query Language).
        
        Args:
            jql: JQL query string
            limit: Maximum number of issues to retrieve
            
        Returns:
            DataFrame containing issue data
        """
        try:
            # Apply project scoping to the provided JQL
            scoped_jql = self._build_project_scoped_jql(jql)
            result = self.jira.jql(scoped_jql, limit=limit)
            
            if not result.get('issues'):
                project_info = f" in project {self.project_key}" if self.project_key else ""
                logger.warning(f"No issues found for JQL: {jql}{project_info}")
                return pd.DataFrame()
            
            issues_data = []
            for issue in result['issues']:
                issue_data = self._extract_issue_data(issue)
                issues_data.append(issue_data)
            
            df = pd.DataFrame(issues_data)
            project_info = f" in project {self.project_key}" if self.project_key else ""
            logger.info(f"Found {len(df)} issues for JQL: {jql}{project_info}")
            return df
            
        except Exception as e:
            logger.error(f"Error searching issues with JQL {jql}: {e}")
            raise
    
    def get_project_info(self) -> List[Dict[str, Any]]:
        """
        Get information about accessible projects.
        
        Returns:
            List of project dictionaries
        """
        try:
            projects = self.jira.projects()
            project_info = []
            
            for project in projects:
                project_info.append({
                    'key': project['key'],
                    'name': project['name'],
                    'project_type': project.get('projectTypeKey', 'Unknown'),
                    'lead': project.get('lead', {}).get('displayName', 'Unknown')
                })
            
            logger.info(f"Retrieved information for {len(project_info)} projects")
            return project_info
            
        except Exception as e:
            logger.error(f"Error retrieving project information: {e}")
            raise
    
    def get_current_project_scope(self) -> Optional[str]:
        """
        Get the current project scope if set.
        
        Returns:
            Project key if scoped, None otherwise
        """
        return self.project_key
    
    def is_project_scoped(self) -> bool:
        """
        Check if the client is configured for project-scoped searches.
        
        Returns:
            True if project scoping is enabled
        """
        return bool(self.project_key)
    
    def _extract_issue_data(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and structure issue data from Jira API response.
        
        Args:
            issue: Raw issue data from Jira API
            
        Returns:
            Structured issue data dictionary
        """
        fields = issue.get('fields', {})
        
        return {
            'key': issue.get('key', ''),
            'summary': fields.get('summary', ''),
            'status': fields.get('status', {}).get('name', ''),
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'reporter': fields.get('reporter', {}).get('displayName', 'Unknown') if fields.get('reporter') else 'Unknown',
            'created': fields.get('created', ''),
            'updated': fields.get('updated', ''),
            'priority': fields.get('priority', {}).get('name', 'None') if fields.get('priority') else 'None',
            'issue_type': fields.get('issuetype', {}).get('name', ''),
            'labels': fields.get('labels', []),
            'description': fields.get('description', ''),
            'components': [comp.get('name', '') for comp in fields.get('components', [])],
        }
