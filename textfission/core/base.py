from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .config import Config
from .exceptions import TextFissionError

class BaseProcessor(ABC):
    """Base class for all processors"""
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Process the input data"""
        pass

class BaseSplitter(ABC):
    """Base class for text splitters"""
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def split(self, text: str) -> List[str]:
        """Split text into chunks"""
        pass

class BaseQuestionGenerator(ABC):
    """Base class for question generators"""
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def generate(self, chunk: str) -> List[str]:
        """Generate questions from text chunk"""
        pass

class BaseAnswerGenerator(ABC):
    """Base class for answer generators"""
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def generate(self, chunk: str, question: str) -> Dict[str, Any]:
        """Generate answer for a question from text chunk"""
        pass

class BaseModel(ABC):
    """Base class for language models"""
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from prompt"""
        pass

class BaseExporter(ABC):
    """Base class for data exporters"""
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def export(self, data: Any, path: str) -> None:
        """Export data to file"""
        pass 