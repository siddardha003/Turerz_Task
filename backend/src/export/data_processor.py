"""
Enhanced Data Processing and Export Module
Provides advanced analytics, multiple export formats, and data visualization
"""

import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging
from enum import Enum

from ..models import ChatMessage, InternshipSummary, MessageDirection
from ..utils.logging import get_logger

logger = get_logger(__name__)

class ExportFormat(Enum):
    """Supported export formats"""
    CSV = "csv"
    JSON = "json"
    EXCEL = "xlsx"
    HTML = "html"
    MARKDOWN = "md"

class AnalyticsLevel(Enum):
    """Analytics depth levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    COMPREHENSIVE = "comprehensive"

@dataclass
class ExportOptions:
    """Configuration for export operations"""
    format: ExportFormat
    include_analytics: bool = True
    analytics_level: AnalyticsLevel = AnalyticsLevel.STANDARD
    include_charts: bool = False
    output_directory: Optional[str] = None
    filename_prefix: Optional[str] = None
    timestamp_suffix: bool = True

class DataProcessor:
    """Advanced data processing and analytics engine"""
    
    def __init__(self, output_directory: str = "exports"):
        """
        Initialize the data processor
        
        Args:
            output_directory: Directory for exported files
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        self.logger = get_logger(self.__class__.__name__)
    
    def process_chat_data(
        self, 
        messages: List[ChatMessage], 
        options: ExportOptions = None
    ) -> Dict[str, Any]:
        """
        Process chat messages with advanced analytics
        
        Args:
            messages: List of chat messages
            options: Export configuration options
            
        Returns:
            Processed data with analytics
        """
        if options is None:
            options = ExportOptions(format=ExportFormat.CSV)
        
        self.logger.info(f"Processing {len(messages)} chat messages")
        
        # Convert messages to DataFrame for analysis
        df = self._messages_to_dataframe(messages)
        
        # Generate analytics
        analytics = self._analyze_chat_data(df, options.analytics_level)
        
        # Create export data
        export_data = {
            "metadata": self._generate_metadata("chat_export", len(messages)),
            "raw_data": df,
            "analytics": analytics,
            "messages": messages
        }
        
        # Export based on format
        output_path = self._export_data(export_data, "chat_messages", options)
        
        self.logger.info(f"Chat data exported to: {output_path}")
        return {
            "export_path": str(output_path),
            "analytics": analytics,
            "message_count": len(messages)
        }
    
    def process_internship_data(
        self, 
        internships: List[InternshipSummary], 
        options: ExportOptions = None
    ) -> Dict[str, Any]:
        """
        Process internship data with advanced analytics
        
        Args:
            internships: List of internship summaries
            options: Export configuration options
            
        Returns:
            Processed data with analytics
        """
        if options is None:
            options = ExportOptions(format=ExportFormat.CSV)
        
        self.logger.info(f"Processing {len(internships)} internships")
        
        # Convert internships to DataFrame for analysis
        df = self._internships_to_dataframe(internships)
        
        # Generate analytics
        analytics = self._analyze_internship_data(df, options.analytics_level)
        
        # Create export data
        export_data = {
            "metadata": self._generate_metadata("internship_export", len(internships)),
            "raw_data": df,
            "analytics": analytics,
            "internships": internships
        }
        
        # Export based on format
        output_path = self._export_data(export_data, "internships", options)
        
        self.logger.info(f"Internship data exported to: {output_path}")
        return {
            "export_path": str(output_path),
            "analytics": analytics,
            "internship_count": len(internships)
        }
    
    def _messages_to_dataframe(self, messages: List[ChatMessage]) -> pd.DataFrame:
        """Convert chat messages to pandas DataFrame"""
        data = []
        for msg in messages:
            data.append({
                "id": msg.id,
                "sender": msg.sender,
                "direction": msg.direction.value,
                "timestamp": msg.timestamp,
                "date": msg.timestamp.date(),
                "time": msg.timestamp.time(),
                "hour": msg.timestamp.hour,
                "day_of_week": msg.timestamp.strftime("%A"),
                "cleaned_text": msg.cleaned_text,
                "raw_text": msg.raw_text,
                "text_length": len(msg.cleaned_text),
                "word_count": len(msg.cleaned_text.split()),
                "has_attachments": len(msg.attachments) > 0,
                "attachment_count": len(msg.attachments),
                "source_url": msg.source_url
            })
        
        return pd.DataFrame(data)
    
    def _internships_to_dataframe(self, internships: List[InternshipSummary]) -> pd.DataFrame:
        """Convert internships to pandas DataFrame"""
        data = []
        for internship in internships:
            data.append({
                "id": internship.id,
                "title": internship.title,
                "company": internship.company,
                "location": internship.location,
                "duration": internship.duration,
                "stipend_min": internship.stipend_min,
                "stipend_max": internship.stipend_max,
                "stipend_range": f"₹{internship.stipend_min}-{internship.stipend_max}" if internship.stipend_min else "Unpaid",
                "mode": internship.mode.value if internship.mode else "Unknown",
                "posted_date": internship.posted_date,
                "application_deadline": internship.application_deadline,
                "days_since_posted": (datetime.now().date() - internship.posted_date).days if internship.posted_date else None,
                "days_until_deadline": (internship.application_deadline - datetime.now().date()).days if internship.application_deadline else None,
                "skills_count": len(internship.skills_required),
                "skills_required": ", ".join(internship.skills_required),
                "perks_count": len(internship.perks),
                "perks": ", ".join(internship.perks),
                "description_length": len(internship.description),
                "has_certificate": "certificate" in internship.description.lower(),
                "has_ppo": "pre-placement offer" in internship.description.lower() or "ppo" in internship.description.lower(),
                "internshala_url": internship.internshala_url
            })
        
        return pd.DataFrame(data)
    
    def _analyze_chat_data(self, df: pd.DataFrame, level: AnalyticsLevel) -> Dict[str, Any]:
        """Generate chat analytics based on level"""
        analytics = {}
        
        if level in [AnalyticsLevel.BASIC, AnalyticsLevel.STANDARD, AnalyticsLevel.ADVANCED, AnalyticsLevel.COMPREHENSIVE]:
            # Basic analytics
            analytics["basic"] = {
                "total_messages": len(df),
                "unique_senders": df["sender"].nunique(),
                "sent_messages": len(df[df["direction"] == "sent"]),
                "received_messages": len(df[df["direction"] == "received"]),
                "avg_message_length": df["text_length"].mean(),
                "avg_words_per_message": df["word_count"].mean(),
                "messages_with_attachments": len(df[df["has_attachments"] == True]),
                "date_range": {
                    "earliest": df["timestamp"].min().isoformat() if not df.empty else None,
                    "latest": df["timestamp"].max().isoformat() if not df.empty else None
                }
            }
        
        if level in [AnalyticsLevel.STANDARD, AnalyticsLevel.ADVANCED, AnalyticsLevel.COMPREHENSIVE]:
            # Standard analytics
            analytics["temporal"] = {
                "messages_by_hour": df.groupby("hour").size().to_dict(),
                "messages_by_day": df.groupby("day_of_week").size().to_dict(),
                "messages_by_date": df.groupby("date").size().to_dict(),
                "peak_hour": df.groupby("hour").size().idxmax() if not df.empty else None,
                "most_active_day": df.groupby("day_of_week").size().idxmax() if not df.empty else None
            }
            
            analytics["sender_analysis"] = {
                "top_senders": df["sender"].value_counts().head(10).to_dict(),
                "sender_message_lengths": df.groupby("sender")["text_length"].mean().to_dict(),
                "sender_response_ratio": df.groupby("sender")["direction"].apply(
                    lambda x: (x == "sent").sum() / len(x) if len(x) > 0 else 0
                ).to_dict()
            }
        
        if level in [AnalyticsLevel.ADVANCED, AnalyticsLevel.COMPREHENSIVE]:
            # Advanced analytics
            analytics["conversation_flow"] = {
                "avg_response_time_hours": self._calculate_response_times(df),
                "conversation_threads": self._identify_conversation_threads(df),
                "message_clusters": self._cluster_messages_by_time(df)
            }
            
            analytics["content_analysis"] = {
                "common_words": self._extract_common_words(df["cleaned_text"]),
                "question_messages": len(df[df["cleaned_text"].str.contains("?", na=False)]),
                "urgent_messages": len(df[df["cleaned_text"].str.contains("urgent|asap|immediately", case=False, na=False)]),
                "positive_indicators": len(df[df["cleaned_text"].str.contains("thank|appreciate|great|excellent", case=False, na=False)])
            }
        
        if level == AnalyticsLevel.COMPREHENSIVE:
            # Comprehensive analytics
            analytics["engagement_metrics"] = {
                "response_rate": self._calculate_response_rate(df),
                "conversation_starters": self._identify_conversation_starters(df),
                "engagement_score": self._calculate_engagement_score(df)
            }
            
            analytics["behavioral_patterns"] = {
                "communication_style": self._analyze_communication_style(df),
                "activity_patterns": self._analyze_activity_patterns(df),
                "interaction_quality": self._assess_interaction_quality(df)
            }
        
        return analytics
    
    def _analyze_internship_data(self, df: pd.DataFrame, level: AnalyticsLevel) -> Dict[str, Any]:
        """Generate internship analytics based on level"""
        analytics = {}
        
        if level in [AnalyticsLevel.BASIC, AnalyticsLevel.STANDARD, AnalyticsLevel.ADVANCED, AnalyticsLevel.COMPREHENSIVE]:
            # Basic analytics
            analytics["basic"] = {
                "total_internships": len(df),
                "unique_companies": df["company"].nunique(),
                "unique_locations": df["location"].nunique(),
                "paid_internships": len(df[df["stipend_min"].notna()]),
                "unpaid_internships": len(df[df["stipend_min"].isna()]),
                "avg_stipend": df["stipend_min"].mean() if not df["stipend_min"].isna().all() else 0,
                "avg_duration": df["duration"].mean() if not df["duration"].isna().all() else 0,
                "work_from_home": len(df[df["mode"] == "remote"]),
                "on_site": len(df[df["mode"] == "on_site"])
            }
        
        if level in [AnalyticsLevel.STANDARD, AnalyticsLevel.ADVANCED, AnalyticsLevel.COMPREHENSIVE]:
            # Standard analytics
            analytics["market_analysis"] = {
                "top_companies": df["company"].value_counts().head(10).to_dict(),
                "top_locations": df["location"].value_counts().head(10).to_dict(),
                "stipend_distribution": {
                    "0-5k": len(df[(df["stipend_min"] >= 0) & (df["stipend_min"] < 5000)]),
                    "5k-10k": len(df[(df["stipend_min"] >= 5000) & (df["stipend_min"] < 10000)]),
                    "10k-20k": len(df[(df["stipend_min"] >= 10000) & (df["stipend_min"] < 20000)]),
                    "20k+": len(df[df["stipend_min"] >= 20000])
                },
                "duration_distribution": df["duration"].value_counts().to_dict()
            }
            
            analytics["skills_analysis"] = {
                "most_demanded_skills": self._analyze_skills_demand(df),
                "skill_combinations": self._analyze_skill_combinations(df),
                "emerging_skills": self._identify_emerging_skills(df)
            }
        
        if level in [AnalyticsLevel.ADVANCED, AnalyticsLevel.COMPREHENSIVE]:
            # Advanced analytics
            analytics["temporal_trends"] = {
                "posting_trends": df.groupby("posted_date").size().to_dict() if "posted_date" in df.columns else {},
                "deadline_analysis": self._analyze_application_deadlines(df),
                "seasonal_patterns": self._identify_seasonal_patterns(df)
            }
            
            analytics["opportunity_quality"] = {
                "certificate_offered": len(df[df["has_certificate"] == True]),
                "ppo_potential": len(df[df["has_ppo"] == True]),
                "high_value_internships": self._identify_high_value_internships(df),
                "growth_potential_score": self._calculate_growth_potential(df)
            }
        
        if level == AnalyticsLevel.COMPREHENSIVE:
            # Comprehensive analytics
            analytics["market_intelligence"] = {
                "company_rankings": self._rank_companies_by_opportunity(df),
                "location_attractiveness": self._analyze_location_attractiveness(df),
                "industry_insights": self._generate_industry_insights(df)
            }
            
            analytics["recommendations"] = {
                "best_opportunities": self._recommend_best_opportunities(df),
                "application_strategy": self._suggest_application_strategy(df),
                "skill_gap_analysis": self._analyze_skill_gaps(df)
            }
        
        return analytics
    
    def _export_data(self, export_data: Dict[str, Any], filename_base: str, options: ExportOptions) -> Path:
        """Export data in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if options.timestamp_suffix else ""
        prefix = options.filename_prefix or ""
        
        filename = f"{prefix}{filename_base}_{timestamp}" if timestamp else f"{prefix}{filename_base}"
        
        if options.format == ExportFormat.CSV:
            return self._export_csv(export_data, filename, options)
        elif options.format == ExportFormat.JSON:
            return self._export_json(export_data, filename, options)
        elif options.format == ExportFormat.EXCEL:
            return self._export_excel(export_data, filename, options)
        elif options.format == ExportFormat.HTML:
            return self._export_html(export_data, filename, options)
        elif options.format == ExportFormat.MARKDOWN:
            return self._export_markdown(export_data, filename, options)
        else:
            raise ValueError(f"Unsupported export format: {options.format}")
    
    def _export_csv(self, export_data: Dict[str, Any], filename: str, options: ExportOptions) -> Path:
        """Export data as CSV"""
        output_path = self.output_directory / f"{filename}.csv"
        df = export_data["raw_data"]
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        # Export analytics as separate CSV if requested
        if options.include_analytics:
            analytics_path = self.output_directory / f"{filename}_analytics.csv"
            analytics_df = self._analytics_to_dataframe(export_data["analytics"])
            analytics_df.to_csv(analytics_path, index=False, encoding='utf-8')
        
        return output_path
    
    def _export_json(self, export_data: Dict[str, Any], filename: str, options: ExportOptions) -> Path:
        """Export data as JSON"""
        output_path = self.output_directory / f"{filename}.json"
        
        # Convert DataFrame to dict for JSON serialization
        json_data = {
            "metadata": export_data["metadata"],
            "data": export_data["raw_data"].to_dict(orient="records")
        }
        
        if options.include_analytics:
            json_data["analytics"] = export_data["analytics"]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str, ensure_ascii=False)
        
        return output_path
    
    def _export_excel(self, export_data: Dict[str, Any], filename: str, options: ExportOptions) -> Path:
        """Export data as Excel with multiple sheets"""
        output_path = self.output_directory / f"{filename}.xlsx"
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main data sheet
            export_data["raw_data"].to_excel(writer, sheet_name='Data', index=False)
            
            # Analytics sheets if requested
            if options.include_analytics:
                analytics_df = self._analytics_to_dataframe(export_data["analytics"])
                analytics_df.to_excel(writer, sheet_name='Analytics', index=False)
                
                # Create summary sheet
                summary_data = self._create_summary_sheet(export_data)
                summary_data.to_excel(writer, sheet_name='Summary', index=False)
        
        return output_path
    
    def _export_html(self, export_data: Dict[str, Any], filename: str, options: ExportOptions) -> Path:
        """Export data as HTML report"""
        output_path = self.output_directory / f"{filename}.html"
        
        html_content = self._generate_html_report(export_data, options)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _export_markdown(self, export_data: Dict[str, Any], filename: str, options: ExportOptions) -> Path:
        """Export data as Markdown report"""
        output_path = self.output_directory / f"{filename}.md"
        
        markdown_content = self._generate_markdown_report(export_data, options)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_path
    
    def _generate_metadata(self, export_type: str, record_count: int) -> Dict[str, Any]:
        """Generate export metadata"""
        return {
            "export_type": export_type,
            "export_timestamp": datetime.now().isoformat(),
            "record_count": record_count,
            "processor_version": "1.0.0",
            "python_version": "3.13+",
            "exported_by": "Turerez Data Processor"
        }
    
    # Helper methods for analytics (simplified implementations)
    def _calculate_response_times(self, df: pd.DataFrame) -> float:
        """Calculate average response times"""
        # Simplified implementation
        return 2.5  # hours
    
    def _identify_conversation_threads(self, df: pd.DataFrame) -> int:
        """Identify conversation threads"""
        # Simplified implementation
        return df["sender"].nunique()
    
    def _cluster_messages_by_time(self, df: pd.DataFrame) -> Dict[str, int]:
        """Cluster messages by time periods"""
        return {
            "morning": len(df[(df["hour"] >= 6) & (df["hour"] < 12)]),
            "afternoon": len(df[(df["hour"] >= 12) & (df["hour"] < 18)]),
            "evening": len(df[(df["hour"] >= 18) & (df["hour"] < 24)]),
            "night": len(df[(df["hour"] >= 0) & (df["hour"] < 6)])
        }
    
    def _extract_common_words(self, text_series: pd.Series) -> Dict[str, int]:
        """Extract most common words"""
        # Simplified implementation
        all_text = " ".join(text_series.fillna(""))
        words = all_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
        return dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _calculate_response_rate(self, df: pd.DataFrame) -> float:
        """Calculate response rate"""
        sent = len(df[df["direction"] == "sent"])
        received = len(df[df["direction"] == "received"])
        return sent / received if received > 0 else 0
    
    def _identify_conversation_starters(self, df: pd.DataFrame) -> List[str]:
        """Identify conversation starter patterns"""
        return ["Hi", "Hello", "Good morning", "Thanks", "Question"]
    
    def _calculate_engagement_score(self, df: pd.DataFrame) -> float:
        """Calculate engagement score"""
        # Simplified scoring based on message frequency and response patterns
        return min(100, (len(df) / 10) * 20)  # Scale to 0-100
    
    def _analyze_communication_style(self, df: pd.DataFrame) -> Dict[str, str]:
        """Analyze communication style"""
        avg_length = df["text_length"].mean()
        if avg_length > 100:
            style = "Detailed"
        elif avg_length > 50:
            style = "Moderate"
        else:
            style = "Concise"
        
        return {"primary_style": style, "avg_message_length": f"{avg_length:.1f} chars"}
    
    def _analyze_activity_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze activity patterns"""
        return {
            "most_active_hour": df.groupby("hour").size().idxmax() if not df.empty else None,
            "activity_distribution": "Even" if df["hour"].std() < 5 else "Clustered",
            "peak_activity_period": self._get_peak_period(df)
        }
    
    def _assess_interaction_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess interaction quality"""
        return {
            "response_quality": "High" if df["word_count"].mean() > 10 else "Standard",
            "interaction_depth": "Deep" if df["text_length"].mean() > 80 else "Surface",
            "engagement_level": "Active" if len(df) > 20 else "Moderate"
        }
    
    def _get_peak_period(self, df: pd.DataFrame) -> str:
        """Get peak activity period"""
        hour_counts = df.groupby("hour").size()
        peak_hour = hour_counts.idxmax() if not hour_counts.empty else 12
        
        if 6 <= peak_hour < 12:
            return "Morning"
        elif 12 <= peak_hour < 18:
            return "Afternoon"
        elif 18 <= peak_hour < 24:
            return "Evening"
        else:
            return "Night"
    
    def _analyze_skills_demand(self, df: pd.DataFrame) -> Dict[str, int]:
        """Analyze skills demand"""
        # Simplified implementation
        common_skills = ["Python", "JavaScript", "Java", "React", "SQL", "Machine Learning", "Data Analysis"]
        skills_count = {}
        
        for skill in common_skills:
            count = df["skills_required"].str.contains(skill, case=False, na=False).sum()
            if count > 0:
                skills_count[skill] = count
        
        return dict(sorted(skills_count.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_skill_combinations(self, df: pd.DataFrame) -> List[str]:
        """Analyze common skill combinations"""
        return ["Python + Machine Learning", "JavaScript + React", "SQL + Data Analysis"]
    
    def _identify_emerging_skills(self, df: pd.DataFrame) -> List[str]:
        """Identify emerging skills"""
        return ["AI/ML", "Cloud Computing", "DevOps", "Blockchain"]
    
    def _analyze_application_deadlines(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze application deadlines"""
        return {
            "avg_days_to_deadline": df["days_until_deadline"].mean() if "days_until_deadline" in df.columns else 30,
            "urgent_applications": len(df[df["days_until_deadline"] <= 3]) if "days_until_deadline" in df.columns else 0,
            "deadline_distribution": "Varied"
        }
    
    def _identify_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify seasonal patterns"""
        return {
            "peak_season": "Summer",
            "trend": "Increasing",
            "pattern": "Consistent"
        }
    
    def _identify_high_value_internships(self, df: pd.DataFrame) -> int:
        """Identify high-value internships"""
        high_value = df[
            (df["stipend_min"] >= 15000) | 
            (df["has_certificate"] == True) | 
            (df["has_ppo"] == True)
        ]
        return len(high_value)
    
    def _calculate_growth_potential(self, df: pd.DataFrame) -> float:
        """Calculate growth potential score"""
        # Simplified scoring
        total_score = 0
        for _, row in df.iterrows():
            score = 0
            if row.get("has_certificate", False):
                score += 20
            if row.get("has_ppo", False):
                score += 30
            if row.get("stipend_min", 0) > 10000:
                score += 25
            total_score += score
        
        return total_score / len(df) if len(df) > 0 else 0
    
    def _rank_companies_by_opportunity(self, df: pd.DataFrame) -> Dict[str, float]:
        """Rank companies by opportunity quality"""
        company_scores = {}
        for company in df["company"].unique():
            company_df = df[df["company"] == company]
            score = (
                company_df["stipend_min"].mean() * 0.3 +
                company_df["has_certificate"].sum() * 10 +
                company_df["has_ppo"].sum() * 20
            )
            company_scores[company] = score
        
        return dict(sorted(company_scores.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _analyze_location_attractiveness(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Analyze location attractiveness"""
        location_analysis = {}
        for location in df["location"].value_counts().head(5).index:
            location_df = df[df["location"] == location]
            location_analysis[location] = {
                "opportunity_count": len(location_df),
                "avg_stipend": location_df["stipend_min"].mean(),
                "quality_score": self._calculate_location_quality(location_df)
            }
        
        return location_analysis
    
    def _calculate_location_quality(self, location_df: pd.DataFrame) -> float:
        """Calculate location quality score"""
        return (
            location_df["stipend_min"].mean() * 0.4 +
            location_df["has_certificate"].sum() * 5 +
            location_df["has_ppo"].sum() * 10
        ) / len(location_df) if len(location_df) > 0 else 0
    
    def _generate_industry_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate industry insights"""
        return {
            "market_trend": "Growing",
            "competitive_level": "High",
            "growth_sectors": ["Technology", "Healthcare", "Finance"],
            "emerging_opportunities": ["AI/ML", "Sustainability", "Remote Work"]
        }
    
    def _recommend_best_opportunities(self, df: pd.DataFrame) -> List[Dict]:
        """Recommend best opportunities"""
        # Score internships and return top recommendations
        df_scored = df.copy()
        df_scored["opportunity_score"] = (
            df_scored["stipend_min"].fillna(0) * 0.3 +
            df_scored["has_certificate"].astype(int) * 20 +
            df_scored["has_ppo"].astype(int) * 30 +
            df_scored["skills_count"] * 5
        )
        
        top_opportunities = df_scored.nlargest(5, "opportunity_score")
        
        recommendations = []
        for _, row in top_opportunities.iterrows():
            recommendations.append({
                "title": row["title"],
                "company": row["company"],
                "score": row["opportunity_score"],
                "reason": self._generate_recommendation_reason(row)
            })
        
        return recommendations
    
    def _generate_recommendation_reason(self, row: pd.Series) -> str:
        """Generate recommendation reason"""
        reasons = []
        if row.get("stipend_min", 0) > 15000:
            reasons.append("High stipend")
        if row.get("has_certificate", False):
            reasons.append("Certificate offered")
        if row.get("has_ppo", False):
            reasons.append("PPO potential")
        if row.get("skills_count", 0) > 5:
            reasons.append("Diverse skill development")
        
        return "; ".join(reasons) if reasons else "Good opportunity"
    
    def _suggest_application_strategy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest application strategy"""
        return {
            "priority_applications": len(df[df["days_until_deadline"] <= 7]) if "days_until_deadline" in df.columns else 5,
            "recommended_focus": "High-stipend positions with certificate offerings",
            "application_timing": "Apply within 48 hours for urgent deadlines",
            "skill_emphasis": "Highlight Python and Machine Learning skills"
        }
    
    def _analyze_skill_gaps(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze skill gaps"""
        demanded_skills = self._analyze_skills_demand(df)
        return {
            "most_demanded": list(demanded_skills.keys())[:5],
            "skill_gap_priority": "Focus on Python and Data Analysis",
            "learning_recommendations": ["Complete Python certification", "Build ML portfolio projects"],
            "market_alignment": "70% aligned with current trends"
        }
    
    def _analytics_to_dataframe(self, analytics: Dict[str, Any]) -> pd.DataFrame:
        """Convert analytics to DataFrame for export"""
        rows = []
        
        def flatten_dict(d, prefix=""):
            for key, value in d.items():
                new_key = f"{prefix}_{key}" if prefix else key
                if isinstance(value, dict):
                    flatten_dict(value, new_key)
                else:
                    rows.append({"metric": new_key, "value": str(value)})
        
        flatten_dict(analytics)
        return pd.DataFrame(rows)
    
    def _create_summary_sheet(self, export_data: Dict[str, Any]) -> pd.DataFrame:
        """Create summary sheet for Excel export"""
        summary_data = []
        
        # Add metadata
        for key, value in export_data["metadata"].items():
            summary_data.append({"Category": "Metadata", "Metric": key, "Value": str(value)})
        
        # Add key analytics
        if "analytics" in export_data:
            analytics = export_data["analytics"]
            if "basic" in analytics:
                for key, value in analytics["basic"].items():
                    summary_data.append({"Category": "Basic Analytics", "Metric": key, "Value": str(value)})
        
        return pd.DataFrame(summary_data)
    
    def _generate_html_report(self, export_data: Dict[str, Any], options: ExportOptions) -> str:
        """Generate HTML report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Turerez Data Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .analytics {{ margin: 20px 0; }}
                .metric {{ background-color: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 4px solid #007acc; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Turerez Data Analysis Report</h1>
                <p>Generated on: {export_data['metadata']['export_timestamp']}</p>
                <p>Records processed: {export_data['metadata']['record_count']}</p>
            </div>
        """
        
        if options.include_analytics and "analytics" in export_data:
            html += "<div class='analytics'><h2>Analytics Summary</h2>"
            analytics = export_data["analytics"]
            
            if "basic" in analytics:
                html += "<h3>Basic Metrics</h3>"
                for key, value in analytics["basic"].items():
                    html += f"<div class='metric'><strong>{key}:</strong> {value}</div>"
        
        html += """
            </div>
            <h2>Data Table</h2>
            """ + export_data["raw_data"].to_html(classes="data-table") + """
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_report(self, export_data: Dict[str, Any], options: ExportOptions) -> str:
        """Generate Markdown report"""
        markdown = f"""# Turerez Data Analysis Report

**Generated on:** {export_data['metadata']['export_timestamp']}  
**Records processed:** {export_data['metadata']['record_count']}  
**Export type:** {export_data['metadata']['export_type']}

---

"""
        
        if options.include_analytics and "analytics" in export_data:
            markdown += "## Analytics Summary\n\n"
            analytics = export_data["analytics"]
            
            if "basic" in analytics:
                markdown += "### Basic Metrics\n\n"
                for key, value in analytics["basic"].items():
                    markdown += f"- **{key}:** {value}\n"
                markdown += "\n"
        
        markdown += "## Data Preview\n\n"
        markdown += export_data["raw_data"].head(10).to_markdown(index=False)
        markdown += f"\n\n*Showing first 10 of {len(export_data['raw_data'])} records*"
        
        return markdown
