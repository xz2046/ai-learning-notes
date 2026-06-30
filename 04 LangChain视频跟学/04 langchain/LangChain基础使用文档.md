# LangChain 基础使用文档

> 整理自 `04 langchain/` 目录下 21 个实战代码练习（已按学习顺序编号 01~21）
> 更新时间：2026-06-18

---

## 目录

1. [环境与模型连接](#1-环境与模型连接)
2. [提示词模板](#2-提示词模板)
3. [输出解析器](#3-输出解析器)
4. [链式调用（LCEL）](#4-链式调用lcel)
5. [自定义 Runnable](#5-自定义-runnable)
6. [文档加载器](#6-文档加载器)
7. [文本分割](#7-文本分割)
8. [嵌入模型](#8-嵌入模型)
9. [向量存储](#9-向量存储)
10. [检索增强生成（RAG）](#10-检索增强生成rag)
11. [会话记忆](#11-会话记忆)
12. [最佳实践与注意事项](#12-最佳实践与注意事项)

---

## 1. 环境与模型连接

### 1.1 ChatOpenAI 初始化

LangChain 通过 `ChatOpenAI` 统一调用各种兼容 OpenAI API 的模型（DeepSeek、OpenAI、阿里百炼等）。

```python
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="deepseek-v4-flash",                    # 模型名称
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),  # API密钥（推荐从环境变量读取）
    base_url="https://api.deepseek.com",          # API地址
    temperature=0.7,                              # 发散程度 0~2
    streaming=True,                               # 流式输出（可选）
)
```

**参数说明：**
- `model`：模型名称，根据API提供商填写
- `api_key`：永远不要硬编码在代码中，使用环境变量 `os.environ.get()`
- `base_url`：兼容 OpenAI API 的服务地址
- `temperature`：0=最确定，2=最发散，通常 0.7 左右
- `streaming=True`：启用流式输出，配合 `llm.stream()` 使用

### 1.2 消息格式与调用

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="你是一个简洁专业的助手"),
    HumanMessage(content="解释一下向量数据库的作用"),
    AIMessage(content="向量数据库是一种专门用于存储和查询高维向量数据的数据库。"),
    HumanMessage(content="解释一下RAG是什么"),
]

# 简写格式（角色：system, human, ai）
messages_jx = [
    ("system", "你是一个简洁专业的助手"),
    ("human", "解释一下向量数据库的作用"),
    ("ai", "向量数据库是一种专门用于存储和查询高维向量数据的数据库。"),
    ("human", "解释一下RAG是什么"),
]

# 流式调用
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)

# 普通调用
response = llm.invoke(messages)
print(response.content)
```

---

## 2. 提示词模板

### 2.1 PromptTemplate（基础模板）

```python
from langchain_core.prompts import PromptTemplate

# 方式一：from_template（推荐）
prompt = PromptTemplate.from_template("你是一个{role}助手，请用{style}的风格回答问题。")
formatted = prompt.format(role="专业", style="夸张")

# 方式二：invoke 注入变量
chain = prompt | llm
response = chain.invoke({"role": "专业", "style": "夸张"})
```

### 2.2 ChatPromptTemplate（对话模板）

支持多轮消息格式，可配合 `MessagesPlaceholder` 插入历史记录。

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个边塞诗人，可以作诗。"),
    MessagesPlaceholder("history"),          # 历史消息占位符
    ("human", "请再来一首唐诗"),
])

history_data = [
    ("human", "你来写一个唐诗"),
    ("ai", "床前明月光，疑是地上霜，举头望明月，低头思故乡"),
    ("human", "好诗再来一个"),
    ("ai", "锄禾日当午，汗滴禾下锄，谁知盘中餐，粒粒皆辛苦"),
]

prompt_text = chat_prompt.invoke({"history": history_data}).to_string()
```

### 2.3 FewShotPromptTemplate（少样本模板）

```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

# 定义示例模板
example_template = PromptTemplate.from_template("单词：{word}, 反义词：{antonym}")

# 示例数据
examples_data = [
    {"word": "大", "antonym": "小"},
    {"word": "上", "antonym": "下"},
]

few_shot_template = FewShotPromptTemplate(
    example_prompt=example_template,      # 示例数据的模板
    examples=examples_data,               # 示例数据（list套dict）
    prefix="告知我单词的反义词，我提供如下的示例：",  # 示例前的提示
    suffix="基于前面的示例告知我，{input_word}的反义词是？",  # 示例后的提问
    input_variables=["input_word"],       # 需要注入的变量
)

result = few_shot_template.invoke(input={"input_word": "左"}).to_string()
```

---

## 3. 输出解析器

### 3.1 StrOutputParser（字符串解析器）

将模型输出的 AIMessage 转为纯字符串，方便下游处理。

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()

chain = prompt | model | parser
result: str = chain.invoke({"lastname": "张", "gender": "女儿"})
# result 是 str 类型，非 AIMessage
```

### 3.2 JsonOutputParser（JSON解析器）

将模型的 JSON 输出自动解析为 Python 字典，支持流式增量解析。

```python
from langchain_core.output_parsers import JsonOutputParser

jsonparser = JsonOutputParser()
strparser = StrOutputParser()

first_prompt = PromptTemplate.from_template(
    "我邻居姓：{lastname}，刚生了{gender}，请起名。请严格以json格式返回，包含name字段。"
)
second_prompt = PromptTemplate.from_template(
    "请根据这个名字：{name}，分析这个名字的寓意。"
)

# JSON输出 -> 解析为dict -> 注入到下一个prompt
chain = first_prompt | model | jsonparser | second_prompt | model | strparser

for chunk in chain.stream({"lastname": "张", "gender": "女儿"}):
    print(chunk, end="", flush=True)
```

**关键点**：`jsonparser` 将模型输出的 `{"name": "xxx"}` 解析为 Python dict，然后 dict 的键名自动匹配下一个 prompt 的变量名 `{name}`。

---

## 4. 链式调用（LCEL）

### 4.1 管道符 `|` 组合链

LangChain 表达式语言（LCEL）使用 `|` 将多个组件串联成管道。**每个组件必须实现 Runnable 接口**。

```python
# 基础链
chain = prompt | model

# 带解析器的链
chain = prompt | model | strparser

# 多步骤链（起名 -> 解析 -> 分析寓意）
chain = first_prompt | model | jsonparser | second_prompt | model | strparser

# 调用
res = chain.invoke({"lastname": "张", "gender": "女儿"})

# 流式输出
for chunk in chain.stream({"history": history_data}):
    print(chunk.content, end="", flush=True)
```

### 4.2 管道符原理

Python 的 `|` 运算符在 LangChain 中被重载，类似 Unix 管道：**前一个组件的输出作为后一个组件的输入**。

| 组件 | 输入类型 | 输出类型 |
|------|---------|---------|
| PromptTemplate | dict | PromptValue |
| ChatOpenAI | PromptValue / messages | AIMessage |
| StrOutputParser | AIMessage | str |
| JsonOutputParser | AIMessage | dict |
| RunnableLambda | 任意 | 任意 |
| Retriever | str | list[Document] |

---

## 5. 自定义 Runnable

### 5.1 RunnableLambda

用 lambda 或普通函数转换成 Runnable，插入链中做数据转换。

```python
from langchain_core.runnables import RunnableLambda

# 方式一：lambda 表达式
my_func = RunnableLambda(lambda x: f"这个名字是：{x}")

# 方式二：直接在链中用 lambda（等价）
chain = first_prompt | model | (lambda ai_msg: {"name": ai_msg.content}) | second_prompt | model | strparser

# 方式三：自定义函数
def print_prompt(prompt):
    print(prompt.to_string())
    print("=" * 20)
    return prompt

chain = prompt | print_prompt | model | strparser
```

### 5.2 RunnablePassthrough

直接透传输入，常用于分支场景：**同一个输入同时流向多个下游**。

```python
from langchain_core.runnables import RunnablePassthrough

# 典型用法：同时传用户提问 + 向量检索结果给 prompt
chain = (
    {
        "input": RunnablePassthrough(),       # 透传用户的输入
        "context": retriever | format_func    # 同时从向量库检索
    }
    | prompt
    | model
    | StrOutputParser()
)

res = chain.invoke("怎么减肥？")
# 相当于 {"input": "怎么减肥？", "context": "检索到的参考资料"}
```

---

## 6. 文档加载器

### 6.1 TextLoader（文本文件）

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader(
    file_path="path/to/file.txt",
    encoding="utf-8",
)
docs = loader.load()  # -> list[Document]
```

### 6.2 CSVLoader（CSV文件）

```python
from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(
    file_path="./data.csv",
    csv_args={
        "delimiter": ",",                    # 分隔符
        # "fieldnames": ['name', 'age'],     # 自定义列名（无表头时使用）
    },
    encoding="utf-8",
)

# 批量加载
documents = loader.load()     # -> list[Document]

# 懒加载（大文件推荐）
for doc in loader.lazy_load():
    print(doc)
```

### 6.3 JSONLoader（JSON/JSONLines）

```python
from langchain_community.document_loaders import JSONLoader

# 使用 jq 语法抽取特定字段
loader = JSONLoader(
    file_path="./data.json",
    jq_schema=".milestones.[].year",         # jq 查询语法
    text_content=False,                       # 抽取的内容不是纯字符串
    json_lines=True,                          # JSONLines格式（每行一个独立json）
)

data = loader.load()
```

**jq 语法速查**：
- `.field` → 取字段
- `.[]` → 遍历数组
- `.a.[].b` → 取数组 a 中每个元素的 b 字段

### 6.4 PyMuPDFLoader（PDF文件）

```python
from langchain_community.document_loaders import PyMuPDFLoader

loader = PyMuPDFLoader(
    file_path="./document.pdf",
    mode="single",        # "single"=整体不分割, "page"=按页分割
    # password="2222",    # 加密PDF的密码
)
docs = loader.load()      # -> list[Document]，每页一个（mode="page"时）
```

---

## 7. 文本分割

### 7.1 RecursiveCharacterTextSplitter

按优先级逐级查找分割符，尽量保持语义完整。**RAG 系统中最重要的预处理步骤**。

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,              # 每段最大字符数
    chunk_overlap=100,           # 相邻段落重叠字符数
    separators=[                 # 分割优先级（从高到低）
        "\n\n",                  # 段落分割
        "\n",                    # 行分割
        "。", "！", "？",         # 中文句号（中文文档推荐）
        "，",                    # 逗号
        " ",                     # 空格
        "",                      # 字符级别（兜底）
    ],
    length_function=len,         # 计算长度的函数（可自定义）
)

# 分割已加载的文档
splitted_docs = splitter.split_documents(docs)

# 或直接分割文本
splitted_texts = splitter.split_text(long_text)
```

**参数调优建议：**
- `chunk_size`：太小则上下文不足，太大则检索噪声增加。RAG 推荐 500~1000
- `chunk_overlap`：解决切割点可能丢失关键信息的问题，推荐 10%~20%
- `separators`：中文文档建议加入 `"。"`，`"！"`，`"？"` 作为分隔符

---

## 8. 嵌入模型

### 8.1 本地模型：BGE-M3（HuggingFace）

```python
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 国内镜像
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_OFFLINE"] = "1"                     # 离线模式

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name=local_model_path,             # 优先使用本地快照路径
    model_kwargs={"device": "cpu"},          # 有GPU填 "cuda"
    encode_kwargs={"normalize_embeddings": True},  # 向量归一化（检索推荐开启）
)

# 单文本向量化
query_emb = embeddings.embed_query("什么是文本向量")
print(f"向量维度: {len(query_emb)}")         # BGE-M3 输出 1024 维

# 批量文档向量化
doc_embs = embeddings.embed_documents([
    "BGE-M3 是多语言混合检索向量模型",
    "LangChain 用于构建大语言模型应用",
])
```

### 8.2 在线API：阿里百炼 DashScope

```python
from langchain_community.embeddings import DashScopeEmbeddings
import os

os.environ["DashScope_API_KEY"] = "sk-xxx"

embeddings = DashScopeEmbeddings(
    model="text-embedding-v4"               # 阿里百炼嵌入模型
)

# 用法同上
query_vec = embeddings.embed_query("LangChain如何接入阿里嵌入模型？")
doc_vecs = embeddings.embed_documents([...])
```

---

## 9. 向量存储

### 9.1 InMemoryVectorStore（内存向量存储）

适合小规模数据、测试和原型阶段，数据不持久化。

```python
from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embedding=embeddings)

# 方式一：添加文本（自动向量化）
vector_store.add_texts([
    "减肥就是要少吃多练",
    "跑步是很好的运动哦",
])

# 方式二：添加 Document 对象（可以指定ID）
vector_store.add_documents(
    documents=documents,
    ids=["id1", "id2", "id3"],
)

# 删除
vector_store.delete(["id1", "id2"])

# 相似度检索（k=返回最相似的N条）
result = vector_store.similarity_search("怎么减肥？", k=2)

# 转换为检索器（Runnable接口）
retriever = vector_store.as_retriever(search_kwargs={"k": 2})
# retriever.invoke("查询") -> list[Document]
```

### 9.2 Chroma（持久化向量存储）

适合正式项目，数据持久化到磁盘。

```python
from langchain_chroma import Chroma

# 创建/加载持久化向量库
vector_store = Chroma(
    collection_name="test",                  # 集合名称
    embedding_function=embeddings,            # 嵌入函数
    persist_directory="./chroma_db/",         # 持久化目录
)

# 增删查与 InMemoryVectorStore 一致
vector_store.add_documents(documents=documents, ids=["id1", "id2"])
vector_store.delete(["id1"])
result = vector_store.similarity_search("查询内容", k=2)
```

---

## 10. 检索增强生成（RAG）

### 10.1 手动RAG链路

```python
vector_store.add_texts(["参考资料1", "参考资料2", ...])
input_text = "用户问题"

# 1. 检索
result = vector_store.similarity_search(input_text, k=2)
reference_text = "[" + "".join(doc.page_content for doc in result) + "]"

# 2. 构建带上下文的prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "以参考资料为主回答。参考资料:{context}。"),
    ("user", "用户提问：{input}"),
])

# 3. 回答
chain = prompt | model | StrOutputParser()
res = chain.invoke({"input": input_text, "context": reference_text})
```

### 10.2 LCEL 完整RAG链路（推荐）

```python
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough

# 1. 格式化检索结果的函数
def format_docs(docs: list[Document]):
    if not docs:
        return "无相关参考资料"
    return "[" + "".join(doc.page_content for doc in docs) + "]"

# 2. 创建检索器
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# 3. 构建RAG链
chain = (
    {
        "input": RunnablePassthrough(),        # 用户提问
        "context": retriever | format_docs     # 检索+格式化
    }
    | prompt                                    # 组装提示词
    | model                                     # LLM生成
    | StrOutputParser()                         # 提取文本
)

res = chain.invoke("怎么减肥？")
```

**RunnablePassthrough 的作用**：用户输入"怎么减肥？"同时传给两个分支——
- `input` 分支：原样透传
- `context` 分支：先检索向量库，再格式化结果

### 10.3 数据流说明

```
用户输入: "怎么减肥？"
       │
       ▼
┌──────────────────────┐
│  RunnablePassthrough  │
│  + retriever          │
│                      │
│  → {"input": "...",   │
│     "context": "..."} │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  ChatPromptTemplate   │
│  → 填充 {input}       │
│     和 {context}      │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  ChatOpenAI           │
│  → 生成回答           │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  StrOutputParser      │
│  → 纯文本输出         │
└──────────────────────┘
```

---

## 11. 会话记忆

### 11.1 内存记忆（临时）

```python
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个历史记录助手，根据会话历史回答。"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

store = {}  # session_id -> ChatMessageHistory

def get_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

base_chain = prompt | model | strparser

chain_with_history = RunnableWithMessageHistory(
    base_chain,
    get_history,
    input_messages_key="input",       # prompt 中的用户输入变量名
    history_messages_key="chat_history",  # prompt 中的历史消息变量名
)

# 使用：传入 session_id 来区分不同对话
config = {"configurable": {"session_id": "user_001"}}

res1 = chain_with_history.invoke({"input": "今天早上有雾"}, config=config)
res2 = chain_with_history.invoke({"input": "今天整体天气如何"}, config=config)
# 第二次回答会自动包含历史记录
```

### 11.2 文件持久化记忆

自定义 `FileChatMessageHistory`，将记忆保存到本地 JSON 文件，重启不丢失。

```python
import os, json
from typing import Sequence
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory

class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, storage_path):
        self.session_id = session_id
        self.storage_path = storage_path
        self.file_path = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages = list(self.messages)
        all_messages.extend(messages)
        # BaseMessage -> dict -> JSON写入文件
        new_messages = [message_to_dict(msg) for msg in all_messages]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f)

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return messages_from_dict(data)  # dict列表 -> BaseMessage列表
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)

# 使用方式同内存记忆，只是 get_history 改为：
def get_history(session_id):
    return FileChatMessageHistory(session_id, "./chat_history")
```

**关键API**：
- `message_to_dict(msg)` → dict（BaseMessage → 可序列化字典）
- `messages_from_dict([dict, ...])` → list[BaseMessage]（字典列表 → 消息对象）

---

## 12. 最佳实践与注意事项

### 12.1 常见模式速查

| 场景 | 核心组件 | 代码模式 |
|------|---------|---------|
| 简单问答 | PromptTemplate + ChatOpenAI | `prompt \| llm` |
| 流式输出 | ChatOpenAI(streaming=True) | `llm.stream(messages)` |
| JSON控制 | JsonOutputParser | `prompt \| model \| jsonparser` |
| 多步处理 | Chain组合 | `p1 \| m1 \| p2 \| m2 \| parser` |
| RAG系统 | Retriever + RunnablePassthrough | `{input:..., context:...} \| prompt \| llm` |
| 多轮对话 | RunnableWithMessageHistory | `chain.with_history(get_history)` |
| 文档问答 | 文档加载器 + 分割器 + 向量库 | `load → split → embed → retrieve → answer` |

### 12.2 注意事项

1. **环境变量管理**：API 密钥永远从 `os.environ.get()` 读取，不要硬编码
2. **嵌入模型选择**：中文场景推荐 BGE-M3 或 阿里百炼 text-embedding-v4
3. **分割参数**：`chunk_size` 和 `chunk_overlap` 需要根据文档类型调整，多做实验
4. **向量归一化**：检索场景推荐 `normalize_embeddings=True`，提高余弦相似度计算的准确性
5. **链的组件**：每个组件必须实现 Runnable 接口才能用 `|` 连接
6. **文件记忆路径**：使用前确保 `os.chdir()` 到脚本所在目录，否则相对路径可能失效
7. **PDF加载**：`PyMuPDFLoader` 的 `mode="single"` 将整个PDF作为一个 Document，`mode="page"` 按页分割
8. **CSV表头**：有表头的 CSV 不需要 `fieldnames` 参数；无表头时需要指定

### 12.3 学习路线图

```
基础 → 提示词 → 链 → 记忆 → 加载器 → 分割 → 嵌入 → 向量库 → RAG
 │        │       │     │       │        │       │       │        │
 ▼        ▼       ▼     ▼       ▼        ▼       ▼       ▼        ▼
连接模型  模板  组合链  对话  各种格式  分段  文本转    存储   检索+回答
        技巧   串联    历史  数据加载        向量   索引
```

可以从这个路线图的起点开始，每个模块在 `04 langchain/` 目录下有对应的练习代码。

---

## 附录：文件编号对照表

| 编号 | 文件名 | 对应模块 |
|:---:|--------|---------|
| 01 | `01_连接模型.py` | 模型连接（ChatOpenAI、消息格式） |
| 02 | `02_基础提示词模板.py` | PromptTemplate 基础模板 |
| 03 | `03_对话提示词模板.py` | ChatPromptTemplate + MessagesPlaceholder |
| 04 | `04_少样本提示词模板.py` | FewShotPromptTemplate |
| 05 | `05_字符串输出解析器.py` | StrOutputParser |
| 06 | `06_JSON输出解析器.py` | JsonOutputParser + 链组合 |
| 07 | `07_链式调用基础.py` | LCEL 管道符、invoke/stream |
| 08 | `08_管道符运算符原理.py` | Python `\|` 运算符重载原理 |
| 09 | `09_自定义Runnable函数.py` | RunnableLambda |
| 10 | `10_临时会话记忆.py` | RunnableWithMessageHistory + InMemory |
| 11 | `11_持久化会话记忆.py` | FileChatMessageHistory（JSON文件） |
| 12 | `12_文本加载器与文档分割.py` | TextLoader + RecursiveCharacterTextSplitter |
| 13 | `13_CSV加载器.py` | CSVLoader（含参数配置） |
| 14 | `14_JSON加载器.py` | JSONLoader（jq语法） |
| 15 | `15_PDF加载器.py` | PyMuPDFLoader |
| 16 | `16_本地嵌入模型_BGEM3.py` | HuggingFaceEmbeddings（BGE-M3） |
| 17 | `17_阿里百炼嵌入模型.py` | DashScopeEmbeddings（text-embedding-v4） |
| 18 | `18_内存向量存储.py` | InMemoryVectorStore |
| 19 | `19_Chroma持久化存储.py` | Chroma（持久化到磁盘） |
| 20 | `20_RAG检索增强问答.py` | RAG 手动版（检索+拼接+回答） |
| 21 | `21_LCEL完整RAG链路.py` | RAG 完整 LCEL 版（含 RunnablePassthrough） |
