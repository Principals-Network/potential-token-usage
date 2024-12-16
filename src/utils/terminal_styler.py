from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich import print as rprint
import time
from termcolor import colored
import sys

console = Console()

ASCII_LOGO = """
   ____                           ____      _     _                 _ 
  / ___|__ _ _ __ ___  ___ _ __ |  _ \\ ___(_) __| | __ _ _ __   | |
 | |   / _` | '__/ _ \\/ _ \\ '__|| |_) | '__| |/ _` |/ _` | '_ \\  | |
 | |__| (_| | | |  __/  __/ |   |  __/| |  | | (_| | (_| | | | | |_|
  \\____\\__,_|_|  \\___|\\___|_|   |_|   |_|  |_|\\__,_|\\__,_|_| |_| (_)
"""

def print_logo():
    """Print the styled ASCII logo."""
    console.print(Panel(ASCII_LOGO, style="bold blue"))

def print_phase_header(text):
    """Print a styled phase header."""
    console.print(f"\n[bold cyan]=== {text} ===[/bold cyan]")

def print_step_header(text):
    """Print a styled step header."""
    console.print(f"\n[bold yellow]--- {text} ---[/bold yellow]")

def print_section(title, content):
    """Print a styled section with title and content."""
    console.print(Panel(content, title=f"[bold green]{title}[/bold green]", 
                       border_style="green"))

def animated_ellipsis(text, duration=3):
    """Show animated ellipsis while processing."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=text, total=None)
        time.sleep(duration)

def print_success(text):
    """Print a success message."""
    console.print(f"[bold green]✓ {text}[/bold green]")

def print_info(text):
    """Print an info message."""
    console.print(f"[bold blue]ℹ {text}[/bold blue]")

def print_warning(text):
    """Print a warning message."""
    console.print(f"[bold yellow]⚠ {text}[/bold yellow]")

def print_error(text):
    """Print an error message."""
    console.print(f"[bold red]✗ {text}[/bold red]")

def create_progress_bar(text):
    """Create and return a progress bar."""
    return Progress(
        "[progress.description]{task.description}",
        "[progress.percentage]{task.percentage:>3.0f}%",
        "[progress.bar]{task.completed}/{task.total}",
    )

def typing_animation(text, delay=0.03):
    """Create a typing animation effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write('\n') 