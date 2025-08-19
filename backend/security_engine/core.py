"""
B15 Security Engine - Core Security Framework

This module provides the central security coordination layer that integrates
all security components across the ZeroDev AI platform, including:
- Authentication & Authorization
- Request filtering and validation  
- Rate limiting and DDoS protection
- Audit logging and monitoring
- Security policy enforcement
- Threat detection and response
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Request
from pydantic import BaseModel, Field

# Use standard logging instead of custom logger for now
logger = logging.getLogger(__name__)

from .filters import analyze_prompt


class SecurityContext(BaseModel):
    """Security context for requests"""
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: str = "guest"
    ip_address: str = ""
    user_agent: str = ""
    request_id: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    
    
class SecurityViolation(BaseModel):
    """Security violation details"""
    violation_type: str
    severity: str  # low, medium, high, critical
    message: str
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)


class RateLimitInfo(BaseModel):
    """Rate limiting information"""
    key: str
    requests_per_window: int = 0
    window_start: datetime = Field(default_factory=datetime.now)
    blocked_until: Optional[datetime] = None


class SecurityEngine:
    """Central Security Engine for ZeroDev AI Platform"""
    
    def __init__(self):
        # Simplified initialization for testing
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        self.blocked_ips: set[str] = set()
        self.suspicious_patterns: Dict[str, int] = {}
        
        # Security configuration
        self.config = {
            "rate_limit": {
                "requests_per_minute": 60,
                "burst_requests": 100,
                "block_duration_minutes": 15,
                "suspicious_threshold": 10
            },
            "content_security": {
                "max_prompt_length": 10000,
                "block_score_threshold": 25,
                "warn_score_threshold": 10
            },
            "authentication": {
                "token_expiry_hours": 24,
                "refresh_token_expiry_days": 30,
                "max_failed_attempts": 5,
                "lockout_duration_minutes": 30
            }
        }
        
    async def create_security_context(self, request: Request) -> SecurityContext:
        """Create security context from request"""
        try:
            # Extract user info if authenticated
            user_id, user_email, user_role = None, None, "guest"
            
            if hasattr(request.state, 'user') and request.state.user:
                user_id = str(request.state.user.id)
                user_email = request.state.user.email
                user_role = getattr(request.state.user, 'role', 'user')
            
            # Get IP address safely
            ip_address = "unknown"
            if request.client and request.client.host:
                ip_address = request.client.host
            
            # Generate request ID
            request_id = hashlib.md5(
                f"{ip_address}{time.time()}{request.url}".encode()
            ).hexdigest()[:16]
            
            return SecurityContext(
                user_id=user_id,
                user_email=user_email,
                user_role=user_role,
                ip_address=ip_address,
                user_agent=request.headers.get("user-agent", ""),
                request_id=request_id
            )
            
        except Exception as e:
            logger.error(f"Error creating security context: {e}")
            ip_address = "unknown"
            if request.client and request.client.host:
                ip_address = request.client.host
            return SecurityContext(ip_address=ip_address)
    
    async def check_rate_limit(self, context: SecurityContext, endpoint: str) -> Tuple[bool, Optional[SecurityViolation]]:
        """Check rate limiting for requests"""
        rate_key = f"{context.ip_address}:{endpoint}"
        now = datetime.now()
        
        # Check if IP is blocked
        if context.ip_address in self.blocked_ips:
            violation = SecurityViolation(
                violation_type="rate_limit",
                severity="high",
                message=f"IP address {context.ip_address} is blocked",
                details={"ip_address": context.ip_address, "endpoint": endpoint}
            )
            return False, violation
        
        # Get or create rate limit info
        if rate_key not in self.rate_limits:
            self.rate_limits[rate_key] = RateLimitInfo(key=rate_key, window_start=now)
        
        rate_info = self.rate_limits[rate_key]
        
        # Check if still blocked
        if rate_info.blocked_until and now < rate_info.blocked_until:
            violation = SecurityViolation(
                violation_type="rate_limit",
                severity="medium",
                message=f"Rate limit exceeded. Blocked until {rate_info.blocked_until}",
                details={
                    "blocked_until": rate_info.blocked_until.isoformat(),
                    "endpoint": endpoint
                }
            )
            return False, violation
        
        # Reset window if expired (1-minute windows)
        if now > rate_info.window_start + timedelta(minutes=1):
            rate_info.requests_per_window = 0
            rate_info.window_start = now
            rate_info.blocked_until = None
        
        # Check limits
        max_requests = self.config["rate_limit"]["requests_per_minute"]
        rate_info.requests_per_window += 1
        
        if rate_info.requests_per_window > max_requests:
            # Block for specified duration
            block_duration = timedelta(minutes=self.config["rate_limit"]["block_duration_minutes"])
            rate_info.blocked_until = now + block_duration
            
            # Add to suspicious patterns
            self.suspicious_patterns[context.ip_address] = (
                self.suspicious_patterns.get(context.ip_address, 0) + 1
            )
            
            # If too many violations, block IP
            if self.suspicious_patterns[context.ip_address] >= self.config["rate_limit"]["suspicious_threshold"]:
                self.blocked_ips.add(context.ip_address)
                logger.warning(f"IP {context.ip_address} added to blocklist for repeated violations")
            
            violation = SecurityViolation(
                violation_type="rate_limit",
                severity="medium",
                message=f"Rate limit exceeded: {rate_info.requests_per_window}/{max_requests} requests",
                details={
                    "requests_count": rate_info.requests_per_window,
                    "max_requests": max_requests,
                    "blocked_until": rate_info.blocked_until.isoformat()
                }
            )
            return False, violation
        
        return True, None
    
    async def validate_content(self, content: str, context: SecurityContext) -> Tuple[bool, List[SecurityViolation]]:
        """Validate content for security issues"""
        violations: List[SecurityViolation] = []
        
        # Length check
        max_length = self.config["content_security"]["max_prompt_length"]
        if len(content) > max_length:
            violations.append(SecurityViolation(
                violation_type="content_length",
                severity="medium",
                message=f"Content too long: {len(content)}/{max_length} characters",
                details={"length": len(content), "max_length": max_length}
            ))
        
        # Content analysis using existing filters
        try:
            analysis_result: Dict[str, Any] = analyze_prompt(content, context.user_role)
            
            block_threshold = self.config["content_security"]["block_score_threshold"]
            warn_threshold = self.config["content_security"]["warn_score_threshold"]
            
            total_score: float = analysis_result.get("total_score", 0.0)
            
            if total_score >= block_threshold:
                violations.append(SecurityViolation(
                    violation_type="content_policy",
                    severity="high",
                    message="Content blocked due to security policy violations",
                    details={
                        "score": total_score,
                        "violations": analysis_result.get("violations", [])
                    }
                ))
                return False, violations
            
            elif total_score >= warn_threshold:
                violations.append(SecurityViolation(
                    violation_type="content_warning",
                    severity="low", 
                    message="Content flagged for review",
                    details={
                        "score": total_score,
                        "violations": analysis_result.get("violations", [])
                    }
                ))
        
        except Exception as e:
            logger.error(f"Error in content validation: {e}")
            violations.append(SecurityViolation(
                violation_type="validation_error",
                severity="medium",
                message="Content validation failed",
                details={"error": str(e)}
            ))
        
        # Allow content but with warnings
        return True, violations
    
    async def validate_request_signature(self, request: Request, secret_key: str) -> bool:
        """Validate request HMAC signature for sensitive operations"""
        try:
            signature = request.headers.get("x-signature")
            if not signature:
                return False
            
            # Reconstruct expected signature
            body = await request.body()
            timestamp = request.headers.get("x-timestamp", "")
            payload = f"{timestamp}:{request.method}:{request.url}:{body.decode()}"
            
            expected_signature = hmac.new(
                secret_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error validating request signature: {e}")
            return False
    
    async def log_security_event(self, context: SecurityContext, event_type: str, 
                                violation: Optional[SecurityViolation] = None, 
                                additional_data: Optional[Dict[str, Any]] = None):
        """Log security events for monitoring and auditing"""
        try:
            log_data: Dict[str, Any] = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "request_id": context.request_id,
                "user_id": context.user_id,
                "ip_address": context.ip_address,
                "user_agent": context.user_agent
            }
            
            if violation:
                log_data["violation"] = {
                    "type": violation.violation_type,
                    "severity": violation.severity,
                    "message": violation.message,
                    "details": violation.details
                }
            
            if additional_data:
                log_data["additional_data"] = additional_data
            
            # For now, just log to standard logging
            # In production, this would send to audit logging service
            logger.info(f"Security Event: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    async def perform_security_check(self, request: Request, content: Optional[str] = None, 
                                   endpoint: str = "") -> Tuple[bool, List[SecurityViolation]]:
        """Perform comprehensive security check"""
        violations = []
        
        try:
            # Create security context
            context = await self.create_security_context(request)
            
            # Check rate limits
            rate_allowed, rate_violation = await self.check_rate_limit(context, endpoint)
            if not rate_allowed and rate_violation:
                violations.append(rate_violation)
                await self.log_security_event(context, "rate_limit_violation", rate_violation)
                return False, violations
            
            # Validate content if provided
            if content:
                content_allowed, content_violations = await self.validate_content(content, context)
                violations.extend(content_violations)
                
                # Block request if content is not allowed
                if not content_allowed:
                    await self.log_security_event(context, "content_blocked", 
                                                content_violations[0] if content_violations else None)
                    return False, violations
                
                # Log warnings
                for violation in content_violations:
                    if violation.severity in ["medium", "high"]:
                        await self.log_security_event(context, "content_warning", violation)
            
            # Log successful security check
            if not violations:
                await self.log_security_event(context, "security_check_passed")
            
            return True, violations
            
        except Exception as e:
            logger.error(f"Error in security check: {e}")
            violation = SecurityViolation(
                violation_type="security_check_error",
                severity="high",
                message="Security check failed",
                details={"error": str(e)}
            )
            return False, [violation]
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status and statistics"""
        now = datetime.now()
        
        # Count active rate limits
        active_limits = sum(1 for rl in self.rate_limits.values() 
                          if rl.blocked_until and rl.blocked_until > now)
        
        # Count recent requests
        recent_requests = sum(rl.requests_per_window for rl in self.rate_limits.values()
                            if now - rl.window_start < timedelta(minutes=5))
        
        return {
            "status": "active",
            "blocked_ips_count": len(self.blocked_ips),
            "active_rate_limits": active_limits,
            "recent_requests": recent_requests,
            "suspicious_ips": len(self.suspicious_patterns),
            "config": self.config,
            "last_updated": now.isoformat()
        }


# Singleton instance
security_engine = SecurityEngine()
