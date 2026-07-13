from typing import Annotated

from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
import os
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com",
)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# 第一个参数是唯一的节点名称 
# 第二个参数是任何时候都将被调用的函数或对象
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        user_input = "你知道LangGraph吗?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break