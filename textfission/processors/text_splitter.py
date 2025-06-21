from typing import List, Optional, Dict, Any, Protocol
from ..core.base import BaseSplitter
from ..core.exceptions import ProcessingError
import re
from tqdm import tqdm
import unicodedata
import langdetect
from nltk.tokenize import sent_tokenize
import nltk
from functools import lru_cache

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class Tokenizer(Protocol):
    """Tokenizer interface for text segmentation"""
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into sentences or other meaningful units"""
        ...

class NLTKTokenizer:
    """NLTK-based tokenizer implementation"""
    
    def __init__(self, language: str = 'english'):
        self.language = language
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using NLTK's sent_tokenize"""
        return sent_tokenize(text, language=self.language)

class APITokenizer:
    """API-based tokenizer implementation"""
    
    def __init__(self, api_url: str, api_key: Optional[str] = None):
        self.api_url = api_url
        self.api_key = api_key
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using external API"""
        # TODO: Implement API call
        raise NotImplementedError("API tokenizer not implemented yet")

class TextPreprocessor:
    """Text preprocessing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing unwanted characters and normalizing whitespace"""
        # Remove control characters
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text by converting to NFC form and handling special characters"""
        # Convert to NFC form
        text = unicodedata.normalize('NFC', text)
        # Replace special quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        return text

class SmartTextSplitter(BaseSplitter):
    """Advanced text splitter with semantic awareness and multi-language support"""
    
    def __init__(self, config, tokenizer: Optional[Tokenizer] = None):
        super().__init__(config)
        self.min_chars = config.processing_config.min_chars
        self.max_chars = config.processing_config.max_chars
        self.tokenizer = tokenizer or NLTKTokenizer()
        self.preprocessor = TextPreprocessor()
        
        # Language-specific settings
        self.language_settings = {
            'en': {
                'section_markers': ['#', '##', '###', 'Chapter', 'Section'],
                'paragraph_end': [r'\n\s*\n', r'\n\s*[A-Z]'],
                'sentence_end': ['.', '!', '?', ';']
            },
            'zh': {
                'section_markers': ['#', '##', '###', '第', '章', '节'],
                'paragraph_end': [r'\n\s*\n', r'\n\s*[一-龯]'],
                'sentence_end': ['。', '！', '？', '；', '.', '!', '?']
            }
        }
        
        # Cache for language detection
        self._detect_language = lru_cache(maxsize=1000)(self._detect_language_impl)
    
    def _detect_language_impl(self, text: str) -> str:
        """Detect language of text with caching"""
        try:
            return langdetect.detect(text)
        except:
            return 'en'  # Default to English if detection fails
    
    def split(self, text: str) -> List[str]:
        """Split text into semantically meaningful chunks"""
        try:
            # Preprocess text
            text = self.preprocessor.clean_text(text)
            text = self.preprocessor.normalize_text(text)
            
            # Detect language
            lang = self._detect_language(text)
            
            # Get language-specific settings
            settings = self.language_settings.get(lang, self.language_settings['en'])
            
            # Split into sections first
            sections = self._split_into_sections(text, settings)
            
            # Process each section
            chunks = []
            for section in sections:
                section_chunks = self._process_section(section, settings)
                chunks.extend(section_chunks)
            
            # Merge small chunks
            return self._merge_chunks(chunks)
            
        except Exception as e:
            raise ProcessingError(f"Error splitting text: {str(e)}")
    
    def _split_into_sections(self, text: str, settings: Dict[str, Any]) -> List[str]:
        """Split text into sections based on markers"""
        sections = []
        current_section = []
        
        for line in text.split('\n'):
            if any(line.strip().startswith(marker) for marker in settings['section_markers']):
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
            current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def _process_section(self, section: str, settings: Dict[str, Any]) -> List[str]:
        """Process a section into chunks using the configured tokenizer"""
        # Split into paragraphs
        paragraphs = re.split('|'.join(settings['paragraph_end']), section)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        for paragraph in paragraphs:
            # Use configured tokenizer to split into sentences
            sentences = self.tokenizer.tokenize(paragraph)
            
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                sentence_length = len(sentence)
                
                if current_length + sentence_length <= self.max_chars:
                    current_chunk.append(sentence)
                    current_length += sentence_length
                else:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_length = sentence_length
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _merge_chunks(self, chunks: List[str]) -> List[str]:
        """Merge small chunks while maintaining semantic boundaries"""
        merged = []
        current_chunk = ""
        
        for chunk in chunks:
            # 如果当前块加上新块超过限制，先保存当前块
            if current_chunk and len(current_chunk) + len(chunk) + 1 > self.max_chars:
                merged.append(current_chunk)
                current_chunk = ""
            
            # 如果单个块就超过限制，需要进一步分割
            if len(chunk) > self.max_chars:
                if current_chunk:
                    merged.append(current_chunk)
                    current_chunk = ""
                # 按字符分割超长块
                for i in range(0, len(chunk), self.max_chars):
                    merged.append(chunk[i:i + self.max_chars])
            else:
                # 正常合并
                if current_chunk:
                    current_chunk += " " + chunk
                else:
                    current_chunk = chunk
        
        if current_chunk:
            merged.append(current_chunk)
        
        return merged

class RecursiveTextSplitter(BaseSplitter):
    """Recursive text splitter that splits text into chunks based on separators"""
    
    def __init__(self, config):
        super().__init__(config)
        self.separators = ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
        self.min_chars = config.processing_config.min_chars
        self.max_chars = config.processing_config.max_chars

    def split(self, text: str) -> List[str]:
        """Split text into chunks recursively"""
        try:
            chunks = self._split_recursive(text)
            return [chunk for chunk in chunks if len(chunk.strip()) > 0]
        except Exception as e:
            raise ProcessingError(f"Error splitting text: {str(e)}")

    def _split_recursive(self, text: str, separators: Optional[List[str]] = None) -> List[str]:
        """Recursively split text using separators"""
        if separators is None:
            separators = self.separators

        if not separators:
            return [text]

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            # If we've exhausted all separators, split by character
            return self._split_by_length(text)

        # Split by current separator
        parts = text.split(separator)
        chunks = []

        for part in parts:
            if len(part) <= self.max_chars:
                chunks.append(part)
            else:
                # Recursively split longer parts
                sub_chunks = self._split_recursive(part, remaining_separators)
                chunks.extend(sub_chunks)

        # Merge small chunks
        return self._merge_chunks(chunks)

    def _split_by_length(self, text: str) -> List[str]:
        """Split text into chunks of maximum length"""
        chunks = []
        for i in range(0, len(text), self.max_chars):
            chunk = text[i:i + self.max_chars]
            if len(chunk.strip()) > 0:
                chunks.append(chunk)
        return chunks

    def _merge_chunks(self, chunks: List[str]) -> List[str]:
        """Merge small chunks together"""
        merged = []
        current_chunk = ""

        for chunk in chunks:
            if len(current_chunk) + len(chunk) <= self.max_chars:
                current_chunk += chunk
            else:
                if current_chunk:
                    merged.append(current_chunk)
                current_chunk = chunk

        if current_chunk:
            merged.append(current_chunk)

        return merged

class MarkdownSplitter(RecursiveTextSplitter):
    """Specialized splitter for Markdown documents"""
    
    def __init__(self, config):
        super().__init__(config)
        self.separators = ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]

    def split(self, text: str) -> List[str]:
        """Split Markdown text into chunks"""
        try:
            # Remove code blocks temporarily
            code_blocks = []
            text_without_code = re.sub(
                r'```[\s\S]*?```',
                lambda m: code_blocks.append(m.group(0)) or f"CODE_BLOCK_{len(code_blocks)}",
                text
            )

            # Split the text
            chunks = super().split(text_without_code)

            # Restore code blocks
            for i, chunk in enumerate(chunks):
                for j, code_block in enumerate(code_blocks):
                    chunks[i] = chunks[i].replace(f"CODE_BLOCK_{j}", code_block)

            return chunks
        except Exception as e:
            raise ProcessingError(f"Error splitting Markdown text: {str(e)}")

class TextProcessor:
    """Main text processing class"""
    
    def __init__(self, config, splitter: Optional[BaseSplitter] = None):
        self.config = config
        self.splitter = splitter or RecursiveTextSplitter(config)

    def process_text(self, text: str) -> List[str]:
        """Process text and return chunks"""
        try:
            return self.splitter.split(text)
        except Exception as e:
            raise ProcessingError(f"Error processing text: {str(e)}")

    def process_file(self, file_path: str) -> List[str]:
        """Process text file and return chunks"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.process_text(text)
        except Exception as e:
            raise ProcessingError(f"Error processing file {file_path}: {str(e)}")

    def process_batch(self, texts: List[str], show_progress: bool = True) -> List[List[str]]:
        """Process multiple texts and return chunks for each"""
        try:
            if show_progress:
                texts = tqdm(texts, desc="Processing texts")
            return [self.process_text(text) for text in texts]
        except Exception as e:
            raise ProcessingError(f"Error processing batch: {str(e)}") 