#!/usr/bin/env python3
"""
Configuration Validator for GenAI Jira Assistant
Helps diagnose configuration issues before running the application.
"""
import os
from dotenv import load_dotenv
from typing import Dict, List, Tuple

def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check if all required environment variables are set."""
    load_dotenv()
    
    required_vars = [
        'API_KEY',
        'LLM_FARM_URL', 
        'JIRA_URL',
        'JIRA_USERNAME',
        'JIRA_TOKEN',
        'JIRA_PROJECT'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value in ['your-llm-farm-api-key', 'your-username', 'your-jira-token', 
                      'YOUR-PROJECT-KEY', 'your-llm-farm-api-key-here',
                      'your.email@company.com', 'your-jira-api-token-here',
                      'YOURPROJECTKEY']:
            placeholder_vars.append(var)
    
    all_good = len(missing_vars) == 0 and len(placeholder_vars) == 0
    issues = missing_vars + placeholder_vars
    
    return all_good, issues

def test_imports() -> Tuple[bool, List[str]]:
    """Test if all required modules can be imported."""
    import_issues = []
    
    try:
        from orchestrator import JiraOrchestrator
        print("✅ Orchestrator import: OK")
    except Exception as e:
        import_issues.append(f"Orchestrator: {str(e)}")
        
    try:
        from jira_client import JiraClient
        print("✅ JiraClient import: OK")
    except Exception as e:
        import_issues.append(f"JiraClient: {str(e)}")
        
    try:
        from llm_farm_client import LLMFarmClient
        print("✅ LLMFarmClient import: OK")
    except Exception as e:
        import_issues.append(f"LLMFarmClient: {str(e)}")
        
    try:
        from logger import get_logger
        print("✅ Logger import: OK")
    except Exception as e:
        import_issues.append(f"Logger: {str(e)}")
    
    return len(import_issues) == 0, import_issues

def test_jira_connection() -> Tuple[bool, str]:
    """Test Jira connection."""
    try:
        from jira_client import JiraClient
        client = JiraClient()
        if client.health_check():
            return True, "Jira connection successful"
        else:
            return False, "Jira health check failed"
    except Exception as e:
        return False, f"Jira connection error: {str(e)}"

def test_llm_farm_connection() -> Tuple[bool, str]:
    """Test LLM Farm connection."""
    try:
        from llm_farm_client import LLMFarmClient
        client = LLMFarmClient()
        if client.health_check():
            return True, "LLM Farm connection successful"
        else:
            return False, "LLM Farm health check failed"
    except Exception as e:
        return False, f"LLM Farm connection error: {str(e)}"

def main():
    """Main validation function."""
    print("🔍 GenAI Jira Assistant - Configuration Validator")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Checking Environment Variables...")
    env_ok, env_issues = check_environment_variables()
    
    if env_ok:
        print("✅ All environment variables are configured correctly")
    else:
        print("❌ Environment variable issues found:")
        for issue in env_issues:
            if os.getenv(issue):
                print(f"  ⚠️  {issue}: Still has placeholder value")
            else:
                print(f"  ❌ {issue}: Missing or empty")
        print("\n💡 Please update your .env file with actual values")
        print("💡 See .env.example for reference")
        return
    
    # Test imports
    print("\n📦 Testing Module Imports...")
    imports_ok, import_issues = test_imports()
    
    if not imports_ok:
        print("❌ Import issues found:")
        for issue in import_issues:
            print(f"  ❌ {issue}")
        print("\n💡 Please check your dependencies: pip install -r requirements.txt")
        return
    
    # Test connections
    print("\n🔗 Testing Connections...")
    
    print("Testing Jira connection...")
    jira_ok, jira_msg = test_jira_connection()
    if jira_ok:
        print(f"✅ {jira_msg}")
    else:
        print(f"❌ {jira_msg}")
    
    print("Testing LLM Farm connection...")
    llm_ok, llm_msg = test_llm_farm_connection()
    if llm_ok:
        print(f"✅ {llm_msg}")
    else:
        print(f"❌ {llm_msg}")
    
    # Summary
    print("\n" + "=" * 60)
    if env_ok and imports_ok and jira_ok and llm_ok:
        print("🎉 All checks passed! Your application should work correctly.")
        print("🚀 You can now run: streamlit run app.py")
    else:
        print("⚠️  Some issues found. Please address them before running the application.")
        if not jira_ok or not llm_ok:
            print("💡 Connection issues are often due to:")
            print("   - Incorrect URLs or credentials")
            print("   - Network connectivity problems")  
            print("   - API tokens that have expired")

if __name__ == "__main__":
    main()
