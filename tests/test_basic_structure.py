#!/usr/bin/env python3
"""
Simple import test for the new folder structure (without external dependencies).
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_basic_imports():
    """Test basic imports without external dependencies."""
    print("🧪 Testing basic imports...")
    
    try:
        # Test utils (no external deps)
        print("  ✓ Testing utils module...")
        from src.utils.config import Config
        from src.utils.debug_utils import setup_logging, get_debug_info
        
        # Test clients (has atlassian-python-api dep)
        print("  ✓ Testing clients module...")
        from src.clients.jira_client import JiraClient
        
        print("✅ Basic imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_structure_only():
    """Test just the folder structure and Python path."""
    print("\n📁 Testing folder structure...")
    
    paths_to_check = [
        "src",
        "src/core",
        "src/agents", 
        "src/clients",
        "src/tools",
        "src/llm",
        "src/ui",
        "src/utils",
        "tests",
        "docs",
        "scripts"
    ]
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for path in paths_to_check:
        full_path = os.path.join(project_root, path)
        if os.path.exists(full_path):
            print(f"  ✓ {path}/")
        else:
            print(f"  ❌ {path}/ (missing)")
            return False
    
    print("✅ Folder structure is correct!")
    return True

def main():
    """Run basic tests."""
    print("🏗️  Testing Jira AI Chatbot - Folder Structure")
    print("=" * 50)
    
    # Test structure
    structure_ok = test_structure_only()
    
    # Test basic imports  
    imports_ok = test_basic_imports()
    
    # Summary
    print("\n" + "=" * 50)
    if structure_ok and imports_ok:
        print("🎉 Basic structure tests passed!")
        print("\nThe new folder structure is working correctly.")
        print("\nNote: LangChain imports may require installing dependencies.")
        print("Run 'pip install -r requirements.txt' to install all dependencies.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
