# TextFission 错误处理指南

## 错误类型

TextFission 定义了一系列自定义异常类来处理不同类型的错误。所有异常都继承自基类 `TextFissionError`。

### 1. 配置错误 (ConfigurationError)

配置相关的错误。

常见原因:
- 配置文件格式错误
- 缺少必要的配置项
- 配置值无效

示例:
```python
try:
    config = ConfigManager.get_instance().load_config("invalid.yaml")
except ConfigurationError as e:
    print(f"配置错误: {e.message}")
```

### 2. 模型错误 (ModelError)

模型相关的错误。

常见原因:
- 模型加载失败
- 模型参数无效
- 模型资源不足

示例:
```python
try:
    model = ModelManager.get_instance().load_model("invalid_model")
except ModelError as e:
    print(f"模型错误: {e.message}")
```

### 3. 生成错误 (GenerationError)

文本生成相关的错误。

常见原因:
- 生成参数无效
- 生成超时
- 生成结果无效

示例:
```python
try:
    result = generator.generate(text)
except GenerationError as e:
    print(f"生成错误: {e.message}")
```

### 4. 处理错误 (ProcessingError)

文本处理相关的错误。

常见原因:
- 输入文本格式错误
- 处理超时
- 处理资源不足

示例:
```python
try:
    chunks = processor.process(text)
except ProcessingError as e:
    print(f"处理错误: {e.message}")
```

### 5. 验证错误 (ValidationError)

数据验证相关的错误。

常见原因:
- 输入数据格式错误
- 必填字段缺失
- 字段值无效

示例:
```python
try:
    validator.validate(data)
except ValidationError as e:
    print(f"验证错误: {e.message}")
```

### 6. 缓存错误 (CacheError)

缓存相关的错误。

常见原因:
- 缓存操作失败
- 缓存已满
- 缓存项过期

示例:
```python
try:
    value = cache.get("key")
except CacheError as e:
    print(f"缓存错误: {e.message}")
```

### 7. 导出错误 (ExportError)

数据导出相关的错误。

常见原因:
- 导出格式不支持
- 写入文件失败
- 导出超时

示例:
```python
try:
    exporter.export(data, "output.json")
except ExportError as e:
    print(f"导出错误: {e.message}")
```

### 8. API错误 (APIError)

API调用相关的错误。

常见原因:
- API请求失败
- API限流
- API响应无效

示例:
```python
try:
    response = api_client.request()
except APIError as e:
    print(f"API错误: {e.message}")
```

### 9. 资源错误 (ResourceError)

资源相关的错误。

常见原因:
- 文件不存在
- 权限不足
- 内存不足

示例:
```python
try:
    file = open("missing.txt")
except ResourceError as e:
    print(f"资源错误: {e.message}")
```

### 10. 超时错误 (TimeoutError)

超时相关的错误。

常见原因:
- 操作超时
- 连接超时
- 响应超时

示例:
```python
try:
    result = process_with_timeout()
except TimeoutError as e:
    print(f"超时错误: {e.message}")
```

### 11. 重试错误 (RetryError)

重试相关的错误。

常见原因:
- 重试次数超限
- 重试间隔无效
- 重试条件不满足

示例:
```python
try:
    result = process_with_retry()
except RetryError as e:
    print(f"重试错误: {e.message}")
```

## 错误处理最佳实践

### 1. 使用错误处理器

使用 `ErrorHandler` 类来统一处理异常:

```python
from textfission.core import ErrorHandler, ErrorCodes

try:
    process_data()
except Exception as e:
    error = ErrorHandler.handle_error(
        e,
        error_code=ErrorCodes.PROCESSING_ERROR,
        details={"input": data}
    )
    logger.error(
        f"处理失败: {error.message}",
        error_code=error.error_code,
        details=error.details
    )
```

### 2. 使用重试装饰器

对于可能失败的操作,使用重试装饰器:

```python
from textfission.core import ErrorHandler, ErrorCodes

@ErrorHandler.retry_on_error(
    max_attempts=3,
    delay=1.0,
    backoff=2.0,
    error_codes=[ErrorCodes.API_ERROR]
)
def process_with_retry():
    # 处理代码
    pass
```

### 3. 错误日志记录

使用结构化日志记录错误信息:

```python
from textfission.core import Logger

logger = Logger.get_instance()

try:
    process_data()
except TextFissionError as e:
    logger.error(
        f"处理失败: {e.message}",
        error_code=e.error_code,
        details=e.details,
        stack_trace=True
    )
```

### 4. 错误恢复

实现错误恢复机制:

```python
from textfission.core import ErrorHandler, ErrorCodes

def process_with_recovery():
    try:
        return process_data()
    except TextFissionError as e:
        if e.error_code == ErrorCodes.CACHE_ERROR:
            # 清除缓存并重试
            cache.clear()
            return process_data()
        elif e.error_code == ErrorCodes.API_ERROR:
            # 使用备用API
            return process_with_backup_api()
        else:
            raise
```

### 5. 错误监控

实现错误监控和告警:

```python
from textfission.core import Logger, ErrorHandler

class ErrorMonitor:
    def __init__(self):
        self.logger = Logger.get_instance()
        self.error_counts = {}
    
    def monitor_error(self, error: TextFissionError):
        # 更新错误计数
        self.error_counts[error.error_code] = self.error_counts.get(error.error_code, 0) + 1
        
        # 检查错误阈值
        if self.error_counts[error.error_code] > 10:
            self.logger.critical(
                f"错误频率过高: {error.error_code}",
                count=self.error_counts[error.error_code]
            )
            # 发送告警
            self.send_alert(error)
    
    def send_alert(self, error: TextFissionError):
        # 实现告警逻辑
        pass
```

## 错误代码参考

### 配置错误代码
- INVALID_CONFIG: 配置无效
- MISSING_CONFIG: 配置缺失
- INVALID_VALUE: 配置值无效

### 模型错误代码
- MODEL_ERROR: 模型错误
- API_ERROR: API错误
- RATE_LIMIT: 请求限流

### 生成错误代码
- GENERATION_ERROR: 生成错误
- INVALID_PROMPT: 提示词无效
- INVALID_OUTPUT: 输出无效

### 处理错误代码
- PROCESSING_ERROR: 处理错误
- INVALID_INPUT: 输入无效
- PROCESSING_TIMEOUT: 处理超时

### 验证错误代码
- VALIDATION_ERROR: 验证错误
- INVALID_FORMAT: 格式无效
- MISSING_REQUIRED: 必填项缺失

### 缓存错误代码
- CACHE_ERROR: 缓存错误
- CACHE_MISS: 缓存未命中
- CACHE_FULL: 缓存已满

### 导出错误代码
- EXPORT_ERROR: 导出错误
- WRITE_ERROR: 写入错误

### 资源错误代码
- RESOURCE_ERROR: 资源错误
- FILE_NOT_FOUND: 文件不存在
- PERMISSION_DENIED: 权限不足
- OUT_OF_MEMORY: 内存不足

### 超时错误代码
- TIMEOUT_ERROR: 超时错误
- OPERATION_TIMEOUT: 操作超时
- CONNECTION_TIMEOUT: 连接超时

### 重试错误代码
- RETRY_ERROR: 重试错误
- MAX_RETRIES_EXCEEDED: 超过最大重试次数
- RETRY_FAILED: 重试失败 