"""
Ollama client for LLM interactions.
"""

import logging
import requests
import json
from typing import Dict, Any, Optional, List

from ..config.settings import config

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama LLM service."""
    
    def __init__(self):
        self.base_url = config.OLLAMA_URL
        self.default_model = config.DEFAULT_MODEL
        self.temperature = config.TEMPERATURE
        self.max_tokens = config.MAX_TOKENS
    
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama service not available: {str(e)}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            else:
                logger.error(f"Failed to list models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    def generate_response(self, prompt: str, model: str = None, 
                         context: List[str] = None, **kwargs) -> Optional[str]:
        """
        Generate a response using Ollama.
        
        Args:
            prompt: The input prompt
            model: Model to use (defaults to configured model)
            context: Optional context documents
            **kwargs: Additional parameters
            
        Returns:
            Generated response text or None if failed
        """
        model = model or self.default_model
        
        # Prepare the full prompt with context
        full_prompt = self._prepare_prompt_with_context(prompt, context)
        
        try:
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', self.temperature),
                    "num_predict": kwargs.get('max_tokens', self.max_tokens)
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.error(f"Failed to generate response: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return None
    
    def _prepare_prompt_with_context(self, prompt: str, context: List[str] = None) -> str:
        """Prepare prompt with context documents."""
        if not context:
            return prompt
        
        context_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context)])
        
        full_prompt = f"""Käytä seuraavia dokumentteja vastataksesi kysymykseen:

{context_text}

Kysymys: {prompt}

Vastaus (käytä vain annettujen dokumenttien tietoja):"""
        
        return full_prompt
    
    def pull_model(self, model_name: str) -> bool:
        """
        Pull/download a model.
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {"name": model_name}
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=300  # 5 minutes timeout for model download
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model_name}")
                return True
            else:
                logger.error(f"Failed to pull model {model_name}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {str(e)}")
            return False
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        try:
            payload = {"name": model_name}
            response = requests.post(
                f"{self.base_url}/api/show",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get model info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return None