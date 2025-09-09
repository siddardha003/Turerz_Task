"""
Simple CLI tool for testing Turerz functionality.
Demonstrates model creation and utility functions with chat extraction.
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

from src.models import ChatMessage, InternshipSummary, MessageDirection, InternshipMode
from src.utils.date_parser import parse_stipend_amount, parse_relative_date
from src.config import config
from src.browser.manager_selenium import BrowserManager, InternshalaAuth
from src.chat.extractor import ChatMessageExtractor, ChatMessageAnalyzer
from src.internships.scraper import InternshipScraper, InternshipSearchFilter
from src.export import ExportManager, ExportOptions, ExportFormat, AnalyticsLevel

app = typer.Typer(help="Turerz - Internshala Automation CLI")
console = Console()


@app.command()
def demo():
    """Demonstrate model creation and utility functions."""
    console.print(Panel("🚀 Turerz Demo - Models & Utilities", style="bold blue"))
    
    # Test stipend parsing
    console.print("\n💰 Testing Stipend Parsing:")
    test_stipends = ["₹5K-20K", "10000", "Unpaid", "Performance based"]
    
    for stipend in test_stipends:
        parsed = parse_stipend_amount(stipend)
        console.print(f"  '{stipend}' → {parsed}")
    
    # Test relative date parsing
    console.print("\n📅 Testing Date Parsing:")
    test_dates = ["2 days ago", "1 week ago", "today", "invalid date"]
    
    for date_str in test_dates:
        parsed = parse_relative_date(date_str)
        console.print(f"  '{date_str}' → {parsed}")
    
    # Test ChatMessage model
    console.print("\n💬 Testing ChatMessage Model:")
    
    message = ChatMessage(
        id="msg_001",
        sender="HR Manager",
        direction=MessageDirection.RECEIVED,
        timestamp=datetime.now(),
        raw_text="Thank you for applying! When can you start?",
        cleaned_text="Thank you for applying! When can you start?",
        attachments=[],
        source_url="https://internshala.com/chat/123"
    )
    
    console.print(f"  Message: {message.cleaned_text}")
    console.print(f"  Sender: {message.sender}")
    console.print(f"  Direction: {message.direction.value}")
    
    console.print("\n✅ Demo completed successfully!")


@app.command()
def extract_chats(
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of messages to extract"),
    email: str = typer.Option(None, "--email", "-e", help="Email for login"),
    password: str = typer.Option(None, "--password", "-p", help="Password for login"),
    export_csv: bool = typer.Option(True, "--export", help="Export to CSV file"),
    include_sent: bool = typer.Option(True, "--sent", help="Include sent messages"),
    include_received: bool = typer.Option(True, "--received", help="Include received messages")
):
    """Extract chat messages from Internshala."""
    console.print(Panel("💬 Extracting Chat Messages", style="bold blue"))
    
    async def run_extraction():
        try:
            # Authenticate if credentials provided
            if email and password:
                console.print("🔐 Logging in...")
                auth = InternshalaAuth()
                login_success = await auth.login(email, password)
                if not login_success:
                    console.print("❌ Login failed", style="bold red")
                    return
                console.print("✅ Login successful", style="green")
            
            # Extract messages
            async with ChatMessageExtractor() as extractor:
                console.print(f"📡 Extracting up to {limit} messages...")
                
                messages = await extractor.extract_all_messages(
                    limit=limit,
                    include_sent=include_sent,
                    include_received=include_received
                )
                
                if not messages:
                    console.print("⚠️ No messages found", style="yellow")
                    return
                
                console.print(f"✅ Extracted {len(messages)} messages", style="green")
                
                # Show summary
                analyzer = ChatMessageAnalyzer(messages)
                stats = analyzer.get_summary_stats()
                
                # Create summary table
                summary_table = Table(title="Chat Messages Summary")
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="white")
                
                summary_table.add_row("Total Messages", str(stats.get('total_messages', 0)))
                summary_table.add_row("Sent Messages", str(stats.get('sent_messages', 0)))
                summary_table.add_row("Received Messages", str(stats.get('received_messages', 0)))
                summary_table.add_row("Unique Senders", str(stats.get('unique_senders', 0)))
                summary_table.add_row("Messages with Attachments", str(stats.get('messages_with_attachments', 0)))
                
                if stats.get('date_range'):
                    earliest = stats['date_range']['earliest'].strftime("%Y-%m-%d %H:%M")
                    latest = stats['date_range']['latest'].strftime("%Y-%m-%d %H:%M")
                    summary_table.add_row("Date Range", f"{earliest} to {latest}")
                
                console.print(summary_table)
                
                # Show sample messages
                console.print("\n📋 Sample Messages:")
                messages_table = Table()
                messages_table.add_column("Sender", style="cyan", width=15)
                messages_table.add_column("Direction", style="magenta", width=10)
                messages_table.add_column("Message", style="white", width=50)
                messages_table.add_column("Time", style="yellow", width=15)
                
                for msg in messages[:5]:  # Show first 5 messages
                    direction_emoji = "➡️" if msg.direction == MessageDirection.SENT else "⬅️"
                    messages_table.add_row(
                        msg.sender[:15],
                        f"{direction_emoji} {msg.direction.value}",
                        msg.cleaned_text[:50] + "..." if len(msg.cleaned_text) > 50 else msg.cleaned_text,
                        msg.timestamp.strftime("%H:%M")
                    )
                
                console.print(messages_table)
                
                # Export to CSV
                if export_csv:
                    console.print("\n💾 Exporting to CSV...")
                    csv_file = await extractor.export_to_csv(messages)
                    console.print(f"✅ Exported to: {csv_file}", style="green")
                
                console.print("\n🎉 Chat extraction completed!", style="bold green")
                
        except Exception as e:
            console.print(f"❌ Chat extraction failed: {e}", style="bold red")
    
    asyncio.run(run_extraction())


@app.command()
def test_browser():
    """Test browser automation functionality."""
    console.print(Panel("🚀 Testing Browser Automation", style="bold blue"))
    
    async def run_test():
        try:
            async with BrowserManager() as browser:
                console.print("✅ Browser started successfully", style="green")
                
                # Test navigation
                console.print("📡 Testing navigation to Internshala...")
                await browser.internshala_bot.browser.navigate_to("https://internshala.com")
                
                title = browser.internshala_bot.browser.driver.title
                console.print(f"📄 Page title: {title}", style="cyan")
                
                # Test authentication check
                console.print("🔍 Testing authentication check...")
                is_auth = await browser.check_authentication()
                
                if is_auth:
                    console.print("✅ User is authenticated", style="green")
                else:
                    console.print("ℹ️ User is not authenticated", style="yellow")
                
                console.print("🎉 Browser automation test completed!", style="bold green")
                
        except Exception as e:
            console.print(f"❌ Browser test failed: {e}", style="bold red")
    
    asyncio.run(run_test())


@app.command()
def test_internships_search():
    """Test internship search functionality."""
    console.print(Panel("🔍 Testing Internship Search", style="bold blue"))
    
    async def run_search():
        try:
            async with BrowserManager() as browser:
                console.print("🚀 Starting internship search...")
                
                # Search for Python internships
                internships = await browser.search_internships(
                    query="python",
                    location="",
                    limit=5
                )
                
                if internships:
                    console.print(f"✅ Found {len(internships)} internships", style="green")
                    
                    # Display results in a table
                    table = Table(title="Found Internships")
                    table.add_column("Title", style="cyan")
                    table.add_column("Company", style="magenta")
                    table.add_column("Location", style="yellow")
                    table.add_column("Stipend", style="green")
                    
                    for internship in internships[:3]:  # Show first 3
                        table.add_row(
                            internship.get("title", "N/A")[:30],
                            internship.get("company", "N/A")[:20],
                            internship.get("location", "N/A")[:15],
                            internship.get("stipend", "N/A")[:15]
                        )
                    
                    console.print(table)
                else:
                    console.print("⚠️ No internships found", style="yellow")
                
        except Exception as e:
            console.print(f"❌ Search test failed: {e}", style="bold red")
    
    asyncio.run(run_search())


@app.command()
def login_test(
    email: str = typer.Option(None, "--email", "-e", help="Email for login"),
    password: str = typer.Option(None, "--password", "-p", help="Password for login")
):
    """Test login functionality."""
    console.print(Panel("🔐 Testing Login", style="bold blue"))
    
    if not email:
        email = typer.prompt("Enter email")
    if not password:
        password = typer.prompt("Enter password", hide_input=True)
    
    async def run_login():
        try:
            auth = InternshalaAuth()
            success = await auth.login(email, password)
            
            if success:
                console.print("✅ Login successful!", style="bold green")
            else:
                console.print("❌ Login failed", style="bold red")
                
        except Exception as e:
            console.print(f"❌ Login test failed: {e}", style="bold red")
    
    asyncio.run(run_login())


@app.command()
def analyze_chats(
    csv_file: str = typer.Argument(..., help="Path to CSV file with extracted messages"),
    keyword: str = typer.Option(None, "--search", "-s", help="Search for specific keyword")
):
    """Analyze extracted chat messages from CSV file."""
    console.print(Panel("📊 Analyzing Chat Messages", style="bold blue"))
    
    try:
        import pandas as pd
        
        # Read CSV file
        df = pd.read_csv(csv_file)
        console.print(f"📂 Loaded {len(df)} messages from {csv_file}")
        
        # Convert to ChatMessage objects
        messages = []
        for _, row in df.iterrows():
            try:
                message = ChatMessage(
                    id=row['id'],
                    sender=row['sender'],
                    direction=MessageDirection(row['direction']),
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    raw_text=row['raw_text'],
                    cleaned_text=row['cleaned_text'],
                    attachments=row['attachments'].split('; ') if pd.notna(row['attachments']) and row['attachments'] else [],
                    source_url=row['source_url']
                )
                messages.append(message)
            except Exception as e:
                console.print(f"⚠️ Skipped invalid message: {e}", style="yellow")
        
        # Analyze messages
        analyzer = ChatMessageAnalyzer(messages)
        stats = analyzer.get_summary_stats()
        
        # Display comprehensive analysis
        console.print("\n📈 Analysis Results:")
        
        analysis_table = Table(title="Detailed Analysis")
        analysis_table.add_column("Metric", style="cyan")
        analysis_table.add_column("Value", style="white")
        
        analysis_table.add_row("Total Messages", str(stats.get('total_messages', 0)))
        analysis_table.add_row("Sent Messages", str(stats.get('sent_messages', 0)))
        analysis_table.add_row("Received Messages", str(stats.get('received_messages', 0)))
        analysis_table.add_row("Unique Senders", str(stats.get('unique_senders', 0)))
        
        console.print(analysis_table)
        
        # Show senders
        if stats.get('senders_list'):
            console.print("\n👥 Senders:")
            for sender in stats['senders_list'][:10]:  # Show top 10
                console.print(f"  • {sender}")
        
        # Keyword search if provided
        if keyword:
            console.print(f"\n🔍 Searching for '{keyword}':")
            found_messages = analyzer.find_messages_containing(keyword)
            
            if found_messages:
                console.print(f"Found {len(found_messages)} messages containing '{keyword}'")
                
                for msg in found_messages[:3]:  # Show first 3 matches
                    console.print(f"  📝 [{msg.sender}] {msg.cleaned_text[:100]}...")
            else:
                console.print(f"No messages found containing '{keyword}'", style="yellow")
        
        console.print("\n✅ Analysis completed!", style="bold green")
        
    except ImportError:
        console.print("❌ pandas is required for analysis. Install with: pip install pandas", style="bold red")
    except Exception as e:
        console.print(f"❌ Analysis failed: {e}", style="bold red")


@app.command()
def search_internships(
    keywords: str = typer.Option("", "--keywords", "-k", help="Search keywords (comma-separated)"),
    locations: str = typer.Option("", "--locations", "-l", help="Locations (comma-separated)"),
    min_stipend: int = typer.Option(None, "--min-stipend", help="Minimum stipend amount"),
    max_stipend: int = typer.Option(None, "--max-stipend", help="Maximum stipend amount"),
    work_mode: str = typer.Option(None, "--mode", help="Work mode: remote, on-site, hybrid"),
    categories: str = typer.Option("", "--categories", "-c", help="Categories (comma-separated)"),
    company_types: str = typer.Option("", "--company-types", help="Company types (startup, mnc, etc.)"),
    exclude_unpaid: bool = typer.Option(False, "--exclude-unpaid", help="Exclude unpaid internships"),
    with_job_offer: bool = typer.Option(False, "--with-job-offer", help="Only internships with job offers"),
    extract_details: bool = typer.Option(False, "--details", help="Extract detailed information"),
    limit: int = typer.Option(50, "--limit", help="Maximum number of results"),
    export_csv: bool = typer.Option(True, "--export", help="Export to CSV"),
    email: str = typer.Option(None, "--email", "-e", help="Email for login"),
    password: str = typer.Option(None, "--password", "-p", help="Password for login")
):
    """Advanced internship search with filtering options."""
    console.print(Panel("🔍 Advanced Internship Search", style="bold blue"))
    
    async def run_search():
        try:
            # Authenticate if credentials provided
            if email and password:
                console.print("🔐 Logging in...")
                auth = InternshalaAuth()
                login_success = await auth.login(email, password)
                if not login_success:
                    console.print("❌ Login failed", style="bold red")
                    return
                console.print("✅ Login successful", style="green")
            
            # Build search filter
            search_filter = InternshipSearchFilter(
                keywords=keywords.split(",") if keywords else None,
                locations=locations.split(",") if locations else None,
                min_stipend=min_stipend,
                max_stipend=max_stipend,
                work_mode=InternshipMode(work_mode) if work_mode else None,
                categories=categories.split(",") if categories else None,
                company_types=company_types.split(",") if company_types else None,
                exclude_unpaid=exclude_unpaid,
                with_job_offer=with_job_offer if with_job_offer else None
            )
            
            # Display search criteria
            console.print("\n📋 Search Criteria:")
            criteria_table = Table()
            criteria_table.add_column("Filter", style="cyan")
            criteria_table.add_column("Value", style="white")
            
            if keywords:
                criteria_table.add_row("Keywords", keywords)
            if locations:
                criteria_table.add_row("Locations", locations)
            if min_stipend:
                criteria_table.add_row("Min Stipend", f"₹{min_stipend:,}")
            if max_stipend:
                criteria_table.add_row("Max Stipend", f"₹{max_stipend:,}")
            if work_mode:
                criteria_table.add_row("Work Mode", work_mode)
            if categories:
                criteria_table.add_row("Categories", categories)
            if company_types:
                criteria_table.add_row("Company Types", company_types)
            if exclude_unpaid:
                criteria_table.add_row("Exclude Unpaid", "Yes")
            if with_job_offer:
                criteria_table.add_row("With Job Offer", "Yes")
            
            criteria_table.add_row("Extract Details", "Yes" if extract_details else "No")
            criteria_table.add_row("Limit", str(limit))
            
            console.print(criteria_table)
            
            # Search internships
            async with InternshipScraper() as scraper:
                console.print(f"\n🚀 Searching for internships...")
                
                internships = await scraper.search_internships(
                    search_filter=search_filter,
                    limit=limit,
                    extract_details=extract_details
                )
                
                if not internships:
                    console.print("⚠️ No internships found matching criteria", style="yellow")
                    return
                
                console.print(f"✅ Found {len(internships)} internships", style="green")
                
                # Display results summary
                console.print("\n📊 Results Summary:")
                
                # Count by location
                locations_count = {}
                companies_count = {}
                stipend_ranges = {"Unpaid": 0, "₹1-10K": 0, "₹10-25K": 0, "₹25K+": 0}
                
                for internship in internships:
                    # Location stats
                    location = internship.get('location', 'Unknown')
                    locations_count[location] = locations_count.get(location, 0) + 1
                    
                    # Company stats
                    company = internship.get('company', 'Unknown')
                    companies_count[company] = companies_count.get(company, 0) + 1
                    
                    # Stipend stats
                    stipend_text = internship.get('stipend', '')
                    stipend_min, stipend_max = parse_stipend_amount(stipend_text)
                    
                    if stipend_min is None:
                        stipend_ranges["Unpaid"] += 1
                    elif stipend_min < 10000:
                        stipend_ranges["₹1-10K"] += 1
                    elif stipend_min < 25000:
                        stipend_ranges["₹10-25K"] += 1
                    else:
                        stipend_ranges["₹25K+"] += 1
                
                # Display top locations
                console.print("\n🌍 Top Locations:")
                top_locations = sorted(locations_count.items(), key=lambda x: x[1], reverse=True)[:5]
                for location, count in top_locations:
                    console.print(f"  • {location}: {count} internships")
                
                # Display stipend distribution
                console.print("\n💰 Stipend Distribution:")
                for range_name, count in stipend_ranges.items():
                    if count > 0:
                        console.print(f"  • {range_name}: {count} internships")
                
                # Display sample internships
                console.print("\n📋 Sample Results:")
                results_table = Table()
                results_table.add_column("Title", style="cyan", width=25)
                results_table.add_column("Company", style="magenta", width=20)
                results_table.add_column("Location", style="yellow", width=15)
                results_table.add_column("Stipend", style="green", width=12)
                results_table.add_column("Duration", style="blue", width=10)
                
                for internship in internships[:10]:  # Show first 10
                    results_table.add_row(
                        internship.get('title', 'N/A')[:25],
                        internship.get('company', 'N/A')[:20],
                        internship.get('location', 'N/A')[:15],
                        internship.get('stipend', 'N/A')[:12],
                        internship.get('duration', 'N/A')[:10]
                    )
                
                console.print(results_table)
                
                # Export to CSV
                if export_csv:
                    console.print("\n💾 Exporting to CSV...")
                    csv_file = await scraper.export_to_csv(internships)
                    console.print(f"✅ Exported to: {csv_file}", style="green")
                
                console.print("\n🎉 Internship search completed!", style="bold green")
                
        except Exception as e:
            console.print(f"❌ Internship search failed: {e}", style="bold red")
    
    asyncio.run(run_search())


@app.command()
def quick_search(
    query: str = typer.Argument(..., help="Quick search query"),
    location: str = typer.Option("", "--location", "-l", help="Location filter"),
    min_stipend: int = typer.Option(None, "--min-stipend", help="Minimum stipend"),
    limit: int = typer.Option(20, "--limit", help="Number of results")
):
    """Quick internship search with minimal options."""
    console.print(Panel(f"⚡ Quick Search: '{query}'", style="bold blue"))
    
    async def run_quick_search():
        try:
            # Simple search filter
            search_filter = InternshipSearchFilter(
                keywords=[query],
                locations=[location] if location else None,
                min_stipend=min_stipend,
                exclude_unpaid=True if min_stipend else False
            )
            
            async with InternshipScraper() as scraper:
                console.print(f"🔍 Searching for '{query}' internships...")
                
                internships = await scraper.search_internships(
                    search_filter=search_filter,
                    limit=limit,
                    extract_details=False
                )
                
                if not internships:
                    console.print("⚠️ No internships found", style="yellow")
                    return
                
                console.print(f"✅ Found {len(internships)} internships", style="green")
                
                # Quick results table
                table = Table(title=f"Quick Search Results: {query}")
                table.add_column("#", style="dim", width=3)
                table.add_column("Title", style="cyan", width=30)
                table.add_column("Company", style="magenta", width=20)
                table.add_column("Location", style="yellow", width=15)
                table.add_column("Stipend", style="green", width=12)
                
                for i, internship in enumerate(internships, 1):
                    table.add_row(
                        str(i),
                        internship.get('title', 'N/A')[:30],
                        internship.get('company', 'N/A')[:20],
                        internship.get('location', 'N/A')[:15],
                        internship.get('stipend', 'N/A')[:12]
                    )
                
                console.print(table)
                
                # Auto-export
                csv_file = await scraper.export_to_csv(internships, f"quick_search_{query.replace(' ', '_')}.csv")
                console.print(f"\n💾 Results saved to: {csv_file}", style="dim")
                
        except Exception as e:
            console.print(f"❌ Quick search failed: {e}", style="bold red")
    
    asyncio.run(run_quick_search())


@app.command()
def trending_internships(
    limit: int = typer.Option(30, "--limit", help="Number of results"),
    category: str = typer.Option("", "--category", help="Filter by category"),
    export_csv: bool = typer.Option(True, "--export", help="Export to CSV")
):
    """Find trending/popular internships."""
    console.print(Panel("📈 Trending Internships", style="bold blue"))
    
    async def run_trending():
        try:
            # Search for recent internships with good stipends
            search_filter = InternshipSearchFilter(
                min_stipend=5000,  # At least 5K stipend
                categories=[category] if category else None,
                exclude_unpaid=True
            )
            
            async with InternshipScraper() as scraper:
                console.print("🔥 Finding trending internships...")
                
                internships = await scraper.search_internships(
                    search_filter=search_filter,
                    limit=limit * 2,  # Get more to filter best ones
                    extract_details=False
                )
                
                if not internships:
                    console.print("⚠️ No trending internships found", style="yellow")
                    return
                
                # Sort by stipend and recency (basic trending logic)
                def trending_score(internship):
                    stipend_text = internship.get('stipend', '')
                    stipend_min, _ = parse_stipend_amount(stipend_text)
                    return stipend_min or 0
                
                trending = sorted(internships, key=trending_score, reverse=True)[:limit]
                
                console.print(f"✅ Found {len(trending)} trending internships", style="green")
                
                # Display trending table
                trending_table = Table(title="🔥 Trending Internships")
                trending_table.add_column("Rank", style="gold1", width=5)
                trending_table.add_column("Title", style="cyan", width=25)
                trending_table.add_column("Company", style="magenta", width=20)
                trending_table.add_column("Stipend", style="green", width=12)
                trending_table.add_column("Location", style="yellow", width=15)
                
                for i, internship in enumerate(trending, 1):
                    rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
                    
                    trending_table.add_row(
                        rank_emoji,
                        internship.get('title', 'N/A')[:25],
                        internship.get('company', 'N/A')[:20],
                        internship.get('stipend', 'N/A')[:12],
                        internship.get('location', 'N/A')[:15]
                    )
                
                console.print(trending_table)
                
                # Export if requested
                if export_csv:
                    csv_file = await scraper.export_to_csv(trending, "trending_internships.csv")
                    console.print(f"\n💾 Exported to: {csv_file}", style="green")
                
                console.print("\n🎉 Trending search completed!", style="bold green")
                
        except Exception as e:
            console.print(f"❌ Trending search failed: {e}", style="bold red")
    
    asyncio.run(run_trending())


@app.command()
def export_advanced(
    data_type: str = typer.Argument(..., help="Data type: 'chat', 'internship', or 'combined'"),
    format: str = typer.Option("excel", "--format", "-f", help="Export format: csv, json, excel, html, markdown"),
    analytics_level: str = typer.Option("comprehensive", "--analytics", "-a", help="Analytics level: basic, standard, advanced, comprehensive"),
    include_charts: bool = typer.Option(True, "--charts/--no-charts", help="Include visualizations"),
    output_dir: str = typer.Option("exports", "--output", "-o", help="Output directory")
):
    """Advanced export with analytics and visualizations."""
    
    async def run_export():
        try:
            console.print(Panel(f"📊 Advanced Export - {data_type.title()}", style="bold blue"))
            
            # Initialize export manager
            export_manager = ExportManager(output_dir)
            
            # Configure export options
            export_format = ExportFormat(format.lower())
            analytics_level_enum = AnalyticsLevel(analytics_level.lower())
            
            options = ExportOptions(
                format=export_format,
                include_analytics=True,
                analytics_level=analytics_level_enum,
                include_charts=include_charts,
                timestamp_suffix=True
            )
            
            console.print(f"🔧 Export Configuration:")
            console.print(f"  Format: {format.upper()}")
            console.print(f"  Analytics: {analytics_level.title()}")
            console.print(f"  Charts: {'Yes' if include_charts else 'No'}")
            console.print(f"  Output: {output_dir}")
            
            if data_type.lower() == "chat":
                # Generate sample chat data for demo
                sample_messages = _generate_sample_chat_messages(20)
                result = await export_manager.export_chat_data(sample_messages, options, include_charts)
                
                console.print(f"\n✅ Chat export completed!", style="green")
                console.print(f"📁 Main file: {result['main_export']}")
                console.print(f"📊 Report: {result['report']}")
                
                if result['charts']:
                    console.print(f"📈 Charts generated: {len(result['charts'])}")
                
            elif data_type.lower() == "internship":
                # Generate sample internship data for demo
                sample_internships = _generate_sample_internship_data(50)
                result = await export_manager.export_internship_data(sample_internships, options, include_charts)
                
                console.print(f"\n✅ Internship export completed!", style="green")
                console.print(f"📁 Main file: {result['main_export']}")
                console.print(f"📊 Report: {result['report']}")
                
                if result['charts']:
                    console.print(f"📈 Charts generated: {len(result['charts'])}")
                
            elif data_type.lower() == "combined":
                # Generate sample data for both
                sample_messages = _generate_sample_chat_messages(15)
                sample_internships = _generate_sample_internship_data(30)
                
                result = await export_manager.export_combined_data(sample_messages, sample_internships, options)
                
                console.print(f"\n✅ Combined export completed!", style="green")
                console.print(f"📁 Chat file: {result['chat_export']['main_export']}")
                console.print(f"📁 Internship file: {result['internship_export']['main_export']}")
                console.print(f"📊 Combined report: {result['combined_report']}")
                console.print(f"📈 Dashboard: {result['dashboard']}")
                
            else:
                console.print(f"❌ Invalid data type: {data_type}", style="red")
                console.print("Valid types: chat, internship, combined")
                return
            
            console.print(f"\n🎉 Advanced export completed successfully!", style="bold green")
            
        except Exception as e:
            console.print(f"❌ Export failed: {e}", style="bold red")
    
    asyncio.run(run_export())


@app.command()
def export_history():
    """Show export history and cleanup options."""
    console.print(Panel("📚 Export History", style="bold blue"))
    
    try:
        export_manager = ExportManager()
        history = export_manager.get_export_history()
        
        if not history:
            console.print("📭 No exports found", style="yellow")
            return
        
        # Display history table
        history_table = Table(title="Recent Exports")
        history_table.add_column("Filename", style="cyan", width=30)
        history_table.add_column("Type", style="magenta", width=10)
        history_table.add_column("Size (MB)", style="green", width=10)
        history_table.add_column("Created", style="yellow", width=20)
        
        for export in history[:20]:  # Show last 20 exports
            history_table.add_row(
                export['filename'],
                export['type'].title(),
                f"{export['size_mb']:.2f}",
                export['created'][:19].replace('T', ' ')
            )
        
        console.print(history_table)
        
        # Show summary
        total_size = sum(export['size_mb'] for export in history)
        console.print(f"\n📊 Summary: {len(history)} files, {total_size:.2f} MB total")
        
        # Cleanup option
        cleanup = typer.confirm("🧹 Clean up exports older than 30 days?")
        if cleanup:
            cleaned = export_manager.cleanup_old_exports(30)
            console.print(f"✅ Cleaned up {cleaned} old files", style="green")
    
    except Exception as e:
        console.print(f"❌ Failed to get export history: {e}", style="red")


def _generate_sample_chat_messages(count: int) -> list:
    """Generate sample chat messages for demo"""
    import uuid
    from datetime import datetime, timedelta
    import random
    
    messages = []
    senders = ["You", "TechCorp HR", "StartupXYZ", "InnovateLab", "DataSystems"]
    
    for i in range(count):
        direction = MessageDirection.SENT if random.choice([True, False]) else MessageDirection.RECEIVED
        sender = "You" if direction == MessageDirection.SENT else random.choice(senders[1:])
        
        sample_texts = [
            "Hi, I'm interested in the internship position.",
            "Thank you for your application. Can you tell us about your experience?",
            "I have experience with Python, JavaScript, and data analysis.",
            "When would you be available for an interview?",
            "I'm available next week for a call.",
            "Great! We'll send you the interview details soon.",
            "Looking forward to hearing from you.",
            "Can you share your portfolio?",
            "Here's my GitHub link with recent projects.",
            "The internship starts in 2 weeks. Are you interested?"
        ]
        
        message = ChatMessage(
            id=str(uuid.uuid4()),
            sender=sender,
            direction=direction,
            timestamp=datetime.now() - timedelta(hours=random.randint(0, 168)),  # Last week
            raw_text=random.choice(sample_texts),
            cleaned_text=random.choice(sample_texts),
            attachments=[],
            source_url=f"https://internshala.com/chat/{random.randint(100, 999)}"
        )
        messages.append(message)
    
    return messages


def _generate_sample_internship_data(count: int) -> list:
    """Generate sample internship data for demo"""
    import uuid
    from datetime import datetime, timedelta
    import random
    
    internships = []
    companies = ["TechCorp", "StartupXYZ", "InnovateLab", "DataSystems", "WebSolutions", "CloudTech", "AILabs"]
    locations = ["Bangalore", "Mumbai", "Delhi", "Pune", "Hyderabad", "Chennai", "Gurgaon"]
    titles = ["Python Developer", "Data Analyst", "Web Developer", "ML Engineer", "UI/UX Designer", "Marketing Intern"]
    skills = ["Python", "JavaScript", "React", "SQL", "Machine Learning", "Data Analysis", "HTML/CSS"]
    
    for i in range(count):
        stipend_min = random.choice([None, 5000, 8000, 10000, 15000, 20000, 25000])
        stipend_max = stipend_min + random.randint(2000, 5000) if stipend_min else None
        
        internship = InternshipSummary(
            id=str(uuid.uuid4()),
            title=random.choice(titles),
            company=random.choice(companies),
            location=random.choice(locations),
            duration=random.choice([1, 2, 3, 4, 6]),
            stipend_min=stipend_min,
            stipend_max=stipend_max,
            mode=random.choice([InternshipMode.REMOTE, InternshipMode.ON_SITE, InternshipMode.HYBRID]),
            posted_date=datetime.now().date() - timedelta(days=random.randint(1, 30)),
            application_deadline=datetime.now().date() + timedelta(days=random.randint(5, 45)),
            skills_required=random.sample(skills, k=random.randint(2, 4)),
            perks=random.sample(["Certificate", "Flexible hours", "5-day work week"], k=random.randint(1, 3)),
            description=f"Exciting {random.choice(titles).lower()} opportunity at {random.choice(companies)}. Work with cutting-edge technology and gain hands-on experience.",
            internshala_url=f"https://internshala.com/internship/detail/{random.randint(1000000, 9999999)}"
        )
        internships.append(internship)
    
    return internships


if __name__ == "__main__":
    app()
