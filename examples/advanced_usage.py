from textfission import (
    Config,
    ModelConfig,
    ProcessingConfig,
    OutputConfig,
    TextProcessor,
    RecursiveTextSplitter,
    MarkdownSplitter,
    QuestionProcessor,
    QuestionGenerator,
    AnswerProcessor,
    AnswerGenerator,
    OpenAIModel,
    DatasetExporter
)
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import json

def custom_text_splitter(text: str) -> List[str]:
    """Custom text splitter implementation"""
    # Split text into paragraphs
    paragraphs = text.split("\n\n")
    
    # Process each paragraph
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= 1000:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def custom_question_prompt(text: str) -> str:
    """Custom question generation prompt"""
    return f"""
    You are a professional text analysis expert. Based on the following text, generate 3-5 high-quality questions.
    The questions should be:
    1. Directly related to the text content
    2. Cover different aspects of the text
    3. Have clear answer orientations
    4. Be educational and practical

    Text:
    {text}

    Please return the questions in JSON array format:
    ["Question 1", "Question 2", "..."]
    """

def custom_answer_prompt(text: str, question: str) -> str:
    """Custom answer generation prompt"""
    return f"""
    You are a professional text analysis expert. Based on the following text and question, generate an accurate answer.
    The answer should be:
    1. Directly based on the text content
    2. Concise and clear
    3. Complete and comprehensive
    4. Objective and factual

    Text:
    {text}

    Question:
    {question}

    Please return the answer in JSON format:
    {{
        "answer": "Answer content",
        "confidence": 0.95,
        "sources": ["relevant text snippets"]
    }}
    """

def process_chunk(
    chunk: str,
    question_processor: QuestionProcessor,
    answer_processor: AnswerProcessor
) -> List[Dict[str, Any]]:
    """Process a single chunk and generate QA pairs"""
    # Generate questions with custom prompt
    questions = question_processor.process_with_custom_prompt(
        chunk,
        custom_question_prompt(chunk)
    )
    
    # Generate answers for each question
    qa_pairs = []
    for question in questions:
        answer = answer_processor.process_with_custom_prompt(
            chunk,
            question,
            custom_answer_prompt(chunk, question)
        )
        qa_pairs.append({
            "text": chunk,
            "question": question,
            "answer": answer["answer"],
            "confidence": answer["confidence"],
            "sources": answer.get("sources", [])
        })
    
    return qa_pairs

def main():
    # Create configuration
    config = Config(
        model_config=ModelConfig(
            api_key="your-api-key",
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=2000
        ),
        processing_config=ProcessingConfig(
            chunk_size=1500,
            chunk_overlap=200,
            max_workers=4
        ),
        output_config=OutputConfig(
            format="json",
            encoding="utf-8",
            indent=2
        )
    )

    # Initialize processors
    text_processor = TextProcessor(config)
    question_processor = QuestionProcessor(config)
    answer_processor = AnswerProcessor(config)
    exporter = DatasetExporter(config)

    # Example 1: Custom text splitting
    text = """
    # Python Programming Language

    Python is a high-level, interpreted programming language known for its simplicity and readability.
    It was created by Guido van Rossum and first released in 1991.

    ## Key Features
    - Simple and readable syntax
    - Dynamic typing
    - Automatic memory management
    - Multiple programming paradigms

    ## Use Cases
    Python is widely used in:
    1. Web development
    2. Data science
    3. Machine learning
    4. Automation
    5. Scientific computing
    """
    
    # Use custom text splitter
    chunks = custom_text_splitter(text)
    print(f"Split text into {len(chunks)} chunks")

    # Example 2: Parallel processing
    all_qa_pairs = []
    with ThreadPoolExecutor(max_workers=config.processing_config.max_workers) as executor:
        # Submit tasks
        future_to_chunk = {
            executor.submit(
                process_chunk,
                chunk,
                question_processor,
                answer_processor
            ): chunk for chunk in chunks
        }
        
        # Process results
        for future in future_to_chunk:
            try:
                qa_pairs = future.result()
                all_qa_pairs.extend(qa_pairs)
            except Exception as e:
                print(f"Error processing chunk: {str(e)}")

    # Example 3: Custom export
    # Export to multiple formats
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Export to JSON
    json_path = os.path.join(output_dir, "dataset.json")
    exporter.export(all_qa_pairs, json_path, "json")
    print(f"Exported to JSON: {json_path}")
    
    # Export to CSV
    csv_path = os.path.join(output_dir, "dataset.csv")
    exporter.export(all_qa_pairs, csv_path, "csv")
    print(f"Exported to CSV: {csv_path}")
    
    # Export to TXT
    txt_path = os.path.join(output_dir, "dataset.txt")
    exporter.export(all_qa_pairs, txt_path, "txt")
    print(f"Exported to TXT: {txt_path}")

    # Example 4: Custom model usage
    model = OpenAIModel(config)
    
    # Get embeddings
    embeddings = model.get_embeddings([chunk for chunk in chunks])
    print(f"Generated {len(embeddings)} embeddings")
    
    # Count tokens
    total_tokens = sum(model.count_tokens(chunk) for chunk in chunks)
    print(f"Total tokens: {total_tokens}")

if __name__ == "__main__":
    main() 