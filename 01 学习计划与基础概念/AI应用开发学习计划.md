# AI 应用开发学习计划

## 学习目标

8 周后独立做出一个 AI 助手：**能回答运维知识、能分析日志、能按需调用工具、能用 FastAPI 提供接口、能用 Docker 跑起来**。

## 总原则

每周只做三件事：

- **学概念**
- **写最小 demo**
- **做一次复盘**

核心原则：**每一阶段都要产出能运行的东西**。

---

## 第 1 周：LLM、Prompt、Token、Embedding、RAG

### 本周目标
把基础概念搞清楚，能用自己的话解释。

### 需要掌握
- **LLM**：根据上下文生成文本
- **Token**：模型切分后的基本单位
- **Context Window**：一次能带进去多少上下文
- **Temperature**：控制发散程度
- **Prompt**：你怎么给任务
- **Embedding**：把文本映射成向量
- **RAG**：检索相关资料后再回答
- **Tool Calling**：需要外部能力时调用函数/工具

### 本周任务
写一份笔记：`AI应用开发基础概念.md`

至少写清楚：
- 什么是 LLM
- 什么是幻觉
- RAG 解决什么问题
- Tool Calling 和 RAG 的区别
- 为什么上下文不是越长越好

### 推荐资料
**中文文档/文章**
- OpenAI 官方文档的中文解读文章：用于扫盲，定义以官方原文为准
- LangChain 中文文档：适合了解概念，不适合当第一手原理资料
- 阮一峰 / 科技爱好者周刊中与 AI 工程相关的文章

**中文视频关键词（B 站）**
- `大模型 RAG 入门`
- `Prompt 工程 入门`
- `Embedding 向量数据库`
- `Function Calling 工具调用`

**英文主资料**
- OpenAI Docs
- FAISS / Chroma 官方文档
- FastAPI 官方文档

### 验收标准
- 能解释 LLM、RAG、Embedding、Tool Calling 的关系
- 能说清楚幻觉为什么发生
- 能说明为什么上下文不是越长越好

---

## 第 2 周：Python 直接调模型 API

### 本周目标
不用框架，直接用 Python 调通模型 API。

### 需要掌握
- Python 请求模型 API
- `.env` 管理 key
- 单轮问答
- 多轮对话
- JSON 结构化输出
- 超时和异常处理

### 本周最小项目
项目名：`week2_llm_api_demo`

目录建议：

```bash
week2_llm_api_demo/
  main.py
  multi_chat.py
  structured_output.py
  requirements.txt
  .env.example
  README.md
```

### 你要完成的程序
1. **单轮问答**
2. **多轮对话**
3. **结构化输出**

结构化输出目标示例：

```json
{
  "question_type": "ops",
  "summary": "...",
  "need_rag": true
}
```

### 推荐资料
**中文**
- B 站：`Python 调用 OpenAI API`
- 掘金 / CSDN：只看最近一年内的文章

**官方文档**
- OpenAI API Docs
- python-dotenv 文档

### 验收标准
- 能自己读取环境变量
- 能发请求并处理报错
- 能做多轮对话
- 能控制输出格式

---

## 第 3 周：Prompt、输出约束、基础评估

### 本周目标
学会控制模型输出，不只会“调 API”。

### 需要掌握
- 系统提示词怎么写
- 少样本提示（few-shot）
- 如何约束模型按指定格式输出
- 如何让模型“不知道就说不知道”
- 基础评估思路

### 本周最小项目
项目名：`week3_prompt_eval_demo`

需要写 3 套 prompt：
1. **摘要 prompt**
2. **分类 prompt**
3. **运维问答 prompt**

运维问答输出格式：

```markdown
问题判断:
可能原因:
建议步骤:
风险提示:
```

### 练习方式
准备 10 个问题，测试 prompt 改前和改后的稳定性差异。

### 推荐资料
**中文**
- B 站：`Prompt 工程 实战`
- 公众号 / 知乎：只看具体案例，不看空泛方法论

### 验收标准
- 知道同一问题为什么 prompt 改一下结果会差很多
- 知道结构化输出为什么更适合业务系统
- 知道评估不能只靠主观感觉

---

## 第 4 周：做第一个 RAG

### 本周目标
做出“本地文档问答”系统。

### 技术建议
- Python
- 本地 markdown/txt 文档
- FAISS 或 Chroma
- 一个 embedding 模型/API

### 本周最小项目
项目名：`week4_simple_rag`

目录建议：

```bash
week4_simple_rag/
  data/
    docs/
  ingest.py
  ask.py
  retriever.py
  llm.py
  requirements.txt
  README.md
```

### 本周任务拆分
- Day 1：准备 10~20 篇 markdown/txt 文档
- Day 2：切块，尝试 `chunk_size=500`、`chunk_overlap=100`
- Day 3：做 embedding 和向量库存储
- Day 4：输入问题，返回 top-k 文档片段
- Day 5：拼接上下文生成答案
- Day 6：答案加引用
- Day 7：调整 `top_k`、`chunk_size`、prompt 模板

### 推荐资料
**中文文档/文章**
- `RAG 入门 FAISS Python`
- `Chroma 向量数据库 教程`

**中文视频关键词（B 站）**
- `RAG 实战 Python`
- `LangChain RAG 教程`

### 验收标准
- 能回答文档中的事实问题
- 答案带来源
- 不知道时明确说不知道
- 改参数后知道效果为什么变化

---

## 第 5 周：做成运维知识助手

### 本周目标
把通用 RAG 改造成运维场景助手。

### 需要准备的数据
自己整理一个小型运维知识库，例如：
- `nginx_常见故障.md`
- `mysql_慢查询排查.md`
- `redis_连接异常.md`
- `k8s_pod重启排查.md`
- `linux_磁盘满处理.md`
- `告警处理手册.md`
- `部署回滚流程.md`
- `常见502问题_runbook.md`

### 本周最小项目
项目名：`week5_ops_rag_assistant`

### 要增加的能力
1. **文档元数据**

示例：

```json
{
  "system": "nginx",
  "env": "prod",
  "type": "runbook"
}
```

2. **固定回答格式**

```markdown
### 现象判断
### 可能原因
### 建议排查步骤
### 风险提示
### 参考资料
```

3. **检索过滤**
- 按 `type=runbook`
- 按 `system=nginx`

### 练习问题
- `Nginx 502 一般怎么排查？`
- `Pod 一直 CrashLoopBackOff 怎么办？`
- `Redis 连接超时优先看什么？`

### 推荐资料
**中文资料来源**
- 搜：`SRE runbook`
- 搜：`运维故障排查手册`
- 阿里云 / 腾讯云 / 华为云 文档
- Kubernetes 中文社区文档

### 验收标准
- 回答有步骤，不空泛
- 优先基于知识库回答
- 支持简单过滤
- 风格像故障排查助手

---

## 第 6 周：加日志分析

### 本周目标
让系统具备“看日志”的能力。

### 本周最小项目
项目名：`week6_log_analysis`

### 要实现的功能
输入一段日志，输出：
- 异常摘要
- 可能原因
- 建议下一步动作
- 是否建议检索知识库

### 最小实现方式
先做本地日志文件版：

```bash
logs/
  nginx_error.log
  app.log
```

Python 读取最后几百行后交给模型分析。

### 关键学习点
- 日志太长时怎么截断
- 如何只保留 ERROR/WARN
- 如何提取时间、错误码、服务名
- 如何把日志分析结果再送去 RAG 检索

### 推荐练习
1. 给 nginx 日志做摘要
2. 给应用报错日志做原因分析
3. 从日志提取关键词后检索对应 runbook

### 推荐资料
**中文视频关键词（B 站）**
- `日志分析 大模型`
- `LLM 日志分析`

### 验收标准
- 能从杂乱日志里抓关键报错
- 能输出简洁摘要
- 能把日志和知识库串起来

---

## 第 7 周：加工具调用

### 本周目标
让系统具备“查状态”的能力。

### 核心理解
**RAG 查静态知识，工具调用查动态信息。**

### 本周最小项目
项目名：`week7_ops_tools_agent`

### 先做 mock 工具
例如：

```python
def get_service_status(service_name): ...
def get_recent_alerts(service_name): ...
def get_host_metrics(hostname): ...
def get_pod_restarts(service_name): ...
```

返回假数据示例：

```python
{
  "service": "order-service",
  "status": "degraded",
  "recent_errors": 123
}
```

### 本周任务
1. **问题分类**：判断是知识库、工具还是两者都需要
2. **调工具**：按问题决定调用哪个函数
3. **汇总结果**：把工具结果和 RAG 结果合成最终回答

### 练习题
- `订单服务为什么 5xx 升高？`
- `payment-service 当前状态怎么样？`
- `Pod 重启很多，先查什么？`

### 推荐资料
**中文资料来源**
- 搜：`Function Calling 教程`
- 搜：`工具调用 大模型`

### 验收标准
- 能判断什么时候该调工具
- 调完工具后回答更靠谱
- 工具失败时能降级处理

---

## 第 8 周：FastAPI + Docker 部署

### 本周目标
把前面的能力整合成服务。

### 本周最小项目
项目名：`week8_ops_ai_service`

目录建议：

```bash
week8_ops_ai_service/
  app/
    main.py
    api/
      chat.py
      rag.py
      logs.py
      ops.py
    core/
      config.py
      logger.py
    services/
      llm_service.py
      rag_service.py
      log_service.py
      tool_service.py
    schemas/
      request.py
      response.py
  data/
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env.example
  README.md
```

### 要暴露的接口
- `POST /chat`
- `POST /rag/ask`
- `POST /logs/analyze`
- `POST /ops/ask`

### 本周任务
- Day 1：FastAPI 路由、Pydantic、服务启动
- Day 2：封装 LLM 调用 service
- Day 3：接 RAG
- Day 4：接日志分析
- Day 5：接工具调用
- Day 6：写 Dockerfile
- Day 7：容器测试

### 推荐资料
**中文资料来源**
- FastAPI 中文文档
- Docker 中文教程

重点看：
- Dockerfile
- 镜像 vs 容器
- 端口映射
- volume 挂载
- 环境变量

### 验收标准
- 本地接口可运行
- Swagger 文档可访问
- Docker 能成功启动
- `.env` 配置生效
- 整条链路能演示

---

## 推荐资料清单

### 官方文档
- **OpenAI API Docs**：模型调用、结构化输出、工具调用
- **FastAPI 官方文档**
- **Docker 官方文档**
- **FAISS 官方文档**
- **Chroma 官方文档**

### 中文资料来源建议
- FastAPI 中文文档
- Docker 中文教程
- Kubernetes 中文文档
- 各云厂商运维文档
- 掘金 / 知乎 / CSDN 上最近一年内的实战文章

### 视频关键词（B 站）
- `OpenAI API Python 实战`
- `RAG 入门 实战`
- `FAISS Python 教程`
- `FastAPI 教程`
- `Docker 部署 Python`
- `Function Calling 教程`
- `大模型日志分析`

### 看视频时的筛选标准
优先选：
- 有代码仓库
- 有实际运行演示
- 发布时间较新
- 评论区没有大量“接口过期了”的反馈

---

## 每周固定输出物

每周都交这三样：

1. **一个可运行项目**
2. **一份 README**
3. **一份复盘**：`weekly_review.md`

复盘写三件事：
- 这周学会了什么
- 遇到什么坑
- 下周要补什么

---

## 建议技术栈

### 第 1~6 周
- Python 3.11+
- `requests` 或官方 SDK
- `python-dotenv`
- `pydantic`
- `faiss-cpu` 或 `chromadb`

### 第 7~8 周
- `fastapi`
- `uvicorn`
- `pydantic`
- `docker`

### 可选
- `langchain`
- `llamaindex`

建议：**后补，不要作为第一入口。**

---

## 最后的执行建议

资料顺序按这个来：

1. **官方 API 文档**
2. **一两个中文入门视频**
3. **直接写 demo**
4. **遇到具体问题再查框架文档**

不要走成：

**看一堆中文教程 → 收藏一堆 Agent 视频 → 迟迟不写代码**

那样很容易假学习。