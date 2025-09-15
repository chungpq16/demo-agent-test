#!/usr/bin/env python3
"""
GenAI Application with LLM Farm Integration
Main application entry point for Jira operations via natural language processing.
"""
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from orchestrator import JiraOrchestrator
from logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger()


class GenAIApp:
    """Main GenAI application class."""
    
    def __init__(self):
        """Initialize the application."""
        logger.info("Starting GenAI Application")
        self.orchestrator: Optional[JiraOrchestrator] = None
        self._initialize()
    
    def _initialize(self):
        """Initialize application components."""
        try:
            # Validate environment variables
            self._validate_environment()
            
            # Initialize orchestrator
            self.orchestrator = JiraOrchestrator()
            
            # Perform health check
            health_status = self.orchestrator.health_check()
            
            if not health_status["overall"]:
                logger.warning("Health check failed for some components:")
                for component, status in health_status.items():
                    if not status:
                        logger.warning(f"  - {component}: {status}")
            else:
                logger.info("All components initialized and healthy")
                
        except Exception as e:
            logger.critical(f"Failed to initialize application: {str(e)}")
            raise
    
    def _validate_environment(self):
        """Validate required environment variables."""
        required_vars = [
            'API_KEY',
            'LLM_FARM_URL',
            'JIRA_URL',
            'JIRA_USERNAME',
            'JIRA_TOKEN',
            'JIRA_PROJECT'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        logger.debug("Environment validation passed")
    
    def run_interactive(self):
        """Run the application in interactive mode."""
        logger.info("Starting interactive mode")
        
        print("🤖 GenAI Jira Assistant")
        print("=" * 50)
        print("Type 'help' for available commands, 'quit' to exit")
        print()
        
        while True:
            try:
                user_input = input("➤ ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print(self.orchestrator.get_help())
                    continue
                
                if user_input.lower() == 'health':
                    health = self.orchestrator.health_check()
                    print("🏥 Health Check Results:")
                    for component, status in health.items():
                        emoji = "✅" if status else "❌"
                        print(f"  {emoji} {component}: {'Healthy' if status else 'Unhealthy'}")
                    continue
                
                # Process the request
                print("🔄 Processing...")
                response = self.orchestrator.process_request(user_input)
                print(f"💬 {response}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {str(e)}")
                print(f"❌ Error: {str(e)}")
                print()
    
    def run_single_query(self, query: str) -> str:
        """
        Run a single query and return the result.
        
        Args:
            query: User query string
            
        Returns:
            Response string
        """
        logger.info(f"Processing single query: {query}")
        
        try:
            response = self.orchestrator.process_request(query)
            logger.info("Single query processed successfully")
            return response
        except Exception as e:
            logger.error(f"Error processing single query: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_health_status(self) -> dict:
        """Get application health status."""
        if not self.orchestrator:
            return {"error": "Application not initialized"}
        
        return self.orchestrator.health_check()


def main():
    """Main function."""
    try:
        app = GenAIApp()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == '--health':
                # Health check mode
                health = app.get_health_status()
                print("Health Status:")
                for component, status in health.items():
                    print(f"  {component}: {'✅ Healthy' if status else '❌ Unhealthy'}")
                sys.exit(0 if health.get("overall", False) else 1)
            
            elif sys.argv[1] == '--query':
                # Single query mode
                if len(sys.argv) < 3:
                    print("Usage: python main.py --query \"your question here\"")
                    sys.exit(1)
                
                query = " ".join(sys.argv[2:])
                response = app.run_single_query(query)
                print(response)
                sys.exit(0)
            
            elif sys.argv[1] in ['--help', '-h']:
                # Help mode
                print("""
GenAI Jira Assistant

Usage:
  python main.py                    # Interactive mode
  python main.py --query "question" # Single query mode  
  python main.py --health          # Health check
  python main.py --help           # Show this help

Examples:
  python main.py --query "Show me all open issues"
  python main.py --query "Get details for PROJ-123"
  python main.py --health
                """)
                sys.exit(0)
        
        # Default: run interactive mode
        app.run_interactive()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n👋 Application interrupted. Goodbye!")
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}")
        print(f"❌ Critical Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
