"""
RAG知识检索工具 — 从向量知识库检索设备诊断相关专业知识
"""
from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService
from utils.logger_handler import logger


rag_service = RagSummarizeService()


@tool(description="从知识库检索设备诊断相关专业知识，返回基于参考资料的精准解答")
def rag_summarize(query: str) -> str:
    """
    RAG知识检索工具

    入参：
        query (str) — 检索关键词，贴合用户问题的核心检索词

    返回：
        str — 基于向量库检索到的参考资料生成的精准解答
    """
    logger.info(f"[rag_summarize] 检索关键词: {query}")
    try:
        result = rag_service.rag_summarize(query)
        return result
    except Exception as e:
        logger.error(f"[rag_summarize] 检索失败: {e}")
        return f"知识检索失败: {e}"


# if __name__ == "__main__":
#     import sys, os
#     _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     sys.path.insert(0, _root)
#     for k in list(sys.modules.keys()):
#         if k.startswith(("agent", "rag")):
#             del sys.modules[k]
#     from agent.tools.rag_tool import rag_summarize
#     r = rag_summarize.func(query="设备常见问题")
#     print(r)
