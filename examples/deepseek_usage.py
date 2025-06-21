"""
DeepSeek模型使用示例
DeepSeek使用兼容OpenAI的API接口，可以通过设置自定义API端点来使用
"""

from textfission import (
    Config,
    ModelConfig,
    ProcessingConfig,
    ExportConfig,
    CustomConfig,
    create_dataset,
    ModelFactory
)

def main():
    """使用DeepSeek模型创建数据集的示例"""
    
    # 创建DeepSeek配置
    config = Config(
        model_settings=ModelConfig(
            api_key="sk-2b25f9ffa76045789494cd76a9508d9f",  # DeepSeek API密钥
            model="deepseek-chat",  # DeepSeek模型名称
            temperature=0.7,
            max_tokens=2000,
            api_base_url="https://api.deepseek.com/v1",  # DeepSeek API端点
        ),
        processing_config=ProcessingConfig(
            chunk_size=1500,
            chunk_overlap=200,
            max_workers=4
        ),
        export_config=ExportConfig(
            format="json",
            output_dir="output",
            encoding="utf-8",
            indent=2
        ),
        custom_config=CustomConfig(
            language="zh",  # 支持中文
            min_confidence=0.7,
            min_quality="good",
            max_questions_per_chunk=5,
            min_questions_per_chunk=2,
            question_types=["factual", "inferential", "analytical", "evaluative", "creative"]  # 明确指定问题类型
        )
    )

    # 示例文本
    text = """
    Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。
    它由Guido van Rossum于1991年创建，设计哲学强调代码的可读性。
    Python支持多种编程范式，包括面向对象、命令式和函数式编程。
    它拥有丰富的标准库和第三方包生态系统，广泛应用于Web开发、
    数据科学、人工智能、自动化等领域。
    """

    # 创建数据集
    output_path = "output/deepseek_dataset.json"
    result = create_dataset(text, config, output_path)
    print(f"数据集已创建: {result}")

    # 验证模型类型
    model = ModelFactory.create_model(config)
    model_info = model.get_model_info()
    print(f"使用的模型: {model_info}")

    # 显示支持的模型
    supported_models = ModelFactory.get_supported_models()
    print("支持的模型类型:")
    for model_type, models in supported_models.items():
        print(f"  {model_type}: {models}")

if __name__ == "__main__":
    main() 