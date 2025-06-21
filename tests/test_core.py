import pytest
import os
import json
import time
import tempfile
from pathlib import Path
from textfission.core.config import Config, ModelConfig, ProcessingConfig, ExportConfig, CustomConfig, ConfigManager
from textfission.core.exceptions import (
    TextFissionError,
    ConfigurationError,
    ModelError,
    GenerationError,
    ProcessingError,
    ValidationError,
    CacheError,
    ExportError,
    APIError,
    ResourceError,
    TimeoutError,
    RetryError,
    ErrorHandler,
    ErrorCodes
)

class TestConfig:
    """测试配置管理"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = Config(
            model_settings=ModelConfig(
                api_key="test-key",
                model="gpt-3.5-turbo",
                temperature=0.7
            ),
            processing_config=ProcessingConfig(
                max_workers=4,
                chunk_size=1500
            ),
            export_config=ExportConfig(
                format="json",
                output_dir="output"
            ),
            custom_config=CustomConfig(
                language="zh",
                min_confidence=0.8
            )
        )
        
        assert config.model_settings.api_key == "test-key"
        assert config.model_settings.model == "gpt-3.5-turbo"
        assert config.processing_config.max_workers == 4
        assert config.export_config.format == "json"
        assert config.custom_config.language == "zh"

    def test_config_manager_singleton(self):
        """测试配置管理器单例模式"""
        manager1 = ConfigManager.get_instance()
        manager2 = ConfigManager.get_instance()
        assert manager1 is manager2

    def test_config_from_dict(self):
        """测试从字典创建配置"""
        config_dict = {
            "model_settings": {
                "api_key": "test-key",
                "model": "gpt-3.5-turbo"
            },
            "processing_config": {
                "max_workers": 4
            },
            "export_config": {
                "format": "json"
            },
            "custom_config": {
                "language": "en"
            }
        }
        
        config = Config.from_dict(config_dict)
        assert config.model_settings.api_key == "test-key"
        assert config.processing_config.max_workers == 4

    def test_config_to_dict(self):
        """测试配置转字典"""
        config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        
        config_dict = config.to_dict()
        assert "model_settings" in config_dict
        assert "processing_config" in config_dict
        assert "export_config" in config_dict
        assert "custom_config" in config_dict

    def test_config_yaml_roundtrip(self):
        """测试YAML配置文件的读写"""
        config = Config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml_path = f.name
        
        try:
            # 保存配置
            config.to_yaml(yaml_path)
            assert os.path.exists(yaml_path)
            
            # 加载配置
            loaded_config = Config.from_yaml(yaml_path)
            assert loaded_config.model_settings.api_key == config.model_settings.api_key
        finally:
            os.unlink(yaml_path)

class TestExceptions:
    """测试异常处理"""
    
    def test_base_exception(self):
        """测试基础异常"""
        error = TextFissionError("Test error", error_code="TEST_ERROR")
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.details == {}

    def test_specific_exceptions(self):
        """测试特定异常类型"""
        exceptions = [
            (ConfigurationError, "Configuration error"),
            (ModelError, "Model error"),
            (GenerationError, "Generation error"),
            (ProcessingError, "Processing error"),
            (ValidationError, "Validation error"),
            (CacheError, "Cache error"),
            (ExportError, "Export error"),
            (APIError, "API error"),
            (ResourceError, "Resource error"),
            (TimeoutError, "Timeout error"),
            (RetryError, "Retry error")
        ]
        
        for exception_class, message in exceptions:
            error = exception_class(message)
            assert str(error) == message
            assert isinstance(error, TextFissionError)

    def test_error_handler(self):
        """测试错误处理器"""
        # 测试错误转换
        original_error = ValueError("Invalid value")
        converted_error = ErrorHandler.handle_error(
            original_error,
            error_code=ErrorCodes.INVALID_VALUE
        )
        assert isinstance(converted_error, ValidationError)
        assert converted_error.error_code == ErrorCodes.INVALID_VALUE

    def test_retry_decorator(self):
        """测试重试装饰器"""
        attempt_count = 0
        
        def failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise APIError("API error", error_code=ErrorCodes.API_ERROR)
            return "success"
        
        # 使用装饰器
        decorated_function = ErrorHandler.retry_on_error(
            failing_function,
            max_attempts=3,
            delay=0.1,
            error_codes=[ErrorCodes.API_ERROR]
        )
        
        # 应该最终成功
        result = decorated_function()
        assert result == "success"
        assert attempt_count == 3

    def test_retry_max_attempts(self):
        """测试重试最大次数"""
        def always_failing_function():
            raise APIError("API error", error_code=ErrorCodes.API_ERROR)
        
        # 使用装饰器
        decorated_function = ErrorHandler.retry_on_error(
            always_failing_function,
            max_attempts=2,
            delay=0.1,
            error_codes=[ErrorCodes.API_ERROR]
        )
        
        with pytest.raises(RetryError):
            decorated_function()

class TestErrorCodes:
    """测试错误代码"""
    
    def test_error_codes_exist(self):
        """测试错误代码存在"""
        assert hasattr(ErrorCodes, 'INVALID_CONFIG')
        assert hasattr(ErrorCodes, 'MODEL_ERROR')
        assert hasattr(ErrorCodes, 'API_ERROR')
        assert hasattr(ErrorCodes, 'PROCESSING_ERROR')
        assert hasattr(ErrorCodes, 'VALIDATION_ERROR')
        assert hasattr(ErrorCodes, 'CACHE_ERROR')
        assert hasattr(ErrorCodes, 'EXPORT_ERROR')
        assert hasattr(ErrorCodes, 'RESOURCE_ERROR')
        assert hasattr(ErrorCodes, 'TIMEOUT_ERROR')
        assert hasattr(ErrorCodes, 'RETRY_ERROR')

    def test_error_codes_values(self):
        """测试错误代码值"""
        assert ErrorCodes.INVALID_CONFIG == "INVALID_CONFIG"
        assert ErrorCodes.MODEL_ERROR == "MODEL_ERROR"
        assert ErrorCodes.API_ERROR == "API_ERROR"
        assert ErrorCodes.PROCESSING_ERROR == "PROCESSING_ERROR"
        assert ErrorCodes.VALIDATION_ERROR == "VALIDATION_ERROR"
        assert ErrorCodes.CACHE_ERROR == "CACHE_ERROR"
        assert ErrorCodes.EXPORT_ERROR == "EXPORT_ERROR"
        assert ErrorCodes.RESOURCE_ERROR == "RESOURCE_ERROR"
        assert ErrorCodes.TIMEOUT_ERROR == "TIMEOUT_ERROR"
        assert ErrorCodes.RETRY_ERROR == "RETRY_ERROR" 