#!/usr/bin/env python3
"""
Document ingestion script for LLMFixU.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llmfixu.processors.document_processor import DocumentProcessor
from llmfixu.processors.vector_manager import VectorManager
from llmfixu.utils.helpers import setup_logging, find_files, print_banner, format_file_size
import logging

logger = logging.getLogger(__name__)


def main():
    """Main function for document ingestion."""
    parser = argparse.ArgumentParser(description='Ingest documents into LLMFixU vector database')
    parser.add_argument('input_path', help='Path to document or directory')
    parser.add_argument('--recursive', '-r', action='store_true', 
                       help='Process directories recursively')
    parser.add_argument('--clear', action='store_true',
                       help='Clear existing documents before ingestion')
    parser.add_argument('--chunk-size', type=int, default=1000,
                       help='Chunk size for document splitting')
    parser.add_argument('--chunk-overlap', type=int, default=200,
                       help='Overlap between chunks')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(log_level=log_level)
    
    print_banner()
    logger.info("Starting document ingestion process")
    
    try:
        # Initialize components
        processor = DocumentProcessor()
        vector_manager = VectorManager()
        
        # Clear collection if requested
        if args.clear:
            logger.info("Clearing existing documents...")
            vector_manager.clear_collection()
        
        # Find files to process
        input_path = Path(args.input_path)
        if not input_path.exists():
            logger.error(f"Input path does not exist: {input_path}")
            return 1
        
        if input_path.is_file():
            files_to_process = [str(input_path)]
        else:
            logger.info(f"Scanning directory: {input_path}")
            if args.recursive:
                files_to_process = find_files(str(input_path))
            else:
                files_to_process = [str(f) for f in input_path.iterdir() 
                                  if f.is_file() and f.suffix.lower().lstrip('.') in processor.supported_formats]
        
        logger.info(f"Found {len(files_to_process)} files to process")
        
        # Process files
        processed_count = 0
        failed_count = 0
        total_size = 0
        
        for file_path in files_to_process:
            logger.info(f"Processing: {file_path}")
            
            # Process document
            doc_metadata = processor.process_file(file_path)
            if not doc_metadata:
                failed_count += 1
                continue
            
            # Chunk content
            chunks = processor.chunk_content(
                doc_metadata['content'], 
                args.chunk_size, 
                args.chunk_overlap
            )
            
            # Prepare documents for vector storage
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    'content': chunk,
                    'metadata': {
                        'file_path': doc_metadata['file_path'],
                        'file_name': doc_metadata['file_name'],
                        'file_hash': doc_metadata['file_hash'],
                        'file_type': doc_metadata['file_type'],
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                }
                documents.append(doc)
            
            # Add to vector database
            if vector_manager.add_documents(documents):
                processed_count += 1
                total_size += doc_metadata['file_size']
                logger.info(f"Successfully processed: {file_path} ({len(chunks)} chunks)")
            else:
                failed_count += 1
                logger.error(f"Failed to add to vector database: {file_path}")
        
        # Print summary
        logger.info("=" * 60)
        logger.info("INGESTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Files processed: {processed_count}")
        logger.info(f"Files failed: {failed_count}")
        logger.info(f"Total size: {format_file_size(total_size)}")
        
        # Collection info
        collection_info = vector_manager.get_collection_info()
        logger.info(f"Collection document count: {collection_info.get('document_count', 'Unknown')}")
        
        return 0 if failed_count == 0 else 1
        
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())