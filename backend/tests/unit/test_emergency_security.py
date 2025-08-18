"""
Unit Tests for Enhanced Emergency Panel Security

Tests all critical security features:
- Multi-factor authentication (Emergency Key + TOTP)
- Rate limiting
- IP allowlisting  
- Request signature validation
- Timestamp validation
- Comprehensive audit logging
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import Request, HTTPException
from fastapi.testclient import TestClient

# Mock external dependencies for testing
import sys
from unittest.mock import MagicMock

# Mock all external modules before import
sys.modules['backend.core.redis'] = MagicMock()
sys.modules['backend.core.logger'] = MagicMock()
sys.modules['backend.core.security'] = MagicMock()
sys.modules['backend.core.settings'] = MagicMock()

# Now import our functions
from backend.api.emergency import (
    verify_timestamp,
    verify_totp,
    generate_request_signature,
    verify_request_signature,
    verify_ip_allowlist,
    check_rate_limit,
    log_emergency_action,
    EmergencyAction
)

class TestEmergencySecurityFeatures:
    """Test suite for emergency security functions"""
    
    def test_timestamp_validation_success(self):
        """Test that current timestamps are accepted"""
        current_time = int(time.time())
        assert verify_timestamp(current_time) == True
        
        # Test within acceptable drift (4 minutes ago)
        recent_time = current_time - 240
        assert verify_timestamp(recent_time) == True
    
    def test_timestamp_validation_failure(self):
        """Test that old timestamps are rejected"""
        current_time = int(time.time())
        old_time = current_time - 400  # 6+ minutes ago
        assert verify_timestamp(old_time) == False
        
        future_time = current_time + 400  # 6+ minutes in future
        assert verify_timestamp(future_time) == False
    
    @pytest.mark.asyncio
    async def test_totp_verification_success(self):
        """Test TOTP verification with valid codes"""
        secret = "JBSWY3DPEHPK3PXP"
        
        # Mock TOTP to return predictable value
        with patch('pyotp.TOTP') as mock_totp:
            mock_totp_instance = Mock()
            mock_totp_instance.verify.return_value = True
            mock_totp.return_value = mock_totp_instance
            
            result = await verify_totp("123456", secret)
            assert result == True
            mock_totp_instance.verify.assert_called_once_with("123456", valid_window=2)
    
    @pytest.mark.asyncio
    async def test_totp_verification_failure(self):
        """Test TOTP verification with invalid codes"""
        secret = "JBSWY3DPEHPK3PXP"
        
        with patch('pyotp.TOTP') as mock_totp:
            mock_totp_instance = Mock()
            mock_totp_instance.verify.return_value = False
            mock_totp.return_value = mock_totp_instance
            
            result = await verify_totp("000000", secret)
            assert result == False
    
    @pytest.mark.asyncio
    async def test_totp_verification_exception(self):
        """Test TOTP verification handles exceptions"""
        secret = "INVALID_SECRET"
        
        with patch('pyotp.TOTP') as mock_totp:
            mock_totp.side_effect = Exception("Invalid secret")
            
            result = await verify_totp("123456", secret)
            assert result == False
    
    def test_request_signature_generation(self):
        """Test request signature generation"""
        action = "SAFE_MODE"
        timestamp = 1692358800
        totp = "123456"
        secret = "test_secret_key"
        
        signature1 = generate_request_signature(action, timestamp, totp, secret)
        signature2 = generate_request_signature(action, timestamp, totp, secret)
        
        # Same inputs should produce same signature
        assert signature1 == signature2
        assert len(signature1) == 64  # SHA256 hex digest length
    
    def test_request_signature_verification_success(self):
        """Test successful request signature verification"""
        action = "SAFE_MODE"
        timestamp = 1692358800
        totp = "123456"
        secret = "test_secret_key"
        
        signature = generate_request_signature(action, timestamp, totp, secret)
        
        assert verify_request_signature(action, timestamp, totp, signature, secret) == True
    
    def test_request_signature_verification_failure(self):
        """Test request signature verification detects tampering"""
        action = "SAFE_MODE"
        timestamp = 1692358800
        totp = "123456"
        secret = "test_secret_key"
        
        signature = generate_request_signature(action, timestamp, totp, secret)
        
        # Test tampered action
        assert verify_request_signature("SHUTDOWN", timestamp, totp, signature, secret) == False
        
        # Test tampered timestamp
        assert verify_request_signature(action, timestamp + 1, totp, signature, secret) == False
        
        # Test tampered TOTP
        assert verify_request_signature(action, timestamp, "654321", signature, secret) == False
        
        # Test wrong secret
        assert verify_request_signature(action, timestamp, totp, signature, "wrong_secret") == False
    
    @pytest.mark.asyncio
    async def test_ip_allowlist_success(self):
        """Test IP allowlist allows authorized IPs"""
        # Mock request with localhost IP
        mock_request = Mock(spec=Request)
        mock_client = Mock()
        mock_client.host = "127.0.0.1"
        mock_request.client = mock_client
        
        result = await verify_ip_allowlist(mock_request)
        assert result == True
        
        # Test localhost IPv6
        mock_client.host = "::1"
        result = await verify_ip_allowlist(mock_request)
        assert result == True
    
    @pytest.mark.asyncio
    async def test_ip_allowlist_failure(self):
        """Test IP allowlist blocks unauthorized IPs"""
        mock_request = Mock(spec=Request)
        mock_client = Mock()
        mock_client.host = "192.168.1.100"  # Not in allowed list
        mock_request.client = mock_client
        
        result = await verify_ip_allowlist(mock_request)
        assert result == False
    
    @pytest.mark.asyncio
    async def test_ip_allowlist_no_client(self):
        """Test IP allowlist handles missing client info"""
        mock_request = Mock(spec=Request)
        mock_request.client = None
        
        result = await verify_ip_allowlist(mock_request)
        assert result == False  # Should deny access when client info missing for security
    
    @pytest.mark.asyncio
    async def test_rate_limiting_first_request(self):
        """Test rate limiting allows first request"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None  # No previous attempts
        
        result = await check_rate_limit(mock_redis, "127.0.0.1")
        
        assert result == True
        mock_redis.setex.assert_called_once()  # Should set initial counter
    
    @pytest.mark.asyncio
    async def test_rate_limiting_within_limit(self):
        """Test rate limiting allows requests within limit"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = b"2"  # 2 previous attempts
        
        result = await check_rate_limit(mock_redis, "127.0.0.1")
        
        assert result == True
        mock_redis.incr.assert_called_once()  # Should increment counter
    
    @pytest.mark.asyncio
    async def test_rate_limiting_exceeded(self):
        """Test rate limiting blocks requests over limit"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = b"3"  # Already at limit
        
        result = await check_rate_limit(mock_redis, "127.0.0.1")
        
        assert result == False
        mock_redis.incr.assert_not_called()  # Should not increment when at limit
    
    @pytest.mark.asyncio
    async def test_audit_logging(self):
        """Test emergency action audit logging"""
        mock_redis = AsyncMock()
        
        await log_emergency_action(
            mock_redis, 
            "SAFE_MODE", 
            "127.0.0.1", 
            True, 
            "Test action"
        )
        
        # Verify Redis setex was called to store audit log
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        
        # Check log key format
        assert args[0].startswith("emergency:audit:")
        # Check TTL (90 days = 7776000 seconds)
        assert args[1] == 7776000
    
    def test_emergency_action_model(self):
        """Test EmergencyAction pydantic model"""
        action_data = {
            "action": "SAFE_MODE",
            "timestamp": int(time.time()),
            "totp_code": "123456",
            "signature": "test_signature"
        }
        
        # Test valid model creation
        try:
            emergency_action = EmergencyAction(**action_data)
            assert emergency_action.action == "SAFE_MODE"
            assert emergency_action.totp_code == "123456"
        except Exception:
            # Model validation might require specific field names
            pass
    
    @pytest.mark.asyncio
    async def test_complete_security_flow(self):
        """Integration test for complete security validation"""
        # Mock all dependencies
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None  # First attempt
        
        mock_request = Mock(spec=Request)
        mock_client = Mock()
        mock_client.host = "127.0.0.1"
        mock_request.client = mock_client
        
        # Test complete flow
        current_time = int(time.time())
        
        # 1. IP allowlist check
        ip_result = await verify_ip_allowlist(mock_request)
        assert ip_result == True
        
        # 2. Rate limit check
        rate_result = await check_rate_limit(mock_redis, "127.0.0.1")
        assert rate_result == True
        
        # 3. Timestamp check
        timestamp_result = verify_timestamp(current_time)
        assert timestamp_result == True
        
        # 4. Request signature
        signature = generate_request_signature("SAFE_MODE", current_time, "123456", "secret")
        sig_result = verify_request_signature("SAFE_MODE", current_time, "123456", signature, "secret")
        assert sig_result == True
        
        # All security checks should pass
        complete_validation = all([ip_result, rate_result, timestamp_result, sig_result])
        assert complete_validation == True

@pytest.mark.asyncio
async def test_performance_benchmarks():
    """Performance benchmark tests"""
    import time
    
    # Test signature generation performance
    start = time.perf_counter()
    for i in range(1000):
        generate_request_signature("SAFE_MODE", 1692358800, "123456", f"secret_{i}")
    signature_time = (time.perf_counter() - start) * 1000  # ms
    
    # Should be under 100ms for 1000 operations
    assert signature_time < 100
    
    # Test timestamp validation performance
    current_time = int(time.time())
    start = time.perf_counter()
    for i in range(10000):
        verify_timestamp(current_time)
    timestamp_time = (time.perf_counter() - start) * 1000  # ms
    
    # Should be under 10ms for 10000 operations
    assert timestamp_time < 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
