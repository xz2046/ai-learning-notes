from langchain_community.embeddings import DashScopeEmbeddings
import os
os.environ["DashScope_API_KEY"] = "sk-*****************************"
# 初始化阿里嵌入模型（v4 最新）
embeddings = DashScopeEmbeddings(
    model="text-embedding-v4"
)

# 1. 单文本向量化
query = "LangChain如何接入阿里嵌入模型？"
query_vec = embeddings.embed_query(query)
print(f"向量维度: {len(query_vec)}")
print(f"前5维: {query_vec[:5]}")

# 2. 批量文档向量化
docs = [
    "阿里百炼text-embedding-v4支持8192上下文",
    "LangChain的DashScopeEmbeddings可直接调用阿里API",
    "RAG系统常用阿里嵌入做中文检索"
]
doc_vecs = embeddings.embed_documents(docs)
print(f"\n批量向量数: {len(doc_vecs)}")
