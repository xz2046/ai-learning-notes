import os
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

# 用 dict 模拟长期记忆库
long_term_memory_store = {
    "user_001": {
        "name": "小王",
        "profession": "Python工程师",
        "preference": "喜欢简洁直接的回答",
    }
}


class InputState(TypedDict):
    messages: list
    user_id: str


def load_memory_and_reply(state: InputState):
    user_id = state["user_id"]
    memory = long_term_memory_store.get(user_id, {})

    memory_text = "\n".join([
        f"用户姓名：{memory.get('name', '未知')}",
        f"用户职业：{memory.get('profession', '未知')}",
        f"回答偏好：{memory.get('preference', '未知')}",
    ])

    system_prompt = SystemMessage(
        content=(
            "你是一个中文助手。以下是用户的长期记忆，请优先利用这些信息回答。\n"
            + memory_text
        )
    )

    response = llm.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}


builder = StateGraph(InputState)
builder.add_node("load_memory_and_reply", load_memory_and_reply)
builder.add_edge(START, "load_memory_and_reply")
builder.add_edge("load_memory_and_reply", END)

app = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "session-1001"}}

result = app.invoke(
    {
        "user_id": "user_001",
        "messages": [HumanMessage(content="请根据我的背景，推荐一个适合我的 LangGraph 学习路径")],
    },
    config=config,
)

print(result["messages"][-1].content)