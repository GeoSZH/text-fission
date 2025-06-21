from typing import Dict, Any, Optional
from ..core.base import BaseModel
from ..core.exceptions import ModelError
import erniebot

class ErnieModel(BaseModel):
    """文心一言模型实现"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.model_settings.api_key
        self.model = config.model_settings.model or "ernie-bot"
        self.temperature = config.model_settings.temperature
        
        # 设置API密钥
        erniebot.api_key = self.api_key

    def generate(self, prompt: str, **kwargs) -> str:
        """使用文心一言生成文本"""
        try:
            response = erniebot.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                **kwargs
            )
            return response.get_result()
        except Exception as e:
            raise ModelError(f"文心一言API调用失败: {str(e)}")

    def get_embedding(self, text: str) -> list:
        """获取文本嵌入向量"""
        try:
            response = erniebot.Embedding.create(
                model="ernie-text-embedding",
                input=text
            )
            return response.get_result()
        except Exception as e:
            raise ModelError(f"获取嵌入向量失败: {str(e)}")

    def count_tokens(self, text: str) -> int:
        """计算文本token数量"""
        # 文心一言没有直接的token计数API，使用估算
        return len(text) // 4  # 粗略估算

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "name": self.model,
            "type": "ernie",
            "temperature": self.temperature
        } 