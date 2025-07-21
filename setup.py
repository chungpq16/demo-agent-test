#!/usr/bin/env python3
"""
Setup script for Jira AI Chatbot application.
"""

import os
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required Python packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating .env file from .env.example...")
            with open(env_example, 'r') as source:
                content = source.read()
            
            with open(env_file, 'w') as target:
                target.write(content)
            
            print("✅ .env file created!")
            print("🔧 Please edit .env file with your actual credentials:")
            print("   - JIRA_SERVER_URL: Your Jira instance URL")
            print("   - JIRA_USERNAME: Your email address")
            print("   - JIRA_API_TOKEN: Your Jira API token")
            print("   - OPENAI_API_KEY: Your OpenAI API key")
        else:
            print("❌ .env.example file not found!")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def verify_environment():
    """Verify that required environment variables are set."""
    print("🔍 Verifying environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "JIRA_SERVER_URL",
        "JIRA_USERNAME", 
        "JIRA_API_TOKEN",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith("your-"):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  The following environment variables need to be configured:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n🔧 Please update your .env file with actual values")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_dependencies():
    """Test that all dependencies can be imported."""
    print("🧪 Testing dependencies...")
    
    try:
        import streamlit
        import langchain
        import langgraph
        import pandas
        import atlassian
        print("✅ All dependencies imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Jira AI Chatbot...")
    print("=" * 50)
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        sys.exit(1)
    
    # Step 2: Create .env file
    if not create_env_file():
        print("❌ Setup failed at environment file creation")
        sys.exit(1)
    
    # Step 3: Test dependencies
    if not test_dependencies():
        print("❌ Setup failed at dependency testing")
        sys.exit(1)
    
    # Step 4: Verify environment (optional - may fail if not configured yet)
    env_configured = verify_environment()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    
    if not env_configured:
        print("1. ✏️  Edit .env file with your actual credentials")
        print("2. 🧪 Run: python test_jira.py (to test Jira connection)")
        print("3. 🤖 Run: python test_chatbot.py (to test chatbot)")
        print("4. 🚀 Run: streamlit run app.py (to start the application)")
    else:
        print("1. 🧪 Run: python test_jira.py (to test Jira connection)")
        print("2. 🤖 Run: python test_chatbot.py (to test chatbot)")
        print("3. 🚀 Run: streamlit run app.py (to start the application)")
    
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main()
