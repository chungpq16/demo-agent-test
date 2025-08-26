#!/usr/bin/env python3
"""
Main entry point for the Jira AI Chatbot application.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_streamlit_app():
    """Run the Streamlit web application."""
    import subprocess
    import sys
    
    app_path = os.path.join(project_root, "src", "ui", "app.py")
    
    # Run streamlit with the app file
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        sys.exit(0)

def main():
    """Main entry point - runs the Streamlit web application."""
    print("🚀 Starting Jira AI Chatbot...")
    run_streamlit_app()

if __name__ == "__main__":
    main()
