"""
Agent 工具包 — 所有工具在此统一导出
"""
from agent.tools.node_detail import node_detail_query
from agent.tools.node_traffic import node_traffic_query
from agent.tools.node_status import node_status_query
from agent.tools.node_cmd import node_cmd_execute
from agent.tools.rag_tool import rag_summarize
from langchain_core.tools import tool


@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"


def get_all_tools():
    """返回所有工具列表，供 Agent 注册使用"""
    return [
        node_detail_query,
        node_traffic_query,
        node_status_query,
        node_cmd_execute,
        rag_summarize,
        fill_context_for_report,
    ]


__all__ = [
    "node_detail_query",
    "node_traffic_query",
    "node_status_query",
    "node_cmd_execute",
    "rag_summarize",
    "fill_context_for_report",
    "get_all_tools",
]
