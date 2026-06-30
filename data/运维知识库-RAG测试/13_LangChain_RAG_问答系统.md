# 使用 LangChain 构建 RAG 问答系统

## 1. 架构概述

```
文档 → 加载器 → 文本分割 → 嵌入 → 向量库
查询 → 检索 → 重排 → 提示组装 → LLM → 答案
```

## 2. 依赖安装

```bash
pip install langchain langchain-community langchain-openai \
  chromadb sentence-transformers unstructured rank-bm25
```

## 3. 文档加载与分割

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader = DirectoryLoader("./docs/", glob="*.md", loader_cls=TextLoader)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100,
    separators=["\n## ", "\n### ", "\n", "。", ".", " ", ""]
)
chunks = splitter.split_documents(docs)

print(f"文档数: {len(docs)}, 片段数: {len(chunks)}")
```

## 4. 向量化与存储

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
vectorstore.persist()
```

## 5. 检索

```python
# 纯向量检索
retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

# 混合检索（BM25 + 向量）
from langchain.retrievers import BM25Retriever, EnsembleRetriever

bm25 = BM25Retriever.from_documents(chunks, k=8)
ensemble = EnsembleRetriever(retrievers=[bm25, retriever], weights=[0.3, 0.7])
```

## 6. 提示与生成

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

template = """根据以下上下文信息回答问题。如果无法回答，请如实说明。

上下文：
{context}

问题：{question}

回答要求：引用具体来源片段，保持简洁。"""

prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

chain = (
    {"context": ensemble, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

result = chain.invoke("Nginx 反向代理如何配置超时？")
print(result)
```

## 7. 带来源引用

```python
from langchain_core.runnables import RunnableParallel

def format_docs(docs):
    parts = []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        parts.append(f"[来源: {src}]\n{d.page_content}")
    return "\n\n---\n\n".join(parts)

rag_chain_with_sources = RunnableParallel(
    {"context": ensemble | format_docs, "question": RunnablePassthrough()}
) | prompt | llm | StrOutputParser()
```

## 8. 内存与对话

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

conv_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=ensemble,
    memory=memory,
    return_source_documents=True
)

res = conv_chain.invoke({"question": "刚才提到的 server_name 是什么？"})
print(res["answer"])
```

## 9. 评测

```python
# 简易问答对评测
qa_pairs = [
    ("Nginx 默认监听哪个端口？", "80"),
    ("Docker 默认网络驱动是什么？", "bridge"),
]

correct = 0
for q, expected in qa_pairs:
    answer = chain.invoke(q)
    if expected.lower() in answer.lower():
        correct += 1

print(f"准确率: {correct}/{len(qa_pairs)} ({correct/len(qa_pairs):.1%})")
```

## 10. 部署与优化

- 向量库选持久化方案（Chroma/Weaviate/Milvus）。
- 嵌入与 LLM 可替换为本地模型（Ollama + llama.cpp）降成本。
- 加入缓存（Redis/GPTCache）对重复查询提速。
- 监控：记录延迟、token 消耗、检索命中率、用户反馈。