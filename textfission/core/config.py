from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import yaml
import os
from pathlib import Path

class ModelConfig(BaseModel):
    """Model configuration"""
    api_key: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    api_base_url: Optional[str] = None
    api_keys: List[str] = Field(default_factory=list)
    models: List[str] = Field(default_factory=list)
    use_parallel: bool = False

class ProcessingConfig(BaseModel):
    """Processing configuration"""
    max_workers: int = 4
    batch_size: int = 10
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1
    cache_size: int = 1000
    cache_ttl: int = 3600
    min_chars: int = 100
    max_chars: int = 2000
    chunk_size: int = 1500
    chunk_overlap: int = 200

class ExportConfig(BaseModel):
    """Export configuration"""
    format: str = "json"
    output_dir: str = "output"
    filename_template: str = "{timestamp}_{type}.{format}"
    include_metadata: bool = True
    include_statistics: bool = True
    encoding: str = "utf-8"
    indent: int = 2
    separator: str = "\n\n"

class OutputConfig(BaseModel):
    """Output configuration (alias for ExportConfig)"""
    format: str = "json"
    output_dir: str = "output"
    filename_template: str = "{timestamp}_{type}.{format}"
    include_metadata: bool = True
    include_statistics: bool = True
    encoding: str = "utf-8"
    indent: int = 2
    separator: str = "\n\n"

class CustomConfig(BaseModel):
    """Custom configuration"""
    language: str = "en"
    min_confidence: float = 0.7
    min_quality: str = "good"
    max_questions_per_chunk: int = 5
    min_questions_per_chunk: int = 2
    question_types: List[str] = Field(default_factory=list)
    difficulty_range: tuple = (0.3, 0.8)

class Config(BaseModel):
    """Main configuration class"""
    model_settings: ModelConfig
    processing_config: ProcessingConfig
    export_config: ExportConfig
    custom_config: CustomConfig

    class Config:
        validate_by_name = True

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """Load configuration from YAML file"""
        with open(yaml_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary"""
        return cls(**config_dict)

    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to YAML file"""
        config_dict = self.model_dump()
        
        # 修复tuple序列化问题
        if 'custom_config' in config_dict and 'difficulty_range' in config_dict['custom_config']:
            config_dict['custom_config']['difficulty_range'] = list(config_dict['custom_config']['difficulty_range'])
        
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, allow_unicode=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        config_dict = self.model_dump()
        
        # 修复tuple序列化问题
        if 'custom_config' in config_dict and 'difficulty_range' in config_dict['custom_config']:
            config_dict['custom_config']['difficulty_range'] = list(config_dict['custom_config']['difficulty_range'])
        
        return config_dict

class ConfigManager:
    """Configuration manager"""
    _instance = None
    _config: Optional[Config] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ConfigManager":
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_config(self, config_path: Optional[str] = None) -> Config:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            self._config = Config.from_yaml(config_path)
        else:
            # Load from environment variables
            config_dict = {
                "model_settings": {
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "model": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
                    "temperature": float(os.getenv("TEMPERATURE", "0.7")),
                    "max_tokens": int(os.getenv("MAX_TOKENS", "2000")),
                    "use_parallel": os.getenv("USE_PARALLEL", "false").lower() == "true"
                },
                "processing_config": {
                    "max_workers": int(os.getenv("MAX_WORKERS", "4")),
                    "batch_size": int(os.getenv("BATCH_SIZE", "10")),
                    "timeout": int(os.getenv("TIMEOUT", "30")),
                    "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
                    "cache_size": int(os.getenv("CACHE_SIZE", "1000")),
                    "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),
                    "min_chars": int(os.getenv("MIN_CHARS", "100")),
                    "max_chars": int(os.getenv("MAX_CHARS", "2000")),
                    "chunk_size": int(os.getenv("CHUNK_SIZE", "1500")),
                    "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "200"))
                },
                "export_config": {
                    "format": os.getenv("EXPORT_FORMAT", "json"),
                    "output_dir": os.getenv("OUTPUT_DIR", "output"),
                    "include_metadata": os.getenv("INCLUDE_METADATA", "true").lower() == "true",
                    "include_statistics": os.getenv("INCLUDE_STATISTICS", "true").lower() == "true",
                    "encoding": os.getenv("ENCODING", "utf-8"),
                    "indent": int(os.getenv("INDENT", "2"))
                },
                "custom_config": {
                    "language": os.getenv("LANGUAGE", "en"),
                    "min_confidence": float(os.getenv("MIN_CONFIDENCE", "0.7")),
                    "min_quality": os.getenv("MIN_QUALITY", "good"),
                    "max_questions_per_chunk": int(os.getenv("MAX_QUESTIONS_PER_CHUNK", "5")),
                    "min_questions_per_chunk": int(os.getenv("MIN_QUESTIONS_PER_CHUNK", "2"))
                }
            }
            self._config = Config.from_dict(config_dict)
        return self._config

    def get_config(self) -> Config:
        """Get current configuration"""
        if self._config is None:
            self.load_config()
        return self._config

    def update_config(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration"""
        if self._config is None:
            self.load_config()
        self._config = Config.from_dict({**self._config.dict(), **config_dict})

    def save_config(self, config_path: str) -> None:
        """Save configuration to file"""
        if self._config is None:
            raise ValueError("No configuration loaded")
        self._config.to_yaml(config_path) 