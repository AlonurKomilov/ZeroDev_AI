"""
This module contains the agents responsible for the transformation tasks,
starting with the ForeignCodeScannerAgent.
"""
import os
import ast
import json

from backend.core.logger import get_logger
from backend.transformation.orchestration import transformation_orchestrator, TransformationState

log = get_logger(__name__)


class CodeVisitor(ast.NodeVisitor):
    """
    An AST visitor that extracts information about classes, functions, and imports.
    """
    def __init__(self):
        self.imports = []
        self.functions = []
        self.classes = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.functions.append({
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "lineno": node.lineno
        })
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes.append({
            "name": node.name,
            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
            "lineno": node.lineno
        })
        self.generic_visit(node)


def foreign_code_scanner_agent(job_id: str):
    """
    Scans a cloned repository, parses Python files into an AST, and builds a
    map of the project's architecture.
    """
    log.info(f"Starting foreign_code_scanner_agent for job_id: {job_id}")
    job = transformation_orchestrator.get_job_status(job_id)
    if not job or "error" in job or not job.get("cloned_repo_path"):
        log.error(f"Invalid job or missing cloned_repo_path for job_id: {job_id}")
        return

    repo_path = job["cloned_repo_path"]
    architecture_map = {}

    log.info(f"Scanning Python files in {repo_path}...")
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source_code = f.read()
                        tree = ast.parse(source_code)
                        visitor = CodeVisitor()
                        visitor.visit(tree)

                        architecture_map[relative_path] = {
                            "imports": visitor.imports,
                            "functions": visitor.functions,
                            "classes": visitor.classes,
                        }
                except Exception as e:
                    log.warning(f"Could not parse AST for {file_path}: {e}")
                    architecture_map[relative_path] = {"error": f"Could not parse file: {e}"}

    log.info(f"Finished scanning. Found {len(architecture_map)} Python files.")

    # Update the job state with the architecture map
    transformation_orchestrator.update_job_state(
        job_id,
        TransformationState.REFACTORING, # Set state for the next step
        {"architecture_map": json.dumps(architecture_map, indent=2)}
    )

    # Trigger the next task in the workflow
    from backend.transformation.tasks import refactor_task
    refactor_task.delay(job_id)
    log.info(f"Dispatched refactor_task for job {job_id}.")
