from operator import add
from typing import TypedDict, Annotated
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from langgraph.types import Command


# 配置状态
class State(TypedDict):
    messages: Annotated[list[str], add]


def node_1(state: State):
    new_message = []
    for message in state["messages"]:
        new_message.append(message + "!")
    return Command(goto=END, update={"messages": new_message})


builder = StateGraph(State)
builder.add_node("node1", node_1)
# node1中通过Command同时集成了更新State和指定下个Node
builder.add_edge(START, "node1")
graph = builder.compile()
print(graph.invoke({"messages": ["hello", "world", "hello", "graph"]}))
# {'messages': ['hello', 'world', 'hello', 'graph', 'hello!', 'world!', 'hello!','graph!']}
