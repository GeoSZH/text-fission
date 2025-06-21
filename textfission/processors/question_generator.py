from typing import List, Dict, Any, Optional, Tuple
from ..core.base import BaseQuestionGenerator
from ..core.exceptions import GenerationError
from ..models.factory import ModelFactory
import json
from tqdm import tqdm
import re
from enum import Enum
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time

class QuestionType(Enum):
    """Types of questions that can be generated"""
    FACTUAL = "factual"  # 事实性问题
    INFERENTIAL = "inferential"  # 推理性问题
    ANALYTICAL = "analytical"  # 分析性问题
    EVALUATIVE = "evaluative"  # 评价性问题
    CREATIVE = "creative"  # 创造性问题

@dataclass
class QuestionMetadata:
    """Metadata for a generated question"""
    type: QuestionType
    difficulty: float  # 0.0 to 1.0
    keywords: List[str]
    context_required: bool

class QuestionGenerator(BaseQuestionGenerator):
    """Enhanced question generator using language models"""
    
    def __init__(self, config):
        super().__init__(config)
        self.model = ModelFactory.create_model(config)
        self.language = getattr(config.custom_config, 'language', 'en')
        self.question_prompt = self._get_question_prompt()
        self.max_questions_per_chunk = getattr(config.custom_config, 'max_questions_per_chunk', 5)
        self.min_questions_per_chunk = getattr(config.custom_config, 'min_questions_per_chunk', 2)
        self.question_types = getattr(config.custom_config, 'question_types', [t.value for t in QuestionType])
        self.difficulty_range = getattr(config.custom_config, 'difficulty_range', (0.3, 0.8))

    def _get_question_prompt(self) -> str:
        """Get the enhanced question generation prompt based on language"""
        if self.language == "zh":
            return """
            你是一位专业的文本分析专家，擅长从复杂文本中提取关键信息并生成可用于模型微调的结构化数据。

            ## 核心任务
            根据用户提供的文本，生成高质量的问题。

            ## 约束条件（重要！）
            - 必须基于文本内容直接生成
            - 问题应具有明确答案指向性
            - 需覆盖文本的不同方面
            - 禁止生成假设性、重复或相似问题
            - 问题难度应在{min_difficulty}到{max_difficulty}之间
            - 每个文本块生成{min_questions}到{max_questions}个问题
            - 问题类型应包含：{question_types}

            ## 输出格式
            请返回JSON格式的问题列表，包含问题及其元数据：
            {{
                "questions": [
                    {{
                        "text": "问题1",
                        "type": "问题类型",
                        "difficulty": 难度值,
                        "keywords": ["关键词1", "关键词2"],
                        "context_required": true/false
                    }},
                    ...
                ]
            }}
            """
        else:
            return """
            You are a professional text analysis expert, skilled at extracting key information from complex texts and generating structured data.

            ## Core Task
            Based on the text provided by the user, generate high-quality questions.

            ## Constraints (Important!)
            - Must be directly generated based on the text content
            - Questions should have a clear answer orientation
            - Should cover different aspects of the text
            - It is prohibited to generate hypothetical, repetitive, or similar questions
            - Question difficulty should be between {min_difficulty} and {max_difficulty}
            - Generate {min_questions} to {max_questions} questions per text chunk
            - Question types should include: {question_types}

            ## Output Format
            Please return the questions in JSON format with metadata:
            {{
                "questions": [
                    {{
                        "text": "Question 1",
                        "type": "question_type",
                        "difficulty": difficulty_value,
                        "keywords": ["keyword1", "keyword2"],
                        "context_required": true/false
                    }},
                    ...
                ]
            }}
            """

    def _format_prompt(self) -> str:
        """Format the prompt with configuration values"""
        return self.question_prompt.format(
            min_difficulty=self.difficulty_range[0],
            max_difficulty=self.difficulty_range[1],
            min_questions=self.min_questions_per_chunk,
            max_questions=self.max_questions_per_chunk,
            question_types=", ".join(self.question_types)
        )

    def _validate_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and filter generated questions"""
        valid_questions = []
        for q in questions:
            # Validate required fields
            if not all(k in q for k in ["text", "type", "difficulty", "keywords", "context_required"]):
                continue
            
            # Validate question type
            if q["type"] not in self.question_types:
                continue
            
            # Validate difficulty
            if not self.difficulty_range[0] <= q["difficulty"] <= self.difficulty_range[1]:
                continue
            
            # Validate question text
            if not q["text"].strip() or len(q["text"]) < 10:
                continue
            
            valid_questions.append(q)
        
        return valid_questions

    def _extract_json_from_response(self, response: str) -> dict:
        if not response or not response.strip():
            raise GenerationError("Model returned empty response")
        # 优先提取 markdown 代码块
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        # 再尝试直接提取大括号
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        # 最后直接尝试
        return json.loads(response)

    def generate(self, chunk: str, max_retries: int = 3, retry_delay: float = 2.0) -> List[Dict[str, Any]]:
        """Generate questions with metadata from text chunk, with retry and robust JSON extraction"""
        last_exception = None
        for attempt in range(max_retries):
            try:
                prompt = f"{self._format_prompt()}\n\nText:\n{chunk}"
                response = self.model.generate(prompt)
                result = self._extract_json_from_response(response)
                if not isinstance(result, dict) or "questions" not in result:
                    raise GenerationError("Invalid response format: missing 'questions' key")
                questions = result["questions"]
                if not isinstance(questions, list):
                    raise GenerationError("Questions must be a list")
                valid_questions = self._validate_questions(questions)
                if len(valid_questions) < self.min_questions_per_chunk:
                    raise GenerationError(f"Generated only {len(valid_questions)} valid questions, minimum required is {self.min_questions_per_chunk}")
                return valid_questions[:self.max_questions_per_chunk]
            except Exception as e:
                last_exception = e
                print(f"[重试] 第{attempt+1}次生成失败: {e}")
                time.sleep(retry_delay * (attempt + 1))
        # 最终失败
        raise GenerationError(f"Error generating questions after {max_retries} attempts: {last_exception}")

    def generate_batch(self, chunks: List[str], show_progress: bool = True) -> List[List[Dict[str, Any]]]:
        """Generate questions for multiple chunks in parallel"""
        try:
            # Temporarily disable parallel processing to debug
            results = []
            if show_progress:
                for chunk in tqdm(chunks, desc="Generating questions"):
                    results.append(self.generate(chunk))
            else:
                for chunk in chunks:
                    results.append(self.generate(chunk))
            return results
                
        except Exception as e:
            raise GenerationError(f"Error generating questions in batch: {str(e)}")

    def generate_with_custom_prompt(self, chunk: str, custom_prompt: str) -> List[Dict[str, Any]]:
        """Generate questions using a custom prompt"""
        try:
            # Store original prompt
            original_prompt = self.question_prompt
            
            # Use custom prompt
            self.question_prompt = custom_prompt
            
            # Generate questions
            questions = self.generate(chunk)
            
            # Restore original prompt
            self.question_prompt = original_prompt
            
            return questions
        except Exception as e:
            raise GenerationError(f"Error generating questions with custom prompt: {str(e)}")

class QuestionProcessor:
    """Enhanced question processing class"""
    
    def __init__(self, config, generator: Optional[BaseQuestionGenerator] = None):
        self.config = config
        self.generator = generator or QuestionGenerator(config)

    def process_chunk(self, chunk: str) -> List[Dict[str, Any]]:
        """Process a single chunk and generate questions with metadata"""
        try:
            return self.generator.generate(chunk)
        except Exception as e:
            raise GenerationError(f"Error processing chunk: {str(e)}")

    def process_chunks(self, chunks: List[str], show_progress: bool = True) -> List[List[Dict[str, Any]]]:
        """Process multiple chunks and generate questions with metadata"""
        try:
            return self.generator.generate_batch(chunks, show_progress)
        except Exception as e:
            raise GenerationError(f"Error processing chunks: {str(e)}")

    def process_with_custom_prompt(self, chunk: str, custom_prompt: str) -> List[Dict[str, Any]]:
        """Process a chunk with a custom prompt"""
        try:
            return self.generator.generate_with_custom_prompt(chunk, custom_prompt)
        except Exception as e:
            raise GenerationError(f"Error processing with custom prompt: {str(e)}")

    def filter_questions_by_type(self, questions: List[Dict[str, Any]], question_type: str) -> List[Dict[str, Any]]:
        """Filter questions by type"""
        return [q for q in questions if q["type"] == question_type]

    def filter_questions_by_difficulty(self, questions: List[Dict[str, Any]], min_difficulty: float, max_difficulty: float) -> List[Dict[str, Any]]:
        """Filter questions by difficulty range"""
        return [q for q in questions if min_difficulty <= q["difficulty"] <= max_difficulty]

    def get_question_statistics(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the generated questions"""
        stats = {
            "total_questions": len(questions),
            "type_distribution": {},
            "average_difficulty": 0.0,
            "keywords_frequency": {}
        }
        
        if not questions:
            return stats
        
        # Calculate type distribution
        for q in questions:
            q_type = q["type"]
            stats["type_distribution"][q_type] = stats["type_distribution"].get(q_type, 0) + 1
        
        # Calculate average difficulty
        stats["average_difficulty"] = sum(q["difficulty"] for q in questions) / len(questions)
        
        # Calculate keyword frequency
        for q in questions:
            for keyword in q["keywords"]:
                stats["keywords_frequency"][keyword] = stats["keywords_frequency"].get(keyword, 0) + 1
        
        return stats 