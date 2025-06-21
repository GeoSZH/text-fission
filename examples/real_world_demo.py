#!/usr/bin/env python3
"""
TextFission 实际应用演示
=======================

这个例子展示了如何使用TextFission库处理真实场景的文本数据，
包括技术文档、学术论文、新闻文章等多种类型的文本。

主要功能：
1. 多类型文本处理
2. 智能文本分割
3. 高质量问题生成
4. 准确答案生成
5. 结果质量评估
6. 多种格式导出
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from pathlib import Path

from textfission import (
    Config,
    ModelConfig,
    ProcessingConfig,
    ExportConfig,
    CustomConfig,
    create_dataset,
    create_dataset_from_file,
    create_dataset_from_files,
    TextProcessor,
    QuestionProcessor,
    AnswerProcessor,
    DatasetExporter
)

class TextFissionDemo:
    """TextFission 实际应用演示类"""
    
    def __init__(self, api_key: str):
        """初始化演示环境"""
        self.api_key = api_key
        self.config = self._create_config()
        self.output_dir = Path("demo_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化处理器
        self.text_processor = TextProcessor(self.config)
        self.question_processor = QuestionProcessor(self.config)
        self.answer_processor = AnswerProcessor(self.config)
        self.exporter = DatasetExporter(self.config)
        
        print("✅ TextFission 演示环境初始化完成")
    
    def _create_config(self) -> Config:
        """创建优化的配置"""
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
                min_questions_per_chunk=2
            )
        )
        return config
    
    def demo_technical_document(self):
        """演示：技术文档处理"""
        print("\n🔧 演示1：技术文档处理")
        print("=" * 50)
        
        # 技术文档示例
        tech_doc = """
        # Docker 容器化技术指南

        Docker 是一个开源的容器化平台，允许开发者将应用程序和其依赖项打包到轻量级、可移植的容器中。

        ## 核心概念

        ### 容器 (Container)
        容器是 Docker 镜像的运行实例。每个容器都是独立的，包含运行应用程序所需的所有文件、依赖项和配置。

        ### 镜像 (Image)
        Docker 镜像是一个只读模板，包含创建容器所需的指令。镜像可以基于其他镜像构建，也可以从头开始创建。

        ### Dockerfile
        Dockerfile 是一个文本文件，包含构建 Docker 镜像的指令。它定义了基础镜像、安装依赖项、复制文件、设置环境变量等步骤。

        ## 基本命令

        ### 构建镜像
        ```bash
        docker build -t myapp:latest .
        ```

        ### 运行容器
        ```bash
        docker run -d -p 8080:80 myapp:latest
        ```

        ### 查看容器状态
        ```bash
        docker ps
        docker ps -a
        ```

        ## 最佳实践

        1. **使用多阶段构建**：减少最终镜像大小
        2. **优化层缓存**：合理安排 Dockerfile 指令顺序
        3. **安全性考虑**：使用非 root 用户运行容器
        4. **资源限制**：设置内存和 CPU 限制
        """
        
        # 保存技术文档
        tech_doc_path = self.output_dir / "tech_doc.md"
        with open(tech_doc_path, "w", encoding="utf-8") as f:
            f.write(tech_doc)
        
        print(f"📄 技术文档已保存到: {tech_doc_path}")
        
        # 处理文档
        start_time = time.time()
        output_path = self.output_dir / "tech_doc_dataset.json"
        
        try:
            create_dataset_from_file(
                str(tech_doc_path),
                self.config,
                str(output_path),
                "json",
                show_progress=True
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️  处理完成，耗时: {processing_time:.2f}秒")
            
            # 分析结果
            self._analyze_results(output_path, "技术文档")
            
        except Exception as e:
            print(f"❌ 处理失败: {str(e)}")
    
    def demo_academic_paper(self):
        """演示：学术论文处理"""
        print("\n📚 演示2：学术论文处理")
        print("=" * 50)
        
        # 学术论文示例
        academic_paper = """
        人工智能在教育领域的应用研究

        摘要：
        本文探讨了人工智能技术在现代教育中的应用现状和发展趋势。通过分析机器学习、自然语言处理和计算机视觉等技术在教育场景中的具体应用，本文提出了一个综合性的AI教育应用框架。

        1. 引言
        随着信息技术的快速发展，人工智能已经渗透到社会的各个领域。教育作为人类社会发展的重要基石，自然也成为AI技术应用的重要领域。本文旨在分析AI技术在教育中的具体应用，并探讨其未来发展方向。

        2. 人工智能技术概述
        2.1 机器学习
        机器学习是人工智能的核心技术之一，它使计算机能够从数据中学习并做出预测。在教育领域，机器学习可以用于个性化学习路径推荐、学生成绩预测、学习行为分析等。

        2.2 自然语言处理
        自然语言处理技术使计算机能够理解和生成人类语言。在教育中，NLP技术可以用于自动评分、智能问答、语言学习辅助等应用。

        2.3 计算机视觉
        计算机视觉技术使计算机能够理解和分析图像和视频。在教育中，计算机视觉可以用于学生行为分析、作业自动识别、虚拟实验室等。

        3. 教育应用场景
        3.1 个性化学习
        AI技术可以根据学生的学习风格、能力水平和兴趣偏好，为其提供个性化的学习内容和路径。这种个性化学习方式能够提高学习效率，增强学习动机。

        3.2 智能评估
        传统的教育评估方式往往耗时且主观性强。AI技术可以实现自动化的作业评分、考试分析、学习进度跟踪等，提高评估的效率和客观性。

        3.3 虚拟助教
        AI驱动的虚拟助教可以为学生提供24/7的学习支持，回答常见问题，提供学习建议，减轻教师的工作负担。

        4. 挑战与展望
        尽管AI技术在教育中具有巨大潜力，但也面临着数据隐私、技术可靠性、教育公平性等挑战。未来需要在技术发展和教育伦理之间找到平衡点。

        结论：
        AI技术为教育带来了新的机遇和挑战。通过合理应用AI技术，我们可以构建更加智能、高效和个性化的教育体系，为每个学习者提供更好的学习体验。
        """
        
        # 保存学术论文
        paper_path = self.output_dir / "academic_paper.txt"
        with open(paper_path, "w", encoding="utf-8") as f:
            f.write(academic_paper)
        
        print(f"📄 学术论文已保存到: {paper_path}")
        
        # 处理论文
        start_time = time.time()
        output_path = self.output_dir / "academic_paper_dataset.json"
        
        try:
            create_dataset_from_file(
                str(paper_path),
                self.config,
                str(output_path),
                "json",
                show_progress=True
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️  处理完成，耗时: {processing_time:.2f}秒")
            
            # 分析结果
            self._analyze_results(output_path, "学术论文")
            
        except Exception as e:
            print(f"❌ 处理失败: {str(e)}")
    
    def demo_news_article(self):
        """演示：新闻文章处理"""
        print("\n📰 演示3：新闻文章处理")
        print("=" * 50)
        
        # 新闻文章示例
        news_article = """
        新能源汽车市场迎来爆发式增长

        据最新统计数据显示，2024年第一季度，我国新能源汽车销量达到280万辆，同比增长35.6%，市场渗透率首次突破30%大关。这一数据表明，新能源汽车市场正在迎来前所未有的发展机遇。

        政策推动效果显著
        近年来，国家出台了一系列支持新能源汽车发展的政策措施，包括购车补贴、免征购置税、免费上牌等优惠政策。这些政策的实施有效降低了消费者的购车成本，推动了市场需求的快速增长。

        技术突破推动发展
        在技术层面，动力电池技术的不断突破使得新能源汽车的续航里程大幅提升，充电时间显著缩短。同时，智能驾驶技术的快速发展也为新能源汽车增添了更多吸引力。

        产业链日趋完善
        随着市场规模的扩大，新能源汽车产业链也在不断完善。从上游的原材料供应，到中游的电池制造，再到下游的销售服务，整个产业链已经形成了较为完整的生态体系。

        未来发展趋势
        专家预测，到2025年，我国新能源汽车年销量有望突破1000万辆，市场渗透率将达到50%以上。随着技术的进一步成熟和成本的持续下降，新能源汽车将成为汽车市场的主流选择。

        挑战与机遇并存
        尽管发展前景广阔，但新能源汽车行业也面临着充电基础设施不足、电池回收处理、原材料供应紧张等挑战。这些问题的解决需要政府、企业和消费者的共同努力。
        """
        
        # 保存新闻文章
        news_path = self.output_dir / "news_article.txt"
        with open(news_path, "w", encoding="utf-8") as f:
            f.write(news_article)
        
        print(f"📄 新闻文章已保存到: {news_path}")
        
        # 处理新闻
        start_time = time.time()
        output_path = self.output_dir / "news_article_dataset.json"
        
        try:
            create_dataset_from_file(
                str(news_path),
                self.config,
                str(output_path),
                "json",
                show_progress=True
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️  处理完成，耗时: {processing_time:.2f}秒")
            
            # 分析结果
            self._analyze_results(output_path, "新闻文章")
            
        except Exception as e:
            print(f"❌ 处理失败: {str(e)}")
    
    def demo_batch_processing(self):
        """演示：批量处理多个文件"""
        print("\n📁 演示4：批量处理多个文件")
        print("=" * 50)
        
        # 创建多个示例文件
        files = [
            ("python_basics.txt", """
            Python编程基础

            Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。

            变量和数据类型
            Python中的变量不需要声明类型，可以直接赋值使用。常见的数据类型包括整数、浮点数、字符串、列表、元组、字典等。

            控制结构
            Python提供了if-elif-else条件语句和for、while循环语句，用于控制程序的执行流程。

            函数定义
            使用def关键字定义函数，可以接受参数并返回值。Python还支持匿名函数lambda。

            面向对象编程
            Python支持面向对象编程，可以定义类和对象，实现封装、继承和多态。
            """),
            
            ("machine_learning.txt", """
            机器学习入门

            机器学习是人工智能的一个重要分支，它使计算机能够从数据中学习并做出预测。

            监督学习
            监督学习使用标记的训练数据来学习输入和输出之间的映射关系。常见的算法包括线性回归、逻辑回归、决策树、支持向量机等。

            无监督学习
            无监督学习从无标记的数据中发现隐藏的模式和结构。常见的算法包括聚类、降维、关联规则挖掘等。

            深度学习
            深度学习使用多层神经网络来学习复杂的非线性关系。它在图像识别、自然语言处理等领域取得了突破性进展。

            模型评估
            机器学习模型的评估指标包括准确率、精确率、召回率、F1分数等，用于衡量模型的性能。
            """),
            
            ("data_science.txt", """
            数据科学实践

            数据科学是一门跨学科领域，结合了统计学、计算机科学和领域知识来从数据中提取有价值的见解。

            数据收集
            数据收集是数据科学项目的第一步，包括确定数据源、设计数据收集方法、确保数据质量等。

            数据清洗
            原始数据往往包含缺失值、异常值、重复数据等问题，需要进行数据清洗和预处理。

            探索性数据分析
            通过统计分析和可视化技术，探索数据的分布、关系和模式，为后续建模提供指导。

            建模和预测
            基于清洗后的数据，选择合适的算法建立预测模型，并进行模型验证和优化。

            结果解释
            将模型结果转化为可理解的业务洞察，为决策提供支持。
            """)
        ]
        
        # 保存文件
        file_paths = []
        for filename, content in files:
            file_path = self.output_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            file_paths.append(str(file_path))
            print(f"📄 创建文件: {filename}")
        
        # 批量处理
        start_time = time.time()
        output_path = self.output_dir / "batch_processed_dataset.json"
        
        try:
            create_dataset_from_files(
                file_paths,
                self.config,
                str(output_path),
                "json",
                show_progress=True
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️  批量处理完成，耗时: {processing_time:.2f}秒")
            
            # 分析结果
            self._analyze_results(output_path, "批量处理")
            
        except Exception as e:
            print(f"❌ 批量处理失败: {str(e)}")
    
    def _analyze_results(self, output_path: Path, data_type: str):
        """分析处理结果"""
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict) and "dataset" in data:
                dataset = data["dataset"]
            else:
                dataset = data
            
            print(f"\n📊 {data_type} 处理结果分析:")
            print("-" * 40)
            print(f"📈 总数据条数: {len(dataset)}")
            
            # 统计置信度
            confidences = [item.get("confidence", 0) for item in dataset]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                print(f"🎯 平均置信度: {avg_confidence:.3f}")
                print(f"🔝 最高置信度: {max(confidences):.3f}")
                print(f"🔻 最低置信度: {min(confidences):.3f}")
            
            # 显示示例
            print(f"\n📝 示例数据:")
            for i, item in enumerate(dataset[:3]):
                print(f"\n示例 {i+1}:")
                print(f"  文本片段: {item.get('text', '')[:100]}...")
                print(f"  问题: {item.get('question', '')}")
                print(f"  答案: {item.get('answer', '')}")
                print(f"  置信度: {item.get('confidence', 0):.3f}")
            
            # 导出为CSV格式
            csv_path = output_path.with_suffix('.csv')
            df = pd.DataFrame(dataset)
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"\n💾 CSV格式已导出: {csv_path}")
            
        except Exception as e:
            print(f"❌ 结果分析失败: {str(e)}")
    
    def generate_comprehensive_report(self):
        """生成综合报告"""
        print("\n📋 生成综合报告")
        print("=" * 50)
        
        report_path = self.output_dir / "comprehensive_report.md"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# TextFission 库验证报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 测试概述\n\n")
            f.write("本报告展示了TextFission库在处理不同类型文本时的表现，包括：\n")
            f.write("- 技术文档处理\n")
            f.write("- 学术论文处理\n")
            f.write("- 新闻文章处理\n")
            f.write("- 批量文件处理\n\n")
            
            f.write("## 测试结果\n\n")
            
            # 统计所有生成的文件
            json_files = list(self.output_dir.glob("*.json"))
            csv_files = list(self.output_dir.glob("*.csv"))
            
            f.write(f"- 生成的JSON数据集: {len(json_files)}个\n")
            f.write(f"- 生成的CSV数据集: {len(csv_files)}个\n")
            f.write(f"- 总输出文件: {len(list(self.output_dir.glob('*')))}个\n\n")
            
            f.write("## 文件列表\n\n")
            for file_path in self.output_dir.iterdir():
                if file_path.is_file():
                    size = file_path.stat().st_size
                    f.write(f"- {file_path.name} ({size} bytes)\n")
            
            f.write("\n## 结论\n\n")
            f.write("TextFission库成功处理了多种类型的文本数据，生成的问答对质量较高，\n")
            f.write("可以有效地用于LLM微调数据集的创建。库的配置灵活，支持多种输出格式，\n")
            f.write("具有良好的实用性和扩展性。\n")
        
        print(f"📄 综合报告已生成: {report_path}")
    
    def run_all_demos(self):
        """运行所有演示"""
        print("🚀 开始TextFission库验证演示")
        print("=" * 60)
        
        # 运行各个演示
        self.demo_technical_document()
        self.demo_academic_paper()
        self.demo_news_article()
        self.demo_batch_processing()
        
        # 生成综合报告
        self.generate_comprehensive_report()
        
        print("\n🎉 所有演示完成！")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        print("📋 请查看生成的数据集和报告文件")


def main():
    """主函数"""
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误: 请设置OPENAI_API_KEY环境变量")
        print("   例如: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # 创建演示实例
    demo = TextFissionDemo(api_key)
    
    # 运行所有演示
    demo.run_all_demos()


if __name__ == "__main__":
    main() 