# 📦 AGENT VERSIONS

## agents/ci_cd_agent.py — v2.0.0
- Modular write functions (README, Docker, CI, etc.)
- Retry on write (3x attempts per file)
- `.jsonl` audit log for every generated file
- ✅ Successfully tested in a temporary project scaffold
- Last Updated: 2025-07-18

🔜 Next:
- Add rollback support
- Refactor to plugin model (`BaseScaffoldStep`)
- Create `CI_CDOrchestrator` class
- Externalize logging via `security_engine/audit_log.py`
---

## agents/codegen_agent.py — v1.0.0
- Basic OpenAI code block generation (manual prompt)
- No structured spec yet
- Integrated in minimal flow only
- Last Updated: 2025-07-18

🔜 Next:
- Add spec-driven codegen
- Model router (GPT-4o, Claude)
- Add retry, log, and unit tests
---

## agents/deploy_agent.py — v1.0.0
- Draft file, scaffolded only
- Deployment logic not yet implemented
- No external integration yet
- Last Updated: 2025-07-18

🔜 Next:
- Auto-detect deployment strategy
- CLI + GUI triggers
- Deploy fallback & log reporting
---

## agents/scaffold_agent.py — v1.0.0
- Creates base folder structure
- Adds entrypoint files like `main.py`, `__init__.py`
- Lightweight and functional
- Last Updated: 2025-07-18

🔜 Next:
- Refactor into `BaseScaffoldStep` model
- Add audit logging support
- Include project spec metadata
---