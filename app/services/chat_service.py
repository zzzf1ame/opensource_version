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
# Prompt Engineering
# ==========================================
SYSTEM_PROMPT = """你是一个专业的企业级智能知识库问答助手，名为 "SmartDoc AI"。
请严格遵守以下指令来回答用户的问题：

1. **绝对忠实于上下文**：你必须【仅仅】基于我提供给你的<context>（上下文文本片段）来回答问题。
2. **禁止胡编乱造**：如果你在提供的<context>中找不到答案，请明确回答："我不知道，当前知识库中没有包含相关信息。"
3. **来源标注强制要求**：你在回答中只要引用了上下文的内容，必须在该句最后精确标注来源文件名。
   - 格式要求：^[文件名]
   - 示例："该产品的保修期为三年 ^[保修手册.pdf]。"
4. **语言要求**：使用清晰、专业、有条理的中文进行回答。如果需要，使用 Markdown （加粗、列表）来优化排版格式。

<context>
{context}
</context>
"""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])

async def generate_answer(question: str) -> Dict[str, Any]:
    """
    Core RAG chain execution.
    1. Retrieve relevant contexts
    2. Format contexts and map sources 
    3. Generate LLM response
    4. Compile final response package with citations
    """
    try:
        # BUG 5: 这里的 k 值固定为 4，没有根据问题复杂度动态调整
        # 可能导致简单问题检索过多，复杂问题检索不足
        retrieved_docs = await query_knowledge_base(question, k=4)
        
        # BUG 6: 如果检索结果为空，这里没有提前返回友好提示
        # 会继续执行导致生成无意义的回答
        
        context_parts = []
        sources = []
        
        for i, doc in enumerate(retrieved_docs):
            source_name = doc["metadata"].get("source", f"Unknown_Source_{i}")
            file_name = os.path.basename(source_name) 
            
            content_block = f"[来源: {file_name}]\n{doc['content']}"
            context_parts.append(content_block)
            
            sources.append({
                "file": file_name,
                "content": doc["content"]
            })
            
        compiled_context = "\n\n---\n\n".join(context_parts)
        
        # 构造并调用 LLM
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
