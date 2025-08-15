"""
Celery tasks for data migration.
"""

import time
import zipfile
from pathlib import Path

from backend.core.celery_app import celery_app


@celery_app.task
def export_user_data_task(user_id: str):
    """
    A Celery task to export a user's data.

    This task simulates:
    1. Creating a database dump.
    2. Archiving project files.
    3. Generating a restore script.
    """
    # Create a directory to store the exported data
    export_dir = Path(f"/tmp/export_{user_id}")
    export_dir.mkdir(exist_ok=True)

    # 1. Simulate creating a database dump
    db_dump_path = export_dir / "db_dump.sql"
    with open(db_dump_path, "w") as f:
        f.write(f"-- SQL Dump for user {user_id}\n")
        f.write(f"SELECT * FROM projects WHERE user_id = '{user_id}';\n")
        f.write(f"SELECT * FROM users WHERE id = '{user_id}';\n")

    # 2. Simulate archiving project files
    project_files_dir = export_dir / "projects"
    project_files_dir.mkdir(exist_ok=True)
    with open(project_files_dir / "project_1.py", "w") as f:
        f.write(f"# Project 1 for user {user_id}\n")
    with open(project_files_dir / "project_2.py", "w") as f:
        f.write(f"# Project 2 for user {user_id}\n")

    # 3. Simulate generating a restore script
    restore_script_path = export_dir / "restore.sh"
    with open(restore_script_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"# Restore script for user {user_id}\n")
        f.write("echo 'Restoring database'\n")
        f.write("psql -f db_dump.sql\n")
        f.write("echo 'Restoring project files'\n")
        f.write("cp -r projects/* /path/to/projects/\n")

    # Create a zip file of the exported data
    zip_path = Path(f"/tmp/export_{user_id}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in export_dir.rglob("*"):
            zipf.write(file, file.relative_to(export_dir))

    # Simulate some processing time
    time.sleep(5)

    return {
        "message": f"Export complete for user {user_id}. You can download the data from {zip_path}"
    }
