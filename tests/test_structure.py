#!/usr/bin/env python3
"""
Simple test script to verify the new folder structure works.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all imports work correctly."""
    print("🧪 Testing imports with new folder structure...")
    
    try:
        # Test core imports
        print("  ✓ Testing core module...")
        from src.core.chatbot import JiraChatbot
        
        # Test agents imports
        print("  ✓ Testing agents module...")
        from src.agents.jira_agent import JiraAgent
        
        # Test clients imports
        print("  ✓ Testing clients module...")
        from src.clients.jira_client import JiraClient
        
        # Test tools imports
        print("  ✓ Testing tools module...")
        from src.tools.jira_tools import JIRA_TOOLS, initialize_tools
        
        # Test utils imports
        print("  ✓ Testing utils module...")
        from src.utils.config import Config
        from src.utils.debug_utils import setup_logging, get_debug_info
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_initialization():
    """Test basic initialization without external dependencies."""
    print("\n🔧 Testing basic initialization...")
    
    try:
        # Test config
        from src.utils.config import Config
        config = Config()
        print("  ✓ Config class initialization")
        
        # Test logging setup
        from src.utils.debug_utils import setup_logging
        logger = setup_logging(debug=True)
        print("  ✓ Logging setup")
        
        print("✅ Basic initialization successful!")
        return True
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Jira AI Chatbot - New Folder Structure")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test initialization
    init_ok = test_initialization()
    
    # Summary
    print("\n" + "=" * 50)
    if imports_ok and init_ok:
        print("🎉 All tests passed! The new folder structure is working correctly.")
        print("\nNext steps:")
        print("1. Run 'python main.py --cli' to test CLI mode")
        print("2. Run 'python main.py --web' to test web interface")
        print("3. Configure your .env file with Jira credentials")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
