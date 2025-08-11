"""
ZeroDev AI CLI - Refactored with Click and Rich.

This module provides a command-line interface for interacting with the ZeroDev backend services.
"""

from pathlib import Path
import yaml
import click
from rich.console import Console

# Import agents and other necessary components
from backend.agents.scaffold_agent import scaffold_project
from backend.agents.codegen_agent import generate_code_from_spec
from backend.agents.ci_cd_agent import create_ci_cd_files
from backend.agents.deploy_agent import deploy_project
from backend.models.spec_model import ProjectSpec
from backend.version_engine.rollback import rollback_version
from backend.agents.manager import AgentManager

# Initialize Rich Console for beautiful output
console = Console()

@click.group()
def cli():
    """
    ZeroDev AI CLI: A tool for bootstrapping and managing AI-powered software projects.
    """
    console.print("[bold cyan]ZeroDev AI CLI[/bold cyan] 🚀")

@cli.command()
@click.argument("project_name")
def init(project_name: str):
    """Scaffold a new project directory."""
    console.print(f"Scaffolding new project: [bold magenta]{project_name}[/bold magenta]...")
    scaffold_project(Path.cwd() / project_name)
    console.print(f"✅ Project [bold green]{project_name}[/bold green] scaffolded successfully!")

@cli.command()
@click.argument("project_path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
async def generate(project_path: str):
    """Generate code from a spec file in the given project path."""
    agent_manager = AgentManager()
    project_dir = Path(project_path)
    config_path = project_dir / "config.yaml"

    console.print(f"⚙️ Generating code for project in [bold magenta]{project_dir}[/bold magenta]...")

    if not config_path.exists():
        console.print(f"❌ [bold red]Error:[/bold red] `config.yaml` not found in {project_dir}")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        spec = ProjectSpec(**raw)

        # Use the agent manager to execute the agent with resilience
        await agent_manager.execute_agent(generate_code_from_spec, spec, project_dir)

        console.print("✅ Code generation complete.")
    except Exception as e:
        console.print(f"❌ [bold red]An unexpected error occurred:[/bold red] {e}")

@cli.command("ci-cd")
@click.argument("project_path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
def ci_cd(project_path: str):
    """Add CI/CD, testing, and Docker setup to a project."""
    project_dir = Path(project_path)
    console.print(f"🚀 Setting up CI/CD for [bold magenta]{project_dir.name}[/bold magenta]...")
    create_ci_cd_files(project_path=str(project_dir), project_name=project_dir.name)
    console.print("✅ CI/CD setup complete.")

@cli.command()
@click.argument("project_path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--port", default=8000, help="Host port to expose.")
@click.option("--push", is_flag=True, help="Push image to Docker registry.")
@click.option("--no-health", is_flag=True, help="Skip health check after deploy.")
def deploy(project_path: str, port: int, push: bool, no_health: bool):
    """Build and run the Docker container for a project."""
    project_dir = Path(project_path)
    console.print(f"🚢 Deploying project [bold magenta]{project_dir.name}[/bold magenta]...")
    deploy_project(
        project_path=str(project_dir),
        project_name=project_dir.name,
        port=port,
        push_to_registry=push,
        health_check=not no_health
    )
    console.print("✅ Deployment complete.")

@cli.command()
@click.argument("file_path")
@click.argument("version")
def rollback(file_path: str, version: str):
    """Rollback a file to a previous version."""
    console.print(f"⏪ Rolling back [bold magenta]{file_path}[/bold magenta] to version [bold yellow]{version}[/bold yellow]...")
    rollback_version(file_path, version)
    console.print("✅ Rollback complete.")

if __name__ == "__main__":
    cli()
