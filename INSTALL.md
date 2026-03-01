# 安装指南 (Installation Guide)

## 📋 系统要求

- Python 3.10 或更高版本
- Docker & Docker Compose (可选，推荐)
- 至少 4GB 可用内存
- 至少 2GB 可用磁盘空间

## 🚀 方式一：Docker 部署（推荐）

### 1. 克隆项目

```bash
git clone https://github.com/[your-username]/smartdoc-ai.git
cd smartdoc-ai/opensource_version
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的 API Key：

```env
# 选择 LLM 提供商
LLM_PROVIDER=groq

# 填入对应的 API Key
GROQ_API_KEY=your_actual_groq_api_key_here

# 或者使用 OpenAI
# LLM_PROVIDER=openai
# LLM_API_KEY=your_openai_api_key_here

# 模型名称
MODEL_NAME=llama3-70b-8192
```

### 3. 启动服务

```bash
docker-compose up -d --build
```

### 4. 访问应用

- 前端界面: http://localhost:8501
- API 文档: http://localhost:8000/docs

### 5. 停止服务

```bash
docker-compose down
```

## 🔧 方式二：本地开发部署

### 1. 克隆项目

```bash
git clone https://github.com/[your-username]/smartdoc-ai.git
cd smartdoc-ai/opensource_version
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
cd frontend
pip install -r requirements.txt
cd ..
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的 API Key
```

### 5. 启动后端服务

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. 启动前端服务（新终端）

```bash
cd frontend
streamlit run app.py --server.port 8501
```

### 7. 访问应用

- 前端界面: http://localhost:8501
- API 文档: http://localhost:8000/docs

## 🔑 获取 API Key

### Groq (推荐，免费)

1. 访问 https://console.groq.com
2. 注册账号
3. 在 API Keys 页面创建新的 API Key
4. 复制 Key 到 `.env` 文件

### OpenAI

1. 访问 https://platform.openai.com
2. 注册账号并充值
3. 在 API Keys 页面创建新的 API Key
4. 复制 Key 到 `.env` 文件

## ⚠️ 常见问题

### 问题 1: 端口被占用

如果 8000 或 8501 端口被占用，可以修改 `docker-compose.yml` 或启动命令中的端口号。

### 问题 2: 内存不足

如果遇到内存不足，可以：
- 减少上传文档的大小
- 调整 chunk_size 参数
- 增加系统内存

### 问题 3: API Key 无效

请确保：
- API Key 正确复制，没有多余空格
- API Key 有足够的配额
- 网络可以访问对应的 API 服务

### 问题 4: 文档上传失败

本开源版本存在一些已知问题（详见 BUGS.md），可能导致：
- 大文件上传失败
- 某些格式的 PDF 解析错误
- 向量化处理超时

## 💡 获取技术支持

如果您在安装或使用过程中遇到问题，或需要：
- 完整的生产级版本
- 企业级技术支持
- 定制开发服务

请联系作者：
- 📧 Email: [your-email@example.com]
- 💼 微信: [your-wechat-id]
- 🔗 GitHub: [your-github-username]

---

祝您使用愉快！🎉
