import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os
from typing import List, Dict, Any

from textfission.core.config import (
    ModelConfig, ProcessingConfig, ExportConfig, CustomConfig
)
from textfission.processors.text_splitter import (
    SmartTextSplitter, RecursiveTextSplitter, MarkdownSplitter, TextProcessor
)
from textfission.processors.question_generator import QuestionProcessor
from textfission.processors.answer_generator import AnswerProcessor

# 测试专用配置容器
def create_test_config(model_settings, processing_config, custom_config):
    """创建测试配置"""
    class TestConfig:
        def __init__(self, model_settings, processing_config, custom_config):
            self.model_settings = model_settings
            self.processing_config = processing_config
            self.custom_config = custom_config
    
    return TestConfig(model_settings, processing_config, custom_config)

class TestTextProcessor:
    """测试文本处理器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = create_test_config(
            model_settings=ModelConfig(
                api_key="test-api-key",
                model="gpt-3.5-turbo"
            ),
            processing_config=ProcessingConfig(
                chunk_size=1000,
                chunk_overlap=100,
                min_chars=50,
                max_chars=2000
            ),
            custom_config=CustomConfig()
        )
        self.processor = TextProcessor(self.config)

    def test_processor_initialization(self):
        """测试处理器初始化"""
        assert self.processor.config is not None
        assert hasattr(self.processor, 'splitter')

    def test_process_text(self):
        """测试文本处理"""
        text = "This is a test text. " * 20  # 创建长文本
        chunks = self.processor.process_text(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_process_file(self):
        """测试文件处理"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("This is a test file content. " * 10)
            file_path = f.name

        try:
            chunks = self.processor.process_file(file_path)
            assert isinstance(chunks, list)
            assert len(chunks) > 0
            assert all(isinstance(chunk, str) for chunk in chunks)
        finally:
            os.unlink(file_path)

    def test_process_batch(self):
        """测试批量处理"""
        texts = [
            "First test text. " * 5,
            "Second test text. " * 5,
            "Third test text. " * 5
        ]
        
        results = self.processor.process_batch(texts, show_progress=False)
        assert isinstance(results, list)
        assert len(results) == len(texts)
        assert all(isinstance(result, list) for result in results)

class TestSmartTextSplitter:
    """测试智能文本分割器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = create_test_config(
            model_settings=ModelConfig(
                api_key="test_key",
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=1000
            ),
            processing_config=ProcessingConfig(
                max_workers=2,
                min_chars=50,
                max_chars=100  # 设置较小，便于测试分割
            ),
            custom_config=CustomConfig(
                language="en",
                min_questions_per_chunk=1,
                max_questions_per_chunk=3,
                question_types=["factual", "inferential"],
                difficulty_range=(0.3, 0.8),
                min_confidence=0.7,
                min_quality="good"
            )
        )
        self.splitter = SmartTextSplitter(self.config)

    def test_splitter_initialization(self):
        """测试分割器初始化"""
        assert self.splitter.config is not None
        assert hasattr(self.splitter, 'min_chars')
        assert hasattr(self.splitter, 'max_chars')

    def test_split_simple_text(self):
        """测试简单文本分割"""
        text = "This is a simple test text. It has multiple sentences. Each sentence should be processed correctly."
        chunks = self.splitter.split(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(len(chunk) <= self.splitter.max_chars for chunk in chunks)

    def test_split_long_text(self):
        """测试长文本分割"""
        text = "This is a very long text. " * 100
        chunks = self.splitter.split(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 1  # 应该被分割成多个块
        assert all(len(chunk) <= self.splitter.max_chars for chunk in chunks)

    def test_split_chinese_text(self):
        """测试中文文本分割"""
        text = "这是一个中文测试文本。它包含多个句子。每个句子都应该被正确处理。"
        chunks = self.splitter.split(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(len(chunk) <= self.splitter.max_chars for chunk in chunks)

    def test_split_markdown_text(self):
        """测试Markdown文本分割"""
        text = """
        # 标题1
        这是第一段内容。
        
        ## 标题2
        这是第二段内容。
        
        ### 标题3
        这是第三段内容。
        """
        chunks = self.splitter.split(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0

class TestRecursiveTextSplitter:
    """测试递归文本分割器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = create_test_config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(
                chunk_size=1000,
                chunk_overlap=100
            ),
            custom_config=CustomConfig()
        )
        self.splitter = RecursiveTextSplitter(self.config)

    def test_recursive_split(self):
        """测试递归分割"""
        text = "This is a test text. " * 20
        chunks = self.splitter.split(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_split_with_custom_separators(self):
        """测试自定义分隔符分割"""
        text = "Sentence1.Sentence2.Sentence3.Sentence4"
        chunks = self.splitter.split(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0

class TestMarkdownSplitter:
    """测试Markdown分割器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = create_test_config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(
                chunk_size=1000,
                chunk_overlap=100
            ),
            custom_config=CustomConfig()
        )
        self.splitter = MarkdownSplitter(self.config)

    def test_markdown_split(self):
        """测试Markdown分割"""
        text = """
        # 主标题
        
        这是第一段内容。
        
        ## 子标题
        
        这是第二段内容。
        
        ### 小标题
        
        这是第三段内容。
        """
        chunks = self.splitter.split(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0

class TestQuestionProcessor:
    """测试问题生成器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = create_test_config(
            model_settings=ModelConfig(
                api_key="test_key",
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=1000
            ),
            processing_config=ProcessingConfig(
                max_workers=2,
                min_chars=50,
                max_chars=500
            ),
            custom_config=CustomConfig(
                language="en",
                min_questions_per_chunk=1,
                max_questions_per_chunk=3,
                question_types=["factual", "inferential"],
                difficulty_range=(0.3, 0.8),
                min_confidence=0.7,
                min_quality="good"
            )
        )
        self.processor = QuestionProcessor(self.config)

    def test_processor_initialization(self):
        """测试处理器初始化"""
        assert self.processor.config is not None

    @patch('textfission.models.openai.OpenAIModel.generate')
    def test_process_chunk(self, mock_generate):
        """测试处理单个文本块"""
        # 模拟模型响应 - 返回正确的JSON格式
        mock_response = '''
        {
            "questions": [
                {
                    "text": "What is Python?",
                    "type": "factual",
                    "difficulty": 0.5,
                    "keywords": ["Python", "programming"],
                    "context_required": false
                },
                {
                    "text": "When was Python created?",
                    "type": "factual",
                    "difficulty": 0.6,
                    "keywords": ["Python", "created", "1991"],
                    "context_required": false
                }
            ]
        }
        '''
        mock_generate.return_value = mock_response
        
        chunk = "Python is a programming language created by Guido van Rossum in 1991."
        questions = self.processor.process_chunk(chunk)
        
        assert isinstance(questions, list)
        assert len(questions) > 0
        assert all(isinstance(q, dict) for q in questions)

    @patch('textfission.models.openai.OpenAIModel.generate')
    def test_process_chunks(self, mock_generate):
        """测试处理多个文本块"""
        # 模拟模型响应 - 返回正确的JSON格式
        mock_response = '''
        {
            "questions": [
                {
                    "text": "What is Python?",
                    "type": "factual",
                    "difficulty": 0.5,
                    "keywords": ["Python", "programming"],
                    "context_required": false
                },
                {
                    "text": "When was Python created?",
                    "type": "factual",
                    "difficulty": 0.6,
                    "keywords": ["Python", "created"],
                    "context_required": false
                }
            ]
        }
        '''
        mock_generate.return_value = mock_response
        
        chunks = [
            "Python is a programming language.",
            "Python was created in 1991.",
            "Guido van Rossum created Python."
        ]
        
        questions = self.processor.process_chunks(chunks, show_progress=False)
        
        assert isinstance(questions, list)
        assert len(questions) == len(chunks)
        assert all(isinstance(q, list) for q in questions)

class TestAnswerProcessor:
    """测试答案生成器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.config = create_test_config(
            model_settings=ModelConfig(
                api_key="test_key",
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=1000
            ),
            processing_config=ProcessingConfig(
                max_workers=2,
                min_chars=50,
                max_chars=500
            ),
            custom_config=CustomConfig(
                language="en",
                min_questions_per_chunk=1,
                max_questions_per_chunk=3,
                question_types=["factual", "inferential"],
                difficulty_range=(0.3, 0.8),
                min_confidence=0.7,
                min_quality="good"
            )
        )
        self.processor = AnswerProcessor(self.config)

    def test_processor_initialization(self):
        """测试处理器初始化"""
        assert self.processor.config is not None

    @patch('textfission.models.openai.OpenAIModel.generate')
    def test_process_question(self, mock_generate):
        """测试处理单个问题"""
        # 模拟模型响应 - 返回正确的JSON格式
        mock_response = '''
        {
            "answer": "Python is a high-level programming language.",
            "metadata": {
                "quality": "good",
                "confidence": 0.9,
                "relevance_score": 0.95,
                "completeness_score": 0.8,
                "coherence_score": 0.9,
                "supporting_evidence": ["Python is a programming language"],
                "citations": []
            }
        }
        '''
        mock_generate.return_value = mock_response
        
        chunk = "Python is a programming language created by Guido van Rossum."
        question = "What is Python?"
        
        answer = self.processor.process_question(chunk, question)
        
        assert isinstance(answer, dict)
        assert "answer" in answer
        assert "metadata" in answer
        assert isinstance(answer["answer"], str)
        assert isinstance(answer["metadata"]["confidence"], (int, float))

    @patch('textfission.models.openai.OpenAIModel.generate')
    def test_process_questions(self, mock_generate):
        """测试处理多个问题"""
        # 模拟模型响应 - 返回正确的JSON格式
        mock_response = '''
        {
            "answer": "Python is a high-level programming language.",
            "metadata": {
                "quality": "good",
                "confidence": 0.9,
                "relevance_score": 0.95,
                "completeness_score": 0.8,
                "coherence_score": 0.9,
                "supporting_evidence": ["Python is a programming language"],
                "citations": []
            }
        }
        '''
        mock_generate.return_value = mock_response
        
        chunk = "Python is a programming language created by Guido van Rossum."
        questions = ["What is Python?", "When was Python created?"]
        
        answers = self.processor.process_questions(chunk, questions, show_progress=False)
        
        assert isinstance(answers, list)
        assert len(answers) == len(questions)
        assert all(isinstance(a, dict) for a in answers)
        assert all("answer" in a for a in answers)
        assert all("metadata" in a for a in answers)

    @patch('textfission.models.openai.OpenAIModel.generate')
    def test_process_qa_pairs(self, mock_generate):
        """测试处理问答对"""
        # 模拟模型响应 - 返回正确的JSON格式
        mock_response = '''
        {
            "answer": "Python is a high-level programming language.",
            "metadata": {
                "quality": "good",
                "confidence": 0.9,
                "relevance_score": 0.95,
                "completeness_score": 0.8,
                "coherence_score": 0.9,
                "supporting_evidence": ["Python is a programming language"],
                "citations": []
            }
        }
        '''
        mock_generate.return_value = mock_response
        
        chunks = ["Python is a programming language."]
        questions = [["What is Python?", "When was Python created?"]]
        
        answers = self.processor.process_qa_pairs(chunks, questions, show_progress=False)
        
        assert isinstance(answers, list)
        assert len(answers) == len(chunks)
        assert all(isinstance(a, list) for a in answers)
        assert all(len(a) == len(q) for a, q in zip(answers, questions))

class TestProcessorIntegration:
    @patch('textfission.models.openai.OpenAIModel.generate')
    def test_processor_workflow(self, mock_generate):
        """测试处理器工作流程"""
        # 创建正确的mock响应序列
        # 问题生成器调用次数：1次（1个chunk）
        # 答案生成器调用次数：2次（2个问题）
        mock_generate.side_effect = [
            # 问题生成器的响应
            '''{
                "questions": [
                    {
                        "text": "What is Python programming language?",
                        "type": "factual",
                        "difficulty": 0.5,
                        "keywords": ["Python", "programming"],
                        "context_required": false
                    },
                    {
                        "text": "Who is the creator of Python programming language?",
                        "type": "factual",
                        "difficulty": 0.5,
                        "keywords": ["Python", "Guido"],
                        "context_required": false
                    }
                ]
            }''',
            # 答案生成器的响应 - 第一个问题
            '''{
                "answer": "Python is a high-level programming language.",
                "metadata": {
                    "quality": "good",
                    "confidence": 0.9,
                    "relevance_score": 0.95,
                    "completeness_score": 0.8,
                    "coherence_score": 0.9,
                    "supporting_evidence": ["Python is a programming language"],
                    "citations": [
                        {
                            "text": "Python is a programming language",
                            "position": "Found in original text"
                        }
                    ]
                }
            }''',
            # 答案生成器的响应 - 第二个问题
            '''{
                "answer": "Guido van Rossum is the creator of Python programming language.",
                "metadata": {
                    "quality": "good",
                    "confidence": 0.9,
                    "relevance_score": 0.95,
                    "completeness_score": 0.8,
                    "coherence_score": 0.9,
                    "supporting_evidence": ["Guido van Rossum created Python"],
                    "citations": [
                        {
                            "text": "It was created by Guido van Rossum",
                            "position": "Found in original text"
                        }
                    ]
                }
            }'''
        ]

        config = create_test_config(
            model_settings=ModelConfig(api_key="test-key"),
            processing_config=ProcessingConfig(),
            custom_config=CustomConfig(
                language="en",
                min_questions_per_chunk=2,
                max_questions_per_chunk=5,
                question_types=["factual", "inferential", "analytical", "evaluative", "creative"],
                difficulty_range=(0.3, 0.8),
                min_confidence=0.7,
                min_quality="good"
            )
        )

        text_processor = TextProcessor(config)
        question_processor = QuestionProcessor(config)
        answer_processor = AnswerProcessor(config)

        text = "Python is a programming language. It was created by Guido van Rossum."
        chunks = text_processor.process_text(text)
        assert len(chunks) > 0

        questions = question_processor.process_chunks(chunks, show_progress=False)
        assert len(questions) == len(chunks)

        qa_pairs = []
        for chunk, chunk_questions in zip(chunks, questions):
            if chunk_questions:
                qa_pairs.append([q["text"] for q in chunk_questions])
            else:
                qa_pairs.append([])

        answers = answer_processor.process_qa_pairs(chunks, qa_pairs, show_progress=False)
        assert len(answers) == len(chunks) 