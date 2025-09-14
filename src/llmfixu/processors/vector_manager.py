"""
Vector database manager using ChromaDB.
"""

import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid

from ..config.settings import config

logger = logging.getLogger(__name__)


class VectorManager:
    """Manage vector storage and retrieval using ChromaDB."""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """Connect to ChromaDB instance."""
        try:
            # Try to connect to remote ChromaDB first
            try:
                self.client = chromadb.HttpClient(host=config.CHROMADB_URL.split('://')[-1].split(':')[0], 
                                                port=int(config.CHROMADB_URL.split(':')[-1]))
                logger.info(f"Connected to remote ChromaDB at {config.CHROMADB_URL}")
            except Exception:
                # Fallback to persistent local client
                self.client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIRECTORY)
                logger.info(f"Connected to local ChromaDB at {config.CHROMA_PERSIST_DIRECTORY}")
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=config.CHROMA_COLLECTION_NAME,
                metadata={"description": "LLMFixU document collection"}
            )
            logger.info(f"Using collection: {config.CHROMA_COLLECTION_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document dictionaries with content and metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                doc_id = doc.get('id', str(uuid.uuid4()))
                ids.append(doc_id)
                texts.append(doc['content'])
                
                # Prepare metadata (ChromaDB requires all values to be strings, ints, floats, or bools)
                metadata = {}
                for key, value in doc.get('metadata', {}).items():
                    if isinstance(value, (str, int, float, bool)):
                        metadata[key] = value
                    else:
                        metadata[key] = str(value)
                
                metadatas.append(metadata)
            
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(documents)} documents to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector database: {str(e)}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5, 
                        where: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            List of similar documents with scores
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Format results
            documents = []
            for i in range(len(results['ids'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} similar documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            count = self.collection.count()
            return {
                'name': config.CHROMA_COLLECTION_NAME,
                'document_count': count,
                'metadata': self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            # Get all document IDs
            results = self.collection.get()
            if results['ids']:
                self.collection.delete(ids=results['ids'])
            logger.info("Cleared all documents from collection")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False