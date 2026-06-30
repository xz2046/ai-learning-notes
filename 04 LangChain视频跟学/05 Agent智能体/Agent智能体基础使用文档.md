# LangChain Agent 智能体基础使用文档

> 整理自 `05 Agent智能体/` 目录下 4 个实战代码练习
> 更新时间：2026-06-24

---

## 目录

1. [Agent 概述](#1-agent-概述)
2. [快速上手：创建第一个 Agent](#2-快速上手创建第一个-agent)
3. [工具定义（@tool 装饰器）](#3-工具定义tool-装饰器)
4. [Agent 调用方式](#4-agent-调用方式)
5. [ReAct 框架与思考流程](#5-react-框架与思考流程)
6. [Middleware 中间件](#6-middleware-中间件)
7. [最佳实践与注意事项](#7-最佳实践与注意事项)

---

## 1. Agent 概述

LangChain Agent（智能体）是一个**能自主决策调用哪些工具的 LLM 应用**。

和普通 Chain 的区别：

| 特性 | Chain | Agent |
|------|-------|-------|
| 决策方式 | 固定流程 | LLM 自主决策 |
| 工具调用 | 手动编排 | 自动判断何时调用 |
| 适用场景 | 确定流程 | 不确定步骤的问题 |
| 调用次数 | 单次 | 可多次（如 ReAct 循环） |

**工作流程**（以 ReAct 为例）：

```
用户提问 → Agent思考 → 调用工具 → 观察结果 → 再思考 → 回答用户
                            ↑________________________↓
                                 循环直至可回答
```

---

## 2. 快速上手：创建第一个 Agent

### 2.1 create_agent 基本用法

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import os


@tool
def get_weather(city: str, date: str) -> dict:
    """查询指定城市指定日期的天气"""
    return {"city": city, "date": date, "weather": "晴天"}


agent = create_agent(
    model=ChatOpenAI(
        model="deepseek-v4-flash",
        api_key=os.environ.get("DEEPSEEK_API_KEY2"),
        base_url="https://api.deepseek.com",
        temperature=0.2,
    ),
    tools=[get_weather],
    system_prompt="""
        你是一个聊天助手。
        回答天气问题时必须基于工具返回结果。
        如果工具返回信息不足，不要猜测，直接说明信息不足。
        如果缺少必要参数，先向用户追问。
    """,
)

res = agent.invoke({"messages": [{"role": "user", "content": "明天西安天气如何？"}]})

for msg in res["messages"]:
    print(type(msg).__name__, msg.content)
```

### 2.2 关键点

- **`create_agent`**：LangChain 新版本推荐的高级 API，一行创建完整 Agent
- **`tools`**：传入工具列表，Agent 会自动判断何时调用
- **`system_prompt`**：指导 Agent 的行为规则、约束条件
- **输入格式**：固定为 `{"messages": [{"role": "user", "content": "..."}]}`
- **输出**：`res["messages"]` 包含所有消息（用户消息、AI 思考、工具调用结果、最终回答）

### 2.3 invoke 的输出结构

调用 `agent.invoke()` 返回的 `res["messages"]` 包含完整的执行轨迹：

```
HumanMessage        → 用户原始提问
AIMessage           → Agent的思考/工具调用请求
ToolMessage         → 工具返回的结果
AIMessage           → Agent基于结果的最终回答
...
```

遍历 `res["messages"]` 可以看到 Agent 的完整决策过程。

---

## 3. 工具定义（@tool 装饰器）

### 3.1 基本工具

```python
from langchain_core.tools import tool


@tool
def get_weather(city: str, date: str) -> dict:
    """查询指定城市指定日期的天气"""
    return {"city": city, "date": date, "weather": "晴天"}
```

**自动推导机制**：
- **函数名** → 工具名（`get_weather`）
- **文档字符串** → 工具描述（LLM 据此判断何时调用）
- **类型注解** → 参数 schema（`city: str` 告诉 LLM 需要传入字符串）
- **返回值** → 工具执行结果，返回给 LLM 继续推理

### 3.2 带 description 的工具

```python
@tool(description="获取股价，传入股票名称，返回字符串信息")
def get_price(name: str) -> str:
    return f"股票{name}的价格是20元"


@tool(description="获取股票信息，传入股票名称，返回字符串信息")
def get_info(name: str) -> str:
    return f"股票{name}，是一家A股上市公司，专注于AI领域。"


agent = create_agent(
    model=...,
    tools=[get_price, get_info],   # 多个工具
    system_prompt="你是一个智能助手，可以回答股票相关问题。",
)
```

**`@tool(description=...)` vs 文档字符串**：
- 如果提供了 `description` 参数，以此为准
- 如果未提供，LLM 使用函数文档字符串作为描述
- **description 越清晰，Agent 选错工具的概率越低**

### 3.3 无参数工具

```python
@tool(description="获取体重，返回值是整数，单位千克")
def get_weight() -> int:
    return 90

@tool(description="获取身高，返回值是整数，单位厘米")
def get_height() -> int:
    return 172
```

工具可以有零个或多个参数，LLM 会自动从对话中提取参数值。

### 3.4 工具定义规范

| 要素 | 作用 | 建议 |
|------|------|------|
| 函数名 | 工具标识 | 用英文动词开头，如 `get_weather` |
| 文档字符串/description | 告知 LLM 何时调用 | 写清楚功能、参数含义、返回值 |
| 参数类型注解 | LLM 知道传什么类型 | 必写 `str`、`int`、`float` 等 |
| 返回值类型注解 | 清晰的返回结构 | 必写，方便 LLM 解析 |

---

## 4. Agent 调用方式

### 4.1 invoke（同步调用）

```python
res = agent.invoke({"messages": [{"role": "user", "content": "明天西安天气如何？"}]})
```

返回完整结果后才继续，适合不需要实时展示的场景。

### 4.2 stream（流式输出）

实时展示 Agent 的思考过程和工具调用，体验更好。

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "deepseek股价多少，并介绍一下"}]},
    stream_mode="values"    # 每次迭代输出完整状态
):
    latest_message = chunk['messages'][-1]

    if latest_message.content:
        print(type(latest_message).__name__, latest_message.content)

    try:
        if latest_message.tool_calls:
            print(f"工具调用：{[tc['name'] for tc in latest_message.tool_calls]}")
    except AttributeError:
        pass
```

**stream_mode 参数**：

| mode | 含义 |
|------|------|
| `"values"` | 每次迭代输出当前完整状态，包含所有消息（推荐） |
| `"messages"` | 只输出增量消息（每次一个新消息片段） |

**流式输出中检测工具调用的模式**：

```python
for chunk in agent.stream({"messages": [...]}, stream_mode="values"):
    latest = chunk['messages'][-1]

    # 1. 打印思考内容
    if latest.content:
        print(f"[思考] {latest.content}")

    # 2. 检测是否触发了工具调用
    try:
        if latest.tool_calls:
            for tc in latest.tool_calls:
                print(f"[工具] {tc['name']}({tc['args']})")
    except AttributeError:
        pass
```

---

## 5. ReAct 框架与思考流程

### 5.1 ReAct 是什么

ReAct（Reasoning + Acting）是一种**让 LLM 交替思考和行动的框架**：

```
思考 (Thought) → 行动 (Action/Observe) → 再思考 → 再行动 → 最终回答
```

每个步骤只能调一个工具，观察结果后再决定下一步。

### 5.2 ReAct 案例

```python
@tool(description="获取体重，返回值是整数，单位千克")
def get_weight() -> int:
    return 90

@tool(description="获取身高，返回值是整数，单位厘米")
def get_height() -> int:
    return 172

agent = create_agent(
    model=ChatOpenAI(...),
    tools=[get_weight, get_height],
    system_prompt="""你是严格遵循ReAct框架的智能体，必须按「思考→行动→观察→再思考」的流程解决问题，
且**每轮仅能思考并调用1个工具**，禁止单次调用多个工具。
并告知我你的思考过程，工具的调用原因，按思考、行动、观察三个结构告知我""",
)

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "计算我的BMI"}]},
    stream_mode="values"
):
    latest_message = chunk['messages'][-1]
    if latest_message.content:
        print(type(latest_message).__name__, latest_message.content)
    try:
        if latest_message.tool_calls:
            print(f"工具调用：{[tc['name'] for tc in latest_message.tool_calls]}")
    except AttributeError:
        pass
```

### 5.3 ReAct 执行流程示例

以「计算BMI」为例，Agent 的执行轨迹：

```
# 第1步：用户提问
HumanMessage: 计算我的BMI

# 第2步：思考 → 需要先获取体重
AIMessage: [思考] 用户需要计算BMI，BMI=体重(kg)/身高(m)²。我需要先获取用户的体重...
Tool_calls: get_weight

# 第3步：工具返回
ToolMessage: 90

# 第4步：思考 → 还需要身高
AIMessage: [思考] 体重是90kg，接下来需要获取身高...行动: get_height
Tool_calls: get_height

# 第5步：工具返回
ToolMessage: 172

# 第6步：综合结果，最终回答
AIMessage: 您的BMI=90/(1.72)²≈30.4，属于肥胖范围...
```

**关键约束**：每轮只能调 **1 个工具**，这是 ReAct 的核心理念——每次只获取一条信息，逐步推理。

### 5.4 ReAct vs 多工具并行调用

| 模式 | 特点 | 适用场景 |
|------|------|---------|
| ReAct（单步） | 每轮1个工具，逐步推理 | 步骤依赖的逻辑（先A后B） |
| 并行调用 | 一次喊多个工具 | 独立信息（同时查天气+查新闻） |

默认情况下，LLM 可能一次调用多个工具。通过在 `system_prompt` 中明确约束来启用 ReAct 模式。

---

## 6. Middleware 中间件

### 6.1 什么是 AgentMiddleware

中间件是 Agent 在运行过程中插入的自定义钩子（hook），可以在**Agent 的生命周期关键节点**执行自定义逻辑，如日志、监控、权限校验、参数改造等。

### 6.2 中间件生命周期

```
        before_agent()
              │
              ▼
        before_model()
              │
         ┌────┴────┐
         │ 模型调用  │ ← wrap_model_call()
         └────┬────┘
              │
        after_model()
              │
         ┌────┴────┐
         │ 是否调工具│——否——→ after_agent() → 结束
         └────┬────┘
              │ 是
         ┌────┴────┐
         │ 工具执行  │ ← wrap_tool_call()
         └────┬────┘
              │
              └——→ before_model() 再次循环...
```

### 6.3 完整中间件示例

```python
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import AgentMiddleware
from langgraph.runtime import Runtime


class MyMiddleware(AgentMiddleware):
    """Agent 启动前"""
    def before_agent(self, state: AgentState, runtime: Runtime) -> None:
        print(f"[before_agent] agent启动，并附带 {len(state['messages'])} 条消息")

    """Agent 结束后"""
    def after_agent(self, state: AgentState, runtime: Runtime) -> None:
        print(f"[after_agent] agent结束，并附带 {len(state['messages'])} 条消息")

    """模型即将调用前"""
    def before_model(self, state: AgentState, runtime: Runtime) -> None:
        print(f"[before_model] 模型即将调用，并附带 {len(state['messages'])} 条消息")

    """模型调用结束后"""
    def after_model(self, state: AgentState, runtime: Runtime) -> None:
        print(f"[after_model] 模型调用结束，并附带 {len(state['messages'])} 条消息")

    """模型调用拦截（可修改请求/响应）"""
    def wrap_model_call(self, request, handler):
        print("模型调用啦")
        return handler(request)     # 必须调用 handler 放行

    """工具调用拦截（可修改参数/结果）"""
    def wrap_tool_call(self, request, handler):
        print(f"工具执行：{request.tool_call['name']}")
        print(f"工具执行传入参数：{request.tool_call['args']}")
        return handler(request)     # 必须调用 handler 放行


agent = create_agent(
    model=ChatOpenAI(...),
    tools=[get_weather],
    middleware=[MyMiddleware()],        # 传入中间件实例列表
    system_prompt="你是一个聊天助手,回答用户问题。",
)
```

### 6.4 各钩子方法说明

| 方法 | 触发时机 | 典型用途 |
|------|---------|---------|
| `before_agent(state, runtime)` | Agent 启动，第一次 LLM 调用前 | 初始化上下文、记录开始时间 |
| `after_agent(state, runtime)` | Agent 完全结束 | 统计耗时、记录对话摘要 |
| `before_model(state, runtime)` | 每次 LLM 调用前 | 注入额外提示、限制上下文 |
| `after_model(state, runtime)` | 每次 LLM 调用后 | 校验输出格式、记录日志 |
| `wrap_model_call(request, handler)` | 模型调用拦截 | 修改请求参数、添加重试逻辑 |
| `wrap_tool_call(request, handler)` | 工具调用拦截 | 参数校验、权限检查、结果缓存 |

**重要**：`wrap_model_call` 和 `wrap_tool_call` **必须调用 `handler(request)`** 放行，否则 Agent 会卡死。

### 6.5 中间件在 Agent 中的执行结果

以查天气为例，中间件输出顺序：

```
[before_agent] agent启动，并附带 1 条消息
[before_model] 模型即将调用，并附带 1 条消息
模型调用啦
[after_model] 模型调用结束，并附带 2 条消息
工具执行：get_weather
工具执行传入参数：{'city': '深圳'}
[before_model] 模型即将调用，并附带 ... 条消息
模型调用啦
[after_model] 模型调用结束，并附带 ... 条消息
[after_agent] agent结束，并附带 ... 条消息
```

可以看到每次 Agent 调用都会触发完整的钩子链。

---

## 7. 最佳实践与注意事项

### 7.1 Agent 设计原则

1. **工具描述要精确**：LLM 靠描述决定调哪个工具，`"获取体重"` 比 `"get_weight"` 好
2. **参数类型标注要完整**：`city: str, date: str` 让 LLM 知道传什么
3. **system_prompt 约束行为**：明确什么情况调工具、什么情况直接回答、什么情况追问
4. **temperature 建议 0.2 以下**：Agent 决策需要确定性，高 temperature 容易选错工具
5. **让 Agent 展示思考过程**：在 system_prompt 中要求输出推理过程，方便调试

### 7.2 invoke vs stream 选择

| 方式 | 适用场景 |
|------|---------|
| `agent.invoke()` | 后端处理、不需要实时反馈 |
| `agent.stream(stream_mode="values")` | 用户可见的交互场景，实时展示思考过程 |

### 7.3 tool_calls 的检测

```python
# 安全检测 tool_calls（某些消息类型没有该属性）
try:
    if latest_message.tool_calls:
        for tc in latest_message.tool_calls:
            print(f"{tc['name']}({tc['args']})")
except AttributeError:
    pass
```

`tool_calls` 的结构：

```python
[
    {
        "name": "get_weather",      # 工具名
        "args": {"city": "西安"},    # 参数
        "id": "call_xxx"            # 调用ID
    },
    ...
]
```

### 7.4 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| Agent 不调工具 | 工具描述不够清晰 | 完善 `description`/文档字符串 |
| Agent 调错工具 | 多个工具描述有歧义 | 让描述更具体，区分边界 |
| Agent 一次调太多工具 | 默认并行调用 | system_prompt 明确约束每轮1个 |
| 工具参数传错 | 参数名/类型不清晰 | 加上类型注解和参数说明 |
| Agent 循环不停 | 工具返回不满足LLM预期 | 检查工具返回格式是否清晰 |

### 7.5 学习路线

```
文件编号              内容                          掌握要点
───────  ─────────────────────────────────  ─────────────────────────
01      智能体初体验         create_agent + @tool + invoke + 消息结构
02      Agent流式输出       stream + 多工具 + tool_calls 实时检测
03      ReAct案例          思考→行动→观察循环 + 单步工具调用
04      middleware中间件    AgentMiddleware 生命周期钩子
```

从 01 到 04 依次学习，先掌握基础创建和调用，再理解 ReAct 思维框架，最后通过中间件深入 Agent 执行机制。
