# TextFission 测试计划

## 1. 单元测试

### 1.1 核心模块测试
- [ ] 配置管理测试
  - Config 类创建和验证
  - ConfigManager 单例模式
  - 环境变量加载
  - YAML 配置文件加载

- [ ] 异常处理测试
  - 自定义异常类
  - ErrorHandler 重试机制
  - 错误代码映射

- [ ] 缓存管理测试
  - 内存缓存操作
  - 文件缓存持久化
  - TTL 过期机制
  - 缓存统计

### 1.2 处理器测试
- [ ] 文本分割器测试
  - SmartTextSplitter 语义分割
  - RecursiveTextSplitter 递归分割
  - MarkdownSplitter Markdown 分割
  - 多语言支持

- [ ] 问题生成器测试
  - 问题类型生成
  - 问题质量评估
  - 批量处理

- [ ] 答案生成器测试
  - 答案生成
  - 置信度评分
  - 引用提取

### 1.3 模型测试
- [ ] OpenAI 模型测试
  - API 调用
  - 参数验证
  - 错误重试
  - Token 计数

### 1.4 导出器测试
- [ ] 格式导出测试
  - JSON 导出
  - CSV 导出
  - TXT 导出
  - 多格式导出

## 2. 集成测试

### 2.1 端到端测试
- [ ] 完整流程测试
  - 文本输入 → 分割 → 问题生成 → 答案生成 → 导出
  - 文件输入处理
  - 批量文件处理

### 2.2 API 集成测试
- [ ] OpenAI API 集成
  - 真实 API 调用
  - 速率限制处理
  - 错误恢复

## 3. 性能测试

### 3.1 性能基准测试
- [ ] 处理速度测试
  - 不同文本长度
  - 不同配置参数
  - 并发处理

### 3.2 内存使用测试
- [ ] 内存泄漏检测
- [ ] 大文件处理
- [ ] 缓存效率

## 4. 兼容性测试

### 4.1 Python 版本兼容性
- [ ] Python 3.8
- [ ] Python 3.9
- [ ] Python 3.10
- [ ] Python 3.11

### 4.2 操作系统兼容性
- [ ] Linux
- [ ] macOS
- [ ] Windows

## 5. 安全测试

### 5.1 输入验证
- [ ] 恶意输入处理
- [ ] 特殊字符处理
- [ ] 文件路径验证

### 5.2 API 密钥安全
- [ ] 密钥泄露防护
- [ ] 环境变量安全

## 6. 测试执行步骤

### 步骤 1: 环境准备
```bash
# 创建虚拟环境
python -m venv test_env
source test_env/bin/activate  # Linux/macOS
# 或 test_env\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 步骤 2: 运行单元测试
```bash
# 运行所有测试
pytest

# 运行带覆盖率测试
pytest --cov=textfission --cov-report=html

# 运行特定模块测试
pytest tests/test_core.py
pytest tests/test_processors.py
pytest tests/test_models.py
pytest tests/test_exporters.py
```

### 步骤 3: 运行集成测试
```bash
# 设置测试环境变量
export OPENAI_API_KEY="your-test-api-key"
export MODEL_NAME="gpt-3.5-turbo"

# 运行集成测试
pytest tests/test_integration.py -v
```

### 步骤 4: 运行性能测试
```bash
# 运行性能基准测试
pytest tests/test_performance.py -v
```

### 步骤 5: 运行示例测试
```bash
# 测试基本用法示例
python examples/basic_usage.py

# 测试高级用法示例
python examples/advanced_usage.py
```

## 7. 测试数据准备

### 7.1 测试文本文件
- 创建 `tests/data/` 目录
- 准备不同语言的测试文本
- 准备不同格式的测试文件

### 7.2 Mock 数据
- 创建 API 响应的 Mock 数据
- 准备测试配置文件

## 8. 测试报告

### 8.1 测试结果分析
- 测试覆盖率报告
- 性能基准报告
- 错误统计报告

### 8.2 问题跟踪
- 记录发现的问题
- 优先级分类
- 修复计划

## 9. 持续集成

### 9.1 GitHub Actions 配置
- 自动运行测试
- 代码质量检查
- 覆盖率报告

### 9.2 发布前检查清单
- [ ] 所有测试通过
- [ ] 代码覆盖率 > 80%
- [ ] 文档更新
- [ ] 版本号更新 