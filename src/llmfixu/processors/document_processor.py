"""
Document processor for various file formats.
"""

import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..config.settings import config

# Optional imports with fallbacks
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents and extract text content."""
    
    def __init__(self):
        self.supported_formats = config.SUPPORTED_FORMATS
        self.max_file_size = config.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
    
    def process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a single file and extract metadata and content.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing file metadata and content, or None if processing fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        if file_path.stat().st_size > self.max_file_size:
            logger.error(f"File too large: {file_path} ({file_path.stat().st_size} bytes)")
            return None
        
        file_extension = file_path.suffix.lower().lstrip('.')
        if file_extension not in self.supported_formats:
            logger.error(f"Unsupported file format: {file_extension}")
            return None
        
        try:
            content = self._extract_content(file_path, file_extension)
            if not content:
                logger.warning(f"No content extracted from: {file_path}")
                return None
            
            # Generate file hash for deduplication
            file_hash = self._generate_file_hash(file_path)
            
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'file_hash': file_hash,
                'file_type': file_extension,
                'content': content,
                'content_length': len(content)
            }
            
            logger.info(f"Successfully processed: {file_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return None
    
    def _extract_content(self, file_path: Path, file_extension: str) -> str:
        """Extract text content based on file type."""
        if file_extension == 'pdf':
            return self._extract_pdf_content(file_path)
        elif file_extension == 'docx':
            return self._extract_docx_content(file_path)
        elif file_extension in ['txt', 'md']:
            return self._extract_text_content(file_path)
        elif file_extension == 'html':
            return self._extract_html_content(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
    
    def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        if not HAS_PDF:
            logger.error("PyPDF2 not installed, cannot process PDF files")
            return ""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = []
                for page in pdf_reader.pages:
                    content.append(page.extract_text())
                return '\n'.join(content)
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            return ""
    
    def _extract_docx_content(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        if not HAS_DOCX:
            logger.error("python-docx not installed, cannot process DOCX files")
            return ""
        
        try:
            doc = docx.Document(file_path)
            content = []
            for paragraph in doc.paragraphs:
                content.append(paragraph.text)
            return '\n'.join(content)
        except Exception as e:
            logger.error(f"Error extracting DOCX content: {str(e)}")
            return ""
    
    def _extract_text_content(self, file_path: Path) -> str:
        """Extract text from plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading text file: {str(e)}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text content: {str(e)}")
            return ""
    
    def _extract_html_content(self, file_path: Path) -> str:
        """Extract text from HTML file."""
        if not HAS_BS4:
            logger.error("beautifulsoup4 not installed, cannot process HTML files")
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                return soup.get_text()
        except Exception as e:
            logger.error(f"Error extracting HTML content: {str(e)}")
            return ""
    
    def _generate_file_hash(self, file_path: Path) -> str:
        """Generate SHA256 hash of file content for deduplication."""
        try:
            with open(file_path, 'rb') as file:
                return hashlib.sha256(file.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating file hash: {str(e)}")
            return ""
    
    def chunk_content(self, content: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split content into chunks for vector storage.
        
        Args:
            content: Text content to chunk
            chunk_size: Size of each chunk (defaults to config value)
            overlap: Overlap between chunks (defaults to config value)
            
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or config.CHUNK_SIZE
        overlap = overlap or config.CHUNK_OVERLAP
        
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            
            # Try to break at word boundaries
            if end < len(content):
                last_space = chunk.rfind(' ')
                if last_space > chunk_size * 0.8:  # Only if we don't lose too much content
                    end = start + last_space
                    chunk = content[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(content):
                break
        
        return chunks