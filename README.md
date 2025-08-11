ZeroDev AI Core

This package contains the **M0 bootstrap** for the ZeroDev AI platform:

* **CLI** – `zerodev init <project_name>`
* **Prompt Intake API** – POST `/parse` returns structured spec
* **Scaffold Agent** – generates a minimal FastAPI project scaffold

Run locally:
```bash
pip install -r zerodev_ai/requirements.txt
uvicorn zerodev_ai.prompt_api.main:app --reload  # Prompt API
python -m zerodev_ai.cli.main init demo_app      # Scaffold example project
```

---
⭐ Next steps (M1): add Code Generation Agent & CI/CD integration.
