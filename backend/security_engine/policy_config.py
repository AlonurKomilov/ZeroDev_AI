import json
from pathlib import Path
from typing import Dict, Optional

CONFIG_PATH = Path(__file__).parent / "policy_config.json"

def load_policy_config(role: Optional[str] = None) -> Dict:
    """
    Load policy config based on user role (if available). 
    Fallback to global policy if no role-specific exists.
    """
    if not CONFIG_PATH.exists():
        print("[⚠️] policy_config.json not found.")
        return {"blocked_keywords": [], "risky_keywords": [], "blocked_patterns": []}

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print("[⚠️] Failed to parse config file.")
        return {"blocked_keywords": [], "risky_keywords": [], "blocked_patterns": []}

    if role:
        role_policies = config.get("role_policies", {})
        if role in role_policies:
            return role_policies[role]

    return config.get("default_policy", {})
