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
        
        # Main dashboard content
        analytics_data = st.session_state.analytics_data
        
        # Summary cards at the top
        self._render_summary_cards(analytics_data)
        
        # Charts section
        self._render_charts_section(analytics_data)
        
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
            
            # Analytics options
            st.subheader("🔬 Analytics Options")
            
            enable_sentiment = st.checkbox("Enable Sentiment Analysis", value=True)
            enable_predictions = st.checkbox("Enable Predictive Analytics", value=True)
            enable_bottlenecks = st.checkbox("Enable Bottleneck Detection", value=True)
            
            # Max results
            max_results = st.slider("Max Issues to Analyze", 10, 200, 50)
            
            # Load analytics button
            if st.button("🔄 Load Analytics", type="primary"):
                self._load_analytics_data(
                    project_key=project_key if project_key else None,
                    start_date=start_date,
                    end_date=end_date,
                    max_results=max_results,
                    enable_sentiment=enable_sentiment,
                    enable_predictions=enable_predictions,
                    enable_bottlenecks=enable_bottlenecks
                )
            
            # Auto-refresh option
            st.subheader("🔄 Auto Refresh")
            auto_refresh = st.checkbox("Enable auto-refresh (5 min)")
            if auto_refresh:
                st.rerun()  # This will cause the app to refresh periodically
        
        # Store project key in session state (from environment)
        st.session_state.project_key = project_key
    
    def _load_analytics_data(self, project_key=None, start_date=None, end_date=None, 
                           max_results=50, enable_sentiment=True, enable_predictions=True, 
                           enable_bottlenecks=True):
        """Load analytics data from Jira."""
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
                
                # Default to recent issues if no project specified
                if not jql_parts:
                    jql_parts.append("created >= -30d")
                
                jql = " AND ".join(jql_parts)
                
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
                st.session_state.issues_analyzed = len(issues)
                st.session_state.last_updated = datetime.now()
                
                logger.info(f"✅ Analytics completed for {len(issues)} issues")
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
        tab_names = ["Overview", "Time Analysis", "Team Performance", "Advanced Analytics"]
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
        
        # Time Analysis tab
        with tabs[1]:
            st.markdown("#### ⏰ Time Patterns & Trends")
            
            if 'hourly_pattern' in charts:
                st.plotly_chart(charts['hourly_pattern'], use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if 'daily_pattern' in charts:
                    st.plotly_chart(charts['daily_pattern'], use_container_width=True)
            
            with col2:
                if 'resolution_priority' in charts:
                    st.plotly_chart(charts['resolution_priority'], use_container_width=True)
            
            if 'monthly_trend' in charts:
                st.plotly_chart(charts['monthly_trend'], use_container_width=True)
        
        # Team Performance tab
        with tabs[2]:
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
        
        # Advanced Analytics tab
        with tabs[3]:
            st.markdown("#### 🔮 AI-Powered Insights")
            
            col1, col2 = st.columns(2)
            with col1:
                if 'bottleneck_severity' in charts:
                    st.plotly_chart(charts['bottleneck_severity'], use_container_width=True)
                if 'potential_blockers' in charts:
                    st.plotly_chart(charts['potential_blockers'], use_container_width=True)
            
            with col2:
                if 'bottleneck_types' in charts:
                    st.plotly_chart(charts['bottleneck_types'], use_container_width=True)
                if 'feature_importance' in charts:
                    st.plotly_chart(charts['feature_importance'], use_container_width=True)
    
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
