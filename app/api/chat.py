from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from app.services.chat_service import generate_answer

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

class SourceInfo(BaseModel):
    file: str
    content: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    RAG 对话接口：基于知识库回答用户问题
    """
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        # BUG 1: 这里少了对超长问题的处理，可能导致性能问题
        # 正确的做法应该是: if len(request.question) > 500: raise HTTPException(...)
        
        logger.info(f"Received chat request: {request.question}")
        result = await generate_answer(request.question)
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")
