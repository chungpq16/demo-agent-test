"""
Custom LLM client for LLM farm API endpoint.
"""

import requests
import json
import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for the custom LLM."""
    api_url: str
    api_key: str
    model: str = "meta-llama/Meta-Llama-3-70B-Instruct"
    max_tokens: int = 2048
    temperature: float = 0.7
    verify_ssl: bool = True

class CustomLLMClient:
    """
    Custom LLM client for the LLM farm API endpoint.
    Compatible with OpenAI API format but with custom authentication.
    """
    
    def __init__(self, config: LLMConfig):
        """Initialize the custom LLM client."""
        self.config = config
        self.session = requests.Session()
        
        # Configure SSL verification
        self.session.verify = config.verify_ssl
        if not config.verify_ssl:
            # Disable SSL warnings if verification is disabled
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logger.warning("SSL verification disabled for LLM API calls")
        
        logger.info(f"Custom LLM client initialized - Model: {config.model}, SSL Verify: {config.verify_ssl}")
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "none",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to the LLM farm API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions
            tool_choice: Tool choice strategy ("none", "auto", or specific tool)
            **kwargs: Additional parameters for the API
        
        Returns:
            Response dictionary from the API
        """
        
        # Prepare the request payload
        payload = {
            "messages": messages,
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": 1,
            "stream": False,
            **kwargs
        }
        
        # Add tools if provided (even though the API doesn't support auto tool choice)
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
        
        # Prepare headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "KeyId": self.config.api_key
        }
        
        try:
            logger.debug(f"Sending request to LLM API: {self.config.api_url}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(
                self.config.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.debug(f"LLM API response: {json.dumps(result, indent=2)}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling LLM API: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM API response: {e}")
            raise
    
    def extract_content(self, response: Dict[str, Any]) -> str:
        """
        Extract the content from the LLM response.
        
        Args:
            response: Response from chat_completion
            
        Returns:
            The content string from the response
        """
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting content from response: {e}")
            logger.error(f"Response structure: {json.dumps(response, indent=2)}")
            return "Error: Could not extract response content"

def create_llm_client() -> CustomLLMClient:
    """
    Create a CustomLLMClient from environment variables.
    
    Returns:
        Configured CustomLLMClient instance
    """
    config = LLMConfig(
        api_url=os.getenv("LLM_API_URL", ""),
        api_key=os.getenv("LLM_API_KEY", ""),
        model=os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-70B-Instruct"),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        verify_ssl=os.getenv("LLM_VERIFY_SSL", "true").lower() == "true"
    )
    
    if not config.api_url or not config.api_key:
        raise ValueError("LLM_API_URL and LLM_API_KEY must be set in environment variables")
    
    return CustomLLMClient(config)
