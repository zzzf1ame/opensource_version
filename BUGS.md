# 已知问题列表 (Known Issues)

本文档记录了开源学习版本中的已知问题。这些问题在完整商业版本中已经修复。

## 🐛 后端问题

### 1. 缺少问题长度验证 (chat.py)
- **位置**: `app/api/chat.py`
- **描述**: 没有对用户输入的问题长度进行限制
- **影响**: 超长问题可能导致性能问题或 API 调用失败
- **修复建议**: 添加最大长度检查（建议 500 字符）

### 2. 文件大小未限制 (document.py)
- **位置**: `app/api/document.py`
- **描述**: 上传文件时没有检查文件大小
- **影响**: 大文件可能导致内存溢出或处理超时
- **修复建议**: 添加文件大小限制（建议 10MB）

### 3. 文档列表实现不完整 (document.py)
- **位置**: `app/api/document.py` - `list_documents()`
- **描述**: 只是简单列出文件系统中的文件，没有从 ChromaDB 获取准确信息
- **影响**: 显示的文档列表可能与实际向量库不一致
- **修复建议**: 从 ChromaDB 元数据中获取文档列表

### 4. ChromaDB 计数方法错误 (document.py)
- **位置**: `app/api/document.py` - `list_documents()`
- **描述**: 使用的 `_collection.count()` 方法可能不存在
- **影响**: 获取总分块数时可能抛出异常
- **修复建议**: 使用正确的 ChromaDB API 方法

### 5. 检索数量固定 (chat_service.py)
- **位置**: `app/services/chat_service.py` - `generate_answer()`
- **描述**: k 值固定为 4，没有根据问题复杂度动态调整
- **影响**: 简单问题检索过多，复杂问题检索不足
- **修复建议**: 根据问题长度和复杂度动态调整 k 值

### 6. 空检索结果未处理 (chat_service.py)
- **位置**: `app/services/chat_service.py` - `generate_answer()`
- **描述**: 检索结果为空时没有提前返回友好提示
- **影响**: 可能生成无意义的回答
- **修复建议**: 检查检索结果，为空时返回友好提示

### 7. 分块参数未优化 (rag_service.py)
- **位置**: `app/services/rag_service.py` - `process_document()`
- **描述**: chunk_size 和 chunk_overlap 固定，没有根据文档类型调整
- **影响**: 某些文档类型的分块效果不佳
- **修复建议**: 根据文档类型和内容特征动态调整参数

### 8. 空文档未处理 (rag_service.py)
- **位置**: `app/services/rag_service.py` - `process_document()`
- **描述**: 没有对空文档或分块失败的情况做处理
- **影响**: 可能导致静默失败
- **修复建议**: 添加空文档检查和异常处理

### 9. 持久化方法可能废弃 (rag_service.py)
- **位置**: `app/services/rag_service.py` - `add_document_to_knowledge_base()`
- **描述**: `persist()` 方法在新版本 Chroma 中可能已废弃
- **影响**: 可能导致数据持久化失败
- **修复建议**: 检查 ChromaDB 版本并使用正确的持久化方法

### 10. 检索策略单一 (rag_service.py)
- **位置**: `app/services/rag_service.py` - `query_knowledge_base()`
- **描述**: 只使用简单的 similarity_search，没有使用 MMR 等高级策略
- **影响**: 检索结果可能重复度高，多样性不足
- **修复建议**: 实现 MMR 或混合检索策略

## 🎨 前端问题

### 11. 用户输入未验证 (frontend/app.py)
- **位置**: `frontend/app.py` - 聊天输入处理
- **描述**: 没有对用户输入做任何验证或清理
- **影响**: 可能存在注入风险或导致后端错误
- **修复建议**: 添加输入验证和清理逻辑

## 💡 获取修复版本

以上问题在完整商业版本中均已修复，并包含更多企业级特性：
- 完整的错误处理和日志系统
- 性能优化和缓存机制
- 用户认证和权限管理
- 更多文档格式支持
- 生产级部署配置

如需获取完整版本或技术支持，请联系：
- 📧 Email: [your-email@example.com]
- 💼 微信: [your-wechat-id]
- 🔗 GitHub: [your-github-username]
