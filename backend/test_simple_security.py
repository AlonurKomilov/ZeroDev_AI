"""
Simple Security Engine Test

Basic functionality test for B15 Security Engine
"""

import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import Mock

# Add backend to Python path
sys.path.insert(0, os.path.dirname(__file__))

from security_engine.core import SecurityEngine, SecurityContext


async def test_security_engine_basic():
    """Test basic Security Engine functionality"""
    
    print("🔐 Testing B15 Security Engine...")
    
    # Create Security Engine instance
    security_engine = SecurityEngine()
    
    # Test 1: Security Context Creation
    print("\n1. Testing Security Context Creation...")
    
    # Mock request
    mock_request = Mock()
    mock_request.client.host = "192.168.1.100"
    mock_request.headers = {"user-agent": "TestClient/1.0"}
    mock_request.url.path = "/api/test"
    mock_request.method = "POST"
    mock_request.state.user = None
    
    context = await security_engine.create_security_context(mock_request)
    assert context.ip_address == "192.168.1.100"
    assert context.user_role == "guest"
    assert len(context.request_id) == 16
    print("   ✅ Security context created successfully")
    
    # Test 2: Rate Limiting
    print("\n2. Testing Rate Limiting...")
    
    # Normal requests should pass
    for i in range(10):
        allowed, violation = await security_engine.check_rate_limit(context, "/api/test")
        assert allowed is True
        assert violation is None
    print("   ✅ Normal rate limiting works")
    
    # Test 3: Content Validation
    print("\n3. Testing Content Validation...")
    
    # Clean content should pass
    clean_content = "Please help me create a simple web application using React."
    allowed, violations = await security_engine.validate_content(clean_content, context)
    assert allowed is True
    print("   ✅ Clean content validation passed")
    
    # Test 4: Security Status
    print("\n4. Testing Security Status...")
    
    status = security_engine.get_security_status()
    assert status["status"] == "active"
    assert "blocked_ips_count" in status
    assert "config" in status
    print("   ✅ Security status reporting works")
    
    # Test 5: Comprehensive Security Check
    print("\n5. Testing Comprehensive Security Check...")
    
    allowed, violations = await security_engine.perform_security_check(
        mock_request, clean_content, "/api/generate"
    )
    assert allowed is True
    print("   ✅ Comprehensive security check passed")
    
    print("\n🎉 All B15 Security Engine tests passed!")
    return True


if __name__ == "__main__":
    result = asyncio.run(test_security_engine_basic())
    if result:
        print("\n✅ B15 Security Engine implementation is working correctly!")
    else:
        print("\n❌ B15 Security Engine tests failed!")
        exit(1)
