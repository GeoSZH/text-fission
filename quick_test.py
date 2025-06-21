#!/usr/bin/env python3
"""
TextFission 快速测试脚本
=======================

这个脚本用于快速验证TextFission库的基本功能是否正常工作。
"""

import os
import json
from pathlib import Path

def test_imports():
    """测试导入功能"""
    print("🔍 测试导入功能...")
    try:
        from textfission import (
            Config,
            ModelConfig,
            ProcessingConfig,
            ExportConfig,
            CustomConfig,
            create_dataset
        )
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_config_creation():
    """测试配置创建"""
    print("\n🔧 测试配置创建...")
    try:
        from textfission import Config, ModelConfig, ProcessingConfig, ExportConfig, CustomConfig
        
        config = Config(
            model_settings=ModelConfig(
                api_key="test-key",
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=2000
            ),
            processing_config=ProcessingConfig(
                chunk_size=1000,
                chunk_overlap=100,
                max_workers=2
            ),
            export_config=ExportConfig(
                format="json",
                output_dir="test_output"
            ),
            custom_config=CustomConfig(
                language="zh",
                min_confidence=0.7,
                min_quality="good"
            )
        )
        print("✅ 配置创建成功")
        return config
    except Exception as e:
        print(f"❌ 配置创建失败: {e}")
        return None

def test_text_processing():
    """测试文本处理功能"""
    print("\n📝 测试文本处理功能...")
    try:
        from textfission import TextProcessor
        
        config = test_config_creation()
        if not config:
            return False
        
        text_processor = TextProcessor(config)
        
        # 测试文本
        test_text = """
        Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。
        它支持多种编程范式，包括面向对象、命令式和函数式编程。
        Python拥有丰富的标准库和第三方包生态系统，使其成为数据科学、
        机器学习、Web开发等领域的首选语言。
        """
        
        chunks = text_processor.process_text(test_text)
        print(f"✅ 文本分割成功，生成了 {len(chunks)} 个文本块")
        
        for i, chunk in enumerate(chunks):
            print(f"   块 {i+1}: {chunk[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ 文本处理失败: {e}")
        return False

def test_simple_dataset_creation():
    """测试简单的数据集创建（不调用API）"""
    print("\n📊 测试数据集创建功能...")
    try:
        # 创建测试文件
        test_file = Path("test_input.txt")
        test_content = """
        人工智能是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。
        机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。
        深度学习是机器学习的一个分支，使用神经网络来模拟人脑的工作方式。
        """
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        print(f"✅ 测试文件创建成功: {test_file}")
        
        # 测试文件读取
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"✅ 文件读取成功，内容长度: {len(content)} 字符")
        
        # 清理测试文件
        test_file.unlink()
        print("✅ 测试文件清理完成")
        
        return True
    except Exception as e:
        print(f"❌ 数据集创建测试失败: {e}")
        return False

def test_config_validation():
    """测试配置验证"""
    print("\n⚙️ 测试配置验证...")
    try:
        from textfission import Config, ModelConfig, ProcessingConfig, ExportConfig, CustomConfig
        
        # 测试最小配置
        minimal_config = Config(
            model_settings=ModelConfig(api_key="test"),
            processing_config=ProcessingConfig(),
            export_config=ExportConfig(),
            custom_config=CustomConfig()
        )
        print("✅ 最小配置验证成功")
        
        # 测试完整配置
        full_config = Config(
            model_settings=ModelConfig(
                api_key="test",
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=2000
            ),
            processing_config=ProcessingConfig(
                chunk_size=1000,
                chunk_overlap=100,
                max_workers=4
            ),
            export_config=ExportConfig(
                format="json",
                output_dir="output"
            ),
            custom_config=CustomConfig(
                language="zh",
                min_confidence=0.8
            )
        )
        print("✅ 完整配置验证成功")
        
        return True
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始TextFission库快速测试")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ 检测到API密钥: {api_key[:10]}...")
    else:
        print("⚠️  未检测到OPENAI_API_KEY环境变量")
        print("   注意：某些功能可能需要API密钥才能完全测试")
    
    # 运行测试
    tests = [
        ("导入测试", test_imports),
        ("配置创建测试", test_config_creation),
        ("配置验证测试", test_config_validation),
        ("文本处理测试", test_text_processing),
        ("数据集创建测试", test_simple_dataset_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}出现异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！TextFission库基本功能正常")
    else:
        print("⚠️  部分测试失败，请检查错误信息")
    
    print("\n💡 提示:")
    print("- 要运行完整的API测试，请设置OPENAI_API_KEY环境变量")
    print("- 运行: python examples/real_world_demo.py 进行完整演示")
    print("- 查看文档: README.md")

if __name__ == "__main__":
    main() 