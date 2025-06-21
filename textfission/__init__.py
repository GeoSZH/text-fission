from .core.config import Config, ModelConfig, ProcessingConfig, OutputConfig, ExportConfig, CustomConfig
from .core.exceptions import (
    TextFissionError,
    ConfigurationError,
    ProcessingError,
    GenerationError,
    ModelError,
    ValidationError,
    ExportError
)
from .processors.text_splitter import TextProcessor, RecursiveTextSplitter, MarkdownSplitter
from .processors.question_generator import QuestionProcessor, QuestionGenerator
from .processors.answer_generator import AnswerProcessor, AnswerGenerator
from .models.openai import OpenAIModel
from .models.factory import ModelFactory
from .exporters.base import DatasetExporter, JSONExporter, CSVExporter, TXTExporter

__version__ = "0.1.0"

__all__ = [
    # Core
    "Config",
    "ModelConfig",
    "ProcessingConfig",
    "OutputConfig",
    "ExportConfig",
    "CustomConfig",
    
    # Exceptions
    "TextFissionError",
    "ConfigurationError",
    "ProcessingError",
    "GenerationError",
    "ModelError",
    "ValidationError",
    "ExportError",
    
    # Processors
    "TextProcessor",
    "RecursiveTextSplitter",
    "MarkdownSplitter",
    "QuestionProcessor",
    "QuestionGenerator",
    "AnswerProcessor",
    "AnswerGenerator",
    
    # Models
    "OpenAIModel",
    "ModelFactory",
    
    # Exporters
    "DatasetExporter",
    "JSONExporter",
    "CSVExporter",
    "TXTExporter",
    "create_dataset",
    "create_dataset_from_file",
    "create_dataset_from_files"
]

def create_dataset(
    text: str,
    config: Config,
    output_path: str,
    output_format: str = "json",
    show_progress: bool = True
) -> str:
    """Create a dataset from text"""
    try:
        # Initialize processors
        text_processor = TextProcessor(config)
        question_processor = QuestionProcessor(config)
        answer_processor = AnswerProcessor(config)
        exporter = DatasetExporter(config)
        
        # Process text
        chunks = text_processor.process_text(text)
        
        # Generate questions
        questions = question_processor.process_chunks(chunks, show_progress)
        
        # Generate answers
        answers = answer_processor.process_qa_pairs(chunks, questions, show_progress)
        
        # Prepare dataset
        dataset = []
        for chunk, chunk_questions, chunk_answers in zip(chunks, questions, answers):
            for question, answer in zip(chunk_questions, chunk_answers):
                dataset.append({
                    "text": chunk,
                    "question": question["text"] if isinstance(question, dict) else question,
                    "answer": answer["answer"],
                    "confidence": answer["metadata"]["confidence"]
                })
        
        # Export dataset
        return exporter.export(dataset, output_path, output_format)
    except Exception as e:
        raise TextFissionError(f"Error creating dataset: {str(e)}")

def create_dataset_from_file(
    file_path: str,
    config: Config,
    output_path: str,
    output_format: str = "json",
    show_progress: bool = True
) -> str:
    """Create a dataset from file"""
    try:
        # Initialize processors
        text_processor = TextProcessor(config)
        question_processor = QuestionProcessor(config)
        answer_processor = AnswerProcessor(config)
        exporter = DatasetExporter(config)
        
        # Process file
        chunks = text_processor.process_file(file_path)
        
        # Generate questions
        questions = question_processor.process_chunks(chunks, show_progress)
        
        # Generate answers
        answers = answer_processor.process_qa_pairs(chunks, questions, show_progress)
        
        # Prepare dataset
        dataset = []
        for chunk, chunk_questions, chunk_answers in zip(chunks, questions, answers):
            for question, answer in zip(chunk_questions, chunk_answers):
                dataset.append({
                    "text": chunk,
                    "question": question["text"] if isinstance(question, dict) else question,
                    "answer": answer["answer"],
                    "confidence": answer["metadata"]["confidence"]
                })
        
        # Export dataset
        return exporter.export(dataset, output_path, output_format)
    except Exception as e:
        raise TextFissionError(f"Error creating dataset from file: {str(e)}")

def create_dataset_from_files(
    file_paths: list,
    config: Config,
    output_path: str,
    output_format: str = "json",
    show_progress: bool = True
) -> str:
    """Create a dataset from multiple files"""
    try:
        # Initialize processors
        text_processor = TextProcessor(config)
        question_processor = QuestionProcessor(config)
        answer_processor = AnswerProcessor(config)
        exporter = DatasetExporter(config)
        
        # Process files
        all_chunks = []
        for file_path in file_paths:
            chunks = text_processor.process_file(file_path)
            all_chunks.extend(chunks)
        
        # Generate questions
        questions = question_processor.process_chunks(all_chunks, show_progress)
        
        # Generate answers
        answers = answer_processor.process_qa_pairs(all_chunks, questions, show_progress)
        
        # Prepare dataset
        dataset = []
        for chunk, chunk_questions, chunk_answers in zip(all_chunks, questions, answers):
            for question, answer in zip(chunk_questions, chunk_answers):
                dataset.append({
                    "text": chunk,
                    "question": question["text"] if isinstance(question, dict) else question,
                    "answer": answer["answer"],
                    "confidence": answer["metadata"]["confidence"]
                })
        
        # Export dataset
        return exporter.export(dataset, output_path, output_format)
    except Exception as e:
        raise TextFissionError(f"Error creating dataset from files: {str(e)}") 