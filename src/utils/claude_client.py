import os
import logging
import anthropic
from typing import List, Dict, Any
import json

# Configure logging to write to a file instead of terminal
logging.basicConfig(
    filename='career_planner.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ClaudeClient:
    """Client for interacting with Claude API"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.logger = logging.getLogger(__name__)
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
        
    async def get_response(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Get a response from Claude"""
        try:
            # Log request payload for debugging
            request_payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            self.logger.debug(f"Request payload: {json.dumps(request_payload)}")
            
            # Make API call using the Anthropic SDK
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages
            )
            
            # Log response for debugging
            self.logger.debug(f"Response: {response}")
            
            # Return the response content
            return response.content[0].text
            
        except Exception as e:
            self.logger.error(f"Error calling Claude API: {e}")
            raise