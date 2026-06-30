from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import JSONLoader

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_OFFLINE"] = "1"
# 初始化 BGE-M3

local_model_path = r"C:/Users/admin/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181"
model_name = "BAAI/bge-m3"
embeddings = HuggingFaceEmbeddings(
    model_name=local_model_path,
    model_kwargs={"device": "cpu"},  # 有显卡填 cuda，纯CPU改为 cpu
    encode_kwargs={"normalize_embeddings": True}  # 向量归一化，检索推荐开启
)

vector_store = InMemoryVectorStore(embedding=embeddings)

loader = JSONLoader(file_path=r"C:/Users/admin/Desktop/学习/05 插入部分-视频跟学/098 testData/test.json",
                   jq_schema=".milestones.[].event")

documents = loader.load()

vector_store.add_documents(documents=documents,ids=["id"+ str(i) for i in range(1,len(documents)+1)])
vector_store.delete(["id1","id2"])

result =vector_store.similarity_search("Python是最好的编程语言",k=2)
print(result)