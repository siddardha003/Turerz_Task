"""
Visualization and Chart Generation Module
Provides advanced data visualization capabilities for export
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
import io
import base64
from datetime import datetime
import logging

from ..utils.logging import get_logger

logger = get_logger(__name__)

class DataVisualizer:
    """Advanced data visualization for analytics"""
    
    def __init__(self, output_directory: str = "exports/charts"):
        """
        Initialize the data visualizer
        
        Args:
            output_directory: Directory for chart exports
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(self.__class__.__name__)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_chat_visualizations(self, df: pd.DataFrame, analytics: Dict[str, Any]) -> Dict[str, str]:
        """
        Create comprehensive visualizations for chat data
        
        Args:
            df: Chat messages DataFrame
            analytics: Analytics data
            
        Returns:
            Dictionary of chart file paths
        """
        charts = {}
        
        try:
            # Message activity timeline
            charts['timeline'] = self._create_message_timeline(df)
            
            # Hourly activity heatmap
            charts['hourly_heatmap'] = self._create_hourly_heatmap(df)
            
            # Sender distribution pie chart
            charts['sender_distribution'] = self._create_sender_pie_chart(df)
            
            # Message length distribution
            charts['message_length'] = self._create_message_length_distribution(df)
            
            # Response pattern analysis
            charts['response_patterns'] = self._create_response_pattern_chart(df)
            
            # Word cloud (if available)
            charts['word_cloud'] = self._create_word_cloud(df)
            
            self.logger.info(f"Created {len(charts)} chat visualizations")
            
        except Exception as e:
            self.logger.error(f"Error creating chat visualizations: {e}")
        
        return charts
    
    def create_internship_visualizations(self, df: pd.DataFrame, analytics: Dict[str, Any]) -> Dict[str, str]:
        """
        Create comprehensive visualizations for internship data
        
        Args:
            df: Internships DataFrame
            analytics: Analytics data
            
        Returns:
            Dictionary of chart file paths
        """
        charts = {}
        
        try:
            # Stipend distribution
            charts['stipend_distribution'] = self._create_stipend_distribution(df)
            
            # Location analysis
            charts['location_analysis'] = self._create_location_chart(df)
            
            # Skills demand chart
            charts['skills_demand'] = self._create_skills_demand_chart(df, analytics)
            
            # Company opportunities
            charts['company_opportunities'] = self._create_company_chart(df)
            
            # Duration vs Stipend correlation
            charts['duration_stipend'] = self._create_duration_stipend_scatter(df)
            
            # Market trends
            charts['market_trends'] = self._create_market_trends_chart(df)
            
            # Work mode distribution
            charts['work_mode'] = self._create_work_mode_chart(df)
            
            self.logger.info(f"Created {len(charts)} internship visualizations")
            
        except Exception as e:
            self.logger.error(f"Error creating internship visualizations: {e}")
        
        return charts
    
    def _create_message_timeline(self, df: pd.DataFrame) -> str:
        """Create message activity timeline"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Group by date and count messages
        daily_counts = df.groupby('date').size()
        
        ax.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=6)
        ax.set_title('Message Activity Timeline', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Number of Messages', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_path = self.output_directory / f"chat_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_hourly_heatmap(self, df: pd.DataFrame) -> str:
        """Create hourly activity heatmap"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create hour vs day of week heatmap
        activity_matrix = df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        
        # Reorder days of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        activity_matrix = activity_matrix.reindex(day_order)
        
        sns.heatmap(activity_matrix, annot=True, fmt='d', cmap='YlOrRd', ax=ax)
        ax.set_title('Message Activity Heatmap (Hour vs Day)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Hour of Day', fontsize=12)
        ax.set_ylabel('Day of Week', fontsize=12)
        
        plt.tight_layout()
        
        output_path = self.output_directory / f"chat_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_sender_pie_chart(self, df: pd.DataFrame) -> str:
        """Create sender distribution pie chart"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sender_counts = df['sender'].value_counts()
        colors = plt.cm.Set3(range(len(sender_counts)))
        
        wedges, texts, autotexts = ax.pie(sender_counts.values, labels=sender_counts.index, 
                                         autopct='%1.1f%%', colors=colors, startangle=90)
        
        ax.set_title('Message Distribution by Sender', fontsize=16, fontweight='bold')
        
        # Enhance text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        output_path = self.output_directory / f"chat_senders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_message_length_distribution(self, df: pd.DataFrame) -> str:
        """Create message length distribution"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogram of message lengths
        ax1.hist(df['text_length'], bins=30, edgecolor='black', alpha=0.7, color='skyblue')
        ax1.set_title('Message Length Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Character Count', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Box plot by sender
        df.boxplot(column='text_length', by='sender', ax=ax2)
        ax2.set_title('Message Length by Sender', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Sender', fontsize=12)
        ax2.set_ylabel('Character Count', fontsize=12)
        
        plt.suptitle('')  # Remove default suptitle
        plt.tight_layout()
        
        output_path = self.output_directory / f"chat_length_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_response_pattern_chart(self, df: pd.DataFrame) -> str:
        """Create response pattern analysis chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Count sent vs received messages by hour
        direction_hour = df.groupby(['hour', 'direction']).size().unstack(fill_value=0)
        
        direction_hour.plot(kind='bar', stacked=True, ax=ax, color=['#ff7f0e', '#2ca02c'])
        ax.set_title('Message Direction by Hour', fontsize=16, fontweight='bold')
        ax.set_xlabel('Hour of Day', fontsize=12)
        ax.set_ylabel('Number of Messages', fontsize=12)
        ax.legend(title='Direction', labels=['Received', 'Sent'])
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=0)
        plt.tight_layout()
        
        output_path = self.output_directory / f"chat_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_word_cloud(self, df: pd.DataFrame) -> str:
        """Create word cloud from messages"""
        try:
            from wordcloud import WordCloud
            
            # Combine all message text
            all_text = ' '.join(df['cleaned_text'].fillna(''))
            
            # Create word cloud
            wordcloud = WordCloud(width=800, height=400, background_color='white',
                                max_words=100, colormap='viridis').generate(all_text)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title('Most Common Words in Messages', fontsize=16, fontweight='bold')
            
            plt.tight_layout()
            
            output_path = self.output_directory / f"chat_wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(output_path)
            
        except ImportError:
            self.logger.warning("WordCloud not available, skipping word cloud generation")
            return ""
    
    def _create_stipend_distribution(self, df: pd.DataFrame) -> str:
        """Create stipend distribution chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogram of stipends (excluding unpaid)
        paid_df = df[df['stipend_min'].notna()]
        if not paid_df.empty:
            ax1.hist(paid_df['stipend_min'], bins=20, edgecolor='black', alpha=0.7, color='lightgreen')
            ax1.set_title('Paid Internship Stipend Distribution', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Stipend (₹)', fontsize=12)
            ax1.set_ylabel('Frequency', fontsize=12)
            ax1.grid(True, alpha=0.3)
        
        # Paid vs Unpaid pie chart
        paid_count = len(df[df['stipend_min'].notna()])
        unpaid_count = len(df[df['stipend_min'].isna()])
        
        ax2.pie([paid_count, unpaid_count], labels=['Paid', 'Unpaid'], 
               autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'], startangle=90)
        ax2.set_title('Paid vs Unpaid Internships', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        output_path = self.output_directory / f"internship_stipend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_location_chart(self, df: pd.DataFrame) -> str:
        """Create location analysis chart"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Top 15 locations
        location_counts = df['location'].value_counts().head(15)
        
        bars = ax.barh(range(len(location_counts)), location_counts.values, color='skyblue')
        ax.set_yticks(range(len(location_counts)))
        ax.set_yticklabels(location_counts.index)
        ax.set_xlabel('Number of Internships', fontsize=12)
        ax.set_title('Top Internship Locations', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center')
        
        plt.tight_layout()
        
        output_path = self.output_directory / f"internship_locations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_skills_demand_chart(self, df: pd.DataFrame, analytics: Dict[str, Any]) -> str:
        """Create skills demand chart"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract skills data from analytics
        skills_data = analytics.get('skills_analysis', {}).get('most_demanded_skills', {})
        
        if skills_data:
            skills = list(skills_data.keys())[:10]  # Top 10 skills
            counts = [skills_data[skill] for skill in skills]
            
            bars = ax.bar(range(len(skills)), counts, color='lightcoral')
            ax.set_xticks(range(len(skills)))
            ax.set_xticklabels(skills, rotation=45, ha='right')
            ax.set_ylabel('Demand Count', fontsize=12)
            ax.set_title('Most Demanded Skills', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        output_path = self.output_directory / f"internship_skills_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_company_chart(self, df: pd.DataFrame) -> str:
        """Create company opportunities chart"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Top 15 companies
        company_counts = df['company'].value_counts().head(15)
        
        bars = ax.barh(range(len(company_counts)), company_counts.values, color='gold')
        ax.set_yticks(range(len(company_counts)))
        ax.set_yticklabels(company_counts.index)
        ax.set_xlabel('Number of Internships', fontsize=12)
        ax.set_title('Top Companies by Internship Count', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center')
        
        plt.tight_layout()
        
        output_path = self.output_directory / f"internship_companies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_duration_stipend_scatter(self, df: pd.DataFrame) -> str:
        """Create duration vs stipend scatter plot"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Filter paid internships
        paid_df = df[df['stipend_min'].notna() & df['duration'].notna()]
        
        if not paid_df.empty:
            scatter = ax.scatter(paid_df['duration'], paid_df['stipend_min'], 
                               alpha=0.6, s=60, color='purple')
            ax.set_xlabel('Duration (months)', fontsize=12)
            ax.set_ylabel('Stipend (₹)', fontsize=12)
            ax.set_title('Duration vs Stipend Correlation', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Add trend line
            if len(paid_df) > 1:
                z = np.polyfit(paid_df['duration'], paid_df['stipend_min'], 1)
                p = np.poly1d(z)
                ax.plot(paid_df['duration'], p(paid_df['duration']), "r--", alpha=0.8)
        
        plt.tight_layout()
        
        output_path = self.output_directory / f"internship_duration_stipend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_market_trends_chart(self, df: pd.DataFrame) -> str:
        """Create market trends chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Posted date trends
        if 'posted_date' in df.columns and df['posted_date'].notna().any():
            posting_trends = df.groupby('posted_date').size()
            ax1.plot(posting_trends.index, posting_trends.values, marker='o')
            ax1.set_title('Posting Trends Over Time', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Date', fontsize=12)
            ax1.set_ylabel('Number of Postings', fontsize=12)
            ax1.grid(True, alpha=0.3)
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Work mode distribution
        mode_counts = df['mode'].value_counts()
        ax2.pie(mode_counts.values, labels=mode_counts.index, autopct='%1.1f%%', 
               colors=['lightblue', 'orange', 'lightgreen'], startangle=90)
        ax2.set_title('Work Mode Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        output_path = self.output_directory / f"internship_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _create_work_mode_chart(self, df: pd.DataFrame) -> str:
        """Create work mode analysis chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Work mode distribution
        mode_counts = df['mode'].value_counts()
        bars1 = ax1.bar(mode_counts.index, mode_counts.values, color=['lightblue', 'orange', 'lightgreen'])
        ax1.set_title('Work Mode Distribution', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Number of Internships', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom')
        
        # Stipend by work mode
        if 'stipend_min' in df.columns:
            mode_stipend = df.groupby('mode')['stipend_min'].mean()
            bars2 = ax2.bar(mode_stipend.index, mode_stipend.values, color=['lightblue', 'orange', 'lightgreen'])
            ax2.set_title('Average Stipend by Work Mode', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Average Stipend (₹)', fontsize=12)
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Add value labels
            for bar in bars2:
                height = bar.get_height()
                if not pd.isna(height):
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 200,
                            f'₹{int(height):,}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        output_path = self.output_directory / f"internship_work_mode_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_comparison_dashboard(self, chat_df: pd.DataFrame, internship_df: pd.DataFrame) -> str:
        """Create comprehensive comparison dashboard"""
        fig = plt.figure(figsize=(20, 12))
        
        # Create grid layout
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Chat metrics
        ax1 = fig.add_subplot(gs[0, :2])
        daily_messages = chat_df.groupby('date').size()
        ax1.plot(daily_messages.index, daily_messages.values, marker='o', linewidth=2)
        ax1.set_title('Chat Activity Timeline', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Internship metrics
        ax2 = fig.add_subplot(gs[0, 2:])
        if 'posted_date' in internship_df.columns:
            daily_postings = internship_df.groupby('posted_date').size()
            ax2.plot(daily_postings.index, daily_postings.values, marker='s', linewidth=2, color='orange')
        ax2.set_title('Internship Posting Timeline', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Distribution comparisons
        ax3 = fig.add_subplot(gs[1, 0])
        sender_counts = chat_df['sender'].value_counts().head(5)
        ax3.pie(sender_counts.values, labels=sender_counts.index, autopct='%1.1f%%')
        ax3.set_title('Top Chat Senders', fontsize=12, fontweight='bold')
        
        ax4 = fig.add_subplot(gs[1, 1])
        location_counts = internship_df['location'].value_counts().head(5)
        ax4.pie(location_counts.values, labels=location_counts.index, autopct='%1.1f%%')
        ax4.set_title('Top Internship Locations', fontsize=12, fontweight='bold')
        
        # Hourly patterns
        ax5 = fig.add_subplot(gs[1, 2:])
        chat_hourly = chat_df.groupby('hour').size()
        ax5.bar(chat_hourly.index, chat_hourly.values, alpha=0.7, label='Chat Messages')
        ax5.set_xlabel('Hour of Day')
        ax5.set_ylabel('Activity Count')
        ax5.set_title('Hourly Activity Patterns', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # Summary stats
        ax6 = fig.add_subplot(gs[2, :])
        summary_data = [
            ['Chat Messages', len(chat_df), f"{chat_df['text_length'].mean():.1f} avg chars"],
            ['Unique Senders', chat_df['sender'].nunique(), f"{len(chat_df[chat_df['direction'] == 'sent'])}/{len(chat_df[chat_df['direction'] == 'received'])} sent/received"],
            ['Internships', len(internship_df), f"{len(internship_df[internship_df['stipend_min'].notna()])} paid"],
            ['Companies', internship_df['company'].nunique(), f"₹{internship_df['stipend_min'].mean():.0f} avg stipend"],
            ['Locations', internship_df['location'].nunique(), f"{len(internship_df[internship_df['mode'] == 'remote'])} remote"]
        ]
        
        ax6.axis('tight')
        ax6.axis('off')
        table = ax6.table(cellText=summary_data, 
                         colLabels=['Metric', 'Count', 'Details'],
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax6.set_title('Summary Statistics', fontsize=14, fontweight='bold', pad=20)
        
        plt.suptitle('Turerez Analytics Dashboard', fontsize=20, fontweight='bold')
        
        output_path = self.output_directory / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path)

# Import numpy for trend lines
try:
    import numpy as np
except ImportError:
    # Fallback if numpy not available
    np = None
