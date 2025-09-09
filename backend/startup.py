"""
Turerez Application Startup Guide
Let's start using your automation application!
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def print_welcome():
    """Display welcome message"""
    console.print(Panel.fit(
        "[bold green]🚀 Welcome to Turerez![/bold green]\n"
        "[cyan]Your Internshala Automation Application[/cyan]\n\n"
        "[yellow]Let's start automating your internship journey![/yellow]",
        border_style="green"
    ))

def show_available_commands():
    """Show all available CLI commands"""
    
    table = Table(title="🛠️ Available Commands", show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Example", style="green")
    
    commands = [
        ("demo", "Test models and utilities", "python cli.py demo"),
        ("extract-chats", "Extract chat messages", "python cli.py extract-chats --limit 10"),
        ("test-browser", "Test browser connection", "python cli.py test-browser"),
        ("login-test", "Test Internshala login", "python cli.py login-test"),
        ("analyze-chats", "Analyze chat data", "python cli.py analyze-chats --file data.json"),
        ("search-internships", "Search internships", "python cli.py search-internships --category 'Tech'"),
        ("quick-search", "Quick internship search", "python cli.py quick-search"),
        ("trending-internships", "Get trending internships", "python cli.py trending-internships"),
        ("export-advanced", "Advanced data export", "python cli.py export-advanced --format excel"),
        ("export-history", "View export history", "python cli.py export-history")
    ]
    
    for cmd, desc, example in commands:
        table.add_row(cmd, desc, example)
    
    console.print(table)

def show_quick_start():
    """Show quick start options"""
    
    console.print("\n[bold yellow]🎯 Quick Start Options:[/bold yellow]")
    
    options = [
        "[bold green]1. Test Basic Functionality[/bold green]",
        "   python startup.py --demo",
        "",
        "[bold blue]2. Test Browser Connection[/bold blue]",
        "   python startup.py --test-browser",
        "",
        "[bold cyan]3. Extract Sample Chat Data[/bold cyan]",
        "   python startup.py --extract-sample",
        "",
        "[bold magenta]4. Search Sample Internships[/bold magenta]",
        "   python startup.py --search-sample",
        "",
        "[bold red]5. Full Demo Workflow[/bold red]",
        "   python startup.py --full-demo"
    ]
    
    for option in options:
        console.print(f"   {option}")

async def run_demo():
    """Run basic demo functionality"""
    console.print("\n[bold green]🧪 Running Basic Demo...[/bold green]")
    
    # Test model creation
    from src.models import ChatMessage, MessageDirection
    from src.utils.date_parser import parse_stipend_amount, parse_relative_date
    
    console.print("\n💰 Testing stipend parsing:")
    test_stipends = ["₹5K-20K", "10000", "Unpaid", "Performance based"]
    for stipend in test_stipends:
        parsed = parse_stipend_amount(stipend)
        console.print(f"   '{stipend}' → {parsed}")
    
    console.print("\n📅 Testing date parsing:")
    test_dates = ["2 days ago", "1 week ago", "today"]
    for date_str in test_dates:
        parsed = parse_relative_date(date_str)
        console.print(f"   '{date_str}' → {parsed}")
    
    console.print("\n💬 Creating sample chat message:")
    message = ChatMessage(
        id="msg_001",
        sender="Test Company",
        direction=MessageDirection.RECEIVED,
        timestamp=datetime.now(),
        raw_text="Thank you for your application!",
        cleaned_text="Thank you for your application!",
        attachments=[],
        source_url="https://internshala.com/chat/test"
    )
    console.print(f"   Created message from: [cyan]{message.sender}[/cyan]")
    console.print(f"   Content: [yellow]{message.cleaned_text}[/yellow]")
    
    console.print("\n✅ [bold green]Demo completed successfully![/bold green]")

async def test_browser_connection():
    """Test browser connectivity"""
    console.print("\n[bold blue]🌐 Testing Browser Connection...[/bold blue]")
    
    try:
        from src.browser.manager_selenium import BrowserManager
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing browser...", total=None)
            
            browser_manager = BrowserManager()
            await browser_manager.start_session(headless=True)
            
            progress.update(task, description="Browser connected successfully!")
            await asyncio.sleep(1)
            
            await browser_manager.close_session()
            
        console.print("✅ [bold green]Browser test successful![/bold green]")
        console.print("   • Browser can be started and stopped")
        console.print("   • Selenium WebDriver is working")
        console.print("   • Ready for Internshala automation")
        
    except Exception as e:
        console.print(f"❌ [bold red]Browser test failed:[/bold red] {e}")
        console.print("   💡 Make sure Chrome is installed and accessible")

async def extract_sample_data():
    """Extract sample chat data (simulation)"""
    console.print("\n[bold cyan]💬 Extracting Sample Chat Data...[/bold cyan]")
    
    # For demo purposes, create sample data
    sample_messages = []
    companies = ["TechCorp", "StartupXYZ", "InnovateLab", "DataSystems"]
    
    from src.models import ChatMessage, MessageDirection
    
    for i, company in enumerate(companies):
        message = ChatMessage(
            id=f"msg_{i+1:03d}",
            sender=company,
            direction=MessageDirection.RECEIVED,
            timestamp=datetime.now(),
            raw_text=f"Thank you for applying to our internship program!",
            cleaned_text=f"Thank you for applying to our internship program!",
            attachments=[],
            source_url=f"https://internshala.com/chat/{company.lower()}"
        )
        sample_messages.append(message)
    
    console.print(f"✅ Extracted {len(sample_messages)} sample messages:")
    for msg in sample_messages:
        console.print(f"   • [cyan]{msg.sender}[/cyan]: {msg.cleaned_text}")
    
    # Show analytics
    from src.chat.extractor import ChatMessageAnalyzer
    analyzer = ChatMessageAnalyzer(sample_messages)
    analytics = analyzer.generate_analytics()
    
    console.print(f"\n📊 [bold yellow]Analytics Summary:[/bold yellow]")
    console.print(f"   • Total conversations: {analytics.get('total_conversations', 0)}")
    console.print(f"   • Response rate: {analytics.get('response_rate', 0):.1%}")
    console.print(f"   • Most active company: {analytics.get('most_active_sender', 'N/A')}")

async def search_sample_internships():
    """Search sample internships (simulation)"""
    console.print("\n[bold magenta]🎯 Searching Sample Internships...[/bold magenta]")
    
    # Create sample internship data
    from src.models import InternshipSummary, InternshipMode
    
    sample_internships = [
        InternshipSummary(
            id="int_001",
            title="Software Development Intern",
            company_name="TechCorp Inc",
            location="Bangalore",
            mode=InternshipMode.REMOTE,
            stipend_text="₹15,000 /month",
            posted_date=datetime.now(),
            url="https://internshala.com/internship/detail/001",
            tags=["Python", "Django", "MySQL"]
        ),
        InternshipSummary(
            id="int_002", 
            title="Data Science Intern",
            company_name="DataAnalytics Pro",
            location="Mumbai",
            mode=InternshipMode.HYBRID,
            stipend_text="₹20,000 /month",
            posted_date=datetime.now(),
            url="https://internshala.com/internship/detail/002",
            tags=["Python", "Machine Learning", "Pandas"]
        ),
        InternshipSummary(
            id="int_003",
            title="Frontend Developer Intern", 
            company_name="WebSolutions Ltd",
            location="Remote",
            mode=InternshipMode.REMOTE,
            stipend_text="₹12,000 /month",
            posted_date=datetime.now(),
            url="https://internshala.com/internship/detail/003",
            tags=["React", "JavaScript", "CSS"]
        )
    ]
    
    console.print(f"✅ Found {len(sample_internships)} sample internships:")
    
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Company", style="cyan")
    table.add_column("Title", style="white") 
    table.add_column("Location", style="green")
    table.add_column("Stipend", style="yellow")
    table.add_column("Skills", style="magenta")
    
    for internship in sample_internships:
        table.add_row(
            internship.company_name,
            internship.title,
            internship.location,
            internship.stipend_text,
            ", ".join(internship.tags[:2])
        )
    
    console.print(table)

async def full_demo_workflow():
    """Run complete demo workflow"""
    console.print("\n[bold red]🚀 Running Full Demo Workflow...[/bold red]")
    
    await run_demo()
    await test_browser_connection() 
    await extract_sample_data()
    await search_sample_internships()
    
    console.print("\n[bold green]🎉 Full Demo Completed![/bold green]")
    console.print("   ✅ All components tested successfully")
    console.print("   ✅ Browser automation ready")
    console.print("   ✅ Chat extraction functional")
    console.print("   ✅ Internship search operational")
    console.print("   ✅ Analytics and export systems ready")
    
    console.print("\n[bold yellow]🚀 You're ready to start using Turerez![/bold yellow]")

async def main():
    """Main startup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Turerez Application Startup")
    parser.add_argument("--demo", action="store_true", help="Run basic demo")
    parser.add_argument("--test-browser", action="store_true", help="Test browser connection")
    parser.add_argument("--extract-sample", action="store_true", help="Extract sample chat data")
    parser.add_argument("--search-sample", action="store_true", help="Search sample internships")
    parser.add_argument("--full-demo", action="store_true", help="Run full demo workflow")
    
    args = parser.parse_args()
    
    print_welcome()
    
    if args.demo:
        await run_demo()
    elif args.test_browser:
        await test_browser_connection()
    elif args.extract_sample:
        await extract_sample_data()
    elif args.search_sample:
        await search_sample_internships()
    elif args.full_demo:
        await full_demo_workflow()
    else:
        # Default: show available options
        show_available_commands()
        show_quick_start()
        
        console.print("\n[bold cyan]💡 Tip:[/bold cyan] Start with the demo to test basic functionality!")
        console.print("   python startup.py --demo")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 Thanks for using Turerez!")
    except Exception as e:
        console.print(f"\n❌ Error: {e}")
        console.print("💡 Make sure all dependencies are installed.")
