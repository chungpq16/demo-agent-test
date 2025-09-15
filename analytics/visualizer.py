"""
Jira Analytics Visualization Engine
Creates beautiful charts and visualizations for analytics data.
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

from logger import get_logger

logger = get_logger()


class AnalyticsVisualizer:
    """Creates visualizations for Jira analytics data."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.colors = {
            'primary': '#1f77b4',
            'success': '#2ca02c', 
            'warning': '#ff7f0e',
            'danger': '#d62728',
            'info': '#17a2b8',
            'secondary': '#6c757d'
        }
        logger.info("📊 Analytics Visualizer initialized")
    
    def create_dashboard_charts(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create all dashboard charts from analytics data.
        
        Args:
            analytics_data: Output from JiraAnalyticsEngine
            
        Returns:
            Dictionary of Plotly figures
        """
        logger.info("🎨 Creating dashboard visualizations")
        
        charts = {}
        
        try:
            # Basic metrics charts
            if 'basic_metrics' in analytics_data:
                charts.update(self._create_basic_metric_charts(analytics_data['basic_metrics']))
            
            # Time analysis charts
            if 'time_analysis' in analytics_data:
                charts.update(self._create_time_analysis_charts(analytics_data['time_analysis']))
            
            # Team performance charts
            if 'team_performance' in analytics_data:
                charts.update(self._create_team_performance_charts(analytics_data['team_performance']))
            
            # Sentiment analysis charts
            if 'sentiment_analysis' in analytics_data:
                charts.update(self._create_sentiment_charts(analytics_data['sentiment_analysis']))
            
            # Bottleneck visualization
            if 'bottleneck_detection' in analytics_data:
                charts.update(self._create_bottleneck_charts(analytics_data['bottleneck_detection']))
            
            # Predictive insights
            if 'predictive_insights' in analytics_data:
                charts.update(self._create_predictive_charts(analytics_data['predictive_insights']))
            
            # Workload distribution
            if 'workload_distribution' in analytics_data:
                charts.update(self._create_workload_charts(analytics_data['workload_distribution']))
            
            logger.info(f"✅ Created {len(charts)} visualization charts")
            return charts
            
        except Exception as e:
            logger.error(f"❌ Error creating charts: {str(e)}")
            return {"error": f"Chart creation failed: {str(e)}"}
    
    def _create_basic_metric_charts(self, basic_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic metrics visualizations."""
        charts = {}
        
        # Status distribution pie chart
        if 'status_distribution' in basic_metrics:
            status_data = basic_metrics['status_distribution']
            fig_status = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title="📊 Issue Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            charts['status_pie'] = fig_status
        
        # Priority distribution bar chart
        if 'priority_distribution' in basic_metrics:
            priority_data = basic_metrics['priority_distribution']
            priority_order = ['Low', 'Medium', 'High', 'Critical', 'Urgent']
            # Order the data according to priority
            ordered_priorities = {}
            for p in priority_order:
                if p in priority_data:
                    ordered_priorities[p] = priority_data[p]
            # Add any remaining priorities not in the standard order
            for k, v in priority_data.items():
                if k not in ordered_priorities:
                    ordered_priorities[k] = v
            
            fig_priority = px.bar(
                x=list(ordered_priorities.keys()),
                y=list(ordered_priorities.values()),
                title="⚡ Priority Distribution",
                labels={'x': 'Priority', 'y': 'Number of Issues'},
                color=list(ordered_priorities.keys()),
                color_discrete_sequence=['#28a745', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1']
            )
            charts['priority_bar'] = fig_priority
        
        # Issue type distribution
        if 'type_distribution' in basic_metrics and basic_metrics['type_distribution']:
            type_data = basic_metrics['type_distribution']
            fig_type = px.bar(
                x=list(type_data.keys()),
                y=list(type_data.values()),
                title="🏷️ Issue Type Distribution",
                labels={'x': 'Issue Type', 'y': 'Count'}
            )
            charts['type_bar'] = fig_type
        
        return charts
    
    def _create_time_analysis_charts(self, time_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create time analysis visualizations."""
        charts = {}
        
        # Hourly creation pattern
        if 'hourly_creation_pattern' in time_analysis:
            hourly_data = time_analysis['hourly_creation_pattern']
            fig_hourly = px.line(
                x=list(hourly_data.keys()),
                y=list(hourly_data.values()),
                title="🕐 Issue Creation by Hour of Day",
                labels={'x': 'Hour', 'y': 'Issues Created'},
                markers=True
            )
            fig_hourly.update_layout(xaxis=dict(tickmode='linear'))
            charts['hourly_pattern'] = fig_hourly
        
        # Daily creation pattern
        if 'daily_creation_pattern' in time_analysis:
            daily_data = time_analysis['daily_creation_pattern']
            fig_daily = px.bar(
                x=list(daily_data.keys()),
                y=list(daily_data.values()),
                title="📅 Issue Creation by Day of Week",
                labels={'x': 'Day', 'y': 'Issues Created'},
                color=list(daily_data.values()),
                color_continuous_scale='blues'
            )
            charts['daily_pattern'] = fig_daily
        
        # Monthly trend
        if 'monthly_creation_trend' in time_analysis:
            monthly_data = time_analysis['monthly_creation_trend']
            fig_monthly = px.line(
                x=list(monthly_data.keys()),
                y=list(monthly_data.values()),
                title="📈 Monthly Issue Creation Trend",
                labels={'x': 'Month', 'y': 'Issues Created'},
                markers=True
            )
            charts['monthly_trend'] = fig_monthly
        
        # Resolution time analysis
        if 'resolution_time_analysis' in time_analysis and time_analysis['resolution_time_analysis']:
            res_analysis = time_analysis['resolution_time_analysis']
            
            # Resolution by priority
            if 'avg_by_priority' in res_analysis:
                priority_res = res_analysis['avg_by_priority']
                fig_res_priority = px.bar(
                    x=list(priority_res.keys()),
                    y=list(priority_res.values()),
                    title="⏱️ Average Resolution Time by Priority",
                    labels={'x': 'Priority', 'y': 'Days to Resolve'},
                    color=list(priority_res.keys()),
                    color_discrete_sequence=['#28a745', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1']
                )
                charts['resolution_priority'] = fig_res_priority
        
        return charts
    
    def _create_team_performance_charts(self, team_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Create team performance visualizations."""
        charts = {}
        
        if 'individual_metrics' in team_performance:
            metrics = team_performance['individual_metrics']
            
            if metrics:
                # Workload distribution
                assignees = list(metrics.keys())
                workload_scores = [metrics[a]['workload_score'] for a in assignees]
                
                fig_workload = px.bar(
                    x=assignees,
                    y=workload_scores,
                    title="👥 Team Workload Distribution",
                    labels={'x': 'Team Member', 'y': 'Workload Score'},
                    color=workload_scores,
                    color_continuous_scale='Reds'
                )
                fig_workload.update_layout(xaxis_tickangle=-45)
                charts['team_workload'] = fig_workload
                
                # Average resolution time by assignee
                avg_resolution = [metrics[a]['avg_resolution_days'] for a in assignees]
                if any(r > 0 for r in avg_resolution):  # Only show if we have resolution data
                    fig_resolution = px.bar(
                        x=assignees,
                        y=avg_resolution,
                        title="⏱️ Average Resolution Time by Team Member",
                        labels={'x': 'Team Member', 'y': 'Days'},
                        color=avg_resolution,
                        color_continuous_scale='RdYlGn_r'
                    )
                    fig_resolution.update_layout(xaxis_tickangle=-45)
                    charts['team_resolution'] = fig_resolution
        
        return charts
    
    def _create_sentiment_charts(self, sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create sentiment analysis visualizations."""
        charts = {}
        
        # Sentiment distribution
        if 'sentiment_distribution' in sentiment_analysis:
            sentiment_data = sentiment_analysis['sentiment_distribution']
            colors = {'Positive': '#28a745', 'Neutral': '#6c757d', 'Negative': '#dc3545'}
            
            fig_sentiment = px.pie(
                values=list(sentiment_data.values()),
                names=list(sentiment_data.keys()),
                title="😊 Team Sentiment Analysis",
                color=list(sentiment_data.keys()),
                color_discrete_map=colors
            )
            fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
            charts['sentiment_pie'] = fig_sentiment
        
        # Team mood by assignee
        if 'assignee_sentiment' in sentiment_analysis:
            assignee_sentiment = sentiment_analysis['assignee_sentiment']
            if assignee_sentiment:
                assignees = list(assignee_sentiment.keys())
                sentiments = list(assignee_sentiment.values())
                
                # Color based on sentiment
                colors = ['#28a745' if s > 0.05 else '#dc3545' if s < -0.05 else '#6c757d' for s in sentiments]
                
                fig_team_sentiment = go.Figure(data=go.Bar(
                    x=assignees,
                    y=sentiments,
                    marker_color=colors,
                    text=[f"{s:.3f}" for s in sentiments],
                    textposition='auto'
                ))
                
                fig_team_sentiment.update_layout(
                    title="👥 Team Member Sentiment Scores",
                    xaxis_title="Team Member",
                    yaxis_title="Sentiment Score",
                    xaxis_tickangle=-45
                )
                
                # Add horizontal line at neutral
                fig_team_sentiment.add_hline(y=0, line_dash="dash", line_color="gray")
                
                charts['team_sentiment'] = fig_team_sentiment
        
        return charts
    
    def _create_bottleneck_charts(self, bottleneck_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create bottleneck visualization."""
        charts = {}
        
        if 'bottlenecks_detected' in bottleneck_data:
            bottlenecks = bottleneck_data['bottlenecks_detected']
            
            if bottlenecks:
                # Bottleneck severity distribution
                severities = [b['severity'] for b in bottlenecks]
                severity_counts = {s: severities.count(s) for s in set(severities)}
                
                severity_colors = {
                    'Critical': '#dc3545',
                    'High': '#fd7e14', 
                    'Medium': '#ffc107',
                    'Low': '#28a745'
                }
                
                fig_bottlenecks = px.bar(
                    x=list(severity_counts.keys()),
                    y=list(severity_counts.values()),
                    title="🚧 Bottlenecks by Severity",
                    labels={'x': 'Severity', 'y': 'Count'},
                    color=list(severity_counts.keys()),
                    color_discrete_map=severity_colors
                )
                charts['bottleneck_severity'] = fig_bottlenecks
                
                # Bottleneck types
                types = [b['type'] for b in bottlenecks]
                type_counts = {t: types.count(t) for t in set(types)}
                
                fig_types = px.pie(
                    values=list(type_counts.values()),
                    names=list(type_counts.keys()),
                    title="🔍 Bottleneck Types",
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                charts['bottleneck_types'] = fig_types
        
        return charts
    
    def _create_predictive_charts(self, predictive_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create predictive insights visualizations."""
        charts = {}
        
        if 'potential_blockers' in predictive_data and predictive_data['potential_blockers']:
            blockers = predictive_data['potential_blockers']
            
            # Blocker probability chart
            keys = [b['key'] for b in blockers]
            probabilities = [b.get('blocker_probability', 0) for b in blockers]
            
            fig_blockers = px.bar(
                x=keys,
                y=probabilities,
                title="🔮 Potential Blocker Predictions",
                labels={'x': 'Issue Key', 'y': 'Blocker Probability'},
                color=probabilities,
                color_continuous_scale='Reds'
            )
            fig_blockers.update_layout(xaxis_tickangle=-45)
            charts['potential_blockers'] = fig_blockers
        
        # Feature importance
        if 'feature_importance' in predictive_data:
            importance = predictive_data['feature_importance']
            if importance:
                fig_importance = px.bar(
                    x=list(importance.values()),
                    y=list(importance.keys()),
                    orientation='h',
                    title="🎯 Prediction Feature Importance",
                    labels={'x': 'Importance', 'y': 'Feature'}
                )
                charts['feature_importance'] = fig_importance
        
        return charts
    
    def _create_workload_charts(self, workload_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create workload distribution visualizations."""
        charts = {}
        
        if 'current_workload' in workload_data:
            workload = workload_data['current_workload']
            
            if workload:
                # Remove 'Unassigned' for main chart
                assigned_workload = {k: v for k, v in workload.items() if k != 'Unassigned'}
                
                if assigned_workload:
                    fig_workload = px.bar(
                        x=list(assigned_workload.keys()),
                        y=list(assigned_workload.values()),
                        title="⚖️ Current Workload Distribution",
                        labels={'x': 'Team Member', 'y': 'Open Issues'},
                        color=list(assigned_workload.values()),
                        color_continuous_scale='RdYlBu_r'
                    )
                    
                    # Add average line
                    avg_workload = workload_data.get('avg_workload_per_person', 0)
                    if avg_workload > 0:
                        fig_workload.add_hline(
                            y=avg_workload, 
                            line_dash="dash", 
                            line_color="red",
                            annotation_text=f"Average: {avg_workload:.1f}"
                        )
                    
                    fig_workload.update_layout(xaxis_tickangle=-45)
                    charts['workload_distribution'] = fig_workload
        
        return charts
    
    def create_summary_cards(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create summary cards for key metrics."""
        cards = []
        
        try:
            # Basic metrics cards
            if 'basic_metrics' in analytics_data:
                basic = analytics_data['basic_metrics']
                
                cards.append({
                    'title': 'Total Issues',
                    'value': basic.get('total_issues', 0),
                    'icon': '📊',
                    'color': 'primary'
                })
                
                cards.append({
                    'title': 'Avg Resolution Time',
                    'value': f"{basic.get('avg_resolution_days', 0):.1f} days",
                    'icon': '⏱️',
                    'color': 'info'
                })
                
                cards.append({
                    'title': 'Overdue Issues',
                    'value': basic.get('overdue_count', 0),
                    'icon': '⚠️',
                    'color': 'warning' if basic.get('overdue_count', 0) > 0 else 'success'
                })
            
            # Team performance cards
            if 'team_performance' in analytics_data:
                team = analytics_data['team_performance']
                
                cards.append({
                    'title': 'Team Size',
                    'value': team.get('team_size', 0),
                    'icon': '👥',
                    'color': 'secondary'
                })
                
                cards.append({
                    'title': 'Monthly Velocity',
                    'value': team.get('monthly_velocity', 0),
                    'icon': '🚀',
                    'color': 'success'
                })
            
            # Sentiment cards
            if 'sentiment_analysis' in analytics_data:
                sentiment = analytics_data['sentiment_analysis']
                
                mood = sentiment.get('team_mood', 'Neutral')
                mood_color = 'success' if mood == 'Good' else 'warning' if mood == 'Neutral' else 'danger'
                
                cards.append({
                    'title': 'Team Mood',
                    'value': mood,
                    'icon': '😊' if mood == 'Good' else '😐' if mood == 'Neutral' else '😟',
                    'color': mood_color
                })
            
            # Bottleneck cards
            if 'bottleneck_detection' in analytics_data:
                bottlenecks = analytics_data['bottleneck_detection']
                
                critical_count = bottlenecks.get('critical_count', 0)
                cards.append({
                    'title': 'Critical Bottlenecks',
                    'value': critical_count,
                    'icon': '🚧',
                    'color': 'danger' if critical_count > 0 else 'success'
                })
            
            logger.info(f"📋 Created {len(cards)} summary cards")
            return cards
            
        except Exception as e:
            logger.error(f"❌ Error creating summary cards: {str(e)}")
            return []
