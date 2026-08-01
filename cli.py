import os
import sys
import json
import typer
from typing import Optional

# Ensure UTF-8 output encoding for legacy Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm

from db import init_db, get_application_stats, get_profile_key, save_profile_key
from config_manager import load_config, save_config, DEFAULT_CONFIG
from resume_parser import parse_resume
from job_fetcher import search_jobs
from applier import process_and_apply_job

app = typer.Typer(help="CloudApply - Terminal Job Search & Auto-Application Engine")
console = Console()

@app.command(name="setup")
def setup():
    """Interactive CLI wizard to configure target roles, preferences, and details."""
    console.print(Panel.fit("[bold cyan]CloudApply Configuration Wizard[/bold cyan]", border_style="cyan"))
    
    config = load_config()
    candidate = config.get("candidate", {})
    preferences = config.get("preferences", {})

    full_name = Prompt.ask("Full Name", default=candidate.get("full_name", "Jane Doe"))
    email = Prompt.ask("Email Address", default=candidate.get("email", "janedoe@example.com"))
    phone = Prompt.ask("Phone Number", default=candidate.get("phone", "+1-555-0199"))
    linkedin = Prompt.ask("LinkedIn URL", default=candidate.get("linkedin", "https://linkedin.com/in/janedoe"))
    github = Prompt.ask("GitHub / Portfolio URL", default=candidate.get("github", "https://github.com/janedoe"))
    current_title = Prompt.ask("Current Job Title", default=candidate.get("current_title", "Software Engineer"))
    years_exp = int(Prompt.ask("Years of Experience", default=str(candidate.get("years_experience", 4))))

    roles_str = Prompt.ask("Target Job Roles (comma separated)", default=", ".join(preferences.get("target_roles", ["Software Engineer", "Full Stack Engineer"])))
    target_roles = [r.strip() for r in roles_str.split(",") if r.strip()]

    locations_str = Prompt.ask("Target Locations (comma separated)", default=", ".join(preferences.get("locations", ["Remote", "New York, NY"])))
    locations = [l.strip() for l in locations_str.split(",") if l.strip()]

    min_score = int(Prompt.ask("Minimum Match Score % required to apply", default=str(preferences.get("min_match_score", 65))))

    config["candidate"] = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "current_title": current_title,
        "years_experience": years_exp,
        "work_authorization": "Authorized to work",
        "sponsorship_required": "No"
    }

    config["preferences"] = {
        "target_roles": target_roles,
        "locations": locations,
        "min_match_score": min_score,
        "max_applications_per_run": 10,
        "platforms": ["LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter", "RemoteOK"]
    }

    save_config(config)
    console.print("\n[bold green]✓ Configuration saved successfully![/bold green]\n")

@app.command(name="upload-resume")
def upload_resume(file_path: str):
    """Parse resume PDF/DOCX/TXT file and extract skills & experience."""
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error: File not found at {file_path}[/bold red]")
        raise typer.Exit(1)
        
    console.print(f"[bold yellow]Parsing resume from {file_path}...[/bold yellow]")
    parsed = parse_resume(file_path)
    save_profile_key("resume_parsed", parsed)
    save_profile_key("resume_path", file_path)
    
    console.print(Panel(
        f"[bold green]Resume Parsed Successfully![/bold green]\n\n"
        f"[bold]Detected Email:[/bold] {parsed['email'] or 'Not found'}\n"
        f"[bold]Detected Phone:[/bold] {parsed['phone'] or 'Not found'}\n"
        f"[bold]Extracted Skills ({len(parsed['skills'])}):[/bold] {', '.join(parsed['skills'][:10])}...",
        title="Resume Profile Summary",
        border_style="green"
    ))

@app.command()
def run(dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Simulate without real application submission"),
        limit: int = typer.Option(10, "--limit", "-l", help="Max jobs to process in this run")):
    """Run automated job search, ATS keyword tailoring, cover letter creation, and application sweep."""
    init_db()
    config = load_config()
    resume_parsed = get_profile_key("resume_parsed")
    
    if not resume_parsed:
        # Fallback default resume profile
        resume_parsed = {
            "skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker", "REST API", "Git", "PostgreSQL"],
            "raw_text": "Software Engineer with experience building backend services, web applications, and database integrations."
        }
        console.print("[yellow]Notice: No custom resume uploaded. Using default skill profile. (Run 'python cli.py upload-resume <path>' to attach your own resume)[/yellow]\n")

    target_roles = config["preferences"].get("target_roles", ["Software Engineer"])
    locations = config["preferences"].get("locations", ["Remote"])

    console.print(Panel(
        f"[bold cyan]Starting CloudApply Engine[/bold cyan]\n"
        f"[bold]Target Roles:[/bold] {', '.join(target_roles)}\n"
        f"[bold]Locations:[/bold] {', '.join(locations)}\n"
        f"[bold]Mode:[/bold] {'DRY RUN (Simulation)' if dry_run else 'LIVE APPLICATION'}\n"
        f"[bold]Limit:[/bold] {limit} jobs",
        border_style="cyan"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task1 = progress.add_task("[yellow]Fetching job postings across boards...", total=100)
        jobs = search_jobs(target_roles, locations, results_limit=limit)
        progress.update(task1, completed=100, description=f"[green]Found {len(jobs)} relevant job postings!")

    results_table = Table(title="Application Processing Results")
    results_table.add_column("Company", style="bold white")
    results_table.add_column("Role", style="cyan")
    results_table.add_column("Score", style="magenta")
    results_table.add_column("Status", style="green")
    results_table.add_column("Tailored Keywords", style="yellow")

    applied_count = 0
    skipped_count = 0

    for job in jobs:
        res = process_and_apply_job(job, config, resume_parsed, dry_run=dry_run)
        status = res.get("status", "UNKNOWN")
        score = res.get("match_score", 0)
        keywords = ", ".join(res.get("keywords", [])[:3]) if res.get("keywords") else "-"

        if "APPLIED" in status:
            applied_count += 1
            status_fmt = f"[bold green]{status}[/bold green]"
        else:
            skipped_count += 1
            status_fmt = f"[dim yellow]{status}[/dim yellow]"

        results_table.add_row(
            job["company"],
            job["title"],
            f"{score}%",
            status_fmt,
            keywords
        )

    console.print(results_table)
    console.print(f"\n[bold green]Run Completed![/bold green] Applied: {applied_count} | Skipped: {skipped_count}\n")

@app.command()
def status():
    """View application history dashboard, stats, and interview tracker."""
    init_db()
    stats = get_application_stats()
    
    table = Table(title="Job Application Analytics Dashboard", border_style="cyan")
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="bold white")

    table.add_row("Total Applications Submitted", str(stats.get("APPLIED", 0) + stats.get("SIMULATED_APPLIED", 0)))
    table.add_row("Applications Skipped (Low Match / Dupes)", str(stats.get("SKIPPED_LOW_MATCH", 0) + stats.get("SKIPPED_DUPLICATE", 0)))
    table.add_row("Average Match Score", f"{stats.get('avg_match_score', 0)}%")
    
    console.print(table)

    recent = stats.get("recent", [])
    if recent:
        console.print("\n[bold yellow]Recent Applications & Tailored Packages:[/bold yellow]")
        rec_table = Table(border_style="dim")
        rec_table.add_column("Date", style="dim")
        rec_table.add_column("Role", style="bold white")
        rec_table.add_column("Company", style="cyan")
        rec_table.add_column("Platform", style="blue")
        rec_table.add_column("Score", style="magenta")
        rec_table.add_column("Status", style="green")

        for r in recent:
            # r: (id, job_title, company, platform, match_score, status, applied_at)
            rec_table.add_row(
                str(r[6])[:10] if r[6] else "Today",
                str(r[1]),
                str(r[2]),
                str(r[3]),
                f"{r[4]}%",
                str(r[5])
            )
        console.print(rec_table)

@app.command(name="cloud-deploy")
def cloud_deploy():
    """Generate GitHub Actions workflow so applications run 24/7 in the cloud even when laptop is OFF."""
    workflow_dir = os.path.join(os.path.dirname(__file__), ".github", "workflows")
    os.makedirs(workflow_dir, exist_ok=True)
    workflow_path = os.path.join(workflow_dir, "job_applier.yml")

    content = """name: Continuous Autonomous Job Applier

on:
  schedule:
    # Runs every 6 hours automatically (100% Free on GitHub Actions)
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  apply-jobs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run CloudApply Automated Job Sweep
        run: |
          python cli.py run --limit 10

      - name: Commit & Push DB Application History
        run: |
          git config --global user.name "CloudApply-Bot"
          git config --global user.email "bot@cloudapply.local"
          git add jobs.db generated_applications/
          git diff-index --quiet HEAD || git commit -m "Auto-update job application records [skip ci]"
          git push
"""
    with open(workflow_path, 'w', encoding='utf-8') as f:
        f.write(content)

    console.print(Panel(
        f"[bold green]✓ GitHub Actions Workflow Generated Successfully![/bold green]\n\n"
        f"[bold]Location:[/bold] [yellow]{workflow_path}[/yellow]\n\n"
        f"[bold]How to activate free 24/7 background execution (Runs even when laptop is OFF):[/bold]\n"
        f"1. Push this folder to a GitHub repository (Public or Private).\n"
        f"2. GitHub Actions will automatically trigger every 6 hours.\n"
        f"3. The bot will search, match keywords, tailor resumes, write cover letters, and submit applications autonomously!",
        title="Cloud Background Deployment Ready",
        border_style="green"
    ))

# Alias commands for convenience
@app.command(name="upload_resume", hidden=True)
def upload_resume_alias(file_path: str):
    upload_resume(file_path)

@app.command(name="cloud_deploy", hidden=True)
def cloud_deploy_alias():
    cloud_deploy()

if __name__ == "__main__":
    app()
