import streamlit as st
import time
from rag import RagServer
import config_data
import os

os.chdir(os.path.dirname(__file__))

st.title("业务运维助手")
st.divider()

if "rag" not in st.session_state:
    st.session_state["rag"] = RagServer()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if len(st.session_state["messages"]) == 0:
    st.chat_message("assistant").write("你好，有什么可以帮助您？")

assistant_res_list = []
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    with st.spinner("思考中..."):
        res_stream = st.session_state["rag"].chain.invoke({"input":prompt},config_data.session_config)

        def capture(generator,cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(res_stream,assistant_res_list))
        st.session_state["messages"].append({"role": "assistant", "content": "".join(assistant_res_list)})

