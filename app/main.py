from dotenv import load_dotenv
load_dotenv()  # Load .env BEFORE any other imports that read os.getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# ==========================================
# 1. 基础配置与 Logging Setting
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 2. 初始化 FastAPI 应用实例
# ==========================================
app = FastAPI(
    title="SmartDoc AI",
    description="企业级 RAG 知识库问答系统后端 API",
    version="0.9.0-beta"  # 开源版本号
)

# ==========================================
# 3. 配置 CORS
# ==========================================
origins = [
    "http://localhost",
    "http://localhost:8501", # Streamlit 默认端口
    "*"  # 生产环境中建议缩小来源边界
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 4. 数据模型 / Schema
# ==========================================
class HealthCheckResponse(BaseModel):
    status: str
    message: str

# ==========================================
# 5. 路由端点 / Routes
# ==========================================
@app.get("/health", response_model=HealthCheckResponse, tags=["系统监控"])
async def health_check():
    """
    基础健康检查接口，确保后端服务正常运行。
    """
    logger.info("Health check endpoint called.")
    return HealthCheckResponse(status="ok", message="SmartDoc AI Backend is running.")

from app.api.chat import router as chat_router
from app.api.document import router as document_router

@app.get("/", tags=["系统监控"])
async def root():
    return {
        "message": "Welcome to SmartDoc AI - Open Source Edition!",
        "version": "0.9.0-beta",
        "contact": "For commercial support, contact: [your-email@example.com]"
    }

# Register Routers
app.include_router(chat_router, prefix="/api/v1", tags=["RAG 对话"])
app.include_router(document_router, prefix="/api/v1", tags=["文档管理"])
