from langchain_openai import ChatOpenAI
import os

# 构建阿⾥云百炼⼤模型客户端
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import InMemorySaver


def call_model(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": response}


builder = StateGraph(MessagesState)
builder.add_node(call_model)
builder.add_edge(START, "call_model")
graph = builder.compile()
for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "陕西的省会是哪⾥？"}]},
    stream_mode="updates",
):
    print(chunk)

'''
- `values`：每一步后的完整 state
- `updates`：每一步返回的更新片段
- `messages`：LLM token / 元信息
- `custom`：节点手动写入的调试数据
- `debug`：更全的执行细节
'''