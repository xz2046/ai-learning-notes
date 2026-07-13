from typing import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.constants import START, END
from langgraph.graph import StateGraph


# 配置状态
class State(TypedDict):
    number: int


def node_a(state: State, config: RunnableConfig):
    return {"number": state["number"] + 100}

def node_b(state: State, config: RunnableConfig):
    return {"number": state["number"] - 10}


builder = StateGraph(State)
# Node缓存5秒
builder.add_node("node_1", node_a)
builder.add_node("node_2", node_b)


def routing_func(state: State) -> bool:
    if state["number"] > 5:
        return True
    else:
        return False
    
builder.add_edge("node_1", END)
builder.add_conditional_edges(START, routing_func, {True: "node_1", False: "node_2"})

graph = builder.compile()
print(graph.invoke({"number": 7}))
