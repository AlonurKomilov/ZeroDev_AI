"""
ZeroDev AI Security Engine

This package provides comprehensive security functionality for the ZeroDev AI platform:

Core Components:
- SecurityEngine: Central security coordinator
- Content filters and policy enforcement
- Rate limiting and DDoS protection
- Audit logging and monitoring
- Request validation and authentication

Usage:
    from backend.security_engine import security_engine
    
    # Perform security check
    allowed, violations = await security_engine.perform_security_check(request, content)
    
    # Get security status
    status = security_engine.get_security_status()
"""

from .core import security_engine, SecurityContext, SecurityViolation, SecurityEngine
from .filters import analyze_prompt
from .audit_log import AuditLogger
from .policy_config import load_policy_config, load_filter_rules

__all__ = [
    'security_engine',
    'SecurityEngine',
    'SecurityContext',
    'SecurityViolation', 
    'analyze_prompt',
    'AuditLogger',
    'load_policy_config',
    'load_filter_rules'
]

__version__ = '1.0.0'
