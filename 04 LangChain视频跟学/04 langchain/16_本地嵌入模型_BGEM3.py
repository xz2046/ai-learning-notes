import os
# 配置国内镜像，解决首次执行模型下载网络问题
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_OFFLINE"] = "1"
from langchain_huggingface import HuggingFaceEmbeddings
local_model_path = r"C:/Users/admin/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181"
# 初始化 BGE-M3
model_name = "BAAI/bge-m3"
embeddings = HuggingFaceEmbeddings(
    model_name=local_model_path,  #使用本地快照
    model_kwargs={"device": "cpu"},  # 有显卡填 cuda，纯CPU改为 cpu
    encode_kwargs={"normalize_embeddings": True}  # 向量归一化，检索推荐开启
)

# 测试调用
query = "什么是文本向量"
query_emb = embeddings.embed_query(query)
print(f"向量维度: {len(query_emb)}")

texts = [
    "BGE-M3 是多语言混合检索向量模型",
    "LangChain 用于构建大语言模型应用"
]
doc_embs = embeddings.embed_documents(texts)
print(f"文档向量数量: {len(doc_embs)}")