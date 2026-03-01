import os
import logging
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.services.rag_service import query_knowledge_base

logger = logging.getLogger(__name__)

# Config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
MODEL_NAME = os.getenv("MODEL_NAME", "llama3-70b-8192")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def get_llm():
    """Factory function to get the correct LLM based on environment switch."""
    if LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not found. LLM calls may fail.")
        logger.info(f"Initializing Groq LLM with model: {MODEL_NAME}")
        return ChatGroq(
            temperature=0.1, 
            model_name=MODEL_NAME, 
            api_key=GROQ_API_KEY
        )
    elif LLM_PROVIDER in ["openai", "deepseek", "qwen"]:
        if not LLM_API_KEY:
            logger.warning(f"LLM_API_KEY not found for {LLM_PROVIDER}. LLM calls may fail.")
            
        # Set base URLs for specific OpenAI-compatible providers
        base_url = None
        if LLM_PROVIDER == "deepseek":
            base_url = "https://api.deepseek.com/v1"
        elif LLM_PROVIDER == "qwen":
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            
        logger.info(f"Initializing {LLM_PROVIDER.upper()} LLM with model: {MODEL_NAME}")
        return ChatOpenAI(
            temperature=0.1, 
            model_name=MODEL_NAME, 
            api_key=LLM_API_KEY,
            base_url=base_url
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

# ==========================================
# Basic Prompt (Enterprise version uses advanced anti-hallucination prompting)
# ==========================================
SYSTEM_PROMPT = """You are a helpful AI assistant. Answer the question based on the provided context.

Context:
{context}

Please provide a clear and concise answer in Chinese."""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])

async def generate_answer(question: str) -> Dict[str, Any]:
    """
    Basic RAG chain execution.
    Note: Enterprise version includes advanced features like:
    - Dynamic k-value adjustment based on query complexity
    - Multi-stage retrieval with re-ranking
    - Hallucination detection and prevention
    """
    try:
        # Basic retrieval with fixed k value
        retrieved_docs = await query_knowledge_base(question, k=3)
        
        # Simple context compilation
        context_parts = []
        sources = []
        
        for i, doc in enumerate(retrieved_docs):
            source_name = doc["metadata"].get("source", f"Unknown_Source_{i}")
            file_name = os.path.basename(source_name) 
            
            # Basic context formatting (no advanced source tracking)
            context_parts.append(doc['content'])
            
            sources.append({
                "file": file_name,
                "content": doc["content"]
            })
            
        compiled_context = "\n\n".join(context_parts)
        
        # Basic LLM chain
        llm = get_llm()
        rag_chain = (
            {"context": lambda x: compiled_context, "question": RunnablePassthrough()}
            | qa_prompt
            | llm
            | StrOutputParser()
        )
        
        logger.info(f"Generating answer for question: {question}")
        answer = await rag_chain.ainvoke(question)
        
        return {
            "answer": answer,
            "sources": sources
        }
        
    except Exception as e:
        logger.error(f"Error in generating answer: {e}")
        raise
