# MCP 服务学习笔记

## 1. 先说结论

**MCP（Model Context Protocol）可以理解成“大模型与外部工具/数据源之间的标准化连接协议”。**

它的价值不在于“又多了一种调用工具的方法”，而在于把原本零散、私有、各写各的工具接入方式，抽成了一套更统一的协议层。这样模型框架、客户端、工具服务可以解耦：

- **模型/Agent 框架** 负责推理与编排
- **MCP Client** 负责连接 MCP Server
- **MCP Server** 负责把地图、数据库、文件系统、内部系统 API 等能力暴露为标准工具

如果用一句话概括：**MCP 是给 LLM 生态做“工具接口标准化”的。**

---

## 2. MCP 的概念与定位

### 2.1 MCP 是什么

MCP 是一个面向大模型上下文与工具扩展的协议。它希望解决的问题是：

- 不同应用接工具方式各不相同，难复用
- 工具描述、调用参数、返回结果缺少统一抽象
- 模型、客户端、工具服务之间强耦合

有了 MCP 后，工具服务不再只是一段“框架私有函数”，而是一个对外提供能力的 **MCP Server**。模型应用通过 **MCP Client** 去发现并调用它提供的工具。

---

### 2.2 MCP 里的几个核心角色

可以把 MCP 生态拆成四个角色：

- **Host**：承载大模型应用的宿主环境，比如桌面客户端、IDE、聊天系统、Agent 平台
- **MCP Client**：负责和 MCP Server 建立连接，发起请求，读取工具定义和调用结果
- **MCP Server**：真正对外提供工具能力的服务端
- **LLM / Agent**：决定什么时候调用什么工具，并消费返回结果

在很多框架中，Host、Client、Agent 可能跑在同一个应用里，但概念上最好分开理解。

---

### 2.3 MCP 提供的能力类型

通常可把 MCP 能力理解成三类：

- **Tools**：可调用操作，比如搜索地图、查天气、执行数据库查询
- **Resources**：可读取的资源，比如文件、文档、配置
- **Prompts**：可复用的提示模板

在实际接入中，**Tools 最常用**，因为绝大多数业务需要的是“让模型调用外部动作”。

---

## 3. MCP 的核心价值

MCP 真正有意义的地方，不是“模型能调用地图”这种表面能力，而是下面这几个工程价值：

### 3.1 标准化

过去每个工具都要单独适配框架函数签名、参数格式、认证方式。MCP 提供统一协议后，接入和迁移成本会下降。

### 3.2 解耦

工具服务可独立演进，不必深度绑定某个 Agent 框架。理论上，支持 MCP 的不同客户端都能复用同一个服务。

### 3.3 可发现性

Client 可以动态获取 Server 暴露的工具列表、参数 schema、描述信息，这让 Agent 更容易做自动化工具选择。

### 3.4 更利于企业内部能力封装

企业可以把内部知识库、CRM、工单系统、数据查询接口统一封成 MCP Server，对外只暴露协议层，不暴露内部实现细节。

---

## 4. MCP 与传统工具调用方式的区别

传统 LangChain / Agent 工具调用通常是这样：

- 在本地 Python 里写 `@tool`
- 把函数注册给 agent
- agent 决定要不要调这个函数

这种方式简单，但局限也明显：

- 工具往往只能在当前代码进程内用
- 不同框架之间难复用
- 工具管理、权限控制、远程复用能力较弱

MCP 的思路则是：

- 工具作为一个服务被标准化暴露
- Agent 不一定和工具在同一进程
- 工具可以通过本地进程启动，也可以通过远程 HTTP 暴露

因此可以把两者理解为：

- **本地 Tool**：适合简单、轻量、单项目场景
- **MCP Tool Service**：适合复用、标准化、跨系统接入场景

---

## 5. MCP 的典型通信方式

从你给的高德示例看，至少有两类常见接入模式：

### 5.1 stdio 模式

```json
{
  "mcpServers": {
    "amap-maps": {
      "command": "npx",
      "args": ["-y", "@amap/amap-maps-mcp-server"],
      "env": {
        "AMAP_MAPS_API_KEY": "你的key"
      }
    }
  }
}
```

这种模式本质上是：

- Client 启动一个本地子进程
- 通过标准输入输出和它通信

特点是本地化、隔离性较好，适合桌面客户端、开发环境、本地工具型服务。

### 5.2 Streamable HTTP / Remote HTTP 模式

```json
{
  "mcpServers": {
    "amap-maps-streamableHTTP": {
      "url": "https://mcp.amap.com/mcp?key=你的key"
    }
  }
}
```

这种模式本质上是：

- MCP Server 已经部署在远端
- Client 通过 HTTP 访问

特点是部署方便、易共享，但也更依赖网络、认证、限流和服务端稳定性。

---

## 6. 高德 MCP 服务示例理解

你给的两个配置本质上都指向同一类能力：**让大模型通过 MCP 协议调用高德地图相关服务**，例如地点搜索、地理编码、路线规划、周边查询等。

### 6.1 本地进程版

```json
{
  "mcpServers": {
    "amap-maps": {
      "command": "npx",
      "args": ["-y", "@amap/amap-maps-mcp-server"],
      "env": {
        "AMAP_MAPS_API_KEY": "你的高德 Key"
      }
    }
  }
}
```

适合：

- 本地开发
- 在支持 MCP 的桌面客户端中测试
- 不想自己部署远端服务

### 6.2 远程 HTTP 版

```json
{
  "mcpServers": {
    "amap-maps-streamableHTTP": {
      "url": "https://mcp.amap.com/mcp?key=你的高德 Key"
    }
  }
}
```

适合：

- 快速接入
- 不希望本地安装 Node 工具
- 在支持远程 MCP 的客户端中直接配置

---

## 7. API Key 使用建议

你已经有高德 Key，但**不要把真实 Key 直接写进公开代码、笔记截图、仓库或前端页面里**。正确做法是走环境变量或本地配置。

例如本地 shell：

```bash
set AMAP_MAPS_API_KEY=你的key
```

或 `.env`：

```env
AMAP_MAPS_API_KEY=你的key
```

然后在配置里引用它，而不是明文硬编码。

---

## 8. LangChain / LangGraph 为什么会关心 MCP

MCP 不是 LangChain 专属协议，但 **LangChain / LangGraph 可以作为 MCP Client 的接入层**。它们适合做的事包括：

- 读取 MCP Server 暴露的工具
- 把 MCP Tools 交给 Agent
- 由模型判断什么时候调用哪一个工具
- 把工具结果并入对话流程或状态图

也就是说，MCP 解决的是“工具如何标准化暴露”，LangChain / LangGraph 解决的是“模型如何推理、编排、调用这些工具”。

---

## 9. LangChain MCP 接入思路

这里先讲思路，再给示例。

典型流程是：

1. 配置 MCP Server（本地 stdio 或远程 HTTP）
2. 用 MCP Client 连接服务
3. 获取 server 提供的 tools
4. 转成 LangChain 可用工具对象
5. 交给 agent 或 graph 节点使用

不同版本库的 API 可能略有变化，但整体思想一致：**连接 MCP Server，然后把工具适配到 LangChain。**

---

## 10. LangChain 接入高德 MCP 的示例思路

下面给一个“学习用示意代码”，展示典型接入结构。注意：**MCP 相关 Python 生态近期变化较快，不同版本包名和 API 可能不同，以下代码应按你本地版本微调。** 重点看接入思路。

### 10.1 示例：连接远程高德 MCP 并获取工具

```python
import os
from langchain_openai import ChatOpenAI

# 以下导入路径可能随 MCP / LangChain 版本变化
# 重点看思路：创建 MCP client -> 拉取 tools -> 交给 agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)


client = MultiServerMCPClient(
    {
        "amap-maps": {
            "url": f"https://mcp.amap.com/mcp?key={os.environ.get('AMAP_MAPS_API_KEY')}"
        }
    }
)

# 获取 MCP tools
tools = client.get_tools()

agent = create_react_agent(llm, tools)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "帮我查一下北京南站附近的咖啡店，并给出通俗一点的出行建议"
            }
        ]
    }
)

print(result)
```

这段代码的关键不在每个 API 名字，而在结构：

- `MultiServerMCPClient` 负责管理一个或多个 MCP Server
- `get_tools()` 把 MCP Server 暴露的工具转换成 LangChain / LangGraph 可用工具
- `create_react_agent()` 把这些工具交给 agent 使用

如果你只看本质，就是：**MCP 提供工具，LangChain Agent 消费工具。**

---

### 10.2 stdio 模式接入高德 MCP 的示意

```python
import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

client = MultiServerMCPClient(
    {
        "amap-maps": {
            "command": "npx",
            "args": ["-y", "@amap/amap-maps-mcp-server"],
            "env": {
                "AMAP_MAPS_API_KEY": os.environ.get("AMAP_MAPS_API_KEY")
            }
        }
    }
)

tools = client.get_tools()
agent = create_react_agent(llm, tools)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "帮我查上海虹桥站附近适合商务会面的餐厅"
            }
        ]
    }
)

print(result)
```

这版更接近你给的高德配置。

---

## 11. 如果只想在 LangGraph 节点里调用 MCP

不一定非要把 MCP 工具全交给 ReAct Agent。有些业务更适合在 LangGraph 节点中显式调用工具，流程更可控。

例如：

- 第一步识别用户是否需要地图服务
- 第二步调用高德 MCP 查地点
- 第三步把结果整理成自然语言

示意代码：

```python
import os
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_mcp_adapters.client import MultiServerMCPClient


llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

client = MultiServerMCPClient(
    {
        "amap-maps": {
            "url": f"https://mcp.amap.com/mcp?key={os.environ.get('AMAP_MAPS_API_KEY')}"
        }
    }
)

tools = {tool.name: tool for tool in client.get_tools()}


class MapState(TypedDict):
    user_query: str
    tool_result: str
    final_answer: str


def call_map_tool(state: MapState):
    # 假设存在一个可用的搜索工具，具体工具名以实际 server 返回为准
    tool = tools.get("search_places")
    if not tool:
        return {"tool_result": "未找到 search_places 工具"}

    result = tool.invoke({"query": state["user_query"]})
    return {"tool_result": str(result)}


def answer_node(state: MapState):
    prompt = (
        f"用户问题：{state['user_query']}\n"
        f"地图工具返回结果：{state['tool_result']}\n"
        "请基于工具结果给出简洁、准确、通俗的中文回答。"
    )
    response = llm.invoke(prompt)
    return {"final_answer": response.content}


builder = StateGraph(MapState)
builder.add_node("call_map_tool", call_map_tool)
builder.add_node("answer_node", answer_node)
builder.add_edge(START, "call_map_tool")
builder.add_edge("call_map_tool", "answer_node")
builder.add_edge("answer_node", END)

app = builder.compile()

result = app.invoke({"user_query": "查一下广州塔附近适合亲子游的景点", "tool_result": "", "final_answer": ""})
print(result["final_answer"])
```

这类写法的优点是：**流程清楚、权限好控、行为可预测**。缺点是灵活性不如让 agent 自主决策调用。

---

## 12. 个人 MCP 服务的实现思路

如果你不只是想接第三方 MCP，而是想自己写一个 MCP Server，本质上就是：**把你自己的能力按 MCP 协议暴露出去。**

这个能力可以是：

- 调用你自己的业务 API
- 访问本地文件
- 查询数据库
- 操作内部系统
- 封装一个知识库搜索接口

---

## 13. 一个最小个人 MCP 服务示意

下面给一个偏学习用的 Python 示例，演示“暴露一个天气查询工具”的思路。注意：MCP Python SDK 版本也在演化，实际 API 可能略有不同，这里重点是你理解服务端结构。

```python
# server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")


@mcp.tool()
def get_weather(city: str) -> str:
    """查询某个城市的天气信息"""
    fake_data = {
        "北京": "晴，30度",
        "上海": "多云，28度",
        "广州": "阵雨，32度",
    }
    return fake_data.get(city, f"未找到 {city} 的天气信息")


@mcp.tool()
def add(a: int, b: int) -> int:
    """返回两个整数之和"""
    return a + b


if __name__ == "__main__":
    mcp.run()
```

这份代码做了什么：

- 创建了一个 `FastMCP` 服务
- 用装饰器把普通 Python 函数暴露成 MCP 工具
- 客户端连接后可以发现 `get_weather` 和 `add` 这两个工具

这就是“个人 MCP 服务”的最小雏形。

---

## 14. 个人 MCP 服务的客户端配置示例

如果是本地 stdio 启动，可能会类似：

```json
{
  "mcpServers": {
    "demo-server": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
```

如果你的客户端支持 MCP，这样就能把你本地的 `server.py` 当成一个 MCP Server 来接。

---

## 15. 个人 MCP 服务在业务里怎么设计

一个能用的个人或团队 MCP 服务，通常不只是“写几个函数”这么简单，更重要的是下面几层：

- **协议层**：符合 MCP 规范，对外暴露工具
- **业务层**：真正执行业务逻辑
- **权限层**：谁能调什么工具、能调到什么范围
- **审计层**：记录工具调用日志、参数、结果、错误
- **隔离层**：防止高危操作直接裸奔

如果你做企业内部 MCP，这几层比“函数能不能跑”更重要。

---

## 16. MCP 服务的典型风险

这是必须认真看的一节。MCP 的风险并不小，因为它本质上是在给模型“开工具权限”。

### 16.1 权限过大

如果 MCP 工具直接能访问数据库、文件系统、内部管理接口，而没有严格权限边界，模型一旦误调、被诱导调用，风险很高。

### 16.2 Prompt Injection / Tool Injection

用户可能通过输入诱导模型执行高风险工具调用，例如：

- 读取敏感文件
- 导出内部数据
- 调用删除类接口
- 执行越权查询

所以不能因为“模型决定要调用”就默认可信。

### 16.3 远程 MCP Server 可信度问题

如果接的是第三方远程 MCP Server，你实际上是在把部分能力委托给外部服务。风险包括：

- 服务返回结果不可靠
- 数据会不会被记录
- 是否存在恶意工具定义
- 是否存在供应链风险

### 16.4 参数污染与数据泄露

模型自动生成的工具参数可能不稳定，若缺少严格 schema 校验、白名单和长度限制，可能把隐私数据、认证信息、业务关键字段带出去。

### 16.5 结果不可控

模型可能误用工具、重复调用、串联错误结果，导致：

- 成本上升
- 请求风暴
- 用户得到错误建议
- 对外部服务造成不必要压力

### 16.6 命令执行型服务风险

stdio 模式常通过本地命令启动 MCP Server。如果命令来源不可信、包未审查、版本不固定，就有执行恶意代码的风险。

---

## 17. 风险控制建议

MCP 不可怕，关键是别裸奔。比较稳的控制方法包括：

- **最小权限原则**：只暴露必要工具，不给模型超范围能力
- **参数校验**：对工具参数做 schema 校验、白名单约束、长度限制
- **高危操作二次确认**：涉及写操作、删除操作、导出操作必须人工确认
- **日志审计**：记录谁在什么上下文下调用了什么工具
- **工具分级**：低风险工具允许自动调用，高风险工具必须审批
- **服务白名单**：只接可信的 MCP Server
- **限流与熔断**：避免模型失控重试造成风暴
- **密钥管理**：API Key 放环境变量，不进代码仓库

一句话讲：**MCP 的风险不在协议本身，而在“把什么能力、以什么权限、交给谁、在什么条件下调用”。**

---

## 18. 高德 MCP 这种服务的特有注意点

像高德地图这类 MCP，风险主要集中在三类：

- **Key 泄露**：明文写在脚本、截图、仓库里
- **配额消耗**：Agent 调用过多，导致接口额度被打爆
- **错误信赖**：地图返回结果有时也可能不完整或需要用户二次确认

实践上建议：

- 统一通过环境变量保存 `AMAP_MAPS_API_KEY`
- 给地图类查询做频率控制
- 对路线/地点类结果做二次自然语言整理，不要把原始工具输出直接甩给用户

---

## 19. 学习 MCP 最推荐的路线

如果你是从 LangChain / LangGraph 背景切过来，建议按这个顺序学：

1. 先理解 MCP 是 **协议层**，不是某个单一 SDK
2. 再理解 MCP Server / Client / Host / Tool 的角色划分
3. 接一个现成服务，例如高德 MCP
4. 再自己写一个最小个人 MCP Server
5. 最后补权限、审计、风险控制设计

这样比较稳，不会一上来就被生态细节绕晕。

---

## 20. 最小可复用示例：个人 MCP + LangChain Agent 的概念串联

下面用两段最小代码把“自己写 MCP 服务”和“LangChain 接 MCP”串起来。

### 20.1 服务端

```python
# my_mcp_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-tools")


@mcp.tool()
def search_kb(keyword: str) -> str:
    """搜索个人知识库"""
    data = {
        "langgraph": "LangGraph 适合做状态图驱动的 agent 和工作流编排。",
        "mcp": "MCP 是模型上下文协议，用于标准化工具与资源接入。",
    }
    return data.get(keyword.lower(), "未找到相关知识")


if __name__ == "__main__":
    mcp.run()
```

### 20.2 客户端/Agent 侧

```python
import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

client = MultiServerMCPClient(
    {
        "my-tools": {
            "command": "python",
            "args": ["my_mcp_server.py"]
        }
    }
)

tools = client.get_tools()
agent = create_react_agent(llm, tools)

result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "帮我查一下 langgraph 是做什么的"}
        ]
    }
)

print(result)
```

这两段连起来，你就能完整理解：

- MCP Server 负责暴露工具
- LangChain / LangGraph 负责让模型使用工具
- 模型不需要知道工具内部怎么实现，只需要知道“有什么工具可用”

---

## 21. 总结

MCP 的核心价值可以压成四句话：

1. **MCP 是大模型连接外部工具/资源的标准协议层。**
2. **LangChain / LangGraph 可以作为 MCP Client 的接入与编排层。**
3. **现成 MCP 服务可直接复用，个人也可以把本地函数或业务 API 封装成 MCP Server。**
4. **MCP 真正的难点不是“能不能接上”，而是权限、审计、稳定性和风险控制。**

如果你后面要继续深入，最值得补的两步是：

- 做一版 **LangGraph + 高德 MCP 的完整可运行项目**
- 再做一版 **个人 MCP Server + 权限控制 + 日志审计** 的实战示例
