# 安装指南

## 基本安装

```bash
pip install textfission
```

## 开发环境安装

```bash
pip install textfission[dev]
```

## 完整功能安装

```bash
pip install textfission[all]
```

## 依赖兼容性说明

### 版本冲突解决方案

如果遇到依赖冲突，特别是numpy版本冲突，请尝试以下解决方案：

#### 方案1：使用兼容的numpy版本
```bash
pip install "numpy>=1.21.0,<2.0.0"
pip install textfission
```

#### 方案2：创建虚拟环境
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

### 常见依赖冲突

1. **numpy版本冲突**
   - 问题：`numba`、`scipy`等包需要特定numpy版本
   - 解决：使用 `numpy>=1.21.0,<2.0.0`

2. **pandas版本冲突**
   - 问题：某些包与pandas 3.x不兼容
   - 解决：使用 `pandas>=1.5.0,<3.0.0`

3. **gensim依赖冲突**
   - 问题：gensim需要FuzzyTM包
   - 解决：单独安装 `pip install FuzzyTM>=0.4.0`

## 系统要求

- Python >= 3.8
- 内存：建议 >= 4GB
- 网络：需要访问API服务

## 验证安装

```python
import textfission
print(textfission.__version__)
```

## 故障排除

### 安装失败
1. 升级pip：`pip install --upgrade pip`
2. 清理缓存：`pip cache purge`
3. 使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple textfission`

### 运行时错误
1. 检查API密钥配置
2. 确认网络连接
3. 查看详细错误日志 