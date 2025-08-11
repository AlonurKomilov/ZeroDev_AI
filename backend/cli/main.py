"""ZeroDev AI CLI.
Run:
  - `python -m zerodev_ai.cli.main init <project_name>`
  - `python -m zerodev_ai.cli.main generate <project_path>`
  - `python -m zerodev_ai.cli.main ci_cd <project_path>`
  - `python -m zerodev_ai.cli.main deploy <project_path>`
  - `python -m zerodev_ai.cli.main rollback <file_path> <version>`
"""

import argparse
import asyncio
from pathlib import Path
from backend.agents.scaffold_agent import scaffold_project
from backend.agents.codegen_agent import generate_code_from_spec
from backend.agents.ci_cd_agent import create_ci_cd_files
from backend.agents.deploy_agent import deploy_project
from backend.models.spec_model import ProjectSpec
from backend.version_engine.rollback import rollback_version
import yaml

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zerodev", description="ZeroDev AI CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = sub.add_parser("init", help="Scaffold a new project directory")
    p_init.add_argument("project_name", help="Name of the project to generate")

    # generate
    p_gen = sub.add_parser("generate", help="Generate code from spec in given project path")
    p_gen.add_argument("project_path", help="Path to scaffolded project with config.yaml")

    # ci_cd
    p_ci = sub.add_parser("ci_cd", help="Add CI/CD + test + Docker setup to project")
    p_ci.add_argument("project_path", help="Path to the project")

    # deploy
    p_deploy = sub.add_parser("deploy", help="Build + run Docker container for project")
    p_deploy.add_argument("project_path", help="Path to the project")
    p_deploy.add_argument("--port", type=int, default=8000, help="Host port to expose")
    p_deploy.add_argument("--push", action="store_true", help="Push image to Docker registry")
    p_deploy.add_argument("--no-health", action="store_true", help="Skip health check after deploy")

    # rollback
    p_rb = sub.add_parser("rollback", help="Rollback a file to a previous version")
    p_rb.add_argument("file_path", help="Target file to rollback (e.g. agents/ci_cd_agent.py)")
    p_rb.add_argument("version", help="Version to rollback to (e.g. v1.0.0)")

    return parser

def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "init":
        scaffold_project(Path.cwd() / args.project_name)

    elif args.command == "generate":
        project_dir = Path(args.project_path)
        with open(project_dir / "config.yaml", "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        spec = ProjectSpec(**raw)
        asyncio.run(generate_code_from_spec(spec, project_dir))

    elif args.command == "ci_cd":
        create_ci_cd_files(
            project_path=args.project_path,
            project_name=Path(args.project_path).name
        )

    elif args.command == "deploy":
        deploy_project(
            project_path=args.project_path,
            project_name=Path(args.project_path).name,
            port=args.port,
            push_to_registry=args.push,
            health_check=not args.no_health
        )

    elif args.command == "rollback":
        rollback_version(args.file_path, args.version)

if __name__ == "__main__":
    main()
