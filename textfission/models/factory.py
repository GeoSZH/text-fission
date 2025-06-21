from typing import Dict, Type, Optional
from .base import BaseModel
from .openai import OpenAIModel
from .qianwen import QianwenModel
from .ernie import ErnieModel
from ..core.config import Config
from ..core.exceptions import ModelError

class ModelFactory:
    """模型工厂类，用于创建不同类型的语言模型"""
    
    # 模型类型映射
    MODEL_REGISTRY: Dict[str, Type[BaseModel]] = {
        "openai": OpenAIModel,
        "qianwen": QianwenModel,
        "ernie": ErnieModel,
    }
    
    # 模型名称到类型的映射
    MODEL_NAME_MAPPING = {
        # OpenAI 模型
        "gpt-3.5-turbo": "openai",
        "gpt-4": "openai",
        "gpt-4-turbo": "openai",
        "gpt-4o": "openai",
        "gpt-4o-mini": "openai",
        
        # DeepSeek 模型 (兼容OpenAI接口)
        "deepseek-chat": "openai",
        "deepseek-coder": "openai",
        "deepseek-v2.5": "openai",
        "deepseek-v2.5-chat": "openai",
        "deepseek-coder-v2": "openai",
        
        # 通义千问模型
        "qwen-turbo": "qianwen",
        "qwen-plus": "qianwen",
        "qwen-max": "qianwen",
        "qwen-max-longcontext": "qianwen",
        
        # 文心一言模型
        "ernie-bot": "ernie",
        "ernie-bot-turbo": "ernie",
        "ernie-bot-4": "ernie",
    }
    
    @classmethod
    def create_model(cls, config: Config, model_type: Optional[str] = None) -> BaseModel:
        """
        根据配置创建模型实例
        
        Args:
            config: 配置对象
            model_type: 模型类型，如果为None则根据模型名称自动推断
            
        Returns:
            BaseModel: 模型实例
        """
        if model_type is None:
            model_type = cls._infer_model_type(config.model_settings.model)
        
        if model_type not in cls.MODEL_REGISTRY:
            raise ModelError(f"不支持的模型类型: {model_type}")
        
        model_class = cls.MODEL_REGISTRY[model_type]
        return model_class(config)
    
    @classmethod
    def _infer_model_type(cls, model_name: str) -> str:
        """
        根据模型名称推断模型类型
        
        Args:
            model_name: 模型名称
            
        Returns:
            str: 模型类型
        """
        # 首先检查精确匹配
        if model_name in cls.MODEL_NAME_MAPPING:
            return cls.MODEL_NAME_MAPPING[model_name]
        
        # 检查前缀匹配
        for prefix, model_type in [
            ("gpt-", "openai"),
            ("deepseek-", "openai"),  # DeepSeek兼容OpenAI接口
            ("qwen-", "qianwen"),
            ("ernie-", "ernie"),
        ]:
            if model_name.startswith(prefix):
                return model_type
        
        # 默认返回OpenAI类型（兼容性考虑）
        return "openai"
    
    @classmethod
    def register_model(cls, model_type: str, model_class: Type[BaseModel]) -> None:
        """
        注册新的模型类型
        
        Args:
            model_type: 模型类型名称
            model_class: 模型类
        """
        cls.MODEL_REGISTRY[model_type] = model_class
    
    @classmethod
    def register_model_name(cls, model_name: str, model_type: str) -> None:
        """
        注册模型名称映射
        
        Args:
            model_name: 模型名称
            model_type: 模型类型
        """
        cls.MODEL_NAME_MAPPING[model_name] = model_type
    
    @classmethod
    def get_supported_models(cls) -> Dict[str, list]:
        """
        获取支持的模型列表
        
        Returns:
            Dict[str, list]: 按类型分组的模型列表
        """
        models_by_type = {}
        for model_name, model_type in cls.MODEL_NAME_MAPPING.items():
            if model_type not in models_by_type:
                models_by_type[model_type] = []
            models_by_type[model_type].append(model_name)
        return models_by_type 