"""
Streamlit Analytics Dashboard for Smart Jira Analytics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

from analytics import JiraAnalyticsEngine
from analytics.visualizer import AnalyticsVisualizer
from jira_client import JiraClient
from logger import get_logger

logger = get_logger()


class AnalyticsDashboard:
    """Main analytics dashboard class."""
    
    def __init__(self):
        """Initialize the dashboard."""
        self.analytics_engine = JiraAnalyticsEngine()
        self.visualizer = AnalyticsVisualizer()
        self.jira_client = JiraClient()
        logger.info("📊 Analytics Dashboard initialized")
    
    def render_dashboard(self):
        """Render the complete analytics dashboard."""
        st.title("🚀 Smart Jira Analytics Dashboard")
        st.markdown("---")
        
        # Sidebar controls
        self._render_sidebar()
        
        # Check if we have data to show
        if 'analytics_data' not in st.session_state:
            st.info("👆 Configure your analytics settings in the sidebar and click 'Load Analytics' to begin!")
            return
        
        # Show applied filters if available
        if 'applied_filters' in st.session_state:
            filters = st.session_state.applied_filters
            filter_info = []
            
            if filters.get('status'):
                filter_info.append(f"**Status**: {filters['status']}")
            if filters.get('priority'): 
                filter_info.append(f"**Priority**: {filters['priority']}")
            if filters.get('date_range'):
                filter_info.append(f"**Date Range**: {filters['date_range']}")
            
            if filter_info:
                st.info(f"📊 **Active Filters**: {' | '.join(filter_info)}")
        
        # Main dashboard content
        analytics_data = st.session_state.analytics_data
        
        # Summary cards at the top
        self._render_summary_cards(analytics_data)
        
        # Charts section
        self._render_charts_section(analytics_data)
        
        # Issues table section
        self._render_issues_table(analytics_data)
        
        # AI Insights section
        self._render_ai_insights(analytics_data)
        
        # Raw data section (collapsible)
        self._render_raw_data_section(analytics_data)
    
    def _render_sidebar(self):
        """Render sidebar with controls and filters."""
        with st.sidebar:
            st.header("🎛️ Analytics Controls")
            
            # Get project key from environment
            project_key = os.getenv('JIRA_PROJECT', '').strip()
            if project_key:
                st.info(f"📊 Analyzing Project: **{project_key}**")
            else:
                st.warning("⚠️ No project key configured in environment variables")
            
            # Date range filter
            st.subheader("📅 Date Range")
            date_range = st.selectbox(
                "Select time period",
                ["Last 7 days", "Last 30 days", "Last 90 days", "Last 6 months", "Custom range"]
            )
            
            # Custom date range
            if date_range == "Custom range":
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("From", datetime.now() - timedelta(days=30))
                with col2:
                    end_date = st.date_input("To", datetime.now())
            else:
                # Calculate date range
                days_map = {
                    "Last 7 days": 7,
                    "Last 30 days": 30, 
                    "Last 90 days": 90,
                    "Last 6 months": 180
                }
                days = days_map.get(date_range, 30)
                start_date = datetime.now() - timedelta(days=days)
                end_date = datetime.now()
            
            # Max results
            max_results = st.slider("Max Issues to Analyze", 10, 200, 50)
            
            # Status filter
            st.subheader("🎯 Filters")
            status_options = ["All Statuses", "Open", "In Progress", "Done", "Closed", "Resolved", "TO-DO", "To Do"]
            selected_status = st.selectbox("Status", status_options, index=0)
            
            # Priority filter
            priority_options = ["All Priorities", "Critical", "High", "Medium", "Low", "Blocker", "Major", "Minor", "Trivial"]
            selected_priority = st.selectbox("Priority", priority_options, index=0)
            
            # Load analytics button
            if st.button("🔄 Load Analytics", type="primary"):
                self._load_analytics_data(
                    project_key=project_key if project_key else None,
                    start_date=start_date,
                    end_date=end_date,
                    max_results=max_results,
                    status_filter=selected_status if selected_status != "All Statuses" else None,
                    priority_filter=selected_priority if selected_priority != "All Priorities" else None,
                    enable_sentiment=True,
                    enable_predictions=True,
                    enable_bottlenecks=True
                )
        
        # Store project key in session state (from environment)
        st.session_state.project_key = project_key
    
    def _load_analytics_data(self, project_key=None, start_date=None, end_date=None, 
                           max_results=50, status_filter=None, priority_filter=None,
                           enable_sentiment=True, enable_predictions=True, 
                           enable_bottlenecks=True):
        """Load analytics data from Jira with filters."""
        with st.spinner("🔍 Fetching Jira data and running analytics..."):
            try:
                # Build JQL query
                jql_parts = []
                
                if project_key:
                    jql_parts.append(f"project = {project_key}")
                
                # Add date filter if specified
                if start_date:
                    jql_parts.append(f"created >= '{start_date.strftime('%Y-%m-%d')}'")
                if end_date:
                    jql_parts.append(f"created <= '{end_date.strftime('%Y-%m-%d')}'")
                
                # Add status filter if specified
                if status_filter:
                    # Handle status name variations
                    status_mapping = {
                        'to-do': 'TO-DO',
                        'todo': 'TO-DO',
                        'to do': 'To Do'
                    }
                    normalized_status = status_mapping.get(status_filter.lower(), status_filter)
                    jql_parts.append(f"status = '{normalized_status}'")
                
                # Add priority filter if specified
                if priority_filter:
                    jql_parts.append(f"priority = {priority_filter}")
                
                # Default to recent issues if no project specified
                if not jql_parts:
                    jql_parts.append("created >= -30d")
                
                jql = " AND ".join(jql_parts)
                jql += " ORDER BY created DESC"
                
                logger.info(f"🔍 Loading analytics with JQL: {jql}")
                
                # Get issues from Jira using the client directly
                issues = self.jira_client.search_issues(jql, max_results=max_results)
                
                if not issues:
                    st.error("❌ No issues found with the specified criteria.")
                    return
                
                st.success(f"✅ Found {len(issues)} issues. Running analytics...")
                
                # Run analytics
                analytics_options = {
                    'enable_sentiment_analysis': enable_sentiment,
                    'enable_predictive_analytics': enable_predictions,
                    'enable_bottleneck_detection': enable_bottlenecks
                }
                
                analytics_data = self.analytics_engine.analyze_issues(issues, analytics_options)
                
                # Store in session state
                st.session_state.analytics_data = analytics_data
                st.session_state.raw_issues = issues  # Store raw issues for table display
                st.session_state.issues_analyzed = len(issues)
                st.session_state.last_updated = datetime.now()
                st.session_state.applied_filters = {
                    'status': status_filter,
                    'priority': priority_filter,
                    'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}" if start_date and end_date else None
                }
                
                logger.info(f"✅ Analytics completed for {len(issues)} issues with filters - Status: {status_filter}, Priority: {priority_filter}")
                st.rerun()  # Refresh to show the results
                
            except Exception as e:
                logger.error(f"❌ Error loading analytics: {str(e)}")
                st.error(f"❌ Error loading analytics: {str(e)}")
    
    def _render_summary_cards(self, analytics_data: Dict[str, Any]):
        """Render summary metric cards."""
        st.subheader("📊 Key Metrics Overview")
        
        # Get summary cards from visualizer
        cards = self.visualizer.create_summary_cards(analytics_data)
        
        if not cards:
            st.warning("⚠️ No summary data available.")
            return
        
        # Display cards in columns
        cols = st.columns(len(cards))
        for i, card in enumerate(cards):
            with cols[i]:
                # Create colored card using metric
                delta = None
                if 'delta' in card:
                    delta = card['delta']
                
                st.metric(
                    label=f"{card['icon']} {card['title']}",
                    value=card['value'],
                    delta=delta
                )
    
    def _render_charts_section(self, analytics_data: Dict[str, Any]):
        """Render all charts and visualizations."""
        st.subheader("📈 Analytics Visualizations")
        
        # Get charts from visualizer
        charts = self.visualizer.create_dashboard_charts(analytics_data)
        
        if not charts or 'error' in charts:
            st.warning("⚠️ No chart data available or error creating charts.")
            if 'error' in charts:
                st.error(charts['error'])
            return
        
        # Organize charts in tabs
        tab_names = ["Overview", "Team Performance"]
        tabs = st.tabs(tab_names)
        
        # Overview tab
        with tabs[0]:
            st.markdown("#### 🎯 Status & Priority Overview")
            col1, col2 = st.columns(2)
            
            with col1:
                if 'status_pie' in charts:
                    st.plotly_chart(charts['status_pie'], use_container_width=True)
            
            with col2:
                if 'priority_bar' in charts:
                    st.plotly_chart(charts['priority_bar'], use_container_width=True)
            
            if 'type_bar' in charts:
                st.plotly_chart(charts['type_bar'], use_container_width=True)
        
        # Team Performance tab
        with tabs[1]:
            st.markdown("#### 👥 Team Analytics")
            
            col1, col2 = st.columns(2)
            with col1:
                if 'team_workload' in charts:
                    st.plotly_chart(charts['team_workload'], use_container_width=True)
                if 'workload_distribution' in charts:
                    st.plotly_chart(charts['workload_distribution'], use_container_width=True)
            
            with col2:
                if 'team_resolution' in charts:
                    st.plotly_chart(charts['team_resolution'], use_container_width=True)
                if 'sentiment_pie' in charts:
                    st.plotly_chart(charts['sentiment_pie'], use_container_width=True)
            
            if 'team_sentiment' in charts:
                st.plotly_chart(charts['team_sentiment'], use_container_width=True)
    
    def _render_ai_insights(self, analytics_data: Dict[str, Any]):
        """Render AI-generated insights and recommendations."""
        st.subheader("🤖 AI Insights & Recommendations")
        
        # AI insights from analytics data
        insights = []
        
        # Extract insights from different sections
        if 'ai_insights' in analytics_data:
            ai_insights = analytics_data['ai_insights']
            for insight in ai_insights.get('patterns', []):
                insights.append({
                    'type': 'Pattern',
                    'icon': '🔍',
                    'message': insight
                })
            
            for insight in ai_insights.get('recommendations', []):
                insights.append({
                    'type': 'Recommendation', 
                    'icon': '💡',
                    'message': insight
                })
            
            for insight in ai_insights.get('alerts', []):
                insights.append({
                    'type': 'Alert',
                    'icon': '⚠️', 
                    'message': insight
                })
        
        # Display insights
        if insights:
            for insight in insights:
                if insight['type'] == 'Alert':
                    st.warning(f"{insight['icon']} **{insight['type']}**: {insight['message']}")
                elif insight['type'] == 'Recommendation':
                    st.info(f"{insight['icon']} **{insight['type']}**: {insight['message']}")
                else:
                    st.success(f"{insight['icon']} **{insight['type']}**: {insight['message']}")
        else:
            # Generate basic insights from data
            self._generate_basic_insights(analytics_data)
    
    def _generate_basic_insights(self, analytics_data: Dict[str, Any]):
        """Generate basic insights from analytics data."""
        insights = []
        
        # Basic metrics insights
        if 'basic_metrics' in analytics_data:
            basic = analytics_data['basic_metrics']
            
            overdue_count = basic.get('overdue_count', 0)
            total_issues = basic.get('total_issues', 0)
            
            if overdue_count > 0 and total_issues > 0:
                overdue_pct = (overdue_count / total_issues) * 100
                if overdue_pct > 20:
                    st.warning(f"⚠️ **Alert**: High overdue rate - {overdue_pct:.1f}% of issues are overdue")
                else:
                    st.info(f"📊 **Insight**: {overdue_pct:.1f}% of issues are currently overdue")
        
        # Team performance insights
        if 'team_performance' in analytics_data:
            team = analytics_data['team_performance']
            
            monthly_velocity = team.get('monthly_velocity', 0)
            if monthly_velocity > 0:
                st.success(f"🚀 **Performance**: Team resolved {monthly_velocity} issues this month")
        
        # Sentiment insights
        if 'sentiment_analysis' in analytics_data:
            sentiment = analytics_data['sentiment_analysis']
            
            team_mood = sentiment.get('team_mood', 'Neutral')
            if team_mood == 'Good':
                st.success("😊 **Team Mood**: Positive sentiment detected in team communications")
            elif team_mood == 'Poor':
                st.warning("😟 **Team Mood**: Negative sentiment detected - consider team check-in")
    
    def _render_issues_table(self, analytics_data: Dict[str, Any]):
        """Render table showing all issues used in analytics."""
        st.subheader("📄 Issues Data Table")
        st.markdown("*Reference table showing all Jira issues used for this analytics dashboard*")
        
        if 'raw_issues' not in st.session_state or not st.session_state.raw_issues:
            st.warning("⚠️ No issues data available for display.")
            return
        
        issues = st.session_state.raw_issues
        
        # Convert issues to DataFrame for display
        issues_data = []
        for issue in issues:
            # Extract key information from each issue
            issue_data = {
                'Key': issue.get('key', 'N/A'),
                'Summary': issue.get('summary', 'N/A')[:60] + ('...' if len(issue.get('summary', '')) > 60 else ''),
                'Status': issue.get('status', 'N/A'),
                'Priority': issue.get('priority', 'N/A'),
                'Issue Type': issue.get('issuetype', 'N/A'),
                'Assignee': issue.get('assignee', 'Unassigned'),
                'Created': issue.get('created', 'N/A')[:10] if issue.get('created') else 'N/A',
                'Updated': issue.get('updated', 'N/A')[:10] if issue.get('updated') else 'N/A'
            }
            issues_data.append(issue_data)
        
        if issues_data:
            df = pd.DataFrame(issues_data)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Issues", len(df))
            with col2:
                unique_statuses = df['Status'].nunique()
                st.metric("Unique Statuses", unique_statuses)
            with col3:
                assigned_count = len(df[df['Assignee'] != 'Unassigned'])
                st.metric("Assigned Issues", assigned_count)
            
            # Display the table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("⚠️ No issue data could be processed for the table.")

    def _render_raw_data_section(self, analytics_data: Dict[str, Any]):
        """Render raw analytics data in an expandable section."""
        with st.expander("📋 Raw Analytics Data", expanded=False):
            st.json(analytics_data)
        
        # Show last updated info
        if 'last_updated' in st.session_state:
            last_updated = st.session_state.last_updated
            issues_count = st.session_state.get('issues_analyzed', 0)
            
            st.caption(f"Last updated: {last_updated.strftime('%Y-%m-%d %H:%M:%S')} | Issues analyzed: {issues_count}")


def render_analytics_dashboard():
    """Main function to render the analytics dashboard."""
    dashboard = AnalyticsDashboard()
    dashboard.render_dashboard()


if __name__ == "__main__":
    render_analytics_dashboard()
