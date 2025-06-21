# TextFission API 文档

## 核心模块

### 配置管理 (ConfigManager)

配置管理模块提供了统一的配置管理功能。

#### 类: ConfigManager

单例模式的配置管理器。

##### 方法:

- `get_instance() -> ConfigManager`
  - 获取配置管理器实例
  - 返回: ConfigManager实例

- `load_config(config_path: Optional[str] = None) -> Config`
  - 从文件或环境变量加载配置
  - 参数:
    - config_path: 配置文件路径(可选)
  - 返回: Config实例

- `get_config() -> Config`
  - 获取当前配置
  - 返回: Config实例

- `update_config(config_dict: Dict[str, Any]) -> None`
  - 更新配置
  - 参数:
    - config_dict: 配置字典

- `save_config(config_path: str) -> None`
  - 保存配置到文件
  - 参数:
    - config_path: 配置文件路径

#### 类: Config

配置类,包含所有配置项。

##### 属性:

- `model_config: ModelConfig`
  - 模型配置
- `processing_config: ProcessingConfig`
  - 处理配置
- `export_config: ExportConfig`
  - 导出配置
- `custom_config: CustomConfig`
  - 自定义配置

##### 方法:

- `from_yaml(yaml_path: str) -> Config`
  - 从YAML文件加载配置
  - 参数:
    - yaml_path: YAML文件路径
  - 返回: Config实例

- `to_yaml(yaml_path: str) -> None`
  - 保存配置到YAML文件
  - 参数:
    - yaml_path: YAML文件路径

### 日志管理 (Logger)

日志管理模块提供了结构化的日志记录功能。

#### 类: Logger

单例模式的日志管理器。

##### 方法:

- `get_instance() -> Logger`
  - 获取日志管理器实例
  - 返回: Logger实例

- `setup(name: str = "textfission", level: int = logging.INFO, log_file: Optional[str] = None, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5, console_output: bool = True) -> logging.Logger`
  - 设置日志记录器
  - 参数:
    - name: 日志记录器名称
    - level: 日志级别
    - log_file: 日志文件路径
    - max_bytes: 单个日志文件最大大小
    - backup_count: 备份文件数量
    - console_output: 是否输出到控制台
  - 返回: logging.Logger实例

- `get_logger() -> logging.Logger`
  - 获取当前日志记录器
  - 返回: logging.Logger实例

- `set_level(level: int) -> None`
  - 设置日志级别
  - 参数:
    - level: 日志级别

- `add_file_handler(log_file: str, level: int = logging.INFO, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5) -> None`
  - 添加文件处理器
  - 参数:
    - log_file: 日志文件路径
    - level: 日志级别
    - max_bytes: 单个日志文件最大大小
    - backup_count: 备份文件数量

- `remove_file_handler(log_file: str) -> None`
  - 移除文件处理器
  - 参数:
    - log_file: 日志文件路径

- `log_with_context(level: int, message: str, **kwargs) -> None`
  - 记录带上下文的日志
  - 参数:
    - level: 日志级别
    - message: 日志消息
    - **kwargs: 上下文数据

### 缓存管理 (CacheManager)

缓存管理模块提供了多级缓存功能。

#### 类: CacheManager

单例模式的缓存管理器。

##### 方法:

- `get_instance() -> CacheManager`
  - 获取缓存管理器实例
  - 返回: CacheManager实例

- `setup(max_size: int = 1000, default_ttl: int = 3600, cache_dir: Optional[str] = None) -> Cache`
  - 设置缓存
  - 参数:
    - max_size: 最大缓存条目数
    - default_ttl: 默认过期时间(秒)
    - cache_dir: 缓存目录
  - 返回: Cache实例

- `get_cache() -> Cache`
  - 获取当前缓存实例
  - 返回: Cache实例

#### 类: Cache

缓存类,提供缓存操作功能。

##### 方法:

- `get(key: Any, default: Any = None) -> Any`
  - 获取缓存值
  - 参数:
    - key: 缓存键
    - default: 默认值
  - 返回: 缓存值

- `set(key: Any, value: Any, ttl: Optional[int] = None, persist: bool = False) -> None`
  - 设置缓存值
  - 参数:
    - key: 缓存键
    - value: 缓存值
    - ttl: 过期时间(秒)
    - persist: 是否持久化

- `delete(key: Any) -> None`
  - 删除缓存值
  - 参数:
    - key: 缓存键

- `clear() -> None`
  - 清空缓存

- `get_or_set(key: Any, default_func: Callable[[], Any], ttl: Optional[int] = None, persist: bool = False) -> Any`
  - 获取缓存值,如果不存在则设置
  - 参数:
    - key: 缓存键
    - default_func: 默认值生成函数
    - ttl: 过期时间(秒)
    - persist: 是否持久化
  - 返回: 缓存值

- `exists(key: Any) -> bool`
  - 检查缓存键是否存在
  - 参数:
    - key: 缓存键
  - 返回: 是否存在

- `get_stats() -> Dict[str, Any]`
  - 获取缓存统计信息
  - 返回: 统计信息字典

### 错误处理 (ErrorHandler)

错误处理模块提供了统一的错误处理功能。

#### 类: ErrorHandler

错误处理工具类。

##### 方法:

- `handle_error(error: Exception, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> TextFissionError`
  - 处理异常
  - 参数:
    - error: 异常
    - error_code: 错误代码
    - details: 错误详情
  - 返回: TextFissionError实例

- `retry_on_error(func, max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, error_codes: Optional[list] = None)`
  - 重试装饰器
  - 参数:
    - func: 要重试的函数
    - max_attempts: 最大重试次数
    - delay: 重试延迟(秒)
    - backoff: 延迟增长因子
    - error_codes: 要重试的错误代码列表
  - 返回: 装饰器函数

#### 类: ErrorCodes

错误代码常量类。

##### 常量:

- 配置错误:
  - INVALID_CONFIG
  - MISSING_CONFIG
  - INVALID_VALUE

- 模型错误:
  - MODEL_ERROR
  - API_ERROR
  - RATE_LIMIT

- 生成错误:
  - GENERATION_ERROR
  - INVALID_PROMPT
  - INVALID_OUTPUT

- 处理错误:
  - PROCESSING_ERROR
  - INVALID_INPUT
  - PROCESSING_TIMEOUT

- 验证错误:
  - VALIDATION_ERROR
  - INVALID_FORMAT
  - MISSING_REQUIRED

- 缓存错误:
  - CACHE_ERROR
  - CACHE_MISS
  - CACHE_FULL

- 导出错误:
  - EXPORT_ERROR
  - WRITE_ERROR

- 资源错误:
  - RESOURCE_ERROR
  - FILE_NOT_FOUND
  - PERMISSION_DENIED
  - OUT_OF_MEMORY

- 超时错误:
  - TIMEOUT_ERROR
  - OPERATION_TIMEOUT
  - CONNECTION_TIMEOUT

- 重试错误:
  - RETRY_ERROR
  - MAX_RETRIES_EXCEEDED
  - RETRY_FAILED

## 使用示例

### 配置管理

```python
from textfission.core import ConfigManager

# 获取配置管理器
config_manager = ConfigManager.get_instance()

# 加载配置
config = config_manager.load_config("config.yaml")

# 更新配置
config_manager.update_config({
    "model_config": {
        "temperature": 0.8
    }
})

# 保存配置
config_manager.save_config("config.yaml")
```

### 日志记录

```python
from textfission.core import Logger
import logging

# 获取日志管理器
logger = Logger.get_instance()

# 设置日志记录器
logger.setup(
    name="textfission",
    level=logging.INFO,
    log_file="logs/textfission.log"
)

# 记录日志
logger.info("Processing started", text_length=1000)
logger.error("Processing failed", error="Invalid input")
```

### 缓存管理

```python
from textfission.core import CacheManager

# 获取缓存管理器
cache_manager = CacheManager.get_instance()

# 设置缓存
cache = cache_manager.setup(
    max_size=1000,
    default_ttl=3600,
    cache_dir="cache"
)

# 使用缓存
cache.set("key", "value")
value = cache.get("key")

# 获取或设置
value = cache.get_or_set(
    "key",
    lambda: compute_value(),
    ttl=3600,
    persist=True
)
```

### 错误处理

```python
from textfission.core import ErrorHandler, ErrorCodes

# 处理异常
try:
    process_data()
except Exception as e:
    error = ErrorHandler.handle_error(
        e,
        error_code=ErrorCodes.PROCESSING_ERROR
    )
    print(f"Error: {error.message}")
    print(f"Error code: {error.error_code}")
    print(f"Details: {error.details}")

# 使用重试装饰器
@ErrorHandler.retry_on_error(
    max_attempts=3,
    delay=1.0,
    error_codes=[ErrorCodes.API_ERROR]
)
def process_with_retry():
    # 处理代码
    pass
``` 