"""
基于streamlit完成web页面上传服务
"""

import time
import streamlit as st
from knowledge_base import KnowledgeBaseService
import os

os.chdir(os.path.dirname(__file__))

# 添加网页标题
st.title("知识库更新服务")

# file_uploader
uploader_file = st.file_uploader(
    label="请上传文件，支持：txt、markdown、pdf",
    type=["txt", "md"],
    accept_multiple_files=False,
)

if "counter" not in st.session_state:
    st.session_state["counter"] = 0

if "server" not in st.session_state:
    st.session_state["server"] = KnowledgeBaseService()

if uploader_file is not None:
    # 提前文件名
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = round(uploader_file.size / 1024, 2)
    st.subheader(f"{file_name}文件上传成功")
    st.write(f"上传文件格式为{file_type};文件大小为{file_size}kb")
    

    text = uploader_file.getvalue().decode("utf-8")
    with st.spinner("载入知识库中 。。。"):
        time.sleep(1)
        result = st.session_state["server"].upload_by_str(text, file_name)
        st.write(result)
        
        if "成功" in result:
            st.session_state["counter"] += 1
            st.write(f"恭喜你！！！成功上传了{st.session_state['counter']}个文件")
