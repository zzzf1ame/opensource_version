import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import asyncio

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

async def process_document(file_path: str | Path) -> List[Document]:
    """
    Load a document (PDF or TXT), split it into chunks, and return the chunks.
    """
    file_path_str = str(file_path)
    
    def _load_and_split() -> List[Document]:
        # Document Loader
        if file_path_str.lower().endswith(".pdf"):
            loader = PDFPlumberLoader(file_path_str)
        elif file_path_str.lower().endswith(".txt"):
            loader = TextLoader(file_path_str, encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_path_str}")
            
        documents = loader.load()
        
        # BUG 7: 这里的分块参数可能不是最优的
        # chunk_size 和 chunk_overlap 应该根据文档类型动态调整
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        
        # BUG 8: 没有对空文档或分块失败的情况做处理
        # 如果 chunks 为空，应该抛出异常或警告
        
        return chunks

    try:
        chunks = await asyncio.to_thread(_load_and_split)
        logger.info(f"Processed {file_path_str}: generated {len(chunks)} chunk(s).")
        return chunks
    except Exception as e:
        logger.error(f"Error processing document {file_path_str}: {e}")
        raise

async def add_document_to_knowledge_base(file_path: str | Path) -> int:
    """
    Process a document and add its embeddings to the ChromaDB vector store.
    """
    try:
        chunks = await process_document(file_path)
        if not chunks:
            logger.warning(f"No text chunks extracted from {file_path}")
            return 0
            
        def _add_to_chroma():
            vectorstore = get_vector_store()
            vectorstore.add_documents(chunks)
            # BUG 9: persist() 方法在新版本的 Chroma 中可能已经废弃
            # 这里应该检查版本或使用新的持久化方法
            if hasattr(vectorstore, 'persist'):
                vectorstore.persist()
                
        await asyncio.to_thread(_add_to_chroma)
        
        logger.info(f"Successfully added {len(chunks)} chunks to ChromaDB from {file_path}")
        return len(chunks)
    except Exception as e:
        logger.error(f"Failed to add document to knowledge base: {e}")
        raise

async def query_knowledge_base(question: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Query the vector store for the most relevant document chunks.
    """
    logger.info(f"Querying knowledge base for: '{question}' with k={k}")
    try:
        vectorstore = get_vector_store()
        
        # BUG 10: 这里直接使用 similarity_search，没有考虑使用 MMR 等更好的检索策略
        # 可能导致检索结果重复度高
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
