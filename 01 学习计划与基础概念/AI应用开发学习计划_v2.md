# AI 应用开发学习计划 v2 — 进阶版

## 前置回顾

```
已完成（68.75%）：
  Week 1 ✅  基础概念（LLM/Token/RAG/Embedding）
  Week 2 ✅  Python 调模型 API（单轮/多轮/流式/结构化输出）
  Week 3 ✅  Prompt 工程与评估（3套prompt + 量化评估框架）
  Week 4 ✅  RAG 实战（ChromaDB + 知识库 + 问答界面）
  Week 7 ✅  工具调用/Agent（5个真实工具 + 中间件 + Streamlit）

部分完成：
  Week 5 ⚠️  运维知识助手（有检索能力，缺运维文档库）

未开始：
  Week 6 ❌  日志分析
  Week 8 ❌  FastAPI + Docker 部署

新增学习目标：
  ■ LangGraph 基础
  ■ MCP 服务接入
  ■ Hermes Agent Skills 编写
  ■ 多 Agent 协作
  ■ 记忆持久化

最终产出：
  ■ 单独一个完整的运维助手项目
```

---

## 新学习计划总览

| 阶段 | 内容 | 前置依赖 | 周数 |
|------|------|----------|------|
| **一** | LangGraph 深入 + 记忆持久化 | Week 7 Agent 项目 | 1 周 |
| **二** | 日志分析集成 + MCP 了解 | 阶段一 | 1 周 |
| **三** | Skills 编写 + 多 Agent 协作 | 阶段一 | 1 周 |
| **四** | FastAPI + Docker 部署 | 阶段一/二/三 | 1 周 |
| **五** | 综合运维助手项目 | 全部前置 | 2 周 |

**总计：6 周**

---

## 阶段一：LangGraph 基础 + 记忆持久化

### 本周目标
从「用框架」到「理解框架」—— 拆解当前项目中的 Agent 底层运行机制。

### 背景关联
当前项目用的 `create_agent` 底层就是 LangGraph 的状态图（`CompiledStateGraph`）。你已经用到了：状态传递、中间件、流式输出。这一阶段把「黑盒」变成「透明」。

### 需要掌握

| 知识点 | 说明 | 与已有知识的关联 |
|--------|------|-------------------|
| **StateGraph 基础** | 节点(Node) + 边(Edge) + 状态(State) | `create_agent` 内部就是一个 StateGraph |
| **AgentState 自定义** | 定义自己的状态 schema | `middleware.py` 中的 `AgentState` 就在用 |
| **节点函数** | 每个节点是 `(state) → state` 的函数 | `@before_model` 就是模型节点前执行 |
| **条件边** | 根据输出选择下个节点 | Agent 的「思考→工具→再思考」循环本质就是条件边 |
| **Checkpointer** | 对话历史持久化（内存/文件/SQLite） | 新知识点 |
| **BaseStore** | 跨对话的长期记忆存储 | 新知识点 |

### 本周最小项目（Week 9）

项目名：`09_langgraph_fundamentals`

```bash
09_langgraph_fundamentals/
├── 01_state_graph_basic.py       # 最简 StateGraph：A→B→C
├── 02_conditional_edges.py       # 条件边：if/else 路由
├── 03_agent_state.py             # 自定义 AgentState
├── 04_tool_call_node.py          # 工具调用节点
├── 05_checkpointer.py            # Checkpointer 对话持久化
├── 06_memory_store.py            # BaseStore 长期记忆
├── requirements.txt
└── README.md
```

### 练习任务

1. **复刻当前 Agent**：用 `StateGraph` 手动实现一个简化版 ReAct Agent（不依赖 `create_agent`）
2. **加 Checkpointer**：实现「关闭终端再打开，对话还在」的效果
3. **加 BaseStore**：实现「Agent 能记住用户偏好、上次处理的节点 SN」

### 验收标准
- 能画出当前 Agent 的运行状态图
- 能手动写一个带条件边的 `StateGraph`
- Checkpointer 实现对话持久化
- BaseStore 实现跨对话记忆

### 推荐资料
- LangGraph 官方教程：`https://langchain-ai.github.io/langgraph/tutorials/`
- LangGraph 概念：StateGraph / Nodes / Edges / Checkpointer / Store

---

## 阶段二：日志分析 + MCP 服务了解

### 本周目标
1. 补上原计划 Week 6 的日志分析能力
2. 了解 MCP（Model Context Protocol）是什么，如何接入

### 需要掌握

#### 日志分析（3 天）

| 知识点 | 说明 |
|--------|------|
| 日志截断策略 | 太长时怎么分段、保留关键行 |
| 日志过滤 | ERROR/WARN 提取、时间戳解析 |
| 日志 + RAG 串联 | 分析结果去知识库找对应 runbook |
| 日志 + 工具串联 | 分析结果去调工具查状态 |

#### MCP 服务（3 天）

MCP (Model Context Protocol) 是模型与外部工具之间的标准协议，本质是：

```
模型 ↔ MCP Server (Stdio/HTTP) ↔ 外部工具/数据源
```

| 知识点 | 说明 |
|--------|------|
| **MCP 概念** | 协议分层：Resources / Tools / Prompts |
| **MCP Client** | 如何从客户端连接 MCP Server |
| **MCP Server** | 如何暴露一个工具给 MCP |
| **与 LangChain Tools 的关系** | `@tool` 也可包装为 MCP Tool，两者可桥接 |

### 本周最小项目（Week 10）

项目名：`10_log_analysis_mcp`

```bash
10_log_analysis_mcp/
├── logs/
│   ├── nginx_error.log          # 测试日志
│   └── app_error.log
├── log_analyzer.py               # 日志分析核心
├── mcp_server.py                 # 用 MCP 暴露分析工具
├── mcp_client.py                 # 调用 MCP 服务
├── bridge_langchain.py           # MCP Tool ↔ LangChain Tool 桥接
├── requirements.txt
└── README.md
```

### 练习任务
1. 写一个函数：输入日志路径 → 输出异常摘要（ERROR 聚合 + 时间线）
2. 把该函数包装为 MCP Server 的一个 Tool
3. 从另一个 Python 脚本通过 MCP Client 调用它
4. （可选）从当前 06 Agent 中通过 `node_cmd_execute` 获取远程日志 → 调用日志分析

### 验收标准
- 能分析 nginx 和应用日志
- 知道 MCP 解决什么问题
- 能启动一个 MCP Server 并用 client 调用

### 推荐资料
- MCP 官方规范：`https://modelcontextprotocol.io/`
- MCP Python SDK：`https://github.com/modelcontextprotocol/python-sdk`

---

## 阶段三：Skills 编写 + 多 Agent 协作

### 本周目标
1. 学会编写和发布 Hermes Agent Skills（把你的经验固化为可复用的技能）
2. 从单 Agent 到多 Agent：主管 Agent 分配任务、专家 Agent 执行

### 需要掌握

#### Skills 编写（2 天）

| 知识点 | 说明 |
|--------|------|
| SKILL.md 结构 | YAML 前置元数据 + Markdown 正文 |
| 触发条件 | 哪些场景触发这个 skill |
| 步骤编写 | 可复用的操作步骤 + 命令 |
| 引用和模板 | 关联文件、脚本、模板 |
| Skills 管理 | 增删改查、更新迭代 |

#### 多 Agent 协作（3 天）

| 知识点 | 说明 |
|--------|------|
| **主管/工人模式** | 一个 Supervisor Agent 分配任务给多个 Worker |
| **工具共享模式** | 多个 Agent 共享同一个工具集 |
| **消息传递** | Agent 之间如何传递结果 |
| **LangGraph 多 Agent** | 用 StateGraph 实现多 Agent 拓扑 |

### 本周最小项目（Week 11）

项目名：`11_multi_agent_skills`

```bash
11_multi_agent_skills/
├── supervisor_agent.py           # 主管 Agent
├── workers/
│   ├── node_worker.py            # 节点查询专家
│   ├── log_worker.py             # 日志分析专家
│   └── rag_worker.py             # 知识库检索专家
├── graph.py                      # LangGraph 多 Agent 图
├── skills/
│   └── cdn_troubleshooting.md    # 你自己编写的 skill
├── examples/
│   ├── supervisor.py             # 运行示例
│   └── demo_multi_agent.py
├── requirements.txt
└── README.md
```

### 练习任务
1. 以你修复 06 Agent 问题的经验，写一个 **Hermes Agent Skill**：`cdn_node_diagnosis`，内容包括 CDN 节点诊断的标准步骤
2. 用 LangGraph 实现一个 3-Agent 系统：主管 Agent 接收问题 → 分发给节点查询/日志分析/RAG 专家 → 汇总结果
3. 对比单 Agent vs 多 Agent 的输出质量

### 验收标准
- 能发布一个完整的 SKILL.md
- 多 Agent 系统能正确分配任务
- 知道单 Agent 和多 Agent 各自的适用场景

### 推荐资料
- Skills 格式参照 `~/.hermes/skills/` 下已有 skill
- LangGraph 多 Agent 示例：`https://langchain-ai.github.io/langgraph/tutorials/multi_agent/`

---

## 阶段四：FastAPI + Docker 部署

### 本周目标
把前面积累的能力整合为可部署的服务。

### 需要掌握

| 知识点 | 说明 |
|------|------|
| **FastAPI 基础** | 路由、Pydantic Request/Response、依赖注入 |
| **服务分层** | API 层 → Service 层 → 模型/工具层 |
| **Dockerfile 编写** | 多阶段构建、依赖安装、CMD |
| **docker-compose** | 多服务编排（API + ChromaDB） |
| **环境变量管理** | `.env` 注入、敏感配置分离 |
| **健康检查** | `/health` 端点、启动就绪探针 |

### 本周最小项目（Week 12）

项目名：`12_ops_ai_service`

```bash
12_ops_ai_service/
├── app/
│   ├── main.py                   # FastAPI 入口
│   ├── api/
│   │   ├── chat.py               # POST /chat
│   │   ├── tools.py              # POST /tools/query
│   │   ├── logs.py               # POST /logs/analyze
│   │   └── health.py             # GET /health
│   ├── schemas/
│   │   ├── request.py            # Pydantic 请求模型
│   │   └── response.py           # Pydantic 响应模型
│   └── services/
│       ├── agent_service.py      # Agent 封装
│       ├── log_service.py        # 日志分析
│       └── rag_service.py        # RAG 检索
├── data/                         # 挂载卷
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

### 要暴露的接口

```
GET  /health              → 服务状态
POST /chat                → 通用对话（含 Agent 工具调用）
POST /tools/query         → 直接调工具体（SN + 工具名）
POST /logs/analyze        → 日志分析
GET  /docs                → Swagger 文档（FastAPI 自动生成）
```

### 验收标准
- 本地 `uvicorn app.main:app` 可运行
- Swagger 文档可访问
- `docker build -t ops-ai .` 成功
- `docker-compose up` 启动后 API 可用
- `/health` 返回 200

---

## 阶段五：综合运维助手项目

### 本周目标
用两周时间，把前面全部知识点整合成一个完整、独立、可用的运维助手项目。**不做 demo，做一个别人能直接用的工具。**

### 项目规格

项目名：`ops_assistant_pro`（或其他你喜欢的名字）

```bash
ops_assistant_pro/
├── app/
│   ├── main.py                   # FastAPI 入口
│   ├── api/
│   │   ├── chat.py               # Agent 对话接口
│   │   ├── nodes.py              # 节点管理接口
│   │   ├── logs.py               # 日志分析接口
│   │   └── health.py
│   ├── schemas/
│   ├── services/
│   │   ├── agent_service.py      # 多 Agent 主管
│   │   ├── node_service.py       # 节点查询（复用 06 工具代码）
│   │   ├── log_service.py        # 日志分析
│   │   ├── rag_service.py        # RAG 检索
│   │   └── memory_service.py     # 记忆持久化
│   └── agents/
│       ├── supervisor.py         # 主管 Agent
│       └── workers/
│           ├── node_worker.py    # 节点专家
│           ├── log_worker.py     # 日志专家
│           └── rag_worker.py     # RAG 专家
├── data/
│   ├── chroma/                   # 向量库
│   ├── knowledge/                # 运维知识库（8+ runbook）
│   └── logs/                     # 日志样本
├── config/
│   ├── tools.yaml                # 监控平台配置
│   └── agent.yaml                # Agent 配置
├── mcp/
│   ├── node_server.py            # MCP Server：节点工具
│   └── client.py                 # MCP Client 封装
├── Dockerfile
├── docker-compose.yml
├── skills/
│   ├── cdn_diagnosis.md          # 自编 Skill
│   └── log_troubleshooting.md
├── .env.example
├── requirements.txt
└── README.md
```

### 功能清单

| 功能 | 技术 | 来自阶段 |
|------|------|----------|
| ✅ 节点信息查询 | LangChain Tool + 爬虫 | Phase 1 |
| ✅ 跑量数据查询 | Prometheus API | Phase 1 |
| ✅ 运行状态诊断 | Prometheus API | Phase 1 |
| ✅ 远程命令执行 | 隧道 API | Phase 1 |
| ✅ RAG 知识检索 | ChromaDB + Embedding | Phase 1 |
| ✅ 日志分析 | LLM 日志摘要 | Phase 2 |
| ✅ MCP 服务暴露 | MCP Server/Client | Phase 2 |
| ✅ 多 Agent 协作 | LangGraph Supervisor | Phase 3 |
| ✅ Skills 固化 | Hermes Skills | Phase 3 |
| ✅ 对话持久化 | Checkpointer | Phase 1 |
| ✅ 长期记忆 | BaseStore | Phase 1 |
| ✅ API 服务 | FastAPI | Phase 4 |
| ✅ 容器化 | Docker + Compose | Phase 4 |

### 运维知识库建议

```
data/knowledge/
├── nginx_常见故障.md
├── mysql_慢查询排查.md
├── redis_连接异常.md
├── k8s_pod重启排查.md
├── linux_磁盘满处理.md
├── 告警处理手册.md
├── 部署回滚流程.md
├── 常见502问题_runbook.md
```

（可以用你真实工作中的故障文档替代）

### 验收标准
- 全部接口通过 `/docs` 可测试
- 多 Agent 能正确分配任务
- MCP Server 独立可调用
- Docker 一键启动
- 知识库问答准确
- 日志分析能出摘要
- Agent 能记住用户偏好（上次查过的 SN 等）
- 提供至少 2 个自编 Hermes Skills

---

## 学习路线图总览

```
Week 9  ── LangGraph 基础 + 记忆持久化
              └── 理解 Agent 底层，掌握 Checkpointer / Store

Week 10 ── 日志分析 + MCP 服务
              └── 补完日志分析，理解 MCP 协议

Week 11 ── Skills 编写 + 多 Agent 协作
              └── 从单 Agent 到多 Agent，固化经验为 Skills

Week 12 ── FastAPI + Docker 部署
              └── 让一切能跑成服务

Week 13~14 ── 综合运维助手项目
              └── 整合全部能力，产出独立可用的工具
```

---

## 每周固定输出

每周交这三样，延续原有习惯：

1. **一个可运行项目**（最小 demo 或迭代）
2. **一份 README**
3. **一份知识点笔记**（遇到了什么坑、解决了什么问题）

最终项目额外交：
4. **至少 2 个可发布的 Hermes Skills**
5. **Docker 镜像**
6. **一份项目演示文档**

---

## 建议保持的习惯

```
每天写一点，不要攒到周末。

保持节奏：
  - 看完文档立刻开写
  - 遇到报错先自己读 5 分钟
  - 卡超过 30 分钟去搜或问
  - 做完一个 demo 立刻写笔记
```

## 总进度汇总

| 阶段 | 内容 | 周数 | 可运行项目数 |
|------|------|------|-------------|
| 已完成 | Week 1~7（含 Week 5 部分） | 5.5 周 | 5 个 |
| Phase 1 | LangGraph + 记忆持久化 | 1 周 | 1 个 |
| Phase 2 | 日志分析 + MCP | 1 周 | 1 个 |
| Phase 3 | Skills + 多 Agent | 1 周 | 1 个 |
| Phase 4 | FastAPI + Docker | 1 周 | 1 个 |
| Phase 5 | 综合运维助手 | 2 周 | 1 个 |
| **合计** | | **~12.5 周** | **10 个** |
