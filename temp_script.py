import os
import subprocess
import sys

print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")

# Install dependencies
# Assuming the script is run from the 'backend' directory
requirements_path = "requirements.txt"
alembic_config_path = "alembic.ini"

pip_command = [sys.executable, "-m", "pip", "install", "-r", requirements_path]
print(f"Running command: {' '.join(pip_command)}")
pip_result = subprocess.run(pip_command, capture_output=True, text=True)
print(f"Pip install stdout:\n{pip_result.stdout}")
print(f"Pip install stderr:\n{pip_result.stderr}")


if pip_result.returncode == 0:
    print("Pip install successful.")
    # Run alembic revision
    # When running from the backend dir, no need for -c
    alembic_command = [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", "Add analytics tables for feedback and security"]
    print(f"Running command: {' '.join(alembic_command)}")
    alembic_result = subprocess.run(alembic_command, capture_output=True, text=True)
    print(f"Alembic revision stdout:\n{alembic_result.stdout}")
    print(f"Alembic revision stderr:\n{alembic_result.stderr}")
else:
    print("Pip install failed, skipping alembic command.")
