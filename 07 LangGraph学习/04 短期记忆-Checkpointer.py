import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)


def chatbot(state: MessagesState):
    system_prompt = SystemMessage(content="你是一个简洁、友好的中文助手。")
    messages = [system_prompt] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

app = builder.compile(checkpointer=InMemorySaver())

thread_config = {"configurable": {"thread_id": "chat-demo-001"}}
thread_config2 = {"configurable": {"thread_id": "chat-demo-002"}}

# 第一轮
result = app.invoke(
    {"messages": [HumanMessage(content="我叫李雷，是做前端开发的")]},
    config=thread_config,
)
print("AI:", result["messages"][-1].content)

# 第二轮
result = app.invoke(
    {"messages": [HumanMessage(content="你还记得我的名字和职业吗？")]},
    config=thread_config2, #测试更换thread_id 效果
)
print("AI:", result["messages"][-1].content)