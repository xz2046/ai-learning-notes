from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage
import os

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com",
    temperature=0.7,
    streaming=True,
)

messages = [
    SystemMessage(content="你是一个简洁专业的助手"),
    HumanMessage(content="解释一下向量数据库的作用"),
    AIMessage(content="向量数据库是一种专门用于存储和查询高维向量数据的数据库。"),
    HumanMessage(content="解释一下RAG是什么"),
]

#简写，角色包含：system, human, ai
messages_jx = [("system", "你是一个简洁专业的助手"),
               ("human", "解释一下向量数据库的作用"),
               ("ai", "向量数据库是一种专门用于存储和查询高维向量数据的数据库。"),
               ("human", "解释一下RAG是什么")]

for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
