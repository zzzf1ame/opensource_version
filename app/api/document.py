from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import logging
import os
from pathlib import Path
import shutil

from app.services.rag_service import add_document_to_knowledge_base, get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter()

# 配置上传目录
UPLOAD_DIR = Path("./uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)

class UploadResponse(BaseModel):
    status: str
    message: str
    chunks_processed: int

class DocumentListResponse(BaseModel):
    documents: List[str]
    total_chunks: int

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Basic document upload and vectorization.
    
    Note: Enterprise version includes:
    - File size validation and streaming for large files
    - Virus scanning and content validation
    - Duplicate detection
    - Progress tracking with WebSocket
    """
    try:
        # Basic file type validation
        if not file.filename.endswith(('.pdf', '.txt')):
            raise HTTPException(status_code=400, detail="仅支持 PDF 和 TXT 文件")
        
        # Save file (no size limit check in basic version)
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {file_path}")
        
        # Basic synchronous processing
        chunks_count = add_document_to_knowledge_base(file_path)
        
        return UploadResponse(
            status="success",
            message=f"文件 {file.filename} 处理完成。",
            chunks_processed=chunks_count
        )
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    Basic document listing from file system.
    
    Note: Enterprise version provides:
    - Real-time sync with vector database
    - Document metadata and statistics
    - Search and filtering capabilities
    - Document versioning tracking
    """
    try:
        # Simple file system listing
        uploaded_files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
        
        # Basic chunk count estimation
        try:
            vectorstore = get_vector_store()
            total_chunks = vectorstore._collection.count()
        except:
            total_chunks = len(uploaded_files) * 10
        
        return DocumentListResponse(
            documents=uploaded_files,
            total_chunks=total_chunks
        )
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")
