from typing import Optional, Dict, Any
from ..core.base import BaseModel
from ..core.exceptions import ModelError
import openai
from openai import OpenAI
import time

class OpenAIModel(BaseModel):
    """OpenAI model implementation"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.model_settings.api_key
        self.model = config.model_settings.model
        self.temperature = config.model_settings.temperature
        self.max_tokens = config.model_settings.max_tokens
        self.top_p = config.model_settings.top_p
        self.frequency_penalty = config.model_settings.frequency_penalty
        self.presence_penalty = config.model_settings.presence_penalty
        self.api_base_url = config.model_settings.api_base_url
        
        # Initialize OpenAI client with custom base URL if provided
        if self.api_base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_base_url)
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        # Set default values if not provided
        if not self.model:
            self.model = "gpt-3.5-turbo"
        if self.temperature is None:
            self.temperature = 0.7
        if self.max_tokens is None:
            self.max_tokens = 2000
        if self.top_p is None:
            self.top_p = 1.0
        if self.frequency_penalty is None:
            self.frequency_penalty = 0.0
        if self.presence_penalty is None:
            self.presence_penalty = 0.0

    def generate(self, prompt: str, max_retries: int = 3, retry_delay: float = 1.0) -> str:
        """Generate text using OpenAI model"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise ModelError(f"Failed to generate text after {max_retries} attempts: {str(e)}")
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff

    def generate_with_custom_params(self, prompt: str, **kwargs) -> str:
        """Generate text with custom parameters"""
        try:
            # Get default parameters
            params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": self.top_p,
                "frequency_penalty": self.frequency_penalty,
                "presence_penalty": self.presence_penalty
            }
            
            # Update with custom parameters
            params.update(kwargs)
            
            # Generate response
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise ModelError(f"Error generating text with custom parameters: {str(e)}")

    def get_embedding(self, text: str) -> list:
        """Get embedding for text"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise ModelError(f"Error getting embedding: {str(e)}")

    def get_embeddings(self, texts: list) -> list:
        """Get embeddings for multiple texts"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise ModelError(f"Error getting embeddings: {str(e)}")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": text}
                ],
                max_tokens=1
            )
            return response.usage.prompt_tokens
        except Exception as e:
            raise ModelError(f"Error counting tokens: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return {
            "name": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        } 