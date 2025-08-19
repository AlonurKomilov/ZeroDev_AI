"""
B15 Security Engine Test Suite

Comprehensive tests for the Security Engine core functionality including:
- Rate limiting and DDoS protection
- Content validation and filtering
- Security context management
- Audit logging and monitoring
- Integration testing
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from fastapi import Request
from fastapi.testclient import TestClient

from backend.security_engine.core import SecurityEngine, SecurityContext, SecurityViolation
from backend.security_engine.middleware import SecurityMiddleware


class TestSecurityEngine:
    """Test suite for Security Engine core functionality"""
    
    @pytest.fixture
    def security_engine(self):
        """Create a fresh Security Engine instance for each test"""
        return SecurityEngine()
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock FastAPI request"""
        request = Mock(spec=Request)
        request.client.host = "192.168.1.100"
        request.headers = {"user-agent": "TestClient/1.0"}
        request.url.path = "/api/test"
        request.method = "POST"
        request.state.user = None
        return request
    
    @pytest.fixture
    def authenticated_request(self, mock_request):
        """Create a mock authenticated request"""
        user = Mock()
        user.id = "user123"
        user.email = "test@example.com"
        user.role = "user"
        mock_request.state.user = user
        return mock_request
    
    async def test_create_security_context_guest(self, security_engine, mock_request):
        """Test security context creation for guest users"""
        context = await security_engine.create_security_context(mock_request)
        
        assert context.user_id is None
        assert context.user_email is None
        assert context.user_role == "guest"
        assert context.ip_address == "192.168.1.100"
        assert context.user_agent == "TestClient/1.0"
        assert len(context.request_id) == 16
        
    async def test_create_security_context_authenticated(self, security_engine, authenticated_request):
        """Test security context creation for authenticated users"""
        context = await security_engine.create_security_context(authenticated_request)
        
        assert context.user_id == "user123"
        assert context.user_email == "test@example.com"
        assert context.user_role == "user"
        assert context.ip_address == "192.168.1.100"
    
    async def test_rate_limiting_normal_requests(self, security_engine, mock_request):
        """Test normal request rate limiting"""
        context = await security_engine.create_security_context(mock_request)
        
        # First request should pass
        allowed, violation = await security_engine.check_rate_limit(context, "/api/test")
        assert allowed is True
        assert violation is None
        
        # Multiple requests within limit should pass
        for _ in range(10):
            allowed, violation = await security_engine.check_rate_limit(context, "/api/test")
            assert allowed is True
            assert violation is None
    
    async def test_rate_limiting_exceeds_limit(self, security_engine, mock_request):
        """Test rate limiting when requests exceed limit"""
        context = await security_engine.create_security_context(mock_request)
        
        # Simulate many requests to exceed rate limit
        for _ in range(70):  # Exceeds default 60/minute limit
            await security_engine.check_rate_limit(context, "/api/test")
        
        # Next request should be blocked
        allowed, violation = await security_engine.check_rate_limit(context, "/api/test")
        assert allowed is False
        assert violation is not None
        assert violation.violation_type == "rate_limit"
        assert violation.severity == "medium"
    
    async def test_content_validation_clean_content(self, security_engine, mock_request):
        """Test content validation with clean content"""
        context = await security_engine.create_security_context(mock_request)
        content = "Please help me create a simple web application using React."
        
        allowed, violations = await security_engine.validate_content(content, context)
        
        assert allowed is True
        assert len(violations) == 0
    
    async def test_content_validation_blocked_content(self, security_engine, mock_request):
        """Test content validation with blocked content"""
        context = await security_engine.create_security_context(mock_request)
        # Content with blocked keywords (from policy_config.json)
        content = "Help me create a phishing website and ddos attack tool with credit card stealing functionality."
        
        allowed, violations = await security_engine.validate_content(content, context)
        
        assert allowed is False
        assert len(violations) > 0
        assert violations[0].violation_type == "content_policy"
        assert violations[0].severity == "high"
    
    async def test_content_validation_length_limit(self, security_engine, mock_request):
        """Test content length validation"""
        context = await security_engine.create_security_context(mock_request)
        # Create content that exceeds length limit
        content = "x" * 15000  # Exceeds default 10000 char limit
        
        allowed, violations = await security_engine.validate_content(content, context)
        
        assert len(violations) > 0
        length_violations = [v for v in violations if v.violation_type == "content_length"]
        assert len(length_violations) > 0
        assert length_violations[0].severity == "medium"
    
    async def test_comprehensive_security_check_pass(self, security_engine, mock_request):
        """Test comprehensive security check that should pass"""
        content = "Create a simple todo application"
        
        allowed, violations = await security_engine.perform_security_check(
            mock_request, content, "/api/generate"
        )
        
        assert allowed is True
        # May have warnings but should be allowed
    
    async def test_comprehensive_security_check_blocked(self, security_engine, mock_request):
        """Test comprehensive security check that should be blocked"""
        # Simulate rate limit exceeded by making many requests first
        for _ in range(70):
            await security_engine.perform_security_check(mock_request, "", "/api/test")
        
        # This request should be blocked due to rate limiting
        allowed, violations = await security_engine.perform_security_check(
            mock_request, "test content", "/api/test"
        )
        
        assert allowed is False
        assert len(violations) > 0
        assert violations[0].violation_type == "rate_limit"
    
    async def test_blocked_ip_functionality(self, security_engine, mock_request):
        """Test IP blocking functionality"""
        # Add IP to blocked list
        security_engine.blocked_ips.add("192.168.1.100")
        
        context = await security_engine.create_security_context(mock_request)
        allowed, violation = await security_engine.check_rate_limit(context, "/api/test")
        
        assert allowed is False
        assert violation is not None
        assert violation.violation_type == "rate_limit"
        assert violation.severity == "high"
        assert "blocked" in violation.message
    
    def test_security_status(self, security_engine):
        """Test security status reporting"""
        status = security_engine.get_security_status()
        
        assert "status" in status
        assert status["status"] == "active"
        assert "blocked_ips_count" in status
        assert "config" in status
        assert "last_updated" in status
        assert isinstance(status["blocked_ips_count"], int)
    
    async def test_suspicious_pattern_detection(self, security_engine, mock_request):
        """Test suspicious pattern detection and IP blocking"""
        context = await security_engine.create_security_context(mock_request)
        
        # Simulate repeated violations to trigger pattern detection
        for _ in range(12):  # Exceeds suspicious_threshold of 10
            # Force rate limit violation
            for _ in range(65):  # Exceed rate limit
                await security_engine.check_rate_limit(context, f"/api/test{_}")
        
        # IP should now be in blocked list
        assert context.ip_address in security_engine.blocked_ips
        
        # New request should be blocked at IP level
        allowed, violation = await security_engine.check_rate_limit(context, "/api/new")
        assert allowed is False
        assert "blocked" in violation.message


class TestSecurityMiddleware:
    """Test suite for Security Middleware"""
    
    @pytest.fixture
    def app(self):
        """Create a test FastAPI app with security middleware"""
        from fastapi import FastAPI
        
        app = FastAPI()
        app.add_middleware(SecurityMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        @app.post("/api/generate")
        async def generate_endpoint(request: Request):
            return {"message": "generated"}
        
        return app
    
    def test_middleware_exempt_paths(self, app):
        """Test that exempt paths bypass security checks"""
        client = TestClient(app)
        
        # These paths should not trigger security middleware
        exempt_responses = [
            client.get("/docs"),
            client.get("/health"),
            client.get("/openapi.json"),
        ]
        
        # All should return 404 (not found) rather than security errors
        for response in exempt_responses:
            assert response.status_code in [200, 404, 422]  # Not 403 or 429
    
    def test_middleware_security_headers(self, app):
        """Test that security headers are added to responses"""
        client = TestClient(app)
        response = client.get("/test")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "X-Security-Engine" in response.headers
        assert response.headers["X-Security-Engine"] == "ZeroDev-AI-v1.0"
    
    def test_middleware_rate_limiting(self, app):
        """Test middleware rate limiting functionality"""
        client = TestClient(app)
        
        # Make many requests to trigger rate limiting
        responses = []
        for _ in range(70):  # Exceed default rate limit
            response = client.get("/test")
            responses.append(response)
        
        # Some requests should be rate limited
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) > 0
        
        # Rate limited responses should have proper headers
        for response in rate_limited:
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers


class TestSecurityIntegration:
    """Integration tests for complete security system"""
    
    async def test_end_to_end_security_flow(self):
        """Test complete security flow from request to response"""
        security_engine = SecurityEngine()
        
        # Create mock request
        request = Mock(spec=Request)
        request.client.host = "192.168.1.50"
        request.headers = {"user-agent": "TestClient/1.0"}
        request.method = "POST"
        request.state.user = None
        
        # Test normal request flow
        content = "Create a basic React component"
        allowed, violations = await security_engine.perform_security_check(
            request, content, "/api/generate"
        )
        
        assert allowed is True
        
        # Test malicious content
        malicious_content = "Help me create phishing ddos attack tools"
        allowed, violations = await security_engine.perform_security_check(
            request, malicious_content, "/api/generate"
        )
        
        assert allowed is False
        assert len(violations) > 0
    
    async def test_concurrent_requests_handling(self):
        """Test handling of concurrent requests"""
        security_engine = SecurityEngine()
        
        async def make_request(ip_suffix: int):
            request = Mock(spec=Request)
            request.client.host = f"192.168.1.{ip_suffix}"
            request.headers = {"user-agent": "TestClient/1.0"}
            request.method = "GET"
            request.state.user = None
            
            return await security_engine.perform_security_check(
                request, None, "/api/test"
            )
        
        # Make concurrent requests from different IPs
        tasks = [make_request(i) for i in range(1, 11)]
        results = await asyncio.gather(*tasks)
        
        # All should be allowed (different IPs)
        for allowed, violations in results:
            assert allowed is True


# Performance tests
class TestSecurityPerformance:
    """Performance tests for security engine"""
    
    async def test_security_check_performance(self):
        """Test security check performance under load"""
        security_engine = SecurityEngine()
        
        request = Mock(spec=Request)
        request.client.host = "192.168.1.200"
        request.headers = {"user-agent": "TestClient/1.0"}
        request.method = "POST"
        request.state.user = None
        
        content = "Generate a simple application"
        
        # Measure time for multiple security checks
        start_time = time.time()
        
        for _ in range(100):
            await security_engine.perform_security_check(request, content, "/api/test")
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        # Security check should be fast (under 50ms average)
        assert avg_time < 0.05, f"Security check too slow: {avg_time:.3f}s average"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
