# 🚀 SmartDoc AI: RAG 智能文档问答系统

**基于 FastAPI、LangChain 和 ChromaDB 的企业级检索增强生成(RAG)平台**

![Version](https://img.shields.io/badge/version-0.9.0--beta-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📢 重要声明

本项目为开源学习版本，仅供学习交流使用。如需商业部署或定制开发，请联系作者获取完整生产版本。

**作者联系方式：**
- 📧 Email: [your-email@example.com]
- 💼 微信: [your-wechat-id]
- 🔗 GitHub: [your-github-username]
- 📱 电话: [+86-xxx-xxxx-xxxx]

---

## ⚠️ 使用须知

此版本为教学演示版本，可能存在以下限制：
- 部分功能需要进一步配置和调试
- 建议在测试环境中使用
- 生产环境部署请联系作者获取技术支持

---

## 💡 项目简介

SmartDoc AI 是一个智能文档问答系统，可以将您的 PDF、TXT 文档转化为可交互的知识库。系统采用先进的 RAG（检索增强生成）技术，确保每个回答都有明确的来源引用，避免 AI 幻觉问题。

### 核心特性

- 🧠 智能文档解析：支持 PDF 和文本文件的语义分块处理
- 🔍 来源可追溯：每个答案都标注具体的文件来源
- ⚡ 异步高性能：基于 FastAPI 的异步架构
- 🧩 多模型支持：支持 OpenAI、Groq、DeepSeek、通义千问等多种 LLM
- 📊 本地向量存储：使用 ChromaDB 进行向量持久化
- 🐳 Docker 部署：一键启动完整服务

---

## 🏗️ 系统架构

```
用户 → Streamlit UI (8501) → FastAPI Backend (8000) → ChromaDB
                                    ↓
                              LLM API (Groq/OpenAI)
                                    ↓
                            本地 Embeddings 模型
```

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Docker & Docker Compose (可选)
- Groq API Key 或 OpenAI API Key

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/[your-username]/smartdoc-ai.git
cd smartdoc-ai/opensource_version

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key

# 3. 使用 Docker 启动（推荐）
docker-compose up -d --build

# 或者本地运行
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
streamlit run frontend/app.py --server.port 8501
```

**访问地址：**
- 前端界面: `http://localhost:8501`
- API 文档: `http://localhost:8000/docs`

---

## 📚 API 文档

### 上传文档
```bash
POST /api/v1/upload
Content-Type: multipart/form-data
```

### 对话问答
```bash
POST /api/v1/chat
{
  "question": "你的问题"
}
```

### 查看文档列表
```bash
GET /api/v1/documents
```

---

## 🛠️ 技术栈

- **后端框架**: FastAPI
- **LLM 集成**: LangChain
- **向量数据库**: ChromaDB
- **嵌入模型**: HuggingFace Sentence Transformers
- **前端**: Streamlit
- **文档解析**: PDFPlumber

---

## 📝 开发计划

- [ ] 支持更多文档格式 (Word, Excel)
- [ ] 添加用户认证系统
- [ ] 优化向量检索算法
- [ ] 支持多语言问答
- [ ] 添加对话历史记录

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 💬 技术支持

如遇到问题或需要技术支持，请通过以下方式联系：

- 📧 Email: [your-email@example.com]
- 💼 微信: [your-wechat-id]
- 🔗 GitHub Issues: [项目 Issues 页面]

**商业合作与定制开发请直接联系作者**

---

*Built with ❤️ by [Your Name] | 专注于企业级 AI 解决方案*
