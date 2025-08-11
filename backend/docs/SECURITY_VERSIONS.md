# 📦 SECURITY VERSIONS

## security_engine/audit_log.py — v1.0.0
- Appends `.jsonl` audit logs from agents
- Fields include: timestamp, event, status, file, message
- Used by: ci_cd_agent (temporary), can be externalized
- Last Updated: 2025-07-18

🔜 Next:
- Expose as global `log_event()` import
- Add log rotation or archival mode
- Standardize format for reuse across all agents
---

## security_engine/filters.py — v1.0.0
- Parses prompt text for harmful intent (e.g. `webhook`, `breakpoint`)
- Simple keyword-based matching
- Used in: prompt_api/analyze.py (planned)
- Last Updated: 2025-07-18

🔜 Next:
- Add regex + semantic analysis
- Confidence scoring
- Block + warn modes (soft + hard)
---

## security_engine/policy_config.py — v1.0.0
- Loads security policy config from JSON file
- Validates enforcement levels, block rules, etc.
- Used internally by filters + analyze
- Last Updated: 2025-07-18

🔜 Next:
- Dynamic reload on change
- UI mapping via frontend
- Policy edit endpoint via API
---

## security_engine/policy_config.json — v1.0.0
- Static config file for filtering/trigger control
- Editable list of blocked keywords, scores, etc.
- Last Updated: 2025-07-18

🔜 Next:
- Add tag groups (e.g. "attack", "exploit")
- Include model-specific policy toggles
- Optional online sync
---