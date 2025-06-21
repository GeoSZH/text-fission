import pytest
from unittest.mock import Mock, patch
from textfission.core.config import Config, ModelConfig, ProcessingConfig, ExportConfig, CustomConfig
from textfission.models.factory import ModelFactory
from textfission.models.openai import OpenAIModel
from textfission.models.qianwen import QianwenModel
from textfission.models.ernie import ErnieModel

class TestModelFactory:
    """测试模型工厂"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = Config(
            model_settings=ModelConfig(
                api_key="test-key",
                model="gpt-3.5-turbo",
                temperature=0.7
            ),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )

    def test_create_openai_model(self):
        """测试创建OpenAI模型"""
        model = ModelFactory.create_model(self.config)
        assert isinstance(model, OpenAIModel)
        assert model.model == "gpt-3.5-turbo"

    def test_create_deepseek_model(self):
        """测试创建DeepSeek模型"""
        config = Config(
            model_settings=ModelConfig(
                api_key="test-deepseek-key",
                model="deepseek-chat",
                api_base_url="https://api.deepseek.com/v1",
                temperature=0.7
            ),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        
        model = ModelFactory.create_model(config)
        assert isinstance(model, OpenAIModel)  # DeepSeek使用OpenAI接口
        assert model.model == "deepseek-chat"
        assert model.api_base_url == "https://api.deepseek.com/v1"

    def test_create_qianwen_model(self):
        """测试创建通义千问模型"""
        config = Config(
            model_settings=ModelConfig(
                api_key="test-qianwen-key",
                model="qwen-turbo",
                temperature=0.7
            ),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        
        model = ModelFactory.create_model(config)
        assert isinstance(model, QianwenModel)
        assert model.model == "qwen-turbo"

    def test_create_ernie_model(self):
        """测试创建文心一言模型"""
        config = Config(
            model_settings=ModelConfig(
                api_key="test-ernie-key",
                model="ernie-bot",
                temperature=0.7
            ),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        
        model = ModelFactory.create_model(config)
        assert isinstance(model, ErnieModel)
        assert model.model == "ernie-bot"

    def test_infer_model_type(self):
        """测试模型类型推断"""
        # 测试精确匹配
        assert ModelFactory._infer_model_type("gpt-3.5-turbo") == "openai"
        assert ModelFactory._infer_model_type("deepseek-chat") == "openai"
        assert ModelFactory._infer_model_type("qwen-turbo") == "qianwen"
        assert ModelFactory._infer_model_type("ernie-bot") == "ernie"
        
        # 测试前缀匹配
        assert ModelFactory._infer_model_type("gpt-4-custom") == "openai"
        assert ModelFactory._infer_model_type("deepseek-coder-v2") == "openai"
        assert ModelFactory._infer_model_type("qwen-max") == "qianwen"
        assert ModelFactory._infer_model_type("ernie-bot-4") == "ernie"
        
        # 测试未知模型（默认返回openai）
        assert ModelFactory._infer_model_type("unknown-model") == "openai"

    def test_get_supported_models(self):
        """测试获取支持的模型列表"""
        supported_models = ModelFactory.get_supported_models()
        
        assert "openai" in supported_models
        assert "qianwen" in supported_models
        assert "ernie" in supported_models
        
        # 检查是否包含DeepSeek模型
        assert "deepseek-chat" in supported_models["openai"]
        assert "deepseek-coder" in supported_models["openai"]

    def test_register_model(self):
        """测试注册新模型"""
        class CustomModel(OpenAIModel):
            pass
        
        ModelFactory.register_model("custom", CustomModel)
        assert "custom" in ModelFactory.MODEL_REGISTRY
        assert ModelFactory.MODEL_REGISTRY["custom"] == CustomModel

    def test_register_model_name(self):
        """测试注册模型名称映射"""
        ModelFactory.register_model_name("custom-model", "custom")
        assert "custom-model" in ModelFactory.MODEL_NAME_MAPPING
        assert ModelFactory.MODEL_NAME_MAPPING["custom-model"] == "custom"

    def test_unsupported_model_type(self):
        """测试不支持的模型类型"""
        with pytest.raises(Exception):
            ModelFactory.create_model(self.config, "unsupported_type") 