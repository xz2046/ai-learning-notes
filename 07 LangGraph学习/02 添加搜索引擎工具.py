
import os
from typing import Annotated

from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


os.environ["TAVILY_API_KEY"] = "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"


# 1. 定义工具
tool = TavilySearch(max_results=2)
tools = [tool]

# 2. 定义状态
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 3. 创建图
graph_builder = StateGraph(State)

# 4. 初始化模型
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

# 5. 绑定工具
llm_with_tools = llm.bind_tools(tools)

# 6. 聊天节点
def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 7. 工具节点
tool_node = ToolNode(tools=tools)

# 8. 注册节点
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# 9. 添加边
graph_builder.add_edge(START, "chatbot")

# 如果模型回复里包含 tool_calls，就走 tools；否则结束
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END,
    },
)

# 工具执行后，再回到 chatbot，让模型基于工具结果继续回答
graph_builder.add_edge("tools", "chatbot")

# 10. 编译图
graph = graph_builder.compile()

# 11. 调用示例
result = graph.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "LangGraph 中节点的定义是什么？请先搜索再回答。",
            }
        ]
    }
)

# 12. 输出最终消息
for msg in result["messages"]:
    print(msg)
