"""
Export Manager - Coordinates all export and analytics operations
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
from datetime import datetime
import logging

from .data_processor import DataProcessor, ExportOptions, ExportFormat, AnalyticsLevel
from .visualizer import DataVisualizer
from ..models import ChatMessage, InternshipSummary
from ..utils.logging import get_logger

logger = get_logger(__name__)

class ExportManager:
    """
    Central manager for all export operations
    Coordinates data processing, analytics, and visualization
    """
    
    def __init__(self, base_output_directory: str = "exports"):
        """
        Initialize the export manager
        
        Args:
            base_output_directory: Base directory for all exports
        """
        self.base_directory = Path(base_output_directory)
        self.base_directory.mkdir(exist_ok=True)
        
        # Initialize components
        self.processor = DataProcessor(str(self.base_directory / "data"))
        self.visualizer = DataVisualizer(str(self.base_directory / "charts"))
        
        self.logger = get_logger(self.__class__.__name__)
        
        # Create subdirectories
        (self.base_directory / "reports").mkdir(exist_ok=True)
        (self.base_directory / "archives").mkdir(exist_ok=True)
    
    async def export_chat_data(
        self,
        messages: List[ChatMessage],
        options: Optional[ExportOptions] = None,
        include_visualizations: bool = True
    ) -> Dict[str, Any]:
        """
        Complete chat data export with analytics and visualizations
        
        Args:
            messages: List of chat messages
            options: Export configuration
            include_visualizations: Whether to generate charts
            
        Returns:
            Export summary with all generated files
        """
        if options is None:
            options = ExportOptions(
                format=ExportFormat.EXCEL,
                include_analytics=True,
                analytics_level=AnalyticsLevel.COMPREHENSIVE,
                include_charts=include_visualizations
            )
        
        self.logger.info(f"Starting comprehensive chat export for {len(messages)} messages")
        
        try:
            # Process data and generate analytics
            export_result = self.processor.process_chat_data(messages, options)
            
            # Generate visualizations if requested
            charts = {}
            if include_visualizations and options.include_charts:
                df = self.processor._messages_to_dataframe(messages)
                charts = self.visualizer.create_chat_visualizations(df, export_result['analytics'])
            
            # Create comprehensive report
            report_path = await self._create_chat_report(export_result, charts, options)
            
            # Archive if requested
            archive_path = None
            if options.format == ExportFormat.EXCEL:
                archive_path = await self._archive_export("chat", export_result['export_path'], charts)
            
            result = {
                "export_type": "chat_data",
                "message_count": len(messages),
                "main_export": export_result['export_path'],
                "analytics": export_result['analytics'],
                "charts": charts,
                "report": str(report_path),
                "archive": str(archive_path) if archive_path else None,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Chat export completed successfully: {result['main_export']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Chat export failed: {e}")
            raise
    
    async def export_internship_data(
        self,
        internships: List[InternshipSummary],
        options: Optional[ExportOptions] = None,
        include_visualizations: bool = True
    ) -> Dict[str, Any]:
        """
        Complete internship data export with analytics and visualizations
        
        Args:
            internships: List of internship summaries
            options: Export configuration
            include_visualizations: Whether to generate charts
            
        Returns:
            Export summary with all generated files
        """
        if options is None:
            options = ExportOptions(
                format=ExportFormat.EXCEL,
                include_analytics=True,
                analytics_level=AnalyticsLevel.COMPREHENSIVE,
                include_charts=include_visualizations
            )
        
        self.logger.info(f"Starting comprehensive internship export for {len(internships)} internships")
        
        try:
            # Process data and generate analytics
            export_result = self.processor.process_internship_data(internships, options)
            
            # Generate visualizations if requested
            charts = {}
            if include_visualizations and options.include_charts:
                df = self.processor._internships_to_dataframe(internships)
                charts = self.visualizer.create_internship_visualizations(df, export_result['analytics'])
            
            # Create comprehensive report
            report_path = await self._create_internship_report(export_result, charts, options)
            
            # Archive if requested
            archive_path = None
            if options.format == ExportFormat.EXCEL:
                archive_path = await self._archive_export("internship", export_result['export_path'], charts)
            
            result = {
                "export_type": "internship_data",
                "internship_count": len(internships),
                "main_export": export_result['export_path'],
                "analytics": export_result['analytics'],
                "charts": charts,
                "report": str(report_path),
                "archive": str(archive_path) if archive_path else None,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Internship export completed successfully: {result['main_export']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Internship export failed: {e}")
            raise
    
    async def export_combined_data(
        self,
        messages: List[ChatMessage],
        internships: List[InternshipSummary],
        options: Optional[ExportOptions] = None
    ) -> Dict[str, Any]:
        """
        Export combined chat and internship data with cross-analysis
        
        Args:
            messages: List of chat messages
            internships: List of internship summaries
            options: Export configuration
            
        Returns:
            Combined export summary
        """
        if options is None:
            options = ExportOptions(
                format=ExportFormat.EXCEL,
                include_analytics=True,
                analytics_level=AnalyticsLevel.COMPREHENSIVE,
                include_charts=True
            )
        
        self.logger.info(f"Starting combined export: {len(messages)} messages, {len(internships)} internships")
        
        try:
            # Export individual datasets
            chat_result = await self.export_chat_data(messages, options, False)
            internship_result = await self.export_internship_data(internships, options, False)
            
            # Create combined visualizations
            chat_df = self.processor._messages_to_dataframe(messages)
            internship_df = self.processor._internships_to_dataframe(internships)
            
            dashboard_path = self.visualizer.create_comparison_dashboard(chat_df, internship_df)
            
            # Create combined report
            combined_report = await self._create_combined_report(
                chat_result, internship_result, dashboard_path, options
            )
            
            result = {
                "export_type": "combined_data",
                "chat_export": chat_result,
                "internship_export": internship_result,
                "combined_report": str(combined_report),
                "dashboard": dashboard_path,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("Combined export completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Combined export failed: {e}")
            raise
    
    async def _create_chat_report(
        self,
        export_result: Dict[str, Any],
        charts: Dict[str, str],
        options: ExportOptions
    ) -> Path:
        """Create comprehensive chat report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.base_directory / "reports" / f"chat_report_{timestamp}.md"
        
        report_content = f"""# Chat Messages Analysis Report

**Generated on:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total Messages:** {export_result['message_count']}  
**Export Format:** {options.format.value.upper()}  
**Analytics Level:** {options.analytics_level.value.title()}

---

## Executive Summary

This report provides a comprehensive analysis of chat message data extracted from Internshala conversations.

### Key Metrics
"""
        
        # Add analytics summary
        if 'analytics' in export_result:
            analytics = export_result['analytics']
            if 'basic' in analytics:
                basic = analytics['basic']
                report_content += f"""
- **Total Messages:** {basic.get('total_messages', 0)}
- **Unique Senders:** {basic.get('unique_senders', 0)}
- **Sent Messages:** {basic.get('sent_messages', 0)}
- **Received Messages:** {basic.get('received_messages', 0)}
- **Average Message Length:** {basic.get('avg_message_length', 0):.1f} characters
- **Messages with Attachments:** {basic.get('messages_with_attachments', 0)}
"""
        
        # Add charts section
        if charts:
            report_content += "\n## Visualizations\n\n"
            for chart_name, chart_path in charts.items():
                if chart_path:
                    chart_filename = Path(chart_path).name
                    report_content += f"- **{chart_name.replace('_', ' ').title()}:** `{chart_filename}`\n"
        
        # Add detailed analytics
        if 'analytics' in export_result:
            report_content += "\n## Detailed Analytics\n\n"
            analytics = export_result['analytics']
            
            for section_name, section_data in analytics.items():
                if isinstance(section_data, dict):
                    report_content += f"### {section_name.replace('_', ' ').title()}\n\n"
                    for key, value in section_data.items():
                        if isinstance(value, (int, float)):
                            report_content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                        elif isinstance(value, str):
                            report_content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                    report_content += "\n"
        
        report_content += f"""
---

## Files Generated

- **Main Export:** `{Path(export_result['export_path']).name}`
- **Report:** `{report_path.name}`
"""
        
        if charts:
            report_content += "- **Charts:**\n"
            for chart_name, chart_path in charts.items():
                if chart_path:
                    report_content += f"  - {Path(chart_path).name}\n"
        
        report_content += f"""

---

*Report generated by Turerez Export Manager v1.0*
"""
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path
    
    async def _create_internship_report(
        self,
        export_result: Dict[str, Any],
        charts: Dict[str, str],
        options: ExportOptions
    ) -> Path:
        """Create comprehensive internship report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.base_directory / "reports" / f"internship_report_{timestamp}.md"
        
        report_content = f"""# Internship Data Analysis Report

**Generated on:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total Internships:** {export_result['internship_count']}  
**Export Format:** {options.format.value.upper()}  
**Analytics Level:** {options.analytics_level.value.title()}

---

## Executive Summary

This report provides a comprehensive analysis of internship opportunities scraped from Internshala.

### Key Metrics
"""
        
        # Add analytics summary
        if 'analytics' in export_result:
            analytics = export_result['analytics']
            if 'basic' in analytics:
                basic = analytics['basic']
                report_content += f"""
- **Total Internships:** {basic.get('total_internships', 0)}
- **Unique Companies:** {basic.get('unique_companies', 0)}
- **Unique Locations:** {basic.get('unique_locations', 0)}
- **Paid Internships:** {basic.get('paid_internships', 0)}
- **Unpaid Internships:** {basic.get('unpaid_internships', 0)}
- **Average Stipend:** ₹{basic.get('avg_stipend', 0):,.0f}
- **Work from Home:** {basic.get('work_from_home', 0)}
"""
        
        # Add market analysis
        if 'analytics' in export_result and 'market_analysis' in export_result['analytics']:
            market = export_result['analytics']['market_analysis']
            report_content += "\n### Market Analysis\n\n"
            
            if 'top_companies' in market:
                report_content += "**Top Companies:**\n"
                for company, count in list(market['top_companies'].items())[:5]:
                    report_content += f"- {company}: {count} internships\n"
                report_content += "\n"
            
            if 'top_locations' in market:
                report_content += "**Top Locations:**\n"
                for location, count in list(market['top_locations'].items())[:5]:
                    report_content += f"- {location}: {count} internships\n"
                report_content += "\n"
        
        # Add recommendations
        if 'analytics' in export_result and 'recommendations' in export_result['analytics']:
            recommendations = export_result['analytics']['recommendations']
            report_content += "\n## Recommendations\n\n"
            
            if 'best_opportunities' in recommendations:
                report_content += "### Best Opportunities\n\n"
                for i, opp in enumerate(recommendations['best_opportunities'][:5], 1):
                    report_content += f"{i}. **{opp['title']}** at {opp['company']}\n"
                    report_content += f"   - Score: {opp['score']:.1f}\n"
                    report_content += f"   - Reason: {opp['reason']}\n\n"
        
        # Add charts section
        if charts:
            report_content += "\n## Visualizations\n\n"
            for chart_name, chart_path in charts.items():
                if chart_path:
                    chart_filename = Path(chart_path).name
                    report_content += f"- **{chart_name.replace('_', ' ').title()}:** `{chart_filename}`\n"
        
        report_content += f"""

---

## Files Generated

- **Main Export:** `{Path(export_result['export_path']).name}`
- **Report:** `{report_path.name}`
"""
        
        if charts:
            report_content += "- **Charts:**\n"
            for chart_name, chart_path in charts.items():
                if chart_path:
                    report_content += f"  - {Path(chart_path).name}\n"
        
        report_content += f"""

---

*Report generated by Turerez Export Manager v1.0*
"""
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path
    
    async def _create_combined_report(
        self,
        chat_result: Dict[str, Any],
        internship_result: Dict[str, Any],
        dashboard_path: str,
        options: ExportOptions
    ) -> Path:
        """Create combined analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.base_directory / "reports" / f"combined_report_{timestamp}.md"
        
        report_content = f"""# Combined Analysis Report

**Generated on:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Chat Messages:** {chat_result['message_count']}  
**Internships:** {internship_result['internship_count']}  
**Export Format:** {options.format.value.upper()}

---

## Executive Summary

This report provides a combined analysis of chat messages and internship data, offering insights into communication patterns and market opportunities.

## Chat Data Summary

- **Total Messages:** {chat_result['message_count']}
- **Main Export:** `{Path(chat_result['main_export']).name}`
- **Individual Report:** `{Path(chat_result['report']).name}`

## Internship Data Summary

- **Total Internships:** {internship_result['internship_count']}
- **Main Export:** `{Path(internship_result['main_export']).name}`
- **Individual Report:** `{Path(internship_result['report']).name}`

## Combined Insights

### Activity Correlation
The combined dashboard (`{Path(dashboard_path).name}`) shows the relationship between communication activity and internship opportunities.

### Key Observations
- Communication patterns may indicate optimal timing for internship applications
- Message frequency could correlate with application success rates
- Both datasets show temporal patterns that can inform strategy

## Generated Files

### Data Exports
- **Chat Data:** `{Path(chat_result['main_export']).name}`
- **Internship Data:** `{Path(internship_result['main_export']).name}`

### Reports
- **Chat Report:** `{Path(chat_result['report']).name}`
- **Internship Report:** `{Path(internship_result['report']).name}`
- **Combined Report:** `{report_path.name}`

### Visualizations
- **Combined Dashboard:** `{Path(dashboard_path).name}`
"""
        
        # Add chart listings
        if chat_result.get('charts'):
            report_content += "\n### Chat Charts\n"
            for chart_name, chart_path in chat_result['charts'].items():
                if chart_path:
                    report_content += f"- `{Path(chart_path).name}`\n"
        
        if internship_result.get('charts'):
            report_content += "\n### Internship Charts\n"
            for chart_name, chart_path in internship_result['charts'].items():
                if chart_path:
                    report_content += f"- `{Path(chart_path).name}`\n"
        
        report_content += f"""

---

*Combined report generated by Turerez Export Manager v1.0*
"""
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path
    
    async def _archive_export(
        self,
        export_type: str,
        main_file: str,
        charts: Dict[str, str]
    ) -> Optional[Path]:
        """Archive export files into a single package"""
        try:
            import zipfile
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = self.base_directory / "archives" / f"{export_type}_export_{timestamp}.zip"
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add main export file
                zipf.write(main_file, Path(main_file).name)
                
                # Add charts
                for chart_name, chart_path in charts.items():
                    if chart_path and Path(chart_path).exists():
                        zipf.write(chart_path, f"charts/{Path(chart_path).name}")
            
            self.logger.info(f"Created archive: {archive_path}")
            return archive_path
            
        except Exception as e:
            self.logger.warning(f"Failed to create archive: {e}")
            return None
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get history of recent exports"""
        history = []
        
        # Scan export directories
        for export_dir in [self.base_directory / "data", self.base_directory / "reports"]:
            if export_dir.exists():
                for file_path in export_dir.glob("*"):
                    if file_path.is_file():
                        history.append({
                            "filename": file_path.name,
                            "path": str(file_path),
                            "size_mb": file_path.stat().st_size / (1024 * 1024),
                            "created": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "type": "data" if "data" in str(file_path) else "report"
                        })
        
        # Sort by creation time (newest first)
        history.sort(key=lambda x: x["created"], reverse=True)
        
        return history
    
    def cleanup_old_exports(self, days_old: int = 30) -> int:
        """Clean up old export files"""
        from datetime import timedelta
        
        cleanup_count = 0
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for export_dir in [
            self.base_directory / "data", 
            self.base_directory / "charts", 
            self.base_directory / "reports",
            self.base_directory / "archives"
        ]:
            if export_dir.exists():
                for file_path in export_dir.glob("*"):
                    if file_path.is_file():
                        file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_date < cutoff_date:
                            try:
                                file_path.unlink()
                                cleanup_count += 1
                                self.logger.debug(f"Cleaned up old file: {file_path.name}")
                            except Exception as e:
                                self.logger.warning(f"Failed to clean up {file_path.name}: {e}")
        
        self.logger.info(f"Cleaned up {cleanup_count} old export files")
        return cleanup_count
