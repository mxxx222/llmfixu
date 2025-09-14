"""
Utility functions for LLMFixU system.
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

from ..config.settings import config


def setup_logging(log_level: str = None, log_file: str = None):
    """Set up logging configuration."""
    log_level = log_level or config.LOG_LEVEL
    log_file = log_file or config.LOG_FILE
    
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler with colors if available
    console_handler = logging.StreamHandler()
    if HAS_COLORLOG:
        console_handler.setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    else:
        console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return root_logger


def find_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Find files with specific extensions in a directory.
    
    Args:
        directory: Directory to search
        extensions: List of file extensions to include
        
    Returns:
        List of file paths
    """
    extensions = extensions or config.SUPPORTED_FORMATS
    directory = Path(directory)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    files = []
    for ext in extensions:
        pattern = f"*.{ext}"
        files.extend(directory.rglob(pattern))
    
    return [str(f) for f in files]


def validate_environment() -> Dict[str, bool]:
    """
    Validate that the environment is properly configured.
    
    Returns:
        Dictionary with validation results
    """
    results = {}
    
    # Check if required directories exist
    required_dirs = [
        config.CHROMA_PERSIST_DIRECTORY,
        Path(config.LOG_FILE).parent
    ]
    
    for dir_path in required_dirs:
        dir_path = Path(dir_path)
        results[f"dir_{dir_path.name}"] = dir_path.exists()
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                results[f"dir_{dir_path.name}"] = True
            except Exception:
                results[f"dir_{dir_path.name}"] = False
    
    # Check file size limits
    results['file_size_limit'] = config.MAX_FILE_SIZE_MB > 0
    
    # Check supported formats
    results['supported_formats'] = len(config.SUPPORTED_FORMATS) > 0
    
    return results


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def print_banner():
    """Print LLMFixU banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                         LLMFixU                              ║
    ║                   AI Audit System                           ║
    ║                                                              ║
    ║  Tekoälyavusteinen dokumenttianalyysi ja kyselyjärjestelmä  ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_dependencies() -> Dict[str, bool]:
    """Check if required Python dependencies are available."""
    dependencies = {
        'requests': True,
        'chromadb': True,
        'PyPDF2': True,
        'python-docx': True,
        'beautifulsoup4': True,
        'colorlog': True
    }
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies