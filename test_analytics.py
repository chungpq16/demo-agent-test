#!/usr/bin/env python3
"""
Simple test for Analytics Dashboard
"""
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analytics import JiraAnalyticsEngine
from analytics.visualizer import AnalyticsVisualizer
from logger import get_logger

logger = get_logger()

st.set_page_config(page_title="Analytics Test", layout="wide")

st.title("🧪 Analytics Dashboard Test")

# Sample issue data
sample_issues = [
    {
        'key': 'TEST-1',
        'summary': 'First test issue',
        'status': 'Open',
        'priority': 'High',
        'assignee': 'john.doe@example.com',
        'created': '2025-09-01T10:00:00.000+0000',
        'updated': '2025-09-05T10:00:00.000+0000'
    },
    {
        'key': 'TEST-2', 
        'summary': 'Second test issue',
        'status': 'In Progress',
        'priority': 'Medium',
        'assignee': 'jane.smith@example.com',
        'created': '2025-09-02T10:00:00.000+0000',
        'updated': '2025-09-10T10:00:00.000+0000'
    },
    {
        'key': 'TEST-3',
        'summary': 'Third test issue',
        'status': 'Closed',
        'priority': 'Low',
        'assignee': 'bob.wilson@example.com',
        'created': '2025-09-03T10:00:00.000+0000',
        'updated': '2025-09-15T10:00:00.000+0000'
    }
]

if st.button("🔄 Run Analytics Test"):
    with st.spinner("Running analytics..."):
        try:
            # Initialize analytics engine
            engine = JiraAnalyticsEngine()
            visualizer = AnalyticsVisualizer()
            
            # Run analytics
            st.info("Running analytics on sample data...")
            analytics_data = engine.analyze_issues(sample_issues)
            
            st.success("✅ Analytics completed!")
            
            # Show results
            st.subheader("📊 Analytics Results")
            
            # Basic metrics
            if 'basic_metrics' in analytics_data:
                basic = analytics_data['basic_metrics']
                st.write("**Basic Metrics:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Issues", basic.get('total_issues', 0))
                with col2:
                    st.metric("Avg Resolution Days", f"{basic.get('avg_resolution_days', 0):.1f}")
                with col3:
                    st.metric("Overdue Count", basic.get('overdue_count', 0))
                
                st.write("**Status Distribution:**", basic.get('status_distribution', {}))
                st.write("**Priority Distribution:**", basic.get('priority_distribution', {}))
            
            # Create summary cards
            st.subheader("📋 Summary Cards")
            cards = visualizer.create_summary_cards(analytics_data)
            if cards:
                cols = st.columns(len(cards))
                for i, card in enumerate(cards):
                    with cols[i]:
                        st.metric(
                            label=f"{card['icon']} {card['title']}",
                            value=card['value']
                        )
            
            # Show raw data
            with st.expander("🔍 Raw Analytics Data"):
                st.json(analytics_data)
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.code(str(e))
            import traceback
            st.code(traceback.format_exc())

st.subheader("📋 Sample Data")
st.dataframe(sample_issues)
