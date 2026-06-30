# 业务运维排查助手

基于 **LangChain ReAct Agent** 的 CDN 节点运维智能助手，集成 Streamlit 交互界面，支持设备信息查询、跑量分析、运行状态诊断和命令执行。

## 技术栈

| 层级 | 技术 |
|------|------|
| AI 框架 | LangChain 1.3.11 + LangGraph |
| 大模型 | DeepSeek (通过 OpenAI 兼容接口) |
| 向量库 | ChromaDB + BGE-M3 Embedding |
| 数据源 | 监控平台爬虫 + Grafana Prometheus API |
| 交互界面 | Streamlit |
| 知识库 | RAG 检索增强生成 |

## 项目结构

```
06 Agent实战/
├── app.py                      # Streamlit 入口
├── requirements.txt            # 依赖清单
├── agent/
│   ├── react_agent.py          # ReAct Agent 定义与流式输出
│   └── tools/
│       ├── __init__.py         # 工具统一注册导出
│       ├── common.py           # 共享配置（Prometheus 查询、工具函数）
│       ├── middleware.py        # Agent 中间件（日志、提示词动态切换）
│       ├── node_detail.py      # 工具: 节点详情查询（爬取监控页面）
│       ├── node_traffic.py     # 工具: 节点跑量查询（Grafana PromQL）
│       ├── node_status.py      # 工具: 节点运行状态查询
│       ├── node_cmd.py         # 工具: 节点远程命令执行
│       └── rag_tool.py         # 工具: RAG 知识检索
├── config/
│   ├── tools.yaml              # 监控平台/Grafana/隧道 API 配置
│   ├── prompts.yaml            # 提示词文件路径映射
│   ├── rag.yaml                # LLM / Embedding 模型配置
│   ├── chroma.yaml             # ChromaDB 向量库配置
│   └── agent.yaml              # Agent 扩展配置
├── data/
│   ├── chroma/                 # ChromaDB 持久化目录
│   ├── external/               # 外部数据源
│   │   └── records.csv         # 节点问题记录表
│   ├── md5_text.txt            # 已导入知识库的文件 MD5 记录
│   ├── *.md / *.txt / *.pdf    # 知识库原始文档
├── prompts/
│   ├── main_prompt.txt         # 系统提示词
│   ├── report_prompt.txt       # 报告生成提示词
│   └── rag_summarize_prompt.txt# RAG 总结提示词
├── model/
│   └── factory.py              # 模型工厂（Chat / Embedding）
├── rag/
│   ├── vector_store.py         # 向量库操作（检索/文档加载）
│   └── rag_service.py          # RAG 链式服务
├── utils/
│   ├── config_handler.py       # YAML 配置加载
│   ├── path_tool.py            # 项目根路径工具
│   ├── prompt_loader.py        # 提示词文件加载
│   ├── file_handler.py         # 文件处理（MD5/加载器）
│   └── logger_handler.py       # 日志配置
└── logs/                       # 运行日志（按日期）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

> `langchain==1.3.11` 为自定义构建版本，提供 `create_agent` 及中间件支持。如使用标准版 LangChain，需调整 `agent/react_agent.py` 和 `agent/tools/middleware.py` 的实现。

### 2. 配置

编辑 `config/` 目录下的 YAML 文件：

| 文件 | 必须配置 |
|------|----------|
| `tools.yaml` | `monitor_cookie`、`grafana_cookie`、`tunnel_cmd_cookie` |
| `rag.yaml` | `api_key`（DeepSeek 或兼容 API）、`embeddings_model_local_path` |
| `chroma.yaml` | 一般无需修改，首次需运行知识库加载 |

### 3. 加载知识库（首次）

```bash
python -c "from rag.vector_store import VectorStoreService; VectorStoreService().load_document()"
```

将 `data/` 目录下的 `.txt`、`.md`、`.pdf` 文件向量化存入 ChromaDB。

### 4. 启动

```bash
streamlit run app.py
```

## 工具能力

| 工具 | 功能 | 数据源 |
|------|------|--------|
| `node_detail_query` | 查询节点设备配置、业务状态、任务列表 | 监控平台页面爬虫 |
| `node_traffic_query` | 查询前一日上行跑量（峰值/95值/均值/时序） | Grafana Prometheus |
| `node_status_query` | 查询 CPU/内存/磁盘/Ping/负载状态 | Grafana Prometheus |
| `node_cmd_execute` | 在节点上执行文本 Shell 查询命令 | 隧道 API |
| `rag_summarize` | 从知识库检索专业知识辅助诊断 | ChromaDB 向量库 |
| `fill_context_for_report` | 触发报告生成模式，切换提示词 | — |

## 报告生成流程

触发关键词后 Agent 自动执行：

```
fill_context_for_report → node_detail_query → node_traffic_query → node_status_query → [可选] node_cmd_execute → rag_summarize → 输出完整报告
```

## 工作流

```
用户输入 → ReAct Agent（思考→行动→观察循环）
                ├── 工具调用（查询监控数据）
                ├── RAG 知识补充
                └── 生成回答/报告 → Streamlit 流式输出
```

## 注意事项

- Cookie 凭据会过期，过期后需更新 `config/tools.yaml`
- Embedding 模型路径在 `config/rag.yaml` 中配置，建议使用 HuggingFace Hub 自动下载
- 知识库文件放 `data/` 目录下，支持 `.txt`、`.md`、`.pdf` 格式
