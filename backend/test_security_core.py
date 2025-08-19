"""
Basic Security Engine Core Test

Test the core functionality of B15 Security Engine
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from security_engine.core import SecurityEngine, SecurityContext


def test_security_engine_core():
    """Test Security Engine core functionality"""
    
    print("🔐 Testing B15 Security Engine Core...")
    
    async def run_tests():
        # Create security engine
        security_engine = SecurityEngine()
        
        # Test context creation
        context = SecurityContext(
            request_id="test_123",
            user_id="user123", 
            user_role="user",
            ip_address="192.168.1.1",
            user_agent="Test-Agent"
        )
        
        print("1. Testing content validation...")
        # Test content validation
        test_content = "This is a simple test prompt"
        is_valid, violations = await security_engine.validate_content(test_content, context)
        
        print(f"   Content valid: {is_valid}")
        print(f"   Violations count: {len(violations)}")
        
        # Test logging
        print("2. Testing security logging...")
        await security_engine.log_security_event(context, "test_event")
        print("   ✅ Logging successful")
        
        print("\n🎉 Security Engine Core tests completed!")
        return True
    
    # Run async tests
    result = asyncio.run(run_tests())
    return result


if __name__ == "__main__":
    try:
        result = test_security_engine_core()
        if result:
            print("✅ All Security Engine Core tests passed!")
        else:
            print("❌ Security Engine Core tests failed!")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
