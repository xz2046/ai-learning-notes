import time
from typing import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import CachePolicy
from langgraph.cache.memory import (
    InMemoryCache,
)  # 是langgraph中的,⽽不是langchain中的。


# 配置状态
class State(TypedDict):
    number: int
    user_id: str


# 配置信息


class ConfigSchema(TypedDict):
    user_id: str


def node_1(state: State, config: RunnableConfig):
    time.sleep(3)
    user_id = config["configurable"]["user_id"]
    return {"number": state["number"] + 1, "user_id": user_id}


builder = StateGraph(State, context_schema=ConfigSchema)
# Node缓存5秒
builder.add_node("node1", node_1, cache_policy=CachePolicy(ttl=5))
builder.add_edge(START, "node1")
builder.add_edge("node1", END)
graph = builder.compile(cache=InMemoryCache())
print(
    graph.invoke(
        {"number": 5},
        config={"configurable": {"user_id": "123"}},
        stream_mode="updates",
    )
)
# [{'node1': {'number': 6, 'user_id': '123'}}]
# node⼊参相同，就会⾛缓存
print(
    graph.invoke(
        {"number": 5},
        config={"configurable": {"user_id": "456"}},
        stream_mode="updates",
    )
)
# [{'node1': {'number': 6, 'user_id': '123'}, '__metadata__': {'cached': True}}]
