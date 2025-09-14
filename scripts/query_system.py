#!/usr/bin/env python3
"""
Query script for LLMFixU.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llmfixu.api.query_engine import QueryEngine
from llmfixu.utils.helpers import setup_logging, print_banner, truncate_text
import logging
import json

logger = logging.getLogger(__name__)


def main():
    """Main function for querying documents."""
    parser = argparse.ArgumentParser(description='Query LLMFixU document system')
    parser.add_argument('question', nargs='?', help='Question to ask (if not provided, interactive mode)')
    parser.add_argument('--model', help='LLM model to use')
    parser.add_argument('--context-docs', type=int, default=3,
                       help='Number of context documents to use')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive mode')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(log_level=log_level)
    
    if not args.json:
        print_banner()
    
    try:
        # Initialize query engine
        query_engine = QueryEngine()
        
        # Health check
        health = query_engine.health_check()
        if not health['overall']:
            logger.error("System health check failed:")
            for component, status in health.items():
                if component != 'overall':
                    logger.error(f"  {component}: {'OK' if status else 'FAILED'}")
            return 1
        
        if args.interactive or not args.question:
            # Interactive mode
            logger.info("Entering interactive mode. Type 'quit' or 'exit' to quit.")
            
            while True:
                try:
                    question = input("\nKysymys: ").strip()
                    if question.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if not question:
                        continue
                    
                    result = query_engine.query(
                        question=question,
                        n_context_docs=args.context_docs,
                        model=args.model
                    )
                    
                    print_result(result, args.json, args.verbose)
                    
                except KeyboardInterrupt:
                    print("\nQuitting...")
                    break
                except EOFError:
                    break
        else:
            # Single query mode
            result = query_engine.query(
                question=args.question,
                n_context_docs=args.context_docs,
                model=args.model
            )
            
            print_result(result, args.json, args.verbose)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during query: {str(e)}")
        return 1


def print_result(result, json_output=False, verbose=False):
    """Print query result."""
    if json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    
    print("\n" + "="*60)
    print("VASTAUS:")
    print("="*60)
    print(result['answer'])
    
    if result['sources']:
        print("\n" + "-"*40)
        print("LÄHTEET:")
        print("-"*40)
        for i, source in enumerate(result['sources'], 1):
            relevance = source.get('relevance_score', 0) * 100
            print(f"{i}. {source['file_name']} (relevanssi: {relevance:.1f}%)")
            if verbose and source.get('file_path'):
                print(f"   Polku: {source['file_path']}")
    
    confidence = result.get('confidence', 0) * 100
    print(f"\nLuotettavuus: {confidence:.1f}%")
    
    if verbose:
        print(f"Käytetty malli: {result.get('model_used', 'Unknown')}")
        print(f"Kontekstidokumentteja: {len(result.get('context_docs', []))}")
        
        if result.get('context_docs'):
            print("\nKONTEKSTI:")
            for i, doc in enumerate(result['context_docs'][:2], 1):  # Show first 2
                print(f"{i}. {truncate_text(doc['content'], 150)}")


if __name__ == '__main__':
    sys.exit(main())