import re
from typing import Any, Dict, Optional

from .policy_config import load_filter_rules, load_policy_config


def analyze_prompt(prompt: str, role: Optional[str] = None) -> Dict:
    """
    Analyze the given prompt using scoring and role-based policy config.
    Returns status, total score, violations list with explanations.
    """
    config = load_policy_config(role)
    prompt = prompt.lower()
    violations = []
    total_score = 0
    effective_role = role or "default"

    # Blocked keywords
    for item in config.get("blocked_keywords", []):
        word = item.get("word")
        score = item.get("score", 10)
        if word and word in prompt:
            violations.append(
                {
                    "type": "blocked",
                    "word": word,
                    "score": score,
                    "message": f"The word '{word}' is not allowed for role '{effective_role}'. Please rephrase it.",
                }
            )
            total_score += score

    # Risky keywords
    for item in config.get("risky_keywords", []):
        word = item.get("word")
        score = item.get("score", 5)
        if word and word in prompt:
            violations.append(
                {
                    "type": "risky",
                    "word": word,
                    "score": score,
                    "message": f"The word '{word}' may be risky in your current role '{effective_role}'. Use with caution.",
                }
            )
            total_score += score

    # Blocked patterns
    for item in config.get("blocked_patterns", []):
        pattern = item.get("pattern")
        score = item.get("score", 7)
        if pattern and re.search(pattern, prompt):
            violations.append(
                {
                    "type": "regex",
                    "pattern": pattern,
                    "score": score,
                    "message": f"Pattern '{pattern}' is not allowed in role '{effective_role}'. Please avoid using it.",
                }
            )
            total_score += score

    if any(v["type"] in ["blocked", "regex"] for v in violations):
        status = "blocked"
    elif any(v["type"] == "risky" for v in violations):
        status = "risky"
    else:
        status = "safe"

    return {"status": status, "score": total_score, "violations": violations}


def is_prompt_safe(prompt: str, role: Optional[str] = None) -> bool:
    return analyze_prompt(prompt, role)["status"] == "safe"


def apply_filters(content: Dict[str, Any], direction: str) -> Dict:
    """
    Apply generic filters to content based on direction (inbound/outbound).
    Content is expected to be a dictionary, e.g., representing a request or response.
    """
    rules = load_filter_rules()
    filter_key = f"{direction.lower()}_filters"

    if filter_key not in rules:
        return {"action": "allow", "violations": []}

    violations = []
    highest_risk_action = "allow"
    action_priority = {"allow": 0, "flag": 1, "redact": 2, "block": 3}

    for rule in rules.get(filter_key, []):
        criteria = rule.get("criteria", {})
        action = rule.get("action", "flag")

        match_found = False

        if "file_extension" in criteria and "file_name" in content:
            file_ext = content.get("file_name", "").split(".")[-1]
            if file_ext in criteria["file_extension"]:
                match_found = True

        if not match_found and "body_contains" in criteria and "body" in content:
            for keyword in criteria["body_contains"]:
                if keyword in content.get("body", ""):
                    match_found = True
                    break

        if not match_found and "body_matches_pattern" in criteria and "body" in content:
            for pattern in criteria["body_matches_pattern"]:
                if re.search(pattern, content.get("body", "")):
                    match_found = True
                    break

        if match_found:
            violations.append(rule)
            if action_priority.get(action, 0) > action_priority.get(
                highest_risk_action, 0
            ):
                highest_risk_action = action

    return {"action": highest_risk_action, "violations": violations}
