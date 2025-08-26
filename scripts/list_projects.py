#!/usr/bin/env python3
"""
List all available projects in Jira to find the correct project key.
"""

import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.jira_client import JiraClient
from src.tools.jira_tools import initialize_tools, get_project_summary
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🔍 Listing Available Jira Projects...")
    
    try:
        # Initialize client without project scoping
        client = JiraClient()
        # Temporarily remove project scoping to see all projects
        client.project_key = None
        initialize_tools(client)
        
        # Get all projects
        result = get_project_summary.invoke({})
        print("\n📊 Available Projects:")
        print("=" * 50)
        
        # Parse and display projects
        projects_data = json.loads(result)
        
        print(f"Total Projects: {projects_data.get('total_projects', 0)}")
        print()
        
        for project in projects_data.get('projects', []):
            print(f"🎯 Project Key: {project.get('key', 'Unknown')}")
            print(f"   Name: {project.get('name', 'Unknown')}")
            print(f"   Type: {project.get('project_type', 'Unknown')}")
            print(f"   Lead: {project.get('lead', 'Unknown')}")
            print()
            
        print("💡 Use one of the above project keys in your JIRA_PROJECT_KEY environment variable")
            
    except Exception as e:
        print(f"❌ Error listing projects: {e}")

if __name__ == "__main__":
    main()
