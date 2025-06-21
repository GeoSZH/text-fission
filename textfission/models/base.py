from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..core.config import Config

class BaseModel(ABC):
    """Base class for language models"""
    
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> list:
        """Get embedding for text"""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return {
            "name": "base_model",
            "type": "abstract"
        } 