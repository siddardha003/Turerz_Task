"""
Simple CLI tool for testing Turerz functionality.
Demonstrates model creation and utility functions.
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

app = typer.Typer(help="Turerz - Internshala Automation CLI")
console = Console()


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
def config_info():
from datetime import datetime

from src.models import ChatMessage, InternshipSummary, MessageDirection, InternshipMode
from src.utils.date_parser import parse_stipend_amount, parse_relative_date
from src.config import config
from src.browser.manager_selenium import BrowserManager, InternshalaAuth
from src.chat.extractor import ChatMessageExtractor, ChatMessageAnalyzer

app = typer.Typer(help="Turerz - Internshala Automation CLI")
console = Console()


@app.command()
def test_models():
    """Test core data models and validation."""
    console.print("🧪 Testing Turerz Data Models", style="bold blue")
    
    # Test ChatMessage
    console.print("\n📧 Testing ChatMessage model...")
    try:
        message = ChatMessage(
            id="msg_001",
            sender="John Doe",
            direction=MessageDirection.RECEIVED,
            timestamp=datetime.now(),
            raw_text="Hello, I'm interested in the Web Development internship. What's the stipend?",
            cleaned_text="Hello, I'm interested in the Web Development internship. What's the stipend?",
            source_url="https://internshala.com/chat/001"
        )
        console.print(f"✅ ChatMessage created: {message.sender} -> {message.direction.value}")
    except Exception as e:
        console.print(f"❌ ChatMessage failed: {e}")
    
    # Test InternshipSummary
    console.print("\n💼 Testing InternshipSummary model...")
    try:
        internship = InternshipSummary(
            id="int_001",
            title="Web Development Intern",
            company_name="TechCorp Solutions",
            location="Mumbai",
            mode=InternshipMode.HYBRID,
            stipend_text="₹15K-25K /month",
            posted_date=datetime.now(),
            url="https://internshala.com/internship/detail/web-dev-001",
            is_startup=True,
            tags=["react", "node.js", "javascript"]
        )
        console.print(f"✅ Internship created: {internship.title} at {internship.company_name}")
        console.print(f"   Stipend: {internship.stipend_text} -> {internship.stipend_numeric_min}-{internship.stipend_numeric_max}")
    except Exception as e:
        console.print(f"❌ Internship failed: {e}")


@app.command()
def test_parsers():
    """Test utility parsers and functions."""
    console.print("🔧 Testing Utility Parsers", style="bold green")
    
    # Test stipend parsing
    console.print("\n💰 Testing stipend parsing...")
    stipend_tests = [
        "₹5,000-10,000 /month",
        "₹15K /month", 
        "₹5K-20K /month",
        "Unpaid",
        "₹25,000 /month"
    ]
    
    table = Table(title="Stipend Parsing Results")
    table.add_column("Input", style="cyan")
    table.add_column("Min Amount", style="green")
    table.add_column("Max Amount", style="green")
    
    for stipend in stipend_tests:
        min_amt, max_amt = parse_stipend_amount(stipend)
        table.add_row(
            stipend,
            str(min_amt) if min_amt else "None",
            str(max_amt) if max_amt else "None"
        )
    
    console.print(table)
    
    # Test date parsing
    console.print("\n📅 Testing relative date parsing...")
    date_tests = [
        "last 5 days",
        "yesterday",
        "last week",
        "last month",
        "today"
    ]
    
    for date_str in date_tests:
        result = parse_relative_date(date_str)
        status = "✅" if result else "❌"
        console.print(f"{status} '{date_str}' -> {result}")


@app.command()
def config_info():
    """Show current configuration."""
    console.print("⚙️ Configuration Information", style="bold yellow")
    
    panel_content = f"""
🔧 Environment Settings:
   • Output Directory: {config.output_dir}
   • Log Level: {config.log_level}
   • Headless Mode: {config.headless}
   • Browser Timeout: {config.browser_timeout}ms
   
🚦 Rate Limiting:
   • Requests per minute: {config.requests_per_minute}
   • Concurrent requests: {config.concurrent_requests}
   
📧 Credentials:
   • Email configured: {'✅ Yes' if config.internshala_email != 'your_email@example.com' else '❌ No (using placeholder)'}
   • Password configured: {'✅ Yes' if config.internshala_password != 'your_password' else '❌ No (using placeholder)'}
    """
    
    console.print(Panel(panel_content, title="Turerz Configuration", border_style="blue"))


@app.command()
def mock_scrape():
    """Mock scraping operation to test data flow."""
    console.print("🕷️ Mock Scraping Operation", style="bold magenta")
    
    # Create mock data
    console.print("\n📊 Creating mock internship data...")
    
    mock_internships = [
        {
            "title": "Frontend Developer Intern",
            "company": "StartupCorp",
            "stipend": "₹12K-18K /month",
            "location": "Bangalore",
            "is_startup": True
        },
        {
            "title": "Data Science Intern", 
            "company": "BigTech Solutions",
            "stipend": "₹20,000-30,000 /month",
            "location": "Hyderabad",
            "is_startup": False
        },
        {
            "title": "Marketing Intern",
            "company": "Creative Agency",
            "stipend": "₹8K /month",
            "location": "Mumbai",
            "is_startup": True
        }
    ]
    
    table = Table(title="Mock Internship Results")
    table.add_column("Title", style="cyan")
    table.add_column("Company", style="green")
    table.add_column("Stipend", style="yellow")
    table.add_column("Location", style="blue")
    table.add_column("Startup", style="magenta")
    
    for internship in mock_internships:
        min_amt, max_amt = parse_stipend_amount(internship["stipend"])
        table.add_row(
            internship["title"],
            internship["company"],
            f"{min_amt}-{max_amt}" if min_amt else "Unpaid",
            internship["location"],
            "✅" if internship["is_startup"] else "❌"
        )
    
    console.print(table)
    console.print(f"\n✅ Processed {len(mock_internships)} internships successfully")


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


if __name__ == "__main__":
    app()
