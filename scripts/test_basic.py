#!/usr/bin/env python3
"""
Simple test script to verify basic functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from llmfixu.config.settings import config
        print("✅ Config module imported successfully")
        
        from llmfixu.processors.document_processor import DocumentProcessor
        print("✅ DocumentProcessor imported successfully")
        
        try:
            from llmfixu.processors.vector_manager import VectorManager
            print("✅ VectorManager imported successfully")
        except ImportError as e:
            print(f"⚠️  VectorManager import failed (missing chromadb): {e}")
        
        try:
            from llmfixu.api.ollama_client import OllamaClient
            print("✅ OllamaClient imported successfully")
        except ImportError as e:
            print(f"⚠️  OllamaClient import failed: {e}")
        
        try:
            from llmfixu.api.query_engine import QueryEngine
            print("✅ QueryEngine imported successfully")
        except ImportError as e:
            print(f"⚠️  QueryEngine import failed: {e}")
        
        from llmfixu.utils.helpers import setup_logging
        print("✅ Helpers imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Critical import error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    try:
        from llmfixu.config.settings import config
        
        assert config.OLLAMA_URL
        assert config.CHROMADB_URL
        assert config.CHUNK_SIZE > 0
        assert len(config.SUPPORTED_FORMATS) > 0
        
        print("✅ Configuration loaded and validated")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_document_processor():
    """Test document processor basic functionality."""
    try:
        from llmfixu.processors.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Test chunking
        test_content = "This is a test content. " * 100
        chunks = processor.chunk_content(test_content, chunk_size=50, overlap=10)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 60 for chunk in chunks)  # 50 + some tolerance
        
        print("✅ DocumentProcessor basic functionality works")
        return True
    except Exception as e:
        print(f"❌ DocumentProcessor error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running LLMFixU basic functionality tests...\n")
    
    tests = [
        test_imports,
        test_config,
        test_document_processor
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())