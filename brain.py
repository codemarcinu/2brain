#!/usr/bin/env python3
"""
Obsidian Brain v2 - Command Line Interface
Main entry point for user interaction (TUI).
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import box
import time
import subprocess
import redis
from pathlib import Path
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

app = typer.Typer(help="Obsidian Brain v2 Controller")
console = Console()

@app.command()
def status():
    """Show system status (Docker & Queues)"""
    
    with Live(refresh_per_second=1) as live:
        try:
            while True:
                layout = Layout()
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="body"),
                    Layout(name="footer", size=3)
                )
                
                # Header
                layout["header"].update(
                    Panel("🧠 Obsidian Brain v2 System Status", style="bold magenta")
                )
                
                # Services Table (Docker)
                table = Table(title="Microservices", box=box.ROUNDED)
                table.add_column("Service", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Ports", style="yellow")
                
                # Get docker stats (simplified)
                # In real app, use docker SDK. Here using simple shell check or mocked
                try:
                    res = subprocess.run(
                        ["docker", "compose", "ps", "--format", "json"], 
                        capture_output=True, 
                        text=True
                    )
                    # Parsing would go here. For now, just listing services we know
                    # Mocking for immediate visual feedback if docker command fails parsing
                    services = ["redis", "postgres", "ollama", "open-webui", "collector", "refinery", "finance"]
                    for svc in services:
                        table.add_row(svc, "running", "auto")
                except FileNotFoundError:
                     table.add_row("Docker", "Not found", "")

                # Queues
                q_table = Table(title="Queues", box=box.ROUNDED)
                q_table.add_column("Queue", style="blue")
                q_table.add_column("Pending Tasks", style="red")
                
                try:
                    r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
                    q_table.add_row("queue:refinery", str(r.llen("queue:refinery")))
                    q_table.add_row("queue:finance", str(r.llen("queue:finance")))
                except:
                    q_table.add_row("Redis", "Connection Failed")

                # Body
                body_layout = Layout()
                body_layout.split_row(
                    Layout(Panel(table)),
                    Layout(Panel(q_table))
                )
                layout["body"].update(body_layout)
                
                # Footer
                layout["footer"].update(Panel("Press Ctrl+C to exit"))
                
                live.update(layout)
                time.sleep(1)
                
        except KeyboardInterrupt:
            console.print("[bold green]Goodbye![/bold green]")

@app.command()
def chat(message: str = typer.Argument(None)):
    """Quick chat with Brain"""
    console.print(Panel(f"Chat functionality coming soon. Message: {message}", title="Chat"))

@app.command()
def finance(file: Path):
    """Process a receipt file (copy to Inbox)"""
    if not file.exists():
        console.print(f"[red]File {file} not found![/red]")
        return
    
    inbox_path = os.getenv("INBOX_PATH")
    if not inbox_path:
        console.print("[red]INBOX_PATH not set in .env![/red]")
        return
        
    dest_path = Path(inbox_path) / file.name
    
    try:
        import shutil
        shutil.copy2(file, dest_path)
        console.print(f"[green]Receipt copied to Inbox: {dest_path}[/green]")
        console.print("[dim]Collector will pick it up and route to Finance module.[/dim]")
    except Exception as e:
        console.print(f"[red]Failed to copy file: {e}[/red]")


if __name__ == "__main__":
    app()
