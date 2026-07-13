# AI 应用开发学习笔记

> 从零到一构建 AI 应用的技术栈学习记录
>
> 涵盖：Prompt 工程、RAG、LangChain、Agent 智能体、LangGraph、MCP 等

---

## 📖 学习路线

```
基础概念 → API 调用 → Prompt 工程 → RAG 实战 → Agent 智能体 → 部署上线
```

### 已完成项目

| 周次 | 主题 | 项目 | 核心技能 |
|------|------|------|----------|
| **Week 1** | AI 基础概念 | [`01 学习计划与基础概念`](./01%20学习计划与基础概念/) | LLM / Token / Embedding / RAG 概念 |
| **Week 2** | Python 调用模型 API | [`02 deepseek接入`](./02%20deepseek接入/) | OpenAI SDK / 多轮对话 / 流式输出 / 结构化输出 |
| **Week 3** | Prompt 工程与评估 | [`03 prompt工程与评估`](./03%20prompt工程与评估/) | Zero-shot / Few-shot / 提示词评估框架 |
| **Week 4** | LangChain + RAG 开发 | [`04 LangChain视频跟学`](./04%20LangChain视频跟学/) | LangChain 组件 / Chain / Memory / Document Loaders |
| **Week 4** | RAG 实战项目 | [`05 RAG实战`](./05%20RAG实战/) | ChromaDB / 向量检索 / Streamlit 知识库问答 |
| **Week 7** | Agent 智能体实战 | [`06 Agent实战`](./06%20Agent实战/) | ReAct Agent / 工具调用 / 中间件 / CDN 运维助手 |

---

## 🗂️ 项目结构

```
学习/
├── 01 学习计划与基础概念/      # 学习计划 + AI 基础概念笔记
│   ├── AI应用开发学习计划.md    # 学习路线规划
│   ├── AI应用开发基础概念.md    # LLM / Token / RAG 等概念笔记
│   └── AI应用开发学习计划_v2.md # 进阶版学习计划
│
├── 02 deepseek接入/            # Week 2: Python 调模型 API
│   ├── openai-deepseek/        # 8 个入门脚本
│   │   ├── 初次调用.py
│   │   ├── 多轮对话.py
│   │   ├── 流式输出.py
│   │   ├── json格式输出.py
│   │   ├── tool工具调用.py
│   │   └── ...
│   └── week2_llm_api_demo/     # 封装的 client 工具
│
├── 03 prompt工程与评估/        # Week 3: Prompt 工程
│   ├── OpenAI Prompt工程指南.md
│   ├── 常见Prompt样例集.md
│   └── week3_prompt_eval_demo/ # 评估框架（10个测试用例 + 对比评估 + 报告）
│
├── 04 LangChain视频跟学/       # Week 4: LangChain 框架学习
│   ├── 01 ollama ~ 05 Agent智能体/  # 视频跟学配套代码
│   └── 099 资料/               # 课件 PPT 和学习笔记
│
├── 05 RAG实战/                 # Week 4: RAG 项目
│   ├── app.py                  # Streamlit 界面
│   ├── rag.py                  # RAG 核心服务
│   ├── vector_store.py         # 向量存储服务
│   └── knowledge_base.py       # 知识库管理
│
├── 06 Agent实战/               # Week 7: Agent 智能体项目
│   ├── app.py                  # Streamlit 运维助手界面
│   ├── agent/                  # Agent 核心
│   │   ├── react_agent.py      # ReAct Agent 定义
│   │   └── tools/              # 5 个运维工具
│   ├── rag/                    # RAG 知识库
│   ├── config/                 # 配置文件
│   └── prompts/                # 提示词模板
│
├── 10 文档/                    # 其他学习资料
│
└── README.md                   # 本文件
```

---

## 🛠️ 技术栈

| 领域 | 技术 |
|------|------|
| **编程语言** | Python 3.11+ |
| **AI 框架** | LangChain 1.3.11 / LangGraph |
| **大模型** | DeepSeek / Qwen（通义千问） |
| **向量库** | ChromaDB + BGE-M3 Embedding |
| **前端** | Streamlit |
| **部署** | FastAPI / Docker（规划中） |
| **协议** | MCP Model Context Protocol（规划中） |

---

## 📚 核心知识点

### 1. LLM 基础
- Transformer 架构：自编码模型（BERT）、自回归模型（GPT）、序列到序列模型（T5）
- 关键概念：Token / Context Window / Temperature / Embedding
- 幻觉产生原因与缓解策略（RAG / Prompt 约束）

### 2. API 调用
- OpenAI SDK 统一接口，兼容 DeepSeek / Qwen 等服务商
- 三种角色：System（设定规则）、User（用户提问）、Assistant（模型回复）
- 流式输出（Stream）与结构化输出（JSON mode）

### 3. Prompt 工程
- **六大技巧**：详细描述 / 角色扮演 / 分隔符 / 指定步骤 / 提供示例 / 参考文本
- **Zero-shot**：用语言定义任务，依赖模型预训练知识
- **Few-shot**：提供少量示例，引导输出格式

### 4. RAG 检索增强生成
- 离线：文档 → 切分 → 向量化 → 存入向量库
- 在线：Query → 向量检索 → 组装上下文 → LLM 生成
- Text Splitter 参数：chunk_size / chunk_overlap / separators

### 5. LangChain 组件
- **PromptTemplate** / **FewShotPromptTemplate** / **ChatPromptTemplate**
- **Chain**：`|` 运算符串联组件，前一个输出是下一个输入
- **OutputParser**：StrOutputParser / JsonOutputParser
- **Memory**：InMemoryChatMessageHistory / FileChatMessageHistory
- **Document Loaders**：CSVLoader / JSONLoader / PyPDFLoader / TextLoader

### 6. Agent 智能体
- **ReAct 循环**：思考(Thought) → 行动(Action) → 观察(Observation) → 再思考
- **Tool 系统**：@tool 装饰器定义工具，统一注册导出
- **Middleware**：工具监控 / 模型前置日志 / 动态提示词切换
- **流式输出**：write_stream + 打字效果

### 7. 运维场景实践
- CDN 节点查询：页面爬虫（BeautifulSoup）
- 跑量数据查询：Grafana Prometheus API（PromQL）
- 节点状态诊断：CPU / 内存 / 磁盘 / Ping / Load
- 远程命令执行：隧道接口
- 报告生成：动态提示词切换 + 结构化报告模板

---

## 🚀 后续学习计划

| 阶段 | 内容 |
|------|------|
| **Phase 1** | LangGraph 深入 + 记忆持久化（Checkpointer / BaseStore） |
| **Phase 2** | 日志分析 + MCP 服务接入 |
| **Phase 3** | Hermes Agent Skills 编写 + 多 Agent 协作 |
| **Phase 4** | FastAPI + Docker 部署 |
| **Phase 5** | 综合运维助手项目 |

---

## 🔧 环境配置

本项目使用阿里云百炼平台 / DeepSeek 的 API 服务，需配置以下环境变量：

```bash
# API Key（二选一）
export OPENAI_API_KEY=sk-xxx      # 用于 openai 库
export DASHSCOPE_API_KEY=sk-xxx   # 用于 langchain 库
```

各项目的详细配置见对应目录下的 `config/` 文件夹。

---

## 📝 笔记索引

| 文件 | 内容 |
|------|------|
| [`01 学习计划与基础概念/AI应用开发基础概念.md`](./01%20学习计划与基础概念/AI应用开发基础概念.md) | LLM / Token / RAG / Embedding 核心概念 |
| [`03 prompt工程与评估/评估报告.md`](./03%20prompt工程与评估/week3_prompt_eval_demo/评估报告.md) | Prompt 对比评估结果 |
| [`04 LangChain视频跟学/099 资料/PPT/PPT知识点学习笔记.md`](./04%20LangChain视频跟学/099%20资料/PPT/PPT知识点学习笔记.md) | 课程 PPT 知识点整理 |
| [`06 Agent实战/agent实战项目学习笔记.md`](./06%20Agent实战/agent实战项目学习笔记.md) | Agent 实战项目知识点 |
| [`01 学习计划与基础概念/AI应用开发学习计划_v2.md`](./01%20学习计划与基础概念/AI应用开发学习计划_v2.md) | 进阶学习路线规划 |

---

## 📄 许可

本项目仅供个人学习使用。
