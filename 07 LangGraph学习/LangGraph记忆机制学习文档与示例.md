# LangGraph 最新版短期记忆与长期记忆学习文档

## 1. 先说结论

在 **LangGraph 最新版** 里，可以把记忆分成两类：

- **短期记忆（Short-term Memory）**：一次会话过程中的上下文状态，通常跟着 graph 的 `state` 走，适合保存当前对话消息、当前任务中间结果、临时变量。
- **长期记忆（Long-term Memory）**：跨会话、跨线程、跨时间保存的信息，通常存到外部存储中，比如内存库、数据库、向量库或自定义存储，适合保存用户画像、偏好、历史事实、知识摘要。

如果你现在用的是：

```python
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com",
)
```

那么在 LangGraph 里接入方式基本不变，**重点不在模型怎么配，而在状态怎么设计、检查点怎么持久化、长期记忆怎么读写**。

---

# 2. 先建立整体认知

可以把 LangGraph 想成一个“会流转状态的工作流”。

它的核心不是“连续调用模型”，而是：

- 定义一个 **State（状态）**
- 定义若干 **Node（节点）**
- 节点接收状态，返回状态更新
- graph 在节点之间流转，直到结束

所以“记忆”本质上也是状态管理问题：

- **短期记忆**：保存在 graph 的运行状态里
- **长期记忆**：保存在 graph 外部持久层里，需要时再取回来放进 state

---

# 3. LangGraph 中的短期记忆

## 3.1 什么是短期记忆

短期记忆就是 **当前会话正在使用的上下文**。

比如一个聊天机器人在本轮会话里需要知道：

- 用户刚刚说了什么
- 系统提示词是什么
- 模型已经回复过什么
- 当前任务执行到哪一步
- 工具调用结果是什么

这些都属于短期记忆。

在 LangGraph 里，最常见的承载方式就是：

- `MessagesState`
- 或者自定义 `TypedDict` / `BaseModel` 状态结构

---

## 3.2 最常见的短期记忆：消息历史

对于聊天应用，最常见的 state 是消息列表。

典型思路：

- 用户消息进入 state
- 模型节点读取消息历史
- 生成回复
- 把回复追加回消息历史

这样，后续节点就能看到完整上下文。

### 示例：基于 `MessagesState` 的最小短期记忆

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)


def chatbot(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph = StateGraph(MessagesState)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile()

result = app.invoke(
    {"messages": [HumanMessage(content="我叫小王，记住这个名字")]}
)

print(result)
```

### 这段代码做了什么

`MessagesState` 内部约定了一个 `messages` 字段，用来承载消息列表。

节点里：

```python
response = llm.invoke(state["messages"])
return {"messages": [response]}
```

意思是：

- 把当前完整消息历史发给模型
- 把模型回复追加回状态

这里的“追加”不是你手动拼接，而是 `MessagesState` 的 reducer 帮你处理。

---

## 3.3 为什么说这只是“短期”

因为如果你不做持久化，程序结束、进程重启、用户换线程后，这些状态就没了。

也就是说：

- **graph 运行时有记忆**
- **graph 运行结束后不一定还在**

所以光有 `state` 还不够，要想让会话上下文持续存在，就要配合 **checkpointer（检查点持久化）**。

---

## 3.4 用 Checkpointer 持久化短期记忆

这是 LangGraph 里非常关键的一层。

### 它解决什么问题

假设用户和机器人聊了 20 轮：

- 如果没有持久化，每次调用都得手动带上全部历史
- 有了 checkpointer，LangGraph 可以按 `thread_id` 自动恢复该会话的状态

你可以把它理解成：

- `state` 是“内存里的当前工作区”
- `checkpointer` 是“把工作区快照存起来”

---

## 3.5 使用内存版检查点：适合学习和调试

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)


def chatbot(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

memory = InMemorySaver()
app = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "user-001"}}

result1 = app.invoke(
    {"messages": [HumanMessage(content="我叫小王")]},
    config=config,
)
print(result1["messages"][-1].content)

result2 = app.invoke(
    {"messages": [HumanMessage(content="我叫什么名字？")]},
    config=config,
)
print(result2["messages"][-1].content)
```

### 关键点

这里真正起作用的是：

```python
config = {"configurable": {"thread_id": "user-001"}}
```

LangGraph 会把同一个 `thread_id` 对应的状态串起来。

第二次调用虽然只传了：

```python
{"messages": [HumanMessage(content="我叫什么名字？")]}
```

但它能从检查点里恢复此前的会话消息，所以模型有机会答对。

### 适用场景

- 本地开发
- Demo
- 单进程调试

### 不适用场景

- 生产环境
- 多实例部署
- 进程重启后保留数据

因为 `InMemorySaver` 只存在于当前进程内存里。

---

## 3.6 短期记忆的生产化思路

生产环境一般要用可持久化的 checkpointer，比如数据库方案。

常见方向：

- SQLite：适合本地、小型项目
- Postgres：适合服务端正式环境
- 自定义存储后端：适合已有基础设施

核心原则不变：

- 用 `thread_id` 区分会话
- 用 checkpointer 保存和恢复 state

这样用户一次会话的上下文就不会丢。

---

# 4. LangGraph 中的长期记忆

## 4.1 什么是长期记忆

长期记忆是 **跨会话保留的信息**。

比如：

- 用户叫小王
- 用户喜欢用简洁回答
- 用户是 Python 后端工程师
- 用户曾经把项目部署在 AWS
- 用户长期关注 RAG 和 agent 相关技术

这些信息不属于“这一轮对话临时上下文”，而属于“这个用户长期有效的画像或事实”。

---

## 4.2 为什么不能全塞进短期记忆

因为会出三个问题：

### 1）上下文越来越长
全量聊天记录越积越多，token 成本会越来越高。

### 2）噪音越来越多
很多旧对话其实和当前问题无关，硬塞进去反而干扰模型判断。

### 3）信息稳定性差
“用户的职业”“用户偏好”这类长期信息，不应该依赖某一条历史消息是否正好还在窗口里。

所以长期记忆应该独立存储，在需要时检索回来。

---

## 4.3 长期记忆常见存什么

长期记忆通常分三类：

### 用户画像类
- 姓名
- 职业
- 地区
- 偏好
- 说话风格偏好

### 事实类
- 用户项目名称
- 用户正在做的任务
- 某个实体的固定信息

### 经验总结类
- 用户常见问题模式
- 上次任务的总结
- 过去会话提炼出的摘要

---

## 4.4 长期记忆的实现思路

长期记忆通常不是直接存在 graph state 里，而是：

1. 从对话中抽取值得长期保存的信息
2. 写入外部存储
3. 新会话开始时，按用户 ID / 主题 / 语义检索
4. 把检索结果注入当前 state
5. 再交给模型回答

也就是说：

- **state 是工作区**
- **store 是档案馆**

---

# 5. 短期记忆 vs 长期记忆

| 对比项 | 短期记忆 | 长期记忆 |
|---|---|---|
| 生命周期 | 当前会话/线程 | 跨会话长期存在 |
| 典型内容 | 最近消息、工具结果、任务状态 | 用户画像、稳定事实、偏好、摘要 |
| 存储位置 | graph state + checkpointer | 外部存储/记忆库/数据库/向量库 |
| 使用方式 | 每轮自动参与 graph 流转 | 需要时主动检索并注入 |
| 成本特点 | 上下文长了会涨 token | 检索成本替代全量上下文成本 |
| 典型键 | `thread_id` | `user_id` / `memory_key` / 向量检索 |

一句话理解：

- **短期记忆解决“这段对话别忘”**
- **长期记忆解决“下次见面还记得我”**

---

# 6. 一个完整心智模型

建议你把 LangGraph 记忆设计成三层：

## 第一层：当前输入
本轮用户新发来的内容。

## 第二层：短期记忆
从 checkpointer 恢复的当前线程历史。

## 第三层：长期记忆
从外部 store 检索出来的用户画像、偏好、历史事实。

最后一起组成模型的上下文。

可以理解成：

```text
最终回答 = 当前问题 + 当前会话历史 + 跨会话长期信息
```

---

# 7. 应用示例一：短期记忆聊天机器人

这个例子只关注 **短期记忆**，适合先上手。

## 7.1 代码

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)


def chatbot(state: MessagesState):
    system_prompt = SystemMessage(content="你是一个简洁、友好的中文助手。")
    messages = [system_prompt] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

app = builder.compile(checkpointer=InMemorySaver())

thread_config = {"configurable": {"thread_id": "chat-demo-001"}}

# 第一轮
result = app.invoke(
    {"messages": [HumanMessage(content="我叫李雷，是做前端开发的")]},
    config=thread_config,
)
print("AI:", result["messages"][-1].content)

# 第二轮
result = app.invoke(
    {"messages": [HumanMessage(content="你还记得我的名字和职业吗？")]},
    config=thread_config,
)
print("AI:", result["messages"][-1].content)
```

## 7.2 这个例子学到什么

- `MessagesState` 管消息
- `InMemorySaver` 管线程内的状态保存
- `thread_id` 决定你接着哪条会话往下聊

如果你把 `thread_id` 改掉，相当于开启新会话。

---

# 8. 应用示例二：自定义短期记忆状态

很多业务不只是聊天消息，还会有额外状态，比如：

- 用户名
- 当前任务阶段
- 工具执行结果
- 待办事项

这时就不一定只用 `MessagesState`，可以自定义 state。

## 8.1 代码

```python
import os
from typing import TypedDict, Annotated
from operator import add

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)


class MyState(TypedDict):
    messages: Annotated[list[BaseMessage], add]
    user_name: str
    task_stage: str


def extract_user_info(state: MyState):
    last_user_msg = state["messages"][-1].content
    user_name = state.get("user_name", "")

    if "我叫" in last_user_msg and not user_name:
        try:
            user_name = last_user_msg.split("我叫", 1)[1].split("，")[0].split("。")[0].strip()
        except Exception:
            pass

    return {
        "user_name": user_name,
        "task_stage": "info_extracted",
    }


def reply_node(state: MyState):
    prompt = f"当前用户姓名：{state.get('user_name', '未知')}。请根据对话正常回复。"
    response = llm.invoke(prompt + "\n\n用户输入：" + state["messages"][-1].content)
    return {"messages": [response], "task_stage": "replied"}


builder = StateGraph(MyState)
builder.add_node("extract_user_info", extract_user_info)
builder.add_node("reply_node", reply_node)

builder.add_edge(START, "extract_user_info")
builder.add_edge("extract_user_info", "reply_node")
builder.add_edge("reply_node", END)

app = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "custom-state-001"}}

result = app.invoke(
    {
        "messages": [HumanMessage(content="我叫韩梅梅，最近在准备转型做 AI 应用开发")],
        "user_name": "",
        "task_stage": "start",
    },
    config=config,
)

print(result)
```

## 8.2 这个例子的意义

你会发现短期记忆不只是“聊天历史”，还包括：

- 结构化字段
- 任务执行状态
- 中间处理结果

这才是 LangGraph 的优势：**它的记忆本质是工作流状态，不只是 message history。**

---

# 9. 应用示例三：长期记忆版聊天机器人

下面做一个容易懂的版本：

- 短期记忆：当前 thread 的聊天历史
- 长期记忆：用户画像字典（这里先用 Python dict 模拟数据库）

真实项目里你可以换成 Redis、Postgres、MongoDB、向量库等。

## 9.1 代码

```python
import os
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

# 用 dict 模拟长期记忆库
long_term_memory_store = {
    "user_001": {
        "name": "小王",
        "profession": "Python工程师",
        "preference": "喜欢简洁直接的回答",
    }
}


class InputState(TypedDict):
    messages: list
    user_id: str


def load_memory_and_reply(state: InputState):
    user_id = state["user_id"]
    memory = long_term_memory_store.get(user_id, {})

    memory_text = "\n".join([
        f"用户姓名：{memory.get('name', '未知')}",
        f"用户职业：{memory.get('profession', '未知')}",
        f"回答偏好：{memory.get('preference', '未知')}",
    ])

    system_prompt = SystemMessage(
        content=(
            "你是一个中文助手。以下是用户的长期记忆，请优先利用这些信息回答。\n"
            + memory_text
        )
    )

    response = llm.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}


builder = StateGraph(InputState)
builder.add_node("load_memory_and_reply", load_memory_and_reply)
builder.add_edge(START, "load_memory_and_reply")
builder.add_edge("load_memory_and_reply", END)

app = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "session-1001"}}

result = app.invoke(
    {
        "user_id": "user_001",
        "messages": [HumanMessage(content="请根据我的背景，推荐一个适合我的 LangGraph 学习路径")],
    },
    config=config,
)

print(result["messages"][-1].content)
```

## 9.2 这个例子的重点

这里的长期记忆没有放在会话消息里，而是：

- 根据 `user_id` 去外部 store 取资料
- 临时拼到 system prompt 里
- 再给模型回答

这就是最基础也最常见的长期记忆模式。

---

# 10. 应用示例四：自动写入长期记忆

真正实用的系统不只是“读取长期记忆”，还要能“从对话中自动沉淀长期记忆”。

比如用户说：

- 我叫张三
- 我平时主要写 Java
- 我喜欢回答时少一点废话

这些都值得沉淀。

下面给一个简单规则版示例。

## 10.1 代码

```python
import os
import re
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

long_term_memory_store = {}


class ChatState(TypedDict):
    user_id: str
    messages: list


def save_memory(state: ChatState):
    user_id = state["user_id"]
    text = state["messages"][-1].content

    memory = long_term_memory_store.get(user_id, {})

    name_match = re.search(r"我叫([\u4e00-\u9fa5A-Za-z0-9_]+)", text)
    if name_match:
        memory["name"] = name_match.group(1)

    if "Python" in text:
        memory["profession_or_skill"] = "Python相关开发"
    elif "Java" in text:
        memory["profession_or_skill"] = "Java相关开发"

    if "简洁" in text or "直接" in text:
        memory["reply_preference"] = "简洁直接"

    long_term_memory_store[user_id] = memory
    return {}


def reply(state: ChatState):
    user_id = state["user_id"]
    memory = long_term_memory_store.get(user_id, {})

    memory_text = str(memory)
    system_prompt = SystemMessage(
        content=f"你是中文助手。用户长期记忆如下：{memory_text}"
    )

    response = llm.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}


builder = StateGraph(ChatState)
builder.add_node("save_memory", save_memory)
builder.add_node("reply", reply)

builder.add_edge(START, "save_memory")
builder.add_edge("save_memory", "reply")
builder.add_edge("reply", END)

app = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "thread-a"}}

app.invoke(
    {
        "user_id": "u1001",
        "messages": [HumanMessage(content="我叫张三，是做 Python 开发的，我喜欢简洁直接的回答")],
    },
    config=config,
)

result = app.invoke(
    {
        "user_id": "u1001",
        "messages": [HumanMessage(content="你记得我的偏好吗？")],
    },
    config=config,
)

print(result["messages"][-1].content)
print(long_term_memory_store)
```

## 10.2 这个例子告诉你什么

长期记忆系统至少有两部分：

- **写入策略**：什么时候抽取、抽取什么、如何去重
- **读取策略**：什么时候取、取哪些、怎么注入上下文

规则抽取只是最简单版，实际项目常会升级为：

- LLM 抽取结构化事实
- 写入数据库
- 做冲突合并和版本控制
- 按相关性检索再注入

---

# 11. 更像生产系统的设计方式

如果你要做真正可用的 agent 或聊天产品，建议这么分层。

## 11.1 短期记忆层

职责：维护当前会话上下文。

建议：

- 用 `MessagesState` 或自定义 state
- 用 checkpointer 保存状态
- 通过 `thread_id` 关联会话

适合保存：

- 最近若干轮消息
- 工具调用结果
- 当前任务状态
- 中间变量

---

## 11.2 长期记忆层

职责：保存跨会话的重要信息。

建议：

- 用数据库或 KV 存储保存结构化事实
- 用向量库存语义片段或历史摘要
- 以 `user_id` 为主键做管理

适合保存：

- 用户画像
- 偏好设置
- 历史总结
- 稳定事实

---

## 11.3 记忆编排层

职责：决定什么时候写、什么时候读。

典型流程：

1. 用户发消息
2. 恢复短期记忆
3. 检索长期记忆
4. 组合提示词
5. 模型回答
6. 从本轮对话抽取新长期记忆
7. 写回 store
8. 更新短期状态

这才是比较完整的记忆闭环。

---

# 12. 一个更推荐的实战模式

如果你是做业务系统，我建议采用下面这个套路。

## 模式：短期走线程，长期走用户

### 短期记忆主键
用 `thread_id`

表示：

- 某次具体会话
- 某个任务线程
- 某条工单处理过程

### 长期记忆主键
用 `user_id`

表示：

- 这个用户是谁
- 这个用户长期偏好和历史事实是什么

### 好处

不会把“当前会话上下文”和“跨会话用户画像”混在一起。

这是很重要的边界。

---

# 13. 常见坑

## 13.1 把所有历史都塞给模型

结果：

- token 飙升
- 回复变慢
- 噪音变多

正确做法：

- 短期保留必要上下文
- 长期信息做摘要和检索

---

## 13.2 把长期记忆直接等同于聊天记录

聊天记录只是原材料，不等于长期记忆本身。

长期记忆应该是：

- 抽取后的结构化事实
- 稳定偏好
- 历史摘要

而不是“把 200 轮原始对话全存着”。

---

## 13.3 没有记忆更新策略

用户信息可能变化：

- 职业会变
- 偏好会变
- 项目会结束

所以长期记忆不能只追加不维护。

至少要考虑：

- 覆盖更新
- 时间戳
- 冲突处理
- 可信度评分

---

## 13.4 混淆 `thread_id` 和 `user_id`

这是高频坑。

- `thread_id`：这一次会话是谁
- `user_id`：这个用户是谁

一个用户可以有多个 thread。

---

# 14. 你当前这套 DeepSeek 配置怎么接入

你的模型初始化方式本身可以继续用。

```python
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com",
)
```

只要注意几点：

## 1）安装包
通常需要：

```bash
pip install -U langgraph langchain langchain-openai
```

## 2）导入路径
新版里优先按当前官方包结构使用：

- `from langgraph.graph import StateGraph, START, END`
- `from langgraph.graph import MessagesState`
- `from langgraph.checkpoint.memory import InMemorySaver`

如果你项目版本和本文不一致，少数 import 路径可能会变，优先以你本地安装版本为准。

## 3）DeepSeek 兼容性
`ChatOpenAI` 只要底层接口兼容 OpenAI 风格，通常就能接。如果个别参数行为和 OpenAI 官方模型不同，要以 DeepSeek 实际 API 表现为准。

---

# 15. 推荐学习顺序

建议按这个顺序学，别一上来就做复杂长期记忆系统。

## 第一步：先吃透 `MessagesState`
先理解消息如何在 graph 中流转。

## 第二步：再加 `checkpointer`
理解 `thread_id` 如何恢复会话。

## 第三步：自定义 state
把任务状态、结构化字段加进去。

## 第四步：自己做一个长期记忆 store
哪怕先用 dict、JSON、SQLite 都行。

## 第五步：实现“读长期记忆 + 写长期记忆”闭环
这一步完成，系统就开始像真正产品了。

---

# 16. 一个通俗比喻

把 LangGraph 记忆想成办公桌：

- **短期记忆**：你桌面上摊开的资料，正在处理，随手可用
- **checkpointer**：下班前拍个桌面快照，明天可以接着干
- **长期记忆**：档案柜里的用户资料、项目文档、历史记录

你工作时会：

- 从档案柜拿旧资料
- 放到桌面上处理
- 处理完把重要信息再归档

LangGraph 的记忆机制，本质上就是这套逻辑。

---

# 17. 最后给一个简化版实战模板

这个模板把短期和长期放在一起，结构比较接近真实项目。

```python
import os
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

# 模拟长期记忆库
USER_MEMORY_DB = {
    "u1": {
        "name": "小王",
        "role": "后端工程师",
        "preference": "回答简洁、少废话",
    }
}


class ChatState(TypedDict):
    user_id: str
    messages: list


def chat_node(state: ChatState):
    user_id = state["user_id"]
    user_memory = USER_MEMORY_DB.get(user_id, {})

    memory_prompt = (
        f"用户姓名：{user_memory.get('name', '未知')}\n"
        f"用户角色：{user_memory.get('role', '未知')}\n"
        f"回答偏好：{user_memory.get('preference', '未知')}"
    )

    system_message = SystemMessage(
        content="你是一个中文助手，请结合用户长期记忆进行回答。\n" + memory_prompt
    )

    response = llm.invoke([system_message] + state["messages"])
    return {"messages": [response]}


builder = StateGraph(ChatState)
builder.add_node("chat_node", chat_node)
builder.add_edge(START, "chat_node")
builder.add_edge("chat_node", END)

app = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "thread-u1-001"}}

# 第一轮
res1 = app.invoke(
    {
        "user_id": "u1",
        "messages": [HumanMessage(content="请给我一个 LangGraph 学习路线")],
    },
    config=config,
)
print(res1["messages"][-1].content)

# 第二轮，短期记忆继续生效
res2 = app.invoke(
    {
        "user_id": "u1",
        "messages": [HumanMessage(content="再结合我的职业背景细化一下")],
    },
    config=config,
)
print(res2["messages"][-1].content)
```

这个模板体现了两件事：

- **短期记忆**：依赖 `thread_id` + checkpointer，维持当前会话连续性
- **长期记忆**：依赖 `user_id` + 外部存储，维持跨会话认知

---

# 18. 总结

你只要记住这四句话就够了：

1. **LangGraph 的短期记忆，本质是 state。**
2. **短期记忆要想跨调用延续，需要 checkpointer。**
3. **长期记忆不要直接塞满聊天历史，而要抽取后存到外部 store。**
4. **真实项目里，通常用 `thread_id` 管短期记忆，用 `user_id` 管长期记忆。**

如果你后面要继续往实战走，最值得补的一步是：

- 把长期记忆从 `dict` 升级到 **SQLite / Postgres / Redis / 向量库**
- 再把“规则抽取”升级成“LLM 结构化抽取 + 检索召回”

这样就从学习版，进化到可上线版了。

---

# 19. 附：最小安装命令

```bash
pip install -U langgraph langchain langchain-openai
```

如果你要做数据库长期记忆，再按需要补：

```bash
pip install sqlalchemy psycopg[binary] redis
```

如果要做向量检索，再补对应向量库依赖。

---

# 20. 附：一份适合你当前配置的最小可运行示例

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com",
)


def chatbot(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

app = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "demo-thread-1"}}

app.invoke(
    {"messages": [HumanMessage(content="我叫阿明")]},
    config=config,
)

result = app.invoke(
    {"messages": [HumanMessage(content="你记得我的名字吗？")]},
    config=config,
)

print(result["messages"][-1].content)
```

这份代码就是最基础的“短期记忆”版本。先跑通它，再逐步加长期记忆，路线最稳。