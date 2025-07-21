"""
Jira Tools for LangGraph Agent - Tools for interacting with Jira API.
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from jira_client import JiraClient
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

# Global client variable - will be set by initialize_tools function
jira_client = None

def initialize_tools(client: JiraClient):
    """Initialize tools with a shared Jira client instance."""
    global jira_client
    jira_client = client
    logger.debug(f"Tools initialized with Jira client: {client is not None}")

@tool
def get_issues_by_status(status: str) -> str:
    """
    Retrieve Jira issues filtered by status.
    
    Args:
        status: Issue status to filter by (e.g., 'To Do', 'In Progress', 'Done')
        
    Returns:
        JSON string containing issue data
    """
    if not jira_client:
        return "Error: Jira client not initialized. Please check your credentials."
    
    try:
        df = jira_client.get_issues_by_status(status)
        
        if df.empty:
            return f"No issues found with status: {status}"
        
        # Convert DataFrame to a more readable format
        issues_summary = []
        for _, row in df.iterrows():
            issues_summary.append({
                'key': row['key'],
                'summary': row['summary'],
                'status': row['status'],
                'assignee': row['assignee'],
                'priority': row['priority'],
                'created': row['created']
            })
        
        result = {
            'status_filter': status,
            'total_issues': len(issues_summary),
            'issues': issues_summary
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in get_issues_by_status: {e}")
        return f"Error retrieving issues: {str(e)}"

@tool
def get_issue_details(issue_key: str) -> str:
    """
    Get detailed information about a specific Jira issue.
    
    Args:
        issue_key: Jira issue key (e.g., 'PROJ-123')
        
    Returns:
        JSON string containing detailed issue information
    """
    if not jira_client:
        return "Error: Jira client not initialized. Please check your credentials."
    
    try:
        details = jira_client.get_issue_details(issue_key)
        return json.dumps(details, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in get_issue_details: {e}")
        return f"Error retrieving issue details for {issue_key}: {str(e)}"

@tool
def get_all_issues() -> str:
    """
    Retrieve all accessible Jira issues without any status filter.
    
    Returns:
        JSON string containing all issues data
    """
    if not jira_client:
        return "Error: Jira client not initialized. Please check your credentials."
    
    try:
        df = jira_client.get_all_issues(limit=100)
        
        if df.empty:
            return "No issues found."
        
        # Convert DataFrame to a readable format
        issues_list = []
        for _, row in df.iterrows():
            issues_list.append({
                'key': row['key'],
                'summary': row['summary'],
                'status': row['status'],
                'assignee': row['assignee'],
                'priority': row['priority'],
                'issue_type': row['issue_type'],
                'created': row['created'],
                'updated': row['updated']
            })
        
        result = {
            'total_issues': len(issues_list),
            'issues': issues_list
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in get_all_issues: {e}")
        return f"Error retrieving all issues: {str(e)}"

@tool
def get_all_issues_for_analysis() -> str:
    """
    Retrieve all accessible Jira issues for analysis purposes.
    
    Returns:
        JSON string containing all issues data with summary statistics
    """
    if not jira_client:
        return "Error: Jira client not initialized. Please check your credentials."
    
    try:
        df = jira_client.get_all_issues(limit=200)  # Increased limit for analysis
        
        if df.empty:
            return "No issues found for analysis."
        
        # Generate summary statistics
        status_counts = df['status'].value_counts().to_dict()
        priority_counts = df['priority'].value_counts().to_dict()
        assignee_counts = df['assignee'].value_counts().to_dict()
        issue_type_counts = df['issue_type'].value_counts().to_dict()
        
        # Get recent issues
        df_sorted = df.sort_values('created', ascending=False)
        recent_issues = []
        for _, row in df_sorted.head(10).iterrows():
            recent_issues.append({
                'key': row['key'],
                'summary': row['summary'],
                'status': row['status'],
                'assignee': row['assignee'],
                'created': row['created']
            })
        
        # Analyze labels if available
        all_labels = []
        for labels in df['labels']:
            if isinstance(labels, list):
                all_labels.extend(labels)
        
        label_counts = {}
        for label in all_labels:
            label_counts[label] = label_counts.get(label, 0) + 1
        
        # Sort label counts
        sorted_labels = dict(sorted(label_counts.items(), key=lambda x: x[1], reverse=True))
        
        analysis_result = {
            'total_issues': len(df),
            'summary_statistics': {
                'status_distribution': status_counts,
                'priority_distribution': priority_counts,
                'assignee_distribution': dict(list(assignee_counts.items())[:10]),  # Top 10 assignees
                'issue_type_distribution': issue_type_counts,
                'top_labels': dict(list(sorted_labels.items())[:10])  # Top 10 labels
            },
            'recent_issues': recent_issues,
            'insights': {
                'most_common_status': max(status_counts, key=status_counts.get),
                'most_common_priority': max(priority_counts, key=priority_counts.get),
                'most_active_assignee': max(assignee_counts, key=assignee_counts.get),
                'total_labels_used': len(sorted_labels)
            }
        }
        
        return json.dumps(analysis_result, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in get_all_issues_for_analysis: {e}")
        return f"Error retrieving issues for analysis: {str(e)}"

@tool
def search_issues_by_jql(jql_query: str) -> str:
    """
    Search Jira issues using JQL (Jira Query Language).
    
    Args:
        jql_query: JQL query string
        
    Returns:
        JSON string containing search results
    """
    if not jira_client:
        return "Error: Jira client not initialized. Please check your credentials."
    
    try:
        df = jira_client.search_issues(jql_query)
        
        if df.empty:
            return f"No issues found for JQL query: {jql_query}"
        
        # Convert results to readable format
        search_results = []
        for _, row in df.iterrows():
            search_results.append({
                'key': row['key'],
                'summary': row['summary'],
                'status': row['status'],
                'assignee': row['assignee'],
                'priority': row['priority'],
                'issue_type': row['issue_type']
            })
        
        result = {
            'jql_query': jql_query,
            'total_results': len(search_results),
            'issues': search_results
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in search_issues_by_jql: {e}")
        return f"Error searching issues with JQL: {str(e)}"

@tool
def get_project_summary() -> str:
    """
    Get summary information about accessible Jira projects.
    
    Returns:
        JSON string containing project information
    """
    if not jira_client:
        return "Error: Jira client not initialized. Please check your credentials."
    
    try:
        projects = jira_client.get_project_info()
        
        project_summary = {
            'total_projects': len(projects),
            'projects': projects
        }
        
        return json.dumps(project_summary, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in get_project_summary: {e}")
        return f"Error retrieving project information: {str(e)}"

# List of all available tools for easy import
JIRA_TOOLS = [
    get_issues_by_status,
    get_issue_details,
    get_all_issues,
    get_all_issues_for_analysis,
    search_issues_by_jql,
    get_project_summary
]
