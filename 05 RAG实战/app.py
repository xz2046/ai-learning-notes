"""合并入口：通过侧边栏在「对话」和「知识库」页面之间切换。"""

import os
import time
import streamlit as st

os.chdir(os.path.dirname(__file__))

from rag import RagServer
from knowledge_base import KnowledgeBaseService
import config_data


st.title("业务运维助手")
st.divider()

# -----------------------------------------------------------
# 侧边栏导航（不嵌套 chat_input，保持页面根层级定位）
# -----------------------------------------------------------
page = st.sidebar.radio("导航", ["💬 对话", "📂 知识库"])


# ============================================================
# 页面 1：对话
# ============================================================
if page == "💬 对话":

    if "rag" not in st.session_state:
        st.session_state["rag"] = RagServer()
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # 渲染历史消息
    for message in st.session_state["messages"]:
        st.chat_message(message["role"]).write(message["content"])

    # chat_input 在页面根层级，Streamlit 自动将其固定在底部
    prompt = st.chat_input()

    # 首次进入时显示欢迎语
    if len(st.session_state["messages"]) == 0:
        st.chat_message("assistant").write("你好，有什么可以帮助您？")

    if prompt:
        st.chat_message("user").write(prompt)
        st.session_state["messages"].append({"role": "user", "content": prompt})

        with st.spinner("思考中..."):
            res_stream = st.session_state["rag"].chain.invoke(
                {"input": prompt}, config_data.session_config
            )

            assistant_res_list = []

            def capture(generator, cache_list):
                for chunk in generator:
                    cache_list.append(chunk)
                    yield chunk

            st.chat_message("assistant").write_stream(
                capture(res_stream, assistant_res_list)
            )
            st.session_state["messages"].append(
                {"role": "assistant", "content": "".join(assistant_res_list)}
            )


# ============================================================
# 页面 2：知识库
# ============================================================
if page == "📂 知识库":

    if "server" not in st.session_state:
        st.session_state["server"] = KnowledgeBaseService()

    uploader_file = st.file_uploader(
        label="请上传文件，支持：txt、markdown",
        type=["txt", "md"],
        accept_multiple_files=False,
    )

    if "counter" not in st.session_state:
        st.session_state["counter"] = 0

    if uploader_file is not None:
        file_name = uploader_file.name
        file_type = uploader_file.type
        file_size = round(uploader_file.size / 1024, 2)
        st.subheader(f"{file_name} 文件上传成功")
        st.write(f"上传文件格式为 {file_type}；文件大小为 {file_size} KB")

        text = uploader_file.getvalue().decode("utf-8")
        with st.spinner("载入知识库中 ..."):
            time.sleep(1)
            result = st.session_state["server"].upload_by_str(text, file_name)
            st.write(result)

            if "成功" in result:
                st.session_state["counter"] += 1
                st.write(f"已成功上传 {st.session_state['counter']} 个文件")

    st.divider()
    st.subheader("已上传的文件")

    files = st.session_state["server"].get_file_list()
    if files:
        data = {
            "文件名": [f["filename"] for f in files],
            "上传时间": [f["datetime"] for f in files],
            "操作人": [f["operator"] for f in files],
            "切分段数": [f["chunks"] for f in files],
        }
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("知识库中暂无文件，请上传。")
