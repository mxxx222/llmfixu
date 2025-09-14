#!/usr/bin/env python3
"""
System diagnostics and health check for LLMFixU.
"""

import argparse
import sys
import os
import time
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llmfixu.config.settings import config
from llmfixu.utils.helpers import setup_logging, print_banner, check_dependencies
from llmfixu.processors.vector_manager import VectorManager
from llmfixu.api.ollama_client import OllamaClient
from llmfixu.api.query_engine import QueryEngine
import logging

logger = logging.getLogger(__name__)


def check_services():
    """Check if all required services are running."""
    services = {
        'Ollama': config.OLLAMA_URL,
        'ChromaDB': config.CHROMADB_URL,
        'OpenWebUI': config.OPENWEBUI_URL,
        'n8n': config.N8N_URL
    }
    
    results = {}
    
    print("\n🔍 Checking services...")
    for service, url in services.items():
        try:
            response = requests.get(f"{url}/", timeout=5)
            status = response.status_code < 400
            results[service] = status
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {service}: {url} - {'OK' if status else 'FAILED'}")
        except Exception as e:
            results[service] = False
            print(f"❌ {service}: {url} - FAILED ({str(e)})")
    
    return results


def check_python_dependencies():
    """Check Python dependencies."""
    print("\n📦 Checking Python dependencies...")
    deps = check_dependencies()
    
    all_ok = True
    for dep, status in deps.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {dep}: {'OK' if status else 'MISSING'}")
        if not status:
            all_ok = False
    
    if not all_ok:
        print("\n💡 Install missing dependencies with: pip install -r requirements.txt")
    
    return all_ok


def check_configuration():
    """Check system configuration."""
    print("\n⚙️  Checking configuration...")
    
    checks = {
        'Data directory': Path(config.CHROMA_PERSIST_DIRECTORY).exists(),
        'Log directory': Path(config.LOG_FILE).parent.exists(),
        'Supported formats': len(config.SUPPORTED_FORMATS) > 0,
        'File size limit': config.MAX_FILE_SIZE_MB > 0,
        'Chunk size': config.CHUNK_SIZE > 0,
    }
    
    all_ok = True
    for check, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check}: {'OK' if status else 'FAILED'}")
        if not status:
            all_ok = False
    
    return all_ok


def check_vector_database():
    """Check vector database connection and contents."""
    print("\n🗄️  Checking vector database...")
    
    try:
        vector_manager = VectorManager()
        collection_info = vector_manager.get_collection_info()
        
        print(f"✅ Connection: OK")
        print(f"✅ Collection: {collection_info.get('name', 'Unknown')}")
        print(f"✅ Document count: {collection_info.get('document_count', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Vector database: FAILED ({str(e)})")
        return False


def check_llm_service():
    """Check LLM service and models."""
    print("\n🤖 Checking LLM service...")
    
    try:
        ollama_client = OllamaClient()
        
        if not ollama_client.is_available():
            print("❌ Ollama service: NOT AVAILABLE")
            return False
        
        print("✅ Ollama service: OK")
        
        models = ollama_client.list_models()
        print(f"✅ Available models: {len(models)}")
        
        if models:
            for model in models[:5]:  # Show first 5 models
                print(f"   - {model}")
            if len(models) > 5:
                print(f"   ... and {len(models) - 5} more")
        else:
            print("⚠️  No models found. You may need to pull some models.")
            print("   Example: docker exec llmfixu-ollama ollama pull llama2")
        
        # Test default model
        if config.DEFAULT_MODEL in [m.split(':')[0] for m in models]:
            print(f"✅ Default model ({config.DEFAULT_MODEL}): Available")
        else:
            print(f"⚠️  Default model ({config.DEFAULT_MODEL}): Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM service: FAILED ({str(e)})")
        return False


def run_integration_test():
    """Run a simple integration test."""
    print("\n🧪 Running integration test...")
    
    try:
        query_engine = QueryEngine()
        
        # Health check
        health = query_engine.health_check()
        if not health['overall']:
            print("❌ Integration test: System not healthy")
            return False
        
        # Test query (if there are documents)
        test_results = query_engine.get_similar_documents("test", n_results=1)
        if test_results:
            print("✅ Integration test: Vector search working")
            
            # Test LLM query
            result = query_engine.query("What is this system?", n_context_docs=1)
            if result['answer']:
                print("✅ Integration test: LLM generation working")
                return True
            else:
                print("⚠️  Integration test: LLM generation failed")
                return False
        else:
            print("⚠️  Integration test: No documents found (try ingesting some documents)")
            return True  # Not a failure, just no data
            
    except Exception as e:
        print(f"❌ Integration test: FAILED ({str(e)})")
        return False


def main():
    """Main diagnostic function."""
    parser = argparse.ArgumentParser(description='LLMFixU System Diagnostics')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(log_level=log_level)
    
    if not args.json:
        print_banner()
        print("LLMFixU System Diagnostics")
        print("=" * 60)
    
    # Run all checks
    results = {}
    
    results['dependencies'] = check_python_dependencies()
    results['configuration'] = check_configuration()
    results['services'] = check_services()
    results['vector_database'] = check_vector_database()
    results['llm_service'] = check_llm_service()
    results['integration_test'] = run_integration_test()
    
    # Summary
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r)
    
    if args.json:
        import json
        print(json.dumps({
            'results': results,
            'summary': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'overall_health': passed_checks == total_checks
            }
        }, indent=2))
    else:
        print(f"\n📊 SUMMARY")
        print("=" * 60)
        print(f"Checks passed: {passed_checks}/{total_checks}")
        
        if passed_checks == total_checks:
            print("✅ All systems operational!")
            return 0
        else:
            print("⚠️  Some issues detected. Check the output above.")
            return 1


if __name__ == '__main__':
    sys.exit(main())