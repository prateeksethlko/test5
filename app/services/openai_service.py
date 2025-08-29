import logging
from typing import Dict, List, Optional, Any
from openai import AzureOpenAI
from app.utils.exceptions import OpenAIServiceError

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for managing OpenAI API interactions."""
    
    def __init__(self, api_key: str, endpoint: str, deployment: str, api_version: str):
        if not api_key or not endpoint or not deployment:
            raise OpenAIServiceError("Missing required OpenAI configuration")
        
        self.deployment = deployment
        self.client = self._initialize_client(api_key, endpoint, api_version)
    
    def _initialize_client(self, api_key: str, endpoint: str, api_version: str) -> AzureOpenAI:
        """Initialize Azure OpenAI client with latest SDK."""
        try:
            # Extract base endpoint from full endpoint URL
            if "/openai/deployments/" in endpoint:
                azure_endpoint = endpoint.split("/openai/deployments/")[0]
            else:
                azure_endpoint = endpoint.rstrip("/")
            
            # Use the latest AzureOpenAI client initialization
            return AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise OpenAIServiceError(f"OpenAI client initialization failed: {e}")
    
    def chat_completion(self, messages: List[Dict], tools: Optional[List] = None, 
                       tool_choice: Optional[str] = None, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate chat completion."""
        try:
            params = {
                "model": self.deployment,
                "messages": messages,
                "temperature": temperature
            }
            
            if tools:
                params["tools"] = tools
            if tool_choice:
                params["tool_choice"] = tool_choice
            
            response = self.client.chat.completions.create(**params)
            message = response.choices[0].message
            
            if hasattr(message, "tool_calls") and message.tool_calls:
                return {
                    "tool_calls": [{
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        },
                        "type": "function"
                    } for tc in message.tool_calls]
                }
            else:
                return {"content": message.content}
                
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise OpenAIServiceError(f"Chat completion failed: {e}")
