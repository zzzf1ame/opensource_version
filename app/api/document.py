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
    上传文档并进行向量化处理
    """
    try:
        # 验证文件类型
        if not file.filename.endswith(('.pdf', '.txt')):
            raise HTTPException(status_code=400, detail="仅支持 PDF 和 TXT 文件")
        
        # BUG 2: 这里没有检查文件大小，可能导致大文件上传失败
        # 正确做法: 应该添加文件大小限制检查
        
        # 保存文件
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {file_path}")
        
        # 处理文档并添加到知识库
        chunks_count = await add_document_to_knowledge_base(file_path)
        
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
    获取已上传的文档列表
    """
    try:
        # BUG 3: 这里的实现不完整，只是简单列出文件
        # 实际应该从 ChromaDB 中获取准确的文档信息
        uploaded_files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
        
        # 尝试获取总分块数（这里可能会出错）
        try:
            vectorstore = get_vector_store()
            # BUG 4: 这个方法调用可能不存在，会导致错误
            total_chunks = vectorstore._collection.count()
        except:
            # 出错时返回估算值
            total_chunks = len(uploaded_files) * 10  # 粗略估算
        
        return DocumentListResponse(
            documents=uploaded_files,
            total_chunks=total_chunks
        )
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")
