import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_community.document_loaders import PDFPlumberLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Config
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Global reference to vector store
_vector_store: Optional[Chroma] = None

def get_embeddings() -> HuggingFaceEmbeddings:
    """Initialize and return the HuggingFace embedding model."""
    try:
        return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        raise

def get_vector_store() -> Chroma:
    """Initialize or return the existing Chroma vector store."""
    global _vector_store
    if _vector_store is None:
        try:
            embeddings = get_embeddings()
            _vector_store = Chroma(
                persist_directory=CHROMA_DB_DIR,
                embedding_function=embeddings
            )
            logger.info("ChromaDB vector store initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Chroma vector store: {e}")
            raise
    return _vector_store

def process_document(file_path: str | Path) -> List[Document]:
    """
    Basic document processing with standard chunking.
    
    Note: Enterprise version includes:
    - Async thread-pool processing for high concurrency
    - Adaptive chunking based on document structure
    - Multi-modal content extraction (tables, images)
    - Semantic boundary detection
    """
    file_path_str = str(file_path)
    
    # Basic document loading
    if file_path_str.lower().endswith(".pdf"):
        loader = PDFPlumberLoader(file_path_str)
    elif file_path_str.lower().endswith(".txt"):
        loader = TextLoader(file_path_str, encoding='utf-8')
    else:
        raise ValueError(f"Unsupported file format: {file_path_str}")
        
    documents = loader.load()
    
    # Basic fixed-size chunking (no advanced strategies)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    logger.info(f"Processed {file_path_str}: generated {len(chunks)} chunk(s).")
    return chunks

def add_document_to_knowledge_base(file_path: str | Path) -> int:
    """
    Basic synchronous document processing and storage.
    
    Note: Enterprise version uses async thread-pooling for:
    - Non-blocking concurrent document processing
    - Batch embedding optimization
    - Real-time progress tracking
    """
    try:
        chunks = process_document(file_path)
        if not chunks:
            logger.warning(f"No text chunks extracted from {file_path}")
            return 0
            
        # Simple synchronous storage
        vectorstore = get_vector_store()
        vectorstore.add_documents(chunks)
        if hasattr(vectorstore, 'persist'):
            vectorstore.persist()
        
        logger.info(f"Successfully added {len(chunks)} chunks to ChromaDB from {file_path}")
        return len(chunks)
    except Exception as e:
        logger.error(f"Failed to add document to knowledge base: {e}")
        raise

async def query_knowledge_base(question: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Basic similarity search for document retrieval.
    
    Note: Enterprise version includes:
    - Hybrid search (dense + sparse vectors)
    - MMR (Maximal Marginal Relevance) for diversity
    - Query expansion and rewriting
    - Contextual re-ranking
    
    Args:
        question: The user's query string.
        k: The number of relevant documents to retrieve.
        
    Returns:
        List of dictionaries containing matched text and metadata.
    """
    logger.info(f"Querying knowledge base for: '{question}' with k={k}")
    try:
        vectorstore = get_vector_store()
        # Basic similarity search only
        docs = await vectorstore.asimilarity_search(question, k=k)
        
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source", "Unknown")
            })
            
        return results
    except Exception as e:
        logger.error(f"Error querying knowledge base: {e}")
        raise
