from typing import Dict, Any, Optional
from ..core.base import BaseModel
from ..core.exceptions import ModelError
from dashscope import Generation

class QianwenModel(BaseModel):
    """通义千问模型实现"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.model_settings.api_key
        self.model = config.model_settings.model or "qwen-turbo"
        self.temperature = config.model_settings.temperature
        
        # 设置API密钥
        import os
        os.environ['DASHSCOPE_API_KEY'] = self.api_key

    def generate(self, prompt: str, **kwargs) -> str:
        """使用通义千问生成文本"""
        try:
            response = Generation.call(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                **kwargs
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                raise ModelError(f"通义千问API调用失败: {response.message}")
        except Exception as e:
            raise ModelError(f"通义千问API调用失败: {str(e)}")

    def get_embedding(self, text: str) -> list:
        """获取文本嵌入向量"""
        try:
            from dashscope import TextEmbedding
            response = TextEmbedding.call(
                model="text-embedding-v1",
                input=text
            )
            
            if response.status_code == 200:
                return response.output.embeddings[0].embedding
            else:
                raise ModelError(f"获取嵌入向量失败: {response.message}")
        except Exception as e:
            raise ModelError(f"获取嵌入向量失败: {str(e)}")

    def count_tokens(self, text: str) -> int:
        """计算文本token数量"""
        # 通义千问没有直接的token计数API，使用估算
        return len(text) // 4  # 粗略估算

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "name": self.model,
            "type": "qianwen",
            "temperature": self.temperature
        } 