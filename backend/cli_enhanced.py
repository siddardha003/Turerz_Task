"""
Enhanced CLI with Natural Language Support for Internshala Automation.
Combines MCP tools with natural language processing.
"""

import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.markdown import Markdown
from datetime import datetime
import json

from src.mcp.client import InternshalaAutomationClient
from src.mcp.nlp import NaturalLanguageProcessor
from src.utils.logging import get_logger
from src.config import config

app = typer.Typer(help="Internshala Automation with Natural Language Support")
console = Console()
logger = get_logger(__name__)


@app.command()
def chat():
    """Interactive chat interface for natural language commands."""
    console.print(Panel(
        "[bold blue]🤖 Internshala Automation Assistant[/bold blue]\n\n" +
        "Type natural language commands to interact with Internshala.\n" +
        "Examples:\n" +
        "• 'Download chat messages from the last 5 days'\n" +
        "• 'Find marketing internships at startups'\n" +
        "• 'Search for remote Python opportunities'\n\n" +
        "Type 'help' for more commands or 'exit' to quit.",
        title="Welcome"
    ))
    
    async def run_chat():
        client = InternshalaAutomationClient()
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                
                if user_input.lower() == 'help':
                    help_text = await client.get_help()
                    console.print(Markdown(help_text))
                    continue
                
                if user_input.lower() == 'exports':
                    exports = await client.list_recent_exports()
                    if exports['exports']:
                        table = Table(title="Recent Exports")
                        table.add_column("File", style="cyan")
                        table.add_column("Type", style="magenta")
                        table.add_column("Size (KB)", style="yellow")
                        
                        for export in exports['exports'][:5]:
                            table.add_row(
                                export['filename'],
                                export['type'],
                                str(export['size_kb'])
                            )
                        console.print(table)
                    else:
                        console.print("[yellow]No exports found.[/yellow]")
                    continue
                
                # Process natural language command
                console.print("[dim]Processing your request...[/dim]")
                
                result = await client.process_natural_language_command(user_input)
                
                if result['success']:
                    console.print(f"[green]✅ Understood: {result['parsed_intent']['action']}[/green]")
                    
                    # Show parameters used
                    if result['parsed_intent']['parameters']:
                        console.print(f"[blue]📋 Parameters:[/blue]")
                        for key, value in result['parsed_intent']['parameters'].items():
                            console.print(f"   • {key}: {value}")
                    
                    # Show result
                    if 'result' in result and 'mcp_response' in result['result']:
                        console.print(f"\n[green]🎯 Result:[/green]")
                        response = result['result']['mcp_response']
                        if len(response) > 500:
                            console.print(response[:500] + "...")
                        else:
                            console.print(response)
                else:
                    console.print(f"[red]❌ Error: {result['error']}[/red]")
                    if 'suggestion' in result:
                        console.print(f"[yellow]💡 Suggestion: {result['suggestion']}[/yellow]")
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]❌ Unexpected error: {e}[/red]")
    
    asyncio.run(run_chat())


@app.command()
def process_command(
    command: str = typer.Argument(..., help="Natural language command to process"),
    show_details: bool = typer.Option(False, "--details", "-d", help="Show detailed parsing information")
):
    """Process a single natural language command."""
    
    async def run_command():
        try:
            client = InternshalaAutomationClient()
            
            console.print(f"[cyan]Processing: [/cyan]{command}")
            
            result = await client.process_natural_language_command(command)
            
            if result['success']:
                # Show parsed intent
                intent = result['parsed_intent']
                console.print(f"[green]✅ Action: {intent['action']}[/green]")
                console.print(f"[blue]🎯 Confidence: {intent['confidence']:.2f}[/blue]")
                
                if show_details:
                    console.print(f"\n[yellow]📋 Detailed Parameters:[/yellow]")
                    console.print(json.dumps(intent['parameters'], indent=2))
                
                # Show execution result
                if 'result' in result:
                    console.print(f"\n[green]🚀 Execution Result:[/green]")
                    mcp_response = result['result'].get('mcp_response', 'No response')
                    console.print(mcp_response)
            else:
                console.print(f"[red]❌ Failed to process command[/red]")
                console.print(f"[red]Error: {result['error']}[/red]")
                
                if 'suggestion' in result:
                    console.print(f"\n[yellow]💡 Try this instead:[/yellow]")
                    console.print(result['suggestion'])
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(run_command())


@app.command()
def test_nlp():
    """Test natural language processing capabilities."""
    
    async def run_test():
        console.print(Panel("🧠 Testing Natural Language Processing", style="bold blue"))
        
        test_commands = [
            "Download chat messages from the last 5 days",
            "Find messages that mention stipend above 1000",
            "Show opportunities posted in the last 7 days for Graphic Design", 
            "Download all internships where company is a startup and role is Marketing",
            "Search for remote Python internships",
            "Get details for internship at https://internshala.com/internship/123"
        ]
        
        nlp = NaturalLanguageProcessor()
        
        results_table = Table(title="NLP Parsing Results")
        results_table.add_column("Command", style="cyan", width=40)
        results_table.add_column("Action", style="green", width=20)
        results_table.add_column("Confidence", style="yellow", width=10)
        results_table.add_column("Key Parameters", style="magenta", width=30)
        
        for command in test_commands:
            try:
                intent = await nlp.parse_command(command)
                
                # Extract key parameters for display
                key_params = []
                for key, value in intent.parameters.items():
                    if value is not None and value != "":
                        key_params.append(f"{key}: {value}")
                
                params_str = ", ".join(key_params[:3])  # Show first 3 params
                if len(key_params) > 3:
                    params_str += "..."
                
                results_table.add_row(
                    command[:40] + "..." if len(command) > 40 else command,
                    intent.action,
                    f"{intent.confidence:.2f}",
                    params_str
                )
                
            except Exception as e:
                results_table.add_row(
                    command[:40],
                    "ERROR",
                    "0.00",
                    str(e)[:30]
                )
        
        console.print(results_table)
        console.print("\n[green]✅ NLP testing completed![/green]")
    
    asyncio.run(run_test())


@app.command()
def install_deps():
    """Install required dependencies for MCP and Playwright."""
    console.print(Panel("📦 Installing Dependencies", style="bold blue"))
    
    import subprocess
    import sys
    
    try:
        # Install Python packages
        console.print("Installing Python dependencies...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✅ Python packages installed[/green]")
        else:
            console.print(f"[red]❌ Failed to install packages: {result.stderr}[/red]")
            return
        
        # Install Playwright browsers
        console.print("Installing Playwright browsers...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✅ Playwright browsers installed[/green]")
        else:
            console.print(f"[red]❌ Failed to install browsers: {result.stderr}[/red]")
            return
        
        console.print("\n[green]🎉 All dependencies installed successfully![/green]")
        console.print("[yellow]💡 Don't forget to set your OPENAI_API_KEY in the .env file[/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Installation failed: {e}[/red]")


@app.command()
def setup():
    """Setup guide for MCP integration."""
    console.print(Panel("🚀 MCP Setup Guide", style="bold blue"))
    
    setup_guide = """
# Setting up Internshala MCP Automation

## 1. Environment Configuration
Add these to your `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
INTERNSHALA_EMAIL=your_email@example.com
INTERNSHALA_PASSWORD=your_password
```

## 2. VS Code MCP Setup
1. Install the MCP extension in VS Code
2. Add this to your VS Code settings.json:
```json
{
  "mcp.servers": {
    "internshala-automation": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "cwd": "./backend"
    }
  }
}
```

## 3. Test the Setup
Run these commands to verify everything works:
```bash
python -m cli_enhanced chat          # Interactive mode
python -m cli_enhanced test-nlp      # Test NLP parsing
```

## 4. Example Commands
Try these natural language commands:
- "Download chat messages from the last 5 days"
- "Find marketing internships at startups" 
- "Search for remote Python opportunities"
"""
    
    console.print(Markdown(setup_guide))


if __name__ == "__main__":
    app()
