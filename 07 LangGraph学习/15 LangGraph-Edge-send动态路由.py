from typing import TypedDict, Annotated
import operator
 
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
 
 
class MapState(TypedDict):
    numbers: list[int]
    results: Annotated[list[int], operator.add]
    total: int
 
 
def dispatcher(state: MapState):
    return [Send("square_node", {"number": n}) for n in state["numbers"]]
 
 
class WorkerState(TypedDict):
    number: int
    results: Annotated[list[int], operator.add]
 
 
def square_node(state: WorkerState):
    n = state["number"]
    return {"results": [n * n]}
 
 
def reduce_node(state: MapState):
    return {"total": sum(state["results"])}
 
 
builder = StateGraph(MapState)
 
builder.add_node("square_node", square_node)
builder.add_node("reduce_node", reduce_node)
 
builder.add_conditional_edges(START, dispatcher, ["square_node"])
builder.add_edge("square_node", "reduce_node")
builder.add_edge("reduce_node", END)
 
app = builder.compile()
 
result = app.invoke(
    {
        "numbers": [1, 2, 3, 4],
        "results": [],
        "total": 0,
    }
)
 
print(result)
# 预期：
# {
#   'numbers': [1, 2, 3, 4],
#   'results': [1, 4, 9, 16],
#   'total': 30
# }
 