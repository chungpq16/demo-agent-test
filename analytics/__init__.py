"""
Jira Analytics Engine
AI-powered analytics and insights for Jira data.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from textblob import TextBlob
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

from logger import get_logger

logger = get_logger()


class JiraAnalyticsEngine:
    """AI-powered analytics engine for Jira data analysis."""
    
    def __init__(self):
        """Initialize the analytics engine."""
        self.scaler = StandardScaler()
        self.resolution_model = None
        self.anomaly_detector = None
        logger.info("🧠 Analytics Engine initialized")
    
    def analyze_issues(self, issues: List[Dict[str, Any]], options: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        Comprehensive analysis of Jira issues.
        
        Args:
            issues: List of Jira issues
            options: Dictionary of analysis options to control which analyses to run
            
        Returns:
            Dictionary containing all analytics results
        """
        if not issues:
            logger.warning("⚠️ No issues provided for analysis")
            return {"error": "No issues to analyze"}
        
        if options is None:
            options = {
                'enable_sentiment_analysis': True,
                'enable_predictive_analytics': True,
                'enable_bottleneck_detection': True
            }

        logger.info(f"🔍 Starting comprehensive analysis of {len(issues)} issues")
        
        df = self._prepare_dataframe(issues)
        
        results = {
            "basic_metrics": self._calculate_basic_metrics(df),
            "time_analysis": self._analyze_time_patterns(df),
            "team_performance": self._analyze_team_performance(df),
            "workload_distribution": self._analyze_workload_distribution(df),
            "trend_analysis": self._analyze_trends(df)
        }
        
        # Conditional analyses based on options
        if options.get('enable_sentiment_analysis', True):
            results["sentiment_analysis"] = self._analyze_sentiment(df)
        
        if options.get('enable_bottleneck_detection', True):
            results["bottleneck_detection"] = self._detect_bottlenecks(df)
        
        if options.get('enable_predictive_analytics', True):
            results["predictive_insights"] = self._predict_potential_blockers(df)
            results["anomaly_detection"] = self._detect_anomalies(df)
        
        logger.info("✅ Comprehensive analysis completed")
        return results
    
    def _prepare_dataframe(self, issues: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare and clean the issues dataframe."""
        df = pd.DataFrame(issues)
        
        # Convert date columns and handle timezones
        date_columns = ['created', 'updated']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
                # Convert to timezone-naive by removing timezone info
                df[col] = df[col].dt.tz_localize(None)
        
        # Calculate resolution time (if issue is resolved)
        if 'created' in df.columns and 'updated' in df.columns:
            df['resolution_days'] = (df['updated'] - df['created']).dt.days
        
        # Add derived features - use timezone-naive datetime.now()
        if 'created' in df.columns:
            now_naive = datetime.now()
            df['age_days'] = (now_naive - df['created']).dt.days
        else:
            df['age_days'] = 0
            
        df['is_overdue'] = df['age_days'] > 30  # Consider issues over 30 days as potentially overdue
        
        # Fill missing values - handle missing columns gracefully
        if 'assignee' in df.columns:
            df['assignee'] = df['assignee'].fillna('Unassigned')
        else:
            df['assignee'] = 'Unassigned'
            
        if 'priority' in df.columns:
            df['priority'] = df['priority'].fillna('Medium')
        else:
            df['priority'] = 'Medium'
            
        if 'description' in df.columns:
            df['description'] = df['description'].fillna('')
        else:
            df['description'] = ''
            
        if 'status' in df.columns:
            df['status'] = df['status'].fillna('Open')
        else:
            df['status'] = 'Open'
        
        logger.debug(f"📊 Prepared dataframe with {len(df)} issues and {len(df.columns)} columns")
        return df
    
    def _calculate_basic_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic project metrics."""
        logger.debug("📈 Calculating basic metrics")
        
        if df.empty:
            return {
                "total_issues": 0,
                "status_distribution": {},
                "priority_distribution": {},
                "type_distribution": {},
                "avg_resolution_days": 0,
                "median_resolution_days": 0,
                "assignee_distribution": {},
                "overdue_count": 0
            }
        
        total_issues = len(df)
        
        # Status distribution
        status_counts = df['status'].value_counts().to_dict() if 'status' in df.columns else {}
        
        # Priority distribution
        priority_counts = df['priority'].value_counts().to_dict() if 'priority' in df.columns else {}
        
        # Issue type distribution
        type_counts = df['issue_type'].value_counts().to_dict() if 'issue_type' in df.columns else {}
        
        # Time metrics - handle missing resolution data
        avg_resolution_days = 0
        median_resolution_days = 0
        if 'resolution_days' in df.columns and df['resolution_days'].notna().any():
            valid_resolution = df['resolution_days'].dropna()
            if not valid_resolution.empty:
                avg_resolution_days = float(valid_resolution.mean())
                median_resolution_days = float(valid_resolution.median())
        
        # Assignee metrics
        assignee_counts = df['assignee'].value_counts().to_dict() if 'assignee' in df.columns else {}
        
        # Overdue issues
        overdue_count = int(df['is_overdue'].sum()) if 'is_overdue' in df.columns else 0
        unassigned_count = assignee_counts.get('Unassigned', 0)
        
        return {
            "total_issues": total_issues,
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "type_distribution": type_counts,
            "avg_resolution_days": round(avg_resolution_days, 1),
            "median_resolution_days": round(median_resolution_days, 1),
            "assignee_distribution": assignee_counts,
            "unassigned_percentage": round((unassigned_count / total_issues) * 100, 1),
            "overdue_count": df['is_overdue'].sum() if 'is_overdue' in df.columns else 0
        }
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze time-based patterns in issue creation and resolution."""
        logger.debug("⏰ Analyzing time patterns")
        
        if 'created' not in df.columns:
            return {"error": "No creation date data available"}
        
        # Creation patterns
        df['created_hour'] = df['created'].dt.hour
        df['created_day_of_week'] = df['created'].dt.dayofweek
        df['created_month'] = df['created'].dt.month
        
        # Daily creation pattern
        hourly_creation = df['created_hour'].value_counts().sort_index().to_dict()
        
        # Weekly pattern
        daily_creation = df['created_day_of_week'].value_counts().sort_index().to_dict()
        day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
                    4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        daily_creation = {day_names[k]: v for k, v in daily_creation.items()}
        
        # Monthly trend
        monthly_creation = df['created_month'].value_counts().sort_index().to_dict()
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        monthly_creation = {month_names[k]: v for k, v in monthly_creation.items()}
        
        # Resolution time analysis
        resolution_analysis = {}
        if 'resolution_days' in df.columns:
            resolved_issues = df[df['resolution_days'].notna()]
            if not resolved_issues.empty:
                resolution_analysis = {
                    "avg_by_priority": resolved_issues.groupby('priority')['resolution_days'].mean().to_dict(),
                    "avg_by_type": resolved_issues.groupby('issue_type')['resolution_days'].mean().to_dict() if 'issue_type' in df.columns else {},
                    "resolution_distribution": resolved_issues['resolution_days'].describe().to_dict()
                }
        
        return {
            "hourly_creation_pattern": hourly_creation,
            "daily_creation_pattern": daily_creation,
            "monthly_creation_trend": monthly_creation,
            "resolution_time_analysis": resolution_analysis,
            "peak_creation_hour": max(hourly_creation, key=hourly_creation.get),
            "peak_creation_day": max(daily_creation, key=daily_creation.get)
        }
    
    def _analyze_team_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze team and individual performance metrics."""
        logger.debug("👥 Analyzing team performance")
        
        # Individual performance
        assignee_metrics = {}
        for assignee in df['assignee'].unique():
            if assignee == 'Unassigned':
                continue
                
            assignee_issues = df[df['assignee'] == assignee]
            
            # Calculate metrics
            total_assigned = len(assignee_issues)
            avg_resolution = assignee_issues['resolution_days'].mean() if 'resolution_days' in assignee_issues.columns else 0
            open_issues = len(assignee_issues[assignee_issues['status'].isin(['Open', 'In Progress', 'To Do'])])
            
            assignee_metrics[assignee] = {
                "total_assigned": total_assigned,
                "open_issues": open_issues,
                "avg_resolution_days": round(avg_resolution, 1),
                "workload_score": total_assigned + (open_issues * 2)  # Weight open issues more
            }
        
        # Team velocity (issues resolved per time period)
        if 'updated' in df.columns:
            recent_resolved = df[
                (df['updated'] >= datetime.now() - timedelta(days=30)) &
                (df['status'].isin(['Done', 'Closed', 'Resolved']))
            ]
            monthly_velocity = len(recent_resolved)
        else:
            monthly_velocity = 0
        
        # Identify high performers and overloaded members
        if assignee_metrics:
            best_performer = min(assignee_metrics.items(), 
                               key=lambda x: x[1]['avg_resolution_days'] if x[1]['avg_resolution_days'] > 0 else float('inf'))
            most_overloaded = max(assignee_metrics.items(), key=lambda x: x[1]['workload_score'])
        else:
            best_performer = None
            most_overloaded = None
        
        return {
            "individual_metrics": assignee_metrics,
            "monthly_velocity": monthly_velocity,
            "best_performer": best_performer[0] if best_performer else None,
            "most_overloaded": most_overloaded[0] if most_overloaded else None,
            "team_size": len([a for a in df['assignee'].unique() if a != 'Unassigned'])
        }
    
    def _analyze_sentiment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sentiment in issue descriptions and summaries."""
        logger.debug("😊 Analyzing sentiment")
        
        sentiments = []
        polarities = []
        
        for idx, row in df.iterrows():
            text = f"{row.get('summary', '')} {row.get('description', '')}"
            if text.strip():
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                polarities.append(polarity)
                
                if polarity > 0.1:
                    sentiments.append('Positive')
                elif polarity < -0.1:
                    sentiments.append('Negative')
                else:
                    sentiments.append('Neutral')
            else:
                sentiments.append('Neutral')
                polarities.append(0)
        
        df['sentiment'] = sentiments
        df['sentiment_polarity'] = polarities
        
        # Sentiment distribution
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        
        # Average sentiment by assignee
        assignee_sentiment = df.groupby('assignee')['sentiment_polarity'].mean().to_dict()
        
        # Sentiment trends
        negative_issues = df[df['sentiment'] == 'Negative']
        stress_indicators = len(negative_issues)
        
        # Most negative issues (potential stress indicators)
        most_negative = df.nsmallest(5, 'sentiment_polarity')[['key', 'summary', 'sentiment_polarity']].to_dict('records')
        
        return {
            "sentiment_distribution": sentiment_counts,
            "avg_sentiment_score": round(np.mean(polarities), 3),
            "assignee_sentiment": {k: round(v, 3) for k, v in assignee_sentiment.items()},
            "stress_indicators": stress_indicators,
            "most_negative_issues": most_negative,
            "team_mood": "Good" if np.mean(polarities) > 0.05 else "Neutral" if np.mean(polarities) > -0.05 else "Concerning"
        }
    
    def _detect_bottlenecks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect potential bottlenecks in the workflow."""
        logger.debug("🚧 Detecting bottlenecks")
        
        bottlenecks = []
        
        # Status-based bottlenecks
        status_counts = df['status'].value_counts()
        total_issues = len(df)
        
        for status, count in status_counts.items():
            percentage = (count / total_issues) * 100
            if percentage > 40 and status not in ['Done', 'Closed', 'Resolved']:
                bottlenecks.append({
                    "type": "Status Bottleneck",
                    "description": f"Too many issues in '{status}' status ({percentage:.1f}%)",
                    "severity": "High" if percentage > 60 else "Medium",
                    "affected_count": count
                })
        
        # Assignee bottlenecks
        assignee_counts = df['assignee'].value_counts()
        avg_per_assignee = len(df) / len([a for a in df['assignee'].unique() if a != 'Unassigned'])
        
        for assignee, count in assignee_counts.items():
            if assignee != 'Unassigned' and count > avg_per_assignee * 2:
                bottlenecks.append({
                    "type": "Assignee Overload",
                    "description": f"{assignee} has {count} issues (avg: {avg_per_assignee:.1f})",
                    "severity": "High" if count > avg_per_assignee * 3 else "Medium",
                    "affected_count": count
                })
        
        # Age-based bottlenecks
        old_issues = df[df['age_days'] > 60] if 'age_days' in df.columns else pd.DataFrame()
        if not old_issues.empty:
            bottlenecks.append({
                "type": "Aging Issues",
                "description": f"{len(old_issues)} issues are over 60 days old",
                "severity": "Medium",
                "affected_count": len(old_issues)
            })
        
        # Priority bottlenecks
        high_priority_old = df[
            (df['priority'].isin(['High', 'Critical', 'Urgent'])) & 
            (df['age_days'] > 14)
        ] if 'age_days' in df.columns else pd.DataFrame()
        
        if not high_priority_old.empty:
            bottlenecks.append({
                "type": "High Priority Delays",
                "description": f"{len(high_priority_old)} high priority issues are over 2 weeks old",
                "severity": "Critical",
                "affected_count": len(high_priority_old)
            })
        
        return {
            "bottlenecks_detected": bottlenecks,
            "bottleneck_count": len(bottlenecks),
            "critical_count": len([b for b in bottlenecks if b['severity'] == 'Critical']),
            "recommendations": self._generate_bottleneck_recommendations(bottlenecks)
        }
    
    def _predict_potential_blockers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Use ML to predict which issues might become blockers."""
        logger.debug("🔮 Predicting potential blockers")
        
        if len(df) < 10:  # Need minimum data for ML
            return {"error": "Insufficient data for predictions"}
        
        try:
            # Prepare features for ML
            features_df = df.copy()
            
            # Encode categorical variables
            priority_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4, 'Urgent': 5}
            features_df['priority_score'] = features_df['priority'].map(priority_map).fillna(2)
            
            # Create features
            features = []
            if 'age_days' in features_df.columns:
                features.append('age_days')
            if 'priority_score' in features_df.columns:
                features.append('priority_score')
            
            # Add text-based features
            features_df['summary_length'] = features_df['summary'].str.len().fillna(0)
            features_df['has_description'] = features_df['description'].str.len().fillna(0) > 0
            features.extend(['summary_length', 'has_description'])
            
            # Create target variable (issues that took long to resolve or are old)
            if 'resolution_days' in features_df.columns:
                # Use actual resolution time data
                features_df['is_blocker'] = (features_df['resolution_days'] > features_df['resolution_days'].quantile(0.75)).fillna(False)
            else:
                # Use age as proxy
                features_df['is_blocker'] = features_df['age_days'] > 30
            
            # Prepare data for ML
            X = features_df[features].fillna(0)
            y = features_df['is_blocker'].astype(int)
            
            if X.empty or len(X) < 5:
                return {"error": "Insufficient feature data"}
            
            # Train model
            if len(np.unique(y)) > 1:  # Need both classes
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
                
                self.resolution_model = RandomForestRegressor(n_estimators=50, random_state=42)
                self.resolution_model.fit(X_train, y_train)
                
                # Predict potential blockers
                predictions = self.resolution_model.predict(X)
                features_df['blocker_probability'] = predictions
                
                # Get top potential blockers
                potential_blockers = features_df.nlargest(5, 'blocker_probability')[
                    ['key', 'summary', 'assignee', 'priority', 'age_days', 'blocker_probability']
                ].to_dict('records')
                
                # Feature importance
                feature_importance = dict(zip(features, self.resolution_model.feature_importances_))
                
                return {
                    "potential_blockers": potential_blockers,
                    "model_accuracy": "Trained successfully",
                    "feature_importance": feature_importance,
                    "predictions_made": len(predictions)
                }
            else:
                return {"error": "Insufficient class diversity for prediction"}
                
        except Exception as e:
            logger.error(f"Error in blocker prediction: {str(e)}")
            return {"error": f"Prediction failed: {str(e)}"}
    
    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalous issues that might need attention."""
        logger.debug("🔍 Detecting anomalies")
        
        try:
            # Prepare features for anomaly detection
            numeric_features = []
            if 'age_days' in df.columns:
                numeric_features.append('age_days')
            if 'resolution_days' in df.columns:
                numeric_features.append('resolution_days')
                
            df['summary_length'] = df['summary'].str.len().fillna(0)
            numeric_features.append('summary_length')
            
            if len(numeric_features) < 2:
                return {"error": "Insufficient numeric features for anomaly detection"}
            
            # Prepare data
            X = df[numeric_features].fillna(0)
            
            # Use Isolation Forest for anomaly detection
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = self.anomaly_detector.fit_predict(X)
            
            df['is_anomaly'] = anomaly_labels == -1
            
            # Get anomalous issues
            anomalies = df[df['is_anomaly']][
                ['key', 'summary', 'assignee', 'status', 'age_days'] + 
                (['resolution_days'] if 'resolution_days' in df.columns else [])
            ].head(10).to_dict('records')
            
            return {
                "anomalies_detected": anomalies,
                "anomaly_count": df['is_anomaly'].sum(),
                "anomaly_percentage": round((df['is_anomaly'].sum() / len(df)) * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return {"error": f"Anomaly detection failed: {str(e)}"}
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in issue creation and resolution."""
        logger.debug("📈 Analyzing trends")
        
        if 'created' not in df.columns:
            return {"error": "No date data available for trend analysis"}
        
        # Weekly trends
        df['week'] = df['created'].dt.isocalendar().week
        weekly_creation = df.groupby('week').size().to_dict()
        
        # Monthly trends  
        df['month_year'] = df['created'].dt.to_period('M')
        monthly_trend = df.groupby('month_year').size().to_dict()
        monthly_trend = {str(k): v for k, v in monthly_trend.items()}
        
        # Calculate trend direction
        recent_weeks = sorted(weekly_creation.items())[-4:]  # Last 4 weeks
        if len(recent_weeks) >= 2:
            trend_direction = "Increasing" if recent_weeks[-1][1] > recent_weeks[0][1] else "Decreasing"
        else:
            trend_direction = "Stable"
        
        return {
            "weekly_creation_trend": weekly_creation,
            "monthly_creation_trend": monthly_trend,
            "trend_direction": trend_direction,
            "current_week_issues": weekly_creation.get(datetime.now().isocalendar()[1], 0)
        }
    
    def _analyze_workload_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze workload distribution across team members."""
        logger.debug("⚖️ Analyzing workload distribution")
        
        # Current workload (open issues)
        open_issues = df[df['status'].isin(['Open', 'In Progress', 'To Do', 'New'])]
        workload = open_issues['assignee'].value_counts().to_dict()
        
        # Remove unassigned for balance calculation
        assigned_workload = {k: v for k, v in workload.items() if k != 'Unassigned'}
        
        if not assigned_workload:
            return {"error": "No assigned issues found"}
        
        # Calculate balance metrics
        workloads = list(assigned_workload.values())
        avg_workload = np.mean(workloads)
        std_workload = np.std(workloads)
        
        # Identify imbalances
        overloaded = {k: v for k, v in assigned_workload.items() if v > avg_workload + std_workload}
        underloaded = {k: v for k, v in assigned_workload.items() if v < avg_workload - std_workload}
        
        # Balance score (lower is better)
        balance_score = std_workload / avg_workload if avg_workload > 0 else 1
        
        return {
            "current_workload": workload,
            "avg_workload_per_person": round(avg_workload, 1),
            "workload_std_dev": round(std_workload, 1),
            "balance_score": round(balance_score, 3),
            "balance_rating": "Good" if balance_score < 0.3 else "Fair" if balance_score < 0.6 else "Poor",
            "overloaded_members": overloaded,
            "underloaded_members": underloaded,
            "total_open_issues": len(open_issues)
        }
    
    def _generate_bottleneck_recommendations(self, bottlenecks: List[Dict]) -> List[str]:
        """Generate recommendations based on detected bottlenecks."""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'Status Bottleneck':
                recommendations.append(f"Review workflow for '{bottleneck['description']}' - consider breaking down tasks")
            elif bottleneck['type'] == 'Assignee Overload':
                recommendations.append(f"Redistribute workload - {bottleneck['description']}")
            elif bottleneck['type'] == 'Aging Issues':
                recommendations.append("Review and prioritize old issues - consider closing obsolete ones")
            elif bottleneck['type'] == 'High Priority Delays':
                recommendations.append("Urgent: Review high priority issues that are delayed")
        
        # General recommendations
        if len(bottlenecks) > 3:
            recommendations.append("Consider sprint planning review to address multiple bottlenecks")
        
        return recommendations
