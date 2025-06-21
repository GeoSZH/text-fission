import pytest
import tempfile
from unittest.mock import Mock, patch
from textfission.core.config import Config, ModelConfig, ProcessingConfig, ExportConfig, CustomConfig
from textfission.models.openai import OpenAIModel
from textfission.models.ernie import ErnieModel
from textfission.models.qianwen import QianwenModel

class TestOpenAIModel:
    """测试OpenAI模型"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = Config(
            model_settings=ModelConfig(
                api_key="test-openai-key",
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=1000
            ),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        self.model = OpenAIModel(self.config)

    def test_model_initialization(self):
        """测试模型初始化"""
        assert self.model.api_key == "test-openai-key"
        assert self.model.model == "gpt-3.5-turbo"
        assert self.model.temperature == 0.7
        assert self.model.max_tokens == 1000

    def test_get_model_info(self):
        """测试获取模型信息"""
        info = self.model.get_model_info()
        assert info["name"] == "gpt-3.5-turbo"
        assert info["temperature"] == 0.7
        assert info["max_tokens"] == 1000
        assert "top_p" in info
        assert "frequency_penalty" in info
        assert "presence_penalty" in info

    def test_generate_text(self):
        """测试文本生成"""
        # 模拟OpenAI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated text"
        self.model.client.chat.completions.create = Mock(return_value=mock_response)
        
        result = self.model.generate("Test prompt")
        assert result == "Generated text"

    def test_generate_with_retry(self):
        """测试重试机制"""
        # 第一次失败，第二次成功
        self.model.client.chat.completions.create = Mock(side_effect=[
            Exception("API Error"),
            Mock(choices=[Mock(message=Mock(content="Success"))])
        ])
        
        result = self.model.generate("Test prompt", max_retries=2, retry_delay=0.1)
        assert result == "Success"

    def test_get_embedding(self):
        """测试获取嵌入向量"""
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        self.model.client.embeddings.create = Mock(return_value=mock_response)
        
        embedding = self.model.get_embedding("Test text")
        assert embedding == [0.1, 0.2, 0.3]

    def test_count_tokens(self):
        """测试token计数"""
        mock_response = Mock()
        mock_response.usage.prompt_tokens = 10
        self.model.client.chat.completions.create = Mock(return_value=mock_response)
        
        token_count = self.model.count_tokens("Test text")
        assert token_count == 10

class TestErnieModel:
    """测试文心一言模型"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = Config(
            model_settings=ModelConfig(
                api_key="test-ernie-key",
                model="ernie-bot",
                temperature=0.7
            ),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        self.model = ErnieModel(self.config)

    def test_model_initialization(self):
        """测试模型初始化"""
        assert self.model.api_key == "test-ernie-key"
        assert self.model.model == "ernie-bot"
        assert self.model.temperature == 0.7

    def test_get_model_info(self):
        """测试获取模型信息"""
        info = self.model.get_model_info()
        assert info["name"] == "ernie-bot"
        assert info["type"] == "ernie"
        assert info["temperature"] == 0.7

    @patch('erniebot.ChatCompletion.create')
    def test_generate_text(self, mock_create):
        """测试文本生成"""
        mock_response = Mock()
        mock_response.get_result.return_value = "Generated text"
        mock_create.return_value = mock_response
        
        result = self.model.generate("Test prompt")
        assert result == "Generated text"

    @patch('erniebot.Embedding.create')
    def test_get_embedding(self, mock_create):
        """测试获取嵌入向量"""
        mock_response = Mock()
        mock_response.get_result.return_value = [0.1, 0.2, 0.3]
        mock_create.return_value = mock_response
        
        embedding = self.model.get_embedding("Test text")
        assert embedding == [0.1, 0.2, 0.3]

    def test_count_tokens(self):
        """测试token计数（估算）"""
        text = "This is a test text with 8 words"
        token_count = self.model.count_tokens(text)
        assert token_count > 0
        assert isinstance(token_count, int)

class TestQianwenModel:
    """测试通义千问模型"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = Config(
            model_settings=ModelConfig(
                api_key="test-qianwen-key",
                model="qwen-turbo",
                temperature=0.7
            ),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        self.model = QianwenModel(self.config)

    def test_model_initialization(self):
        """测试模型初始化"""
        assert self.model.api_key == "test-qianwen-key"
        assert self.model.model == "qwen-turbo"
        assert self.model.temperature == 0.7

    def test_get_model_info(self):
        """测试获取模型信息"""
        info = self.model.get_model_info()
        assert info["name"] == "qwen-turbo"
        assert info["type"] == "qianwen"
        assert info["temperature"] == 0.7

    @patch('dashscope.Generation.call')
    def test_generate_text(self, mock_call):
        """测试文本生成"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.output.choices = [Mock()]
        mock_response.output.choices[0].message.content = "Generated text"
        mock_call.return_value = mock_response
        
        result = self.model.generate("Test prompt")
        assert result == "Generated text"

    @patch('dashscope.Generation.call')
    def test_generate_text_error(self, mock_call):
        """测试文本生成错误"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.message = "API Error"
        mock_call.return_value = mock_response
        
        with pytest.raises(Exception):
            self.model.generate("Test prompt")

    @patch('dashscope.TextEmbedding.call')
    def test_get_embedding(self, mock_call):
        """测试获取嵌入向量"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.output.embeddings = [Mock()]
        mock_response.output.embeddings[0].embedding = [0.1, 0.2, 0.3]
        mock_call.return_value = mock_response
        
        embedding = self.model.get_embedding("Test text")
        assert embedding == [0.1, 0.2, 0.3]

    def test_count_tokens(self):
        """测试token计数（估算）"""
        text = "This is a test text with 8 words"
        token_count = self.model.count_tokens(text)
        assert token_count > 0
        assert isinstance(token_count, int)

class TestModelIntegration:
    """测试模型集成"""
    
    def test_model_compatibility(self):
        """测试模型兼容性"""
        config = Config(
            model_settings=ModelConfig(
                api_key="test-key",
                model="gpt-3.5-turbo"
            ),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        
        # 测试所有模型都能正确初始化
        openai_model = OpenAIModel(config)
        ernie_model = ErnieModel(config)
        qianwen_model = QianwenModel(config)
        
        assert openai_model is not None
        assert ernie_model is not None
        assert qianwen_model is not None
        
        # 测试所有模型都有相同的基础方法
        for model in [openai_model, ernie_model, qianwen_model]:
            assert hasattr(model, 'generate')
            assert hasattr(model, 'get_embedding')
            assert hasattr(model, 'count_tokens')
            assert hasattr(model, 'get_model_info') 