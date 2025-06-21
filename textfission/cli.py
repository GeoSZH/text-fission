#!/usr/bin/env python3
"""
TextFission CLI module
"""

import argparse
import sys
import os
from pathlib import Path
from .core.config import Config, ModelConfig, ProcessingConfig, ExportConfig, CustomConfig
from . import create_dataset, create_dataset_from_file, create_dataset_from_files

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="TextFission - 文本分割和问答生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  textfission --text "你的文本内容" --output output.json
  textfission --file input.txt --output output.json
  textfission --files input1.txt input2.txt --output output.json
        """
    )
    
    # 输入参数
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--text", "-t",
        help="输入文本内容"
    )
    input_group.add_argument(
        "--file", "-f",
        help="输入文件路径"
    )
    input_group.add_argument(
        "--files", "-F",
        nargs="+",
        help="多个输入文件路径"
    )
    
    # 输出参数
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="输出文件路径"
    )
    
    # 配置参数
    parser.add_argument(
        "--api-key",
        help="OpenAI API密钥"
    )
    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="使用的模型名称"
    )
    parser.add_argument(
        "--language", "-l",
        default="zh",
        choices=["zh", "en"],
        help="文本语言"
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "csv", "txt"],
        help="输出格式"
    )
    
    # 处理参数
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1500,
        help="文本块大小"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="文本块重叠大小"
    )
    parser.add_argument(
        "--max-questions",
        type=int,
        default=5,
        help="每个文本块最大问题数"
    )
    parser.add_argument(
        "--min-questions",
        type=int,
        default=2,
        help="每个文本块最小问题数"
    )
    
    # 其他参数
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    
    args = parser.parse_args()
    
    try:
        # 创建配置
        config = create_config(args)
        
        # 处理输入
        if args.text:
            result = create_dataset(
                args.text,
                config,
                args.output,
                args.format,
                show_progress=args.verbose
            )
        elif args.file:
            result = create_dataset_from_file(
                args.file,
                config,
                args.output,
                args.format,
                show_progress=args.verbose
            )
        elif args.files:
            result = create_dataset_from_files(
                args.files,
                config,
                args.output,
                args.format,
                show_progress=args.verbose
            )
        
        print(f"✅ 数据集创建成功: {result}")
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)

def create_config(args) -> Config:
    """根据命令行参数创建配置"""
    
    # 获取API密钥
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("需要提供OpenAI API密钥 (--api-key 或 OPENAI_API_KEY 环境变量)")
    
    # 创建配置
    config = Config(
        model_settings=ModelConfig(
            api_key=api_key,
            model=args.model
        ),
        processing_config=ProcessingConfig(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        ),
        export_config=ExportConfig(
            format=args.format
        ),
        custom_config=CustomConfig(
            language=args.language,
            max_questions_per_chunk=args.max_questions,
            min_questions_per_chunk=args.min_questions
        )
    )
    
    return config

if __name__ == "__main__":
    main() 