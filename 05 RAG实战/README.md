# 业务运维 RAG 问答系统

基于 LangChain + Chroma + DeepSeek 构建的本地知识库问答系统，面向 IDC 运维场景，支持文档上传入库、相似检索、多轮对话。

---

## 项目用途

日常运维中经常需要查各种 SOP、appid 对照表、机房资源规则。每次翻文档找答案效率低。这个项目就是把散落在 Markdown 文档中的运维知识**向量化存储**，用自然语言直接提问就能拿到答案。

---

## 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 语言模型 | DeepSeek v4 Flash | 通过 OpenAI 兼容接口调用 |
| Embedding 模型 | BAAI/bge-m3 | 本地运行，约 2GB |
| 向量数据库 | Chroma | 文件级持久化，无需单独部署 |
| 检索框架 | LangChain LCEL | 自定义检索链 + 对话历史管理 |
| Web 界面 | Streamlit | 侧边栏导航，对话 + 知识库两个页面 |
| 历史存储 | JSON 文件 | 每会话一个文件，按需读写 |

---

## 项目架构

```
05 RAG实战/
│
├── app.py                     # [入口] 统一入口，侧边栏切换对话 / 知识库
├── app_qa.py                  # [保留] 仅对话页面（独立运行时用）
├── app_file_uploader.py       # [保留] 仅上传页面（独立运行时用）
│
├── rag.py                     # RAG 核心链
│   ├── 构建 LCEL 管道: 检索 → 拼 context → 调 LLM → 输出
│   ├── 多轮对话支持（RunnableWithMessageHistory）
│   └── 流式输出
│
├── vector_store.py            # 向量存储封装
│   ├── Chroma 初始化与检索
│   ├── 自定义检索器（top-k + 距离阈值过滤）
│   └── get_embedding() 单例（复用 bge-m3 模型）
│
├── knowledge_base.py          # 知识库管理
│   ├── 文档切分（RecursiveCharacterTextSplitter）
│   ├── MD5 去重（避免重复入库）
│   ├── 写入 Chroma 向量库
│   └── get_file_list() 读取已上传文件列表
│
├── file_history_store.py      # 对话历史持久化
│   ├── 继承 BaseChatMessageHistory
│   └── JSON 文件读写
│
├── config_data.py             # 全局配置
│   ├── Chroma 集合名、持久化路径
│   ├── embedding 模型路径
│   ├── 切块参数（chunk_size / chunk_overlap / separators）
│   ├── 检索参数（top_k / max_distance）
│   └── 会话配置
│
├── data/
│   ├── chroma/                # Chroma 向量库持久化文件
│   └── chat_history/          # 对话历史 JSON（按 session_id）
│
├── conf/
│   └── md5_text.txt           # 已上传文档的 MD5 记录
│
└── README.md
```

### 数据流向

```
用户提问（页面根层级，chat_input 自动固定在底部）
  │
  ▼
app.py ──→ rag.py（RAG 链）
              │
              ├── vector_store.get_retriever()
              │       │
              │       ▼
              │   Chroma（相似度搜索 → 距离阈值过滤）
              │       │
              │       ▼
              │   返回相关文档片段
              │
              ├── 拼装 prompt（system + context + history + user）
              │
              ├── DeepSeek API（流式生成回答）
              │
              └── 返回流式结果 → 渲染到页面
                        │
                        ▼
              file_history_store.py 保存本轮对话
```

### 上传流程

```
app.py 知识库页面 ──→ knowledge_base.upload_by_str()
                          │
                          ├── MD5 去重检查
                          │
                          ├── RecursiveCharacterTextSplitter 切块
                          │
                          ├── Chroma.add_texts() 入库
                          │
                          └── 记录 MD5 到 md5_text.txt
```

---

## 各文件功能说明

### 入口文件

| 文件 | 功能 | 启动命令 |
|------|------|---------|
| app.py | **统一入口**，侧边栏切换「对话」和「知识库」两个页面 | `streamlit run app.py` |
| app_qa.py | 仅对话页面（保留兼容） | `streamlit run app_qa.py` |
| app_file_uploader.py | 仅知识库上传页面（保留兼容） | `streamlit run app_file_uploader.py` |

### 核心逻辑

| 文件 | 功能 |
|------|------|
| rag.py | 组装 RAG 检索链、管理多轮对话、调用 LLM |
| vector_store.py | Chroma 向量库操作、自定义过滤检索器、embedding 模型单例管理 |
| knowledge_base.py | 文档切块、MD5 去重、向量入库、读取已上传文件列表 |
| file_history_store.py | 对话历史的 JSON 读写（按 session_id 隔离） |
| config_data.py | 全局配置常量（模型路径、切块参数、检索参数等） |

---

## 运行方式

### 1. 安装依赖

```bash
pip install streamlit langchain-huggingface langchain-chroma langchain-core langchain-openai langchain-text-splitters python-dotenv
```

### 2. 设置 API Key

```bash
set DEEPSEEK_API_KEY2=sk-xxxxxxxxxxxxxxxx
```

或在系统环境变量中配置（推荐）。

### 3. 启动

```bash
cd "05 RAG实战"
streamlit run app.py
```

侧边栏有两个页面：
- **💬 对话** — 问答聊天，输入框固定在页面底部
- **📂 知识库** — 上传文件 + 查看已上传文件列表

首次启动问答页面时，系统会自动加载 bge-m3 embedding 模型（约 2GB），请耐心等待。

---

## 使用步骤

1. **切换至「知识库」页面**，上传运维 SOP 文档（.md / .txt）
2. **切换至「对话」页面**，输入问题，系统会从知识库检索相关内容并生成回答
3. 对话支持上下文记忆，可以在同一会话中连续追问

### 示例问题

- "PDD 的 appid 有哪些？"
- "PDD 异网补点选点条件是什么？"
- "B站业务筛选设备的 NAT 类型要求是什么？"

---

## 关键设计说明

### 检索过滤机制

检索不是简单的 top-k 返回，而是加了**距离阈值过滤**（`max_distance = 0.8`）。如果检索到的文档与问题语义距离过大，会被自动丢弃。当所有文档都被丢弃时，模型会如实返回"找不到相关信息"，而不是基于无关内容编造答案。

### Embedding 模型单例

bge-m3 模型约 2GB，系统使用模块级懒加载单例避免重复加载，无论打开多少个页面或创建多少个实例，模型在内存中只有一份。

### 文档去重

通过 MD5 校验避免同一份文档重复入库。上传时会先检查文档内容的 MD5 是否已记录，已存在的直接跳过。

### 页面切换

对话和知识库通过侧边栏 radio 切换，而非标签页。原因是 Streamlit 的 `st.chat_input()` 自动底部定位只在页面根层级生效，嵌套在容器内会失效。

---

## 完成本项目的学习目标

- [x] 理解 RAG 的两阶段架构：检索（Retrieval）+ 生成（Generation）
- [x] 掌握文本切块策略（chunk_size / chunk_overlap / separators）
- [x] 掌握 Embedding 模型的选择与本地部署
- [x] 掌握向量数据库（Chroma）的读写与检索
- [x] 掌握 LangChain LCEL 链式组装（RunnablePassthrough / RunnableLambda / RunnableWithMessageHistory）
- [x] 理解检索质量对生成结果的影响（top-k + 距离阈值）
- [x] 理解多轮对话中的历史管理
- [x] 掌握 prompt 拼接中 context 与 history 的组织方式
- [x] 用 Streamlit 快速构建原型界面

---

## 已知可改进方向

- [ ] 增加检索阶段的评估（precision / recall），单独评测检索质量
- [ ] 支持 PDF 上传（需要额外做 OCR 或 PDF 文本提取）
- [ ] 支持批量上传多个文件
- [ ] 切换云端 Embedding API（如 text-embedding-3-small）减少本地资源消耗
- [ ] 增加异常处理，API/Chroma 失败时给用户友好提示
- [ ] 多用户会话隔离（当前 session_id 写死 user_001）
- [ ] 支持删除 / 更新知识库文档
