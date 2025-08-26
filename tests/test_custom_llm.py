#!/usr/bin/env python3
"""
Test script for Custom LLM Farm integration.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_custom_llm_import():
    """Test that custom LLM components can be imported."""
    print("🧪 Testing Custom LLM imports...")
    
    try:
        from src.llm.custom_llm_client import CustomLLMClient, LLMConfig, create_llm_client
        print("  ✓ Custom LLM client imports successful")
        
        from src.agents.jira_agent import JiraAgent
        print("  ✓ Updated Jira agent imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config_validation():
    """Test configuration validation for custom LLM."""
    print("\n🔧 Testing configuration...")
    
    try:
        from src.utils.config import Config
        
        # Check if new LLM config attributes exist
        assert hasattr(Config, 'LLM_API_URL'), "LLM_API_URL missing from config"
        assert hasattr(Config, 'LLM_API_KEY'), "LLM_API_KEY missing from config"
        assert hasattr(Config, 'LLM_MODEL'), "LLM_MODEL missing from config"
        assert hasattr(Config, 'LLM_VERIFY_SSL'), "LLM_VERIFY_SSL missing from config"
        
        print("  ✓ Custom LLM configuration attributes present")
        
        # Test validation
        validation = Config.validate_required_config()
        print(f"  ✓ Config validation works - Required fields: {len(validation['configured']) + len(validation['missing'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_environment_variables():
    """Test environment variables setup."""
    print("\n🌍 Testing environment variables...")
    
    required_vars = [
        "LLM_API_URL",
        "LLM_API_KEY", 
        "JIRA_SERVER_URL",
        "JIRA_USERNAME",
        "JIRA_API_TOKEN"
    ]
    
    missing = []
    configured = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value and not value.startswith("your-"):
            configured.append(var)
        else:
            missing.append(var)
    
    print(f"  ✓ Configured: {configured}")
    print(f"  ⚠️  Missing: {missing}")
    
    if missing:
        print("  💡 Set missing environment variables in .env file")
        return False
    else:
        print("  ✅ All required environment variables configured")
        return True

def main():
    """Run all tests."""
    print("🚀 Testing Custom LLM Farm Integration")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_custom_llm_import()
    
    # Test configuration
    config_ok = test_config_validation()
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Summary
    print("\n" + "=" * 50)
    if imports_ok and config_ok:
        print("✅ Custom LLM integration is ready!")
        if env_ok:
            print("🎉 All environment variables configured - ready to test!")
        else:
            print("⚠️  Configure environment variables in .env file to test")
        
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Configure your LLM farm credentials")
        print("3. Run: python main.py")
        return 0
    else:
        print("❌ Some issues found. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
