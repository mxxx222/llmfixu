"""
Query engine that combines vector search with LLM generation.
"""

import logging
from typing import List, Dict, Any, Optional

from ..processors.vector_manager import VectorManager
from ..api.ollama_client import OllamaClient
from ..config.settings import config

logger = logging.getLogger(__name__)


class QueryEngine:
    """Query engine combining vector search and LLM generation."""
    
    def __init__(self):
        self.vector_manager = VectorManager()
        self.ollama_client = OllamaClient()
    
    def query(self, question: str, n_context_docs: int = 3, 
              model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Process a query using RAG (Retrieval-Augmented Generation).
        
        Args:
            question: The question to answer
            n_context_docs: Number of context documents to retrieve
            model: LLM model to use
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing answer, sources, and metadata
        """
        try:
            # 1. Retrieve relevant documents
            logger.info(f"Searching for documents related to: {question}")
            relevant_docs = self.vector_manager.search_documents(
                query=question,
                n_results=n_context_docs
            )
            
            if not relevant_docs:
                return {
                    'answer': 'Anteeksi, en löytänyt asiaankuuluvia dokumentteja kysymykseesi.',
                    'sources': [],
                    'context_docs': [],
                    'confidence': 0.0
                }
            
            # 2. Prepare context
            context_texts = [doc['content'] for doc in relevant_docs]
            
            # 3. Generate answer using LLM
            logger.info("Generating answer using LLM")
            answer = self.ollama_client.generate_response(
                prompt=question,
                context=context_texts,
                model=model,
                **kwargs
            )
            
            if not answer:
                return {
                    'answer': 'Anteeksi, en pystynyt luomaan vastausta kysymykseesi.',
                    'sources': [],
                    'context_docs': relevant_docs,
                    'confidence': 0.0
                }
            
            # 4. Prepare sources information
            sources = []
            for doc in relevant_docs:
                source_info = {
                    'id': doc['id'],
                    'file_name': doc['metadata'].get('file_name', 'Unknown'),
                    'file_path': doc['metadata'].get('file_path', ''),
                    'relevance_score': 1.0 - doc.get('distance', 0.0) if doc.get('distance') is not None else 0.5
                }
                sources.append(source_info)
            
            # 5. Calculate confidence score based on document relevance
            avg_relevance = sum(s['relevance_score'] for s in sources) / len(sources) if sources else 0.0
            confidence = min(avg_relevance, 0.95)  # Cap at 95%
            
            return {
                'answer': answer,
                'sources': sources,
                'context_docs': relevant_docs,
                'confidence': confidence,
                'model_used': model or config.DEFAULT_MODEL
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'answer': f'Virhe kyselyn käsittelyssä: {str(e)}',
                'sources': [],
                'context_docs': [],
                'confidence': 0.0
            }
    
    def batch_query(self, questions: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Process multiple queries in batch.
        
        Args:
            questions: List of questions to process
            **kwargs: Additional parameters for each query
            
        Returns:
            List of query results
        """
        results = []
        for question in questions:
            result = self.query(question, **kwargs)
            results.append(result)
        return results
    
    def get_similar_documents(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get similar documents without LLM generation.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of similar documents
        """
        return self.vector_manager.search_documents(query, n_results)
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all components."""
        try:
            vector_health = bool(self.vector_manager.collection)
            ollama_health = self.ollama_client.is_available()
            
            return {
                'vector_database': vector_health,
                'ollama_service': ollama_health,
                'overall': vector_health and ollama_health
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'vector_database': False,
                'ollama_service': False,
                'overall': False
            }