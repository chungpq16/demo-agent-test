#!/usr/bin/env python3
"""
Quick verification that CLI mode is removed and main.py works correctly.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_main_entry():
    """Test that main.py no longer has CLI mode."""
    print("🧪 Testing main.py entry point...")
    
    try:
        # Read main.py content
        main_path = os.path.join(project_root, "main.py")
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Check that CLI mode is removed
        if "run_cli_mode" in content:
            print("❌ CLI mode function still exists")
            return False
        
        if "--cli" in content:
            print("❌ CLI arguments still exist")
            return False
        
        if "argparse" in content:
            print("❌ Argument parsing still exists")
            return False
        
        print("  ✓ CLI mode completely removed")
        print("  ✓ Main entry point simplified")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing main.py: {e}")
        return False

def test_basic_imports():
    """Test basic imports without running Streamlit."""
    print("\n🧪 Testing basic imports...")
    
    try:
        # Test core imports
        from src.utils.config import Config
        from src.utils.debug_utils import setup_logging
        print("  ✓ Utils modules")
        
        from src.clients.jira_client import JiraClient
        print("  ✓ Clients module")
        
        print("✅ Basic imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run verification tests."""
    print("🔍 Verifying CLI Mode Removal")
    print("=" * 40)
    
    # Test main entry point
    main_ok = test_main_entry()
    
    # Test basic imports
    imports_ok = test_basic_imports()
    
    # Summary
    print("\n" + "=" * 40)
    if main_ok and imports_ok:
        print("✅ CLI mode successfully removed!")
        print("\nThe application now only supports web interface:")
        print("  python main.py")
        return 0
    else:
        print("❌ Some issues found during verification.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
