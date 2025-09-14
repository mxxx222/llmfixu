"""
Configuration management for LLMFixU system.
"""

import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration class for LLMFixU system."""
    
    def __init__(self):
        self.load_env_config()
    
    def load_env_config(self):
        """Load configuration from environment variables."""
        # Service URLs
        self.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://localhost:3000")
        self.CHROMADB_URL = os.getenv("CHROMADB_URL", "http://localhost:8000")
        self.N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
        
        # Database Configuration
        self.CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "llmfixu_documents")
        self.CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma")
        
        # Document Processing
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
        self.SUPPORTED_FORMATS = os.getenv("SUPPORTED_FORMATS", "pdf,txt,md,docx,html").split(",")
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        # AI Configuration
        self.DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama2")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "./logs/llmfixu.log")
        
        # Ensure directories exist
        Path(self.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)
        Path(self.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }


# Global configuration instance
config = Config()