# TextFission

TextFission 是一个强大的文本处理工具,用于将长文本分割成小块,并生成相关的问题和答案。它支持多种语言,提供智能的文本分割策略,并生成高质量的问题和答案。

## 主要特性

### 1. 智能文本分割
- 支持多语言(中英文)
- 基于语义的分割策略
- 自动语言检测
- 保持语义完整性的分块
- 智能文本预处理

### 2. 问题生成
- 多种问题类型(事实性、推理性、分析性等)
- 问题质量评估
- 问题难度控制
- 关键词提取
- 上下文相关性检查

### 3. 答案生成
- 多模型支持
- 答案质量评估
- 引用提取
- 置信度评分
- 相关性检查

### 4. 多模型支持
- **OpenAI模型**: GPT-3.5, GPT-4, GPT-4o等
- **DeepSeek模型**: deepseek-chat, deepseek-coder等（兼容OpenAI接口）
- **通义千问**: qwen-turbo, qwen-plus, qwen-max等
- **文心一言**: ernie-bot, ernie-bot-turbo等
- **自定义模型**: 支持注册新的模型类型

### 5. 系统功能
- 统一的配置管理
- 结构化的日志记录
- 多级缓存机制
- 完善的错误处理
- 并行处理优化

## 安装

```bash
pip install textfission
```

### 依赖兼容性说明

如果遇到依赖冲突，特别是numpy版本冲突，请尝试以下解决方案：

#### 方案1：使用兼容的numpy版本
```bash
pip install "numpy>=1.21.0,<2.0.0"
pip install textfission
```

#### 方案2：创建虚拟环境（推荐）
```bash
python -m venv textfission-env
source textfission-env/bin/activate  # Linux/Mac
# 或
textfission-env\Scripts\activate  # Windows
pip install textfission
```

#### 方案3：使用conda环境
```bash
conda create -n textfission python=3.11
conda activate textfission
pip install textfission
```

### 常见问题

**依赖冲突错误**：如果遇到类似以下错误：
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
```

请参考 [安装指南](docs/installation.md) 中的详细解决方案。

## 快速开始

### 基本用法
```python
from textfission import create_dataset, Config, ModelConfig

# 创建配置
config = Config(
    model_settings=ModelConfig(
        api_key="your-api-key",
        model="gpt-3.5-turbo"
    )
)

# 处理文本
text = "你的长文本内容..."
result = create_dataset(text, config, "output/dataset.json")
```

### 使用DeepSeek模型
```python
from textfission import create_dataset, Config, ModelConfig

# 创建DeepSeek配置
config = Config(
    model_settings=ModelConfig(
        api_key="your-deepseek-api-key",
        model="deepseek-chat",
        api_base_url="https://api.deepseek.com/v1"  # DeepSeek API端点
    )
)

# 处理文本
text = "你的长文本内容..."
result = create_dataset(text, config, "output/deepseek_dataset.json")
```

### 使用通义千问模型
```python
from textfission import create_dataset, Config, ModelConfig

# 创建通义千问配置
config = Config(
    model_settings=ModelConfig(
        api_key="your-qianwen-api-key",
        model="qwen-turbo"
    )
)

# 处理文本
text = "你的长文本内容..."
result = create_dataset(text, config, "output/qianwen_dataset.json")
```

## 配置说明

### 基本配置
```python
config = {
    "model_settings": {
        "api_key": "your-api-key",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
        "api_base_url": None  # 可选：自定义API端点
    },
    "processing_config": {
        "max_workers": 4,
        "batch_size": 10,
        "timeout": 30
    },
    "export_config": {
        "format": "json",
        "output_dir": "output"
    },
    "custom_config": {
        "language": "zh",
        "min_confidence": 0.7,
        "min_quality": "good"
    }
}
```

### 支持的模型

#### OpenAI兼容模型
- **OpenAI**: gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini
- **DeepSeek**: deepseek-chat, deepseek-coder, deepseek-v2.5, deepseek-v2.5-chat, deepseek-coder-v2
- **其他兼容OpenAI接口的模型**: 通过设置`api_base_url`参数支持

#### 通义千问模型
- qwen-turbo, qwen-plus, qwen-max, qwen-max-longcontext

#### 文心一言模型
- ernie-bot, ernie-bot-turbo, ernie-bot-4

### 环境变量
```bash
OPENAI_API_KEY=your-api-key
MODEL_NAME=gpt-3.5-turbo
LANGUAGE=zh
MAX_WORKERS=4
BATCH_SIZE=10
```

## 高级用法

### 1. 使用模型工厂
```python
from textfission import ModelFactory, Config

# 自动推断模型类型
config = Config(...)
model = ModelFactory.create_model(config)

# 手动指定模型类型
model = ModelFactory.create_model(config, model_type="openai")

# 查看支持的模型
supported_models = ModelFactory.get_supported_models()
print(supported_models)
```

### 2. 注册自定义模型
```python
from textfission import ModelFactory
from textfission.models.base import BaseModel

class CustomModel(BaseModel):
    def generate(self, prompt: str) -> str:
        # 实现生成逻辑
        pass
    
    def get_embedding(self, text: str) -> list:
        # 实现嵌入逻辑
        pass
    
    def count_tokens(self, text: str) -> int:
        # 实现token计数逻辑
        pass

# 注册模型
ModelFactory.register_model("custom", CustomModel)
ModelFactory.register_model_name("my-model", "custom")
```

### 3. 自定义文本分割
```python
from textfission.processors import SmartTextSplitter

splitter = SmartTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    language="zh"
)

chunks = splitter.split(text)
```

### 4. 自定义问题生成
```python
from textfission.processors import QuestionGenerator

generator = QuestionGenerator(
    max_questions_per_chunk=5,
    min_questions_per_chunk=2,
    question_types=["factual", "inferential"]
)

questions = generator.generate(chunk)
```

### 5. 自定义答案生成
```python
from textfission.processors import AnswerGenerator

generator = AnswerGenerator(
    min_confidence=0.7,
    min_quality="good"
)

answer = generator.generate(chunk, question)
```

### 6. 使用缓存
```python
from textfission.core import CacheManager

cache = CacheManager.get_instance()
cache.setup(
    max_size=1000,
    default_ttl=3600,
    cache_dir="cache"
)

# 使用缓存
result = cache.get_or_set(
    key="unique_key",
    default_func=lambda: process_text(text)
)
```

### 7. 错误处理
```python
from textfission.core import ErrorHandler, ErrorCodes

@ErrorHandler.retry_on_error(
    max_attempts=3,
    delay=1.0,
    error_codes=[ErrorCodes.API_ERROR]
)
def process_with_retry():
    # 你的处理代码
    pass
```

## 性能优化

### 1. 并行处理
```python
# 启用并行处理
config = {
    "model_settings": {
        "use_parallel": True,
        "api_keys": ["key1", "key2"],
        "models": ["model1", "model2"]
    }
}
```

### 2. 批处理
```python
# 批量处理
results = tf.process_batch(texts, batch_size=10)
```

### 3. 缓存优化
```python
# 配置缓存
config = {
    "processing_config": {
        "cache_size": 1000,
        "cache_ttl": 3600
    }
}
```

## 导出格式

### 1. JSON格式
```json
{
    "chunks": [
        {
            "text": "文本块内容",
            "metadata": {
                "language": "zh",
                "length": 1000
            }
        }
    ],
    "questions": [
        {
            "text": "问题内容",
            "type": "factual",
            "difficulty": 0.7,
            "keywords": ["关键词1", "关键词2"]
        }
    ],
    "answers": [
        {
            "text": "答案内容",
            "metadata": {
                "quality": "good",
                "confidence": 0.9,
                "citations": [
                    {
                        "text": "引用文本",
                        "position": "位置"
                    }
                ]
            }
        }
    ]
}
```

### 2. CSV格式
```csv
chunk_id,chunk_text,question_id,question_text,answer_text,quality,confidence
1,文本块1,1,问题1,答案1,good,0.9
1,文本块1,2,问题2,答案2,excellent,0.95
```

## 错误处理

### 1. 错误类型
- ConfigurationError: 配置相关错误
- ModelError: 模型相关错误
- GenerationError: 生成相关错误
- ProcessingError: 处理相关错误
- ValidationError: 验证相关错误
- CacheError: 缓存相关错误
- ExportError: 导出相关错误
- APIError: API相关错误
- ResourceError: 资源相关错误
- TimeoutError: 超时相关错误
- RetryError: 重试相关错误

### 2. 错误处理示例
```python
try:
    result = tf.process(text)
except TextFissionError as e:
    print(f"Error: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"Details: {e.details}")
```

## 日志记录

### 1. 日志配置
```python
from textfission.core import Logger

logger = Logger.get_instance()
logger.setup(
    name="textfission",
    level=logging.INFO,
    log_file="logs/textfission.log"
)
```

### 2. 日志使用
```python
logger.info("Processing started", text_length=len(text))
logger.error("Processing failed", error=str(e))
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

- 项目主页: https://github.com/GeoSZH/text-fission
- 问题反馈: https://github.com/GeoSZH/text-fission/issues 