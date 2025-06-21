from textfission import (
    Config,
    ModelConfig,
    ProcessingConfig,
    OutputConfig,
    create_dataset,
    create_dataset_from_file,
    create_dataset_from_files
)

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

    # Example 1: Create dataset from text
    text = """
    Python is a high-level, interpreted programming language known for its simplicity and readability.
    It was created by Guido van Rossum and first released in 1991. Python's design philosophy emphasizes
    code readability with its notable use of significant whitespace. Its syntax allows programmers to
    express concepts in fewer lines of code than would be possible in languages such as C++ or Java.
    Python features a dynamic type system and automatic memory management. It supports multiple
    programming paradigms, including structured, object-oriented, and functional programming.
    """
    
    output_path = "output/dataset_from_text.json"
    create_dataset(text, config, output_path)
    print(f"Dataset created from text: {output_path}")

    # Example 2: Create dataset from file
    file_path = "input/sample.txt"
    output_path = "output/dataset_from_file.json"
    create_dataset_from_file(file_path, config, output_path)
    print(f"Dataset created from file: {output_path}")

    # Example 3: Create dataset from multiple files
    file_paths = [
        "input/sample1.txt",
        "input/sample2.txt",
        "input/sample3.txt"
    ]
    output_path = "output/dataset_from_files.json"
    create_dataset_from_files(file_paths, config, output_path)
    print(f"Dataset created from files: {output_path}")

if __name__ == "__main__":
    main() 