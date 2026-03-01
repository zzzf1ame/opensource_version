import streamlit as st
import requests
import os

# ==========================================
# 0. UI 及配置
# ==========================================
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_PREFIX = f"{BACKEND_URL}/api/v1"

st.set_page_config(page_title="SmartDoc AI", page_icon="📚", layout="wide")

# 初始化 Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "您好！我是 SmartDoc AI 助手（开源学习版）。\n\n⚠️ 本版本仅供学习交流使用。\n\n您可以先在左侧上传 PDF 或 TXT 文档，然后向我提问。\n\n如需商业部署或技术支持，请联系：[your-email@example.com]"
        }
    ]

# ==========================================
# 1. 侧边栏：文件管理区
# ==========================================
with st.sidebar:
    st.title("📚 SmartDoc AI")
    st.caption("开源学习版 v0.9.0-beta")
    st.caption("后端 API: " + BACKEND_URL)
    
    st.divider()
    
    # 添加联系方式
    with st.expander("📞 联系作者"):
        st.markdown("""
        **商业合作与技术支持：**
        - 📧 Email: [your-email@example.com]
        - 💼 微信: [your-wechat-id]
        - 🔗 GitHub: [your-github-username]
        """)
    
    st.divider()
    
    st.header("🗂️ 知识库管理")
    uploaded_file = st.file_uploader("上传文档 (仅限 PDF/TXT)", type=["pdf", "txt"], accept_multiple_files=False)
    
    if st.button("🚀 提交并向量化", type="primary"):
        if uploaded_file is not None:
            with st.spinner(f"正在处理 {uploaded_file.name} 中..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_PREFIX}/upload", files=files, timeout=60)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"上传成功！生成了 {data.get('chunks_processed', 0)} 个向量分块。")
                        st.rerun()
                    else:
                        st.error(f"处理失败: {response.json().get('detail', '未知错误')}")
                except requests.exceptions.Timeout:
                    st.error("上传超时，请重试。")
                except Exception as e:
                    st.error(f"系统报错: {e}")
        else:
            st.warning("请先拖拽或选择一个文件。")
            
    st.divider()
    
    # 动态加载并展示已有文档列表
    st.header("📄 已有知识源")
    try:
        list_resp = requests.get(f"{API_PREFIX}/documents", timeout=5)
        if list_resp.status_code == 200:
            doc_data = list_resp.json()
            docs = doc_data.get("documents", [])
            total_chunks = doc_data.get("total_chunks", 0)
            
            if docs:
                for doc in docs:
                    st.markdown(f"- 📎 `{doc}`")
                st.caption(f"总计向量分片数: **{total_chunks}** 块")
            else:
                st.info("当前知识库为空。")
        else:
            st.error("获取文档列表失败")
    except Exception as e:
        st.warning("无法连接到后端获取文档列表。")


# ==========================================
# 2. 主页面：聊天交互区
# ==========================================
st.title("💬 RAG 对话窗口")
st.caption("⚠️ 开源学习版 - 仅供测试使用")

# 呈现历史对话消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # 在 Assistant 回复中渲染附带的引用的源
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("🔍 展开查看引用来源内容"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f"**[{idx+1}] 来自: `{src.get('file', 'Unknown')}`**")
                    st.caption(f"> {src.get('content', '')}")

# 捕获用户输入
if question := st.chat_input("请输入您想检索询问的问题..."):
    # BUG 11: 这里没有对用户输入做任何验证或清理
    # 可能存在注入风险或导致后端错误
    
    # 1. 屏幕增加 User 消息
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # 2. 请求后端生成回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("AI 正在深度检索知识库并在思考中..."):
            try:
                chat_resp = requests.post(
                    f"{API_PREFIX}/chat", 
                    json={"question": question},
                    timeout=50
                )
                
                if chat_resp.status_code == 200:
                    resp_json = chat_resp.json()
                    answer_text = resp_json.get("answer", "")
                    sources = resp_json.get("sources", [])
                    
                    # 渲染助手答案
                    message_placeholder.markdown(answer_text)
                    
                    # 渲染源折叠面板
                    if sources:
                        with st.expander("🔍 展开查看引用来源内容"):
                            for idx, src in enumerate(sources):
                                st.markdown(f"**[{idx+1}] 来自: `{src.get('file', 'Unknown')}`**")
                                st.caption(f"> {src.get('content', '')}")
                                
                    # 记录进 state
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer_text,
                        "sources": sources
                    })
                else:
                    error_msg = f"后端请求出错 (Status {chat_resp.status_code}): {chat_resp.text}"
                    message_placeholder.error(error_msg)
            except Exception as e:
                message_placeholder.error(f"服务器异常，请检查后端状态: {str(e)}")

# 页脚
st.divider()
st.caption("💡 提示：本系统为开源学习版本，如需商业部署请联系作者获取完整版本")
st.caption("📧 联系方式: [your-email@example.com] | 💼 微信: [your-wechat-id]")
