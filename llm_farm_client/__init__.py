"""
LLM Farm Client Module
Handles communication with LLM Farm for natural language processing.
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
from logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger()


class LLMFarmClient:
    """Client for interacting with LLM Farm API."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize LLM Farm client.
        
        Args:
            model: The model to use for completions
        """
        self.model = model
        self._setup_client()
        logger.info(f"LLM Farm client initialized with model: {model}")
    
    def _setup_client(self):
        """Setup OpenAI client with LLM Farm configuration."""
        api_key = os.getenv('API_KEY')
        llm_farm_url = os.getenv('LLM_FARM_URL')
        
        if not api_key:
            raise ValueError("API_KEY not found in environment variables")
        if not llm_farm_url:
            raise ValueError("LLM_FARM_URL not found in environment variables")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=llm_farm_url,
            default_headers={"genaiplatform-farm-subscription-key": api_key}
        )
        
        logger.debug(f"OpenAI client configured with base_url: {llm_farm_url}")
    
    def _generate_messages(self, system_prompt: str, user_prompt: str) -> List[Dict[str, str]]:
        """
        Generate message array for OpenAI API.
        
        Args:
            system_prompt: System prompt for context/instructions
            user_prompt: User prompt/query
            
        Returns:
            List of message dictionaries
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        logger.debug(f"Generated messages: {len(messages)} messages")
        return messages
    
    def completion(self, user_text: str, system_prompt: str = "You are a helpful assistant") -> str:
        """
        Get completion from LLM Farm.
        
        Args:
            user_text: User input text
            system_prompt: System prompt for context
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            logger.debug(f"Starting completion request for user_text length: {len(user_text)}")
            
            messages = self._generate_messages(system_prompt, user_text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                extra_query={"api-version": "2024-08-01-preview"}
            )
            
            result = response.choices[0].message.content
            logger.info(f"Completion successful, response length: {len(result) if result else 0}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in completion request: {str(e)}")
            raise Exception(f"LLM Farm completion failed: {str(e)}")
    
    def completion_with_functions(self, user_text: str, system_prompt: str, functions: List[Dict], function_call: Optional[str] = None) -> Dict:
        """
        Get completion with function calling support.
        
        Args:
            user_text: User input text
            system_prompt: System prompt for context
            functions: List of available functions
            function_call: Specific function to call or "auto"
            
        Returns:
            Complete response object including function calls
        """
        try:
            logger.debug(f"Starting completion with functions: {len(functions)} functions available")
            
            messages = self._generate_messages(system_prompt, user_text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call=function_call or "auto",
                extra_query={"api-version": "2024-08-01-preview"}
            )
            
            logger.info("Completion with functions successful")
            return response
            
        except Exception as e:
            logger.error(f"Error in completion with functions: {str(e)}")
            raise Exception(f"LLM Farm function completion failed: {str(e)}")
    
    def health_check(self) -> bool:
        """
        Check if LLM Farm is accessible and responding.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            test_response = self.completion("Hello", "Respond with 'OK' only")
            logger.info("LLM Farm health check passed")
            return True
        except Exception as e:
            logger.error(f"LLM Farm health check failed: {str(e)}")
            return False
