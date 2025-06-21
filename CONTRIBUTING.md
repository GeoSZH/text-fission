# Contributing to TextFission

感谢您对TextFission项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 Bug报告
- 💡 功能建议
- 📝 文档改进
- 🔧 代码贡献
- 🧪 测试用例

## 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/textfission.git
cd textfission
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -e ".[dev]"
```

### 4. 运行测试
```bash
pytest tests/ -v
```

## 代码规范

### 1. 代码格式化
我们使用以下工具来保持代码质量：

```bash
# 代码格式化
black textfission/ tests/

# 导入排序
isort textfission/ tests/

# 代码检查
flake8 textfission/ tests/

# 类型检查
mypy textfission/
```

### 2. 提交前检查
```bash
make lint
make test
```

## 提交规范

我们使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

- `feat:` 新功能
- `fix:` Bug修复
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```bash
git commit -m "feat: add support for new language model"
git commit -m "fix: resolve issue with text splitting"
git commit -m "docs: update installation guide"
```

## Pull Request 流程

1. **Fork 项目**到您的GitHub账户
2. **创建功能分支**：`git checkout -b feature/your-feature-name`
3. **提交更改**：遵循提交规范
4. **运行测试**：确保所有测试通过
5. **推送分支**：`git push origin feature/your-feature-name`
6. **创建Pull Request**：提供详细的描述

### Pull Request 模板

```markdown
## 描述
简要描述您的更改

## 类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 其他

## 测试
- [ ] 添加了新的测试用例
- [ ] 所有现有测试通过
- [ ] 手动测试验证

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了必要的文档
- [ ] 更新了CHANGELOG（如适用）
```

## 报告问题

在报告问题之前，请：

1. 检查[现有问题](https://github.com/yourusername/textfission/issues)
2. 使用问题模板
3. 提供详细的复现步骤
4. 包含错误日志和系统信息

## 功能建议

对于功能建议：

1. 详细描述您想要的功能
2. 解释为什么需要这个功能
3. 提供使用场景示例
4. 讨论可能的实现方案

## 文档贡献

文档改进同样重要：

1. 修正拼写错误
2. 改进示例代码
3. 添加缺失的说明
4. 翻译文档

## 行为准则

我们致力于为每个人提供友好、安全和欢迎的环境。请：

- 尊重所有贡献者
- 保持专业和礼貌
- 接受建设性批评
- 关注社区利益

## 联系方式

如果您有任何问题，请：

- 在GitHub Issues中提问
- 查看项目文档
- 联系维护者

感谢您的贡献！🎉 