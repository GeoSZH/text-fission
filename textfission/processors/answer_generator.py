from typing import List, Dict, Any, Optional, Tuple
from ..core.base import BaseAnswerGenerator
from ..core.exceptions import GenerationError
from ..models.factory import ModelFactory
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
import re
from statistics import mean, stdev
import time

class AnswerQuality(Enum):
    """Quality levels for generated answers"""
    EXCELLENT = 4  # 优秀
    GOOD = 3      # 良好
    FAIR = 2      # 一般
    POOR = 1      # 差
    
    @classmethod
    def from_string(cls, value: str):
        """从字符串创建枚举值"""
        quality_map = {
            "excellent": cls.EXCELLENT,
            "good": cls.GOOD,
            "fair": cls.FAIR,
            "poor": cls.POOR
        }
        return quality_map.get(value.lower(), cls.FAIR)

@dataclass
class AnswerMetadata:
    """Metadata for a generated answer"""
    quality: AnswerQuality
    confidence: float
    relevance_score: float
    completeness_score: float
    coherence_score: float
    supporting_evidence: List[str]
    citations: List[Dict[str, str]]

class AnswerGenerator(BaseAnswerGenerator):
    """Enhanced answer generator using language models"""
    
    def __init__(self, config):
        super().__init__(config)
        self.models = []
        self.language = getattr(config.custom_config, 'language', 'en')
        self.answer_prompt = self._get_answer_prompt()
        self.min_confidence = getattr(config.custom_config, 'min_confidence', 0.7)
        self.min_quality = getattr(config.custom_config, 'min_quality', AnswerQuality.GOOD)
        self._initialize_models()

    def _initialize_models(self):
        """Initialize multiple models if configured"""
        # Initialize models
        if self.config.model_settings.use_parallel and self.config.model_settings.api_keys:
            for api_key, model_name in zip(self.config.model_settings.api_keys, self.config.model_settings.models):
                model_config = self.config.model_settings.copy()
                model_config.api_key = api_key
                model_config.model = model_name
                self.models.append(ModelFactory.create_model(self.config))
        else:
            # 确保至少有一个默认模型
            self.models.append(ModelFactory.create_model(self.config))

    def _get_answer_prompt(self) -> str:
        """Get the enhanced answer generation prompt based on language"""
        if self.language == "zh":
            return """
            你是一位专业的文本分析专家，擅长从复杂文本中提取关键信息并生成可用于模型微调的结构化数据。

            ## 核心任务
            根据用户提供的文本和问题，生成准确的答案。

            ## 约束条件（重要！）
            - 答案必须基于文本内容直接生成
            - 答案应简洁明了，避免冗余
            - 答案应完整覆盖问题要点
            - 禁止生成假设性、主观或无关内容
            - 答案质量应达到{min_quality}或以上
            - 答案置信度应达到{min_confidence}或以上

            ## 输出格式
            请返回JSON格式的答案，包含答案内容和元数据：
            {{
                "answer": "答案内容",
                "metadata": {{
                    "quality": "答案质量等级",
                    "confidence": 置信度,
                    "relevance_score": 相关性得分,
                    "completeness_score": 完整性得分,
                    "coherence_score": 连贯性得分,
                    "supporting_evidence": ["支持证据1", "支持证据2"],
                    "citations": [
                        {{
                            "text": "引用文本",
                            "position": "在原文中的位置"
                        }}
                    ]
                }}
            }}
            """
        else:
            return """
            You are a professional text analysis expert, skilled at extracting key information from complex texts and generating structured data.

            ## Core Task
            Based on the text and question provided by the user, generate accurate answers.

            ## Constraints (Important!)
            - Answers must be directly generated based on the text content
            - Answers should be concise and avoid redundancy
            - Answers should completely cover the question points
            - It is prohibited to generate hypothetical, subjective, or irrelevant content
            - Answer quality should be {min_quality} or better
            - Answer confidence should be {min_confidence} or higher

            ## Output Format
            Please return the answer in JSON format with metadata:
            {{
                "answer": "Answer content",
                "metadata": {{
                    "quality": "answer_quality_level",
                    "confidence": confidence_score,
                    "relevance_score": relevance_score,
                    "completeness_score": completeness_score,
                    "coherence_score": coherence_score,
                    "supporting_evidence": ["evidence1", "evidence2"],
                    "citations": [
                        {{
                            "text": "cited_text",
                            "position": "position_in_original_text"
                        }}
                    ]
                }}
            }}
            """

    def _format_prompt(self) -> str:
        """Format the prompt with configuration values"""
        # 确保min_quality是字符串
        min_quality_str = self.min_quality.value if hasattr(self.min_quality, 'value') else str(self.min_quality)
        return self.answer_prompt.format(
            min_quality=min_quality_str,
            min_confidence=self.min_confidence
        )

    def _validate_answer(self, answer_data: Dict[str, Any]) -> bool:
        """Validate generated answer"""
        if not isinstance(answer_data, dict):
            return False
        
        if "answer" not in answer_data or "metadata" not in answer_data:
            return False
        
        metadata = answer_data["metadata"]
        required_fields = [
            "quality", "confidence", "relevance_score",
            "completeness_score", "coherence_score",
            "supporting_evidence", "citations"
        ]
        
        if not all(field in metadata for field in required_fields):
            return False
        
        # Validate quality
        try:
            quality = AnswerQuality.from_string(metadata["quality"])
            # 处理min_quality可能是字符串或枚举值的情况
            if isinstance(self.min_quality, str):
                min_quality = AnswerQuality.from_string(self.min_quality)
            else:
                min_quality = self.min_quality
            if quality.value < min_quality.value:
                return False
        except (ValueError, AttributeError):
            return False
        
        # Validate confidence
        if not isinstance(metadata["confidence"], (int, float)):
            return False
        if metadata["confidence"] < self.min_confidence:
            return False
        
        # Validate scores
        for score_field in ["relevance_score", "completeness_score", "coherence_score"]:
            if not isinstance(metadata[score_field], (int, float)):
                return False
            if not 0 <= metadata[score_field] <= 1:
                return False
        
        # Validate supporting evidence
        if not isinstance(metadata["supporting_evidence"], list):
            return False
        
        # Validate citations
        if not isinstance(metadata["citations"], list):
            return False
        # 只验证非空的citations
        for citation in metadata["citations"]:
            if not isinstance(citation, dict):
                return False
            if not all(k in citation for k in ["text", "position"]):
                return False
        
        return True

    def _extract_citations(self, answer: str, chunk: str) -> List[Dict[str, str]]:
        """Extract citations from the answer based on the original text"""
        citations = []
        # Split chunk into sentences
        sentences = re.split(r'[.!?。！？]', chunk)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Find matching sentences in the answer
        for sentence in sentences:
            if sentence in answer:
                citations.append({
                    "text": sentence,
                    "position": f"Found in original text"
                })
        
        return citations

    def _extract_json_from_response(self, response: str) -> dict:
        """Extract JSON from model response, handling markdown code blocks"""
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

    def generate(self, chunk: str, question: str, max_retries: int = 3, retry_delay: float = 2.0) -> Dict[str, Any]:
        """Generate answer for a question from text chunk, with retry and robust JSON extraction"""
        last_exception = None
        for attempt in range(max_retries):
            try:
                # Use the first model if multiple models are available
                model = self.models[0]
                
                # Prepare the prompt
                prompt = f"{self._format_prompt()}\n\nText:\n{chunk}\n\nQuestion:\n{question}"

                # Generate answer using the model
                response = model.generate(prompt)

                # Parse the response using robust extraction
                answer_data = self._extract_json_from_response(response)
                if not self._validate_answer(answer_data):
                    raise GenerationError("Invalid answer format or quality")
                
                # Add citations if not present
                if not answer_data["metadata"]["citations"]:
                    answer_data["metadata"]["citations"] = self._extract_citations(
                        answer_data["answer"], chunk
                    )
                
                return answer_data
            except Exception as e:
                last_exception = e
                print(f"[重试] 第{attempt+1}次生成答案失败: {e}")
                time.sleep(retry_delay * (attempt + 1))
        # 最终失败
        raise GenerationError(f"Error generating answer after {max_retries} attempts: {last_exception}")

    def generate_parallel(self, chunk: str, question: str) -> Dict[str, Dict[str, Any]]:
        """Generate answers for a question from text chunk using multiple models in parallel"""
        try:
            if not self.config.model_settings.use_parallel:
                return {"default": self.generate(chunk, question)}

            # Prepare the prompt
            prompt = f"{self._format_prompt()}\n\nText:\n{chunk}\n\nQuestion:\n{question}"

            # Generate answers using all models in parallel
            answers = {}
            with ThreadPoolExecutor(max_workers=len(self.models)) as executor:
                future_to_model = {
                    executor.submit(model.generate, prompt): model
                    for model in self.models
                }

                for future in as_completed(future_to_model):
                    model = future_to_model[future]
                    try:
                        response = future.result()
                        try:
                            answer_data = self._extract_json_from_response(response)
                            if self._validate_answer(answer_data):
                                answers[model.model] = answer_data
                        except Exception as e:
                            print(f"Error parsing response from model {model.model}: {e}")
                    except Exception as e:
                        print(f"Error generating answer with model {model.model}: {str(e)}")

            return answers

        except Exception as e:
            raise GenerationError(f"Error generating parallel answers: {str(e)}")

    def generate_batch(self, chunk: str, questions: List[str], show_progress: bool = True) -> List[Dict[str, Any]]:
        """Generate answers for multiple questions from a chunk"""
        try:
            if show_progress:
                questions = tqdm(questions, desc="Generating answers")
            return [self.generate(chunk, question) for question in questions]
        except Exception as e:
            raise GenerationError(f"Error generating answers in batch: {str(e)}")

    def generate_batch_parallel(self, chunk: str, questions: List[str], show_progress: bool = True) -> List[Dict[str, Dict[str, Any]]]:
        """Generate answers for multiple questions from a chunk using multiple models in parallel"""
        try:
            if show_progress:
                questions = tqdm(questions, desc="Generating parallel answers")
            return [self.generate_parallel(chunk, question) for question in questions]
        except Exception as e:
            raise GenerationError(f"Error generating parallel answers in batch: {str(e)}")

class AnswerProcessor:
    """Enhanced answer processing class"""
    
    def __init__(self, config, generator: Optional[BaseAnswerGenerator] = None):
        self.config = config
        self.generator = generator or AnswerGenerator(config)

    def process_question(self, chunk: str, question: str) -> Dict[str, Any]:
        """Process a single question and generate answer"""
        try:
            return self.generator.generate(chunk, question)
        except Exception as e:
            raise GenerationError(f"Error processing question: {str(e)}")

    def process_question_parallel(self, chunk: str, question: str) -> Dict[str, Dict[str, Any]]:
        """Process a single question and generate answers using multiple models"""
        try:
            return self.generator.generate_parallel(chunk, question)
        except Exception as e:
            raise GenerationError(f"Error processing question in parallel: {str(e)}")

    def process_questions(self, chunk: str, questions: List[str], show_progress: bool = True) -> List[Dict[str, Any]]:
        """Process multiple questions and generate answers"""
        try:
            return self.generator.generate_batch(chunk, questions, show_progress)
        except Exception as e:
            raise GenerationError(f"Error processing questions: {str(e)}")

    def process_questions_parallel(self, chunk: str, questions: List[str], show_progress: bool = True) -> List[Dict[str, Dict[str, Any]]]:
        """Process multiple questions and generate answers using multiple models"""
        try:
            return self.generator.generate_batch_parallel(chunk, questions, show_progress)
        except Exception as e:
            raise GenerationError(f"Error processing questions in parallel: {str(e)}")

    def process_qa_pairs(self, chunks: List[str], questions: List[List[str]], show_progress: bool = True) -> List[List[Dict[str, Any]]]:
        """Process multiple chunks and their questions to generate answers"""
        try:
            if show_progress:
                pairs = tqdm(zip(chunks, questions), desc="Processing QA pairs", total=len(chunks))
            else:
                pairs = zip(chunks, questions)
            return [self.process_questions(chunk, chunk_questions, False) for chunk, chunk_questions in pairs]
        except Exception as e:
            raise GenerationError(f"Error processing QA pairs: {str(e)}")

    def process_qa_pairs_parallel(self, chunks: List[str], questions: List[List[str]], show_progress: bool = True) -> List[List[Dict[str, Dict[str, Any]]]]:
        """Process multiple chunks and their questions to generate answers using multiple models"""
        try:
            if show_progress:
                chunks = tqdm(zip(chunks, questions), desc="Processing QA pairs in parallel", total=len(chunks))
            return [self.process_questions_parallel(chunk, chunk_questions, False) for chunk, chunk_questions in chunks]
        except Exception as e:
            raise GenerationError(f"Error processing QA pairs in parallel: {str(e)}")

    def get_answer_statistics(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the generated answers"""
        stats = {
            "total_answers": len(answers),
            "quality_distribution": {},
            "average_confidence": 0.0,
            "average_relevance": 0.0,
            "average_completeness": 0.0,
            "average_coherence": 0.0,
            "citation_statistics": {
                "total_citations": 0,
                "average_citations_per_answer": 0.0
            }
        }
        
        if not answers:
            return stats
        
        # Calculate quality distribution
        for answer in answers:
            quality = answer["metadata"]["quality"]
            stats["quality_distribution"][quality] = stats["quality_distribution"].get(quality, 0) + 1
        
        # Calculate average scores
        stats["average_confidence"] = mean(a["metadata"]["confidence"] for a in answers)
        stats["average_relevance"] = mean(a["metadata"]["relevance_score"] for a in answers)
        stats["average_completeness"] = mean(a["metadata"]["completeness_score"] for a in answers)
        stats["average_coherence"] = mean(a["metadata"]["coherence_score"] for a in answers)
        
        # Calculate citation statistics
        total_citations = sum(len(a["metadata"]["citations"]) for a in answers)
        stats["citation_statistics"]["total_citations"] = total_citations
        stats["citation_statistics"]["average_citations_per_answer"] = total_citations / len(answers)
        
        return stats

    def filter_answers_by_quality(self, answers: List[Dict[str, Any]], min_quality: AnswerQuality) -> List[Dict[str, Any]]:
        """Filter answers by minimum quality"""
        return [
            a for a in answers
            if AnswerQuality(a["metadata"]["quality"]).value >= min_quality.value
        ]

    def filter_answers_by_confidence(self, answers: List[Dict[str, Any]], min_confidence: float) -> List[Dict[str, Any]]:
        """Filter answers by minimum confidence"""
        return [
            a for a in answers
            if a["metadata"]["confidence"] >= min_confidence
        ]

    def get_best_answer(self, parallel_answers: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Get the best answer from parallel model outputs"""
        if not parallel_answers:
            raise GenerationError("No answers available")
        
        # Score each answer based on quality and confidence
        scored_answers = []
        for model_name, answer in parallel_answers.items():
            quality_score = AnswerQuality(answer["metadata"]["quality"]).value
            confidence = answer["metadata"]["confidence"]
            relevance = answer["metadata"]["relevance_score"]
            completeness = answer["metadata"]["completeness_score"]
            coherence = answer["metadata"]["coherence_score"]
            
            # Calculate overall score
            score = (
                quality_score * 0.3 +
                confidence * 0.2 +
                relevance * 0.2 +
                completeness * 0.15 +
                coherence * 0.15
            )
            
            scored_answers.append((score, answer))
        
        # Return the answer with the highest score
        return max(scored_answers, key=lambda x: x[0])[1] 