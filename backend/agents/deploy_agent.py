import subprocess
import time
from pathlib import Path

import requests


def deploy_project(
    project_path: str,
    project_name: str,
    port: int = 8000,
    push_to_registry: bool = False,
    health_check: bool = True,
):
    project_dir = Path(project_path)
    dockerfile = project_dir / "Dockerfile"
    image_tag = f"zerodev/{project_name.lower()}:latest"

    if not dockerfile.exists():
        raise FileNotFoundError("Dockerfile not found in project directory.")

    # 1. Old container ni tozalash
    print("[🧹] Removing old container (if exists)...")
    subprocess.run(
        ["docker", "rm", "-f", project_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 2. Docker image yaratish
    print(f"[🔧] Building Docker image: {image_tag}")
    subprocess.run(
        ["docker", "build", "-t", image_tag, "."], cwd=project_path, check=True
    )

    # 3. (ixtiyoriy) DockerHub’ga push
    if push_to_registry:
        print(f"[📤] Pushing to registry: {image_tag}")
        subprocess.run(["docker", "push", image_tag], check=True)

    # 4. Run container
    run_cmd = ["docker", "run", "-d", "-p", f"{port}:8000", "--name", project_name]

    # .env mavjud bo‘lsa — uzatish
    env_file = project_dir / ".env"
    if env_file.exists():
        run_cmd.extend(["--env-file", str(env_file)])

    run_cmd.append(image_tag)

    print(f"[🚀] Running container on port {port}...")
    subprocess.run(run_cmd, check=True)

    # 5. (ixtiyoriy) Health check
    if health_check:
        print("[🔍] Waiting for service to boot...")
        time.sleep(3)
        try:
            res = requests.get(f"http://localhost:{port}/health")
            if res.status_code == 200:
                print("[💚] Health check passed!")
            else:
                print(f"[⚠️] Health check failed: {res.status_code}")
        except Exception as e:
            print(f"[❌] No response from service: {e}")

    print(
        f"[✅] Project '{project_name}' deployed successfully at http://localhost:{port}"
    )
