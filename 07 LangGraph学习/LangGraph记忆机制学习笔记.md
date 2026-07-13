# LangGraph 记忆机制学习笔记

## 1. 记忆机制的整体框架

LangGraph 中的“记忆”本质上不是一个独立模块，而是 **状态管理 + 持久化 + 检索注入** 的组合设计。理解时先分成两层：**短期记忆** 负责当前线程中的连续性，**长期记忆** 负责跨线程、跨时间的持续认知。前者主要依赖 `state` 与 `checkpointer`，后者主要依赖外部存储与检索策略。

一句话概括：**短期记忆解决“当前对话别断片”，长期记忆解决“下次见面还记得你”。**

---

## 2. 短期记忆：State 才是核心

LangGraph 的运行单位是 graph，graph 在节点间流转的内容就是 `state`。因此短期记忆本质上就是 **当前线程的状态快照**。在聊天场景里，这通常表现为消息历史；在工作流场景里，则可能同时包含任务阶段、工具结果、用户槽位信息、待确认参数等。

最常见的短期记忆写法是 `MessagesState`，它适合纯对话场景；如果业务里除了消息外还有结构化字段，就应改成自定义 `TypedDict` 或 `BaseModel` 状态。

### 最小示例：基于 `MessagesState` 的短期记忆

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

这个例子里，`messages` 是短期记忆本体，`checkpointer` 负责保存和恢复线程状态，`thread_id` 决定“接着哪段会话继续”。如果没有 `checkpointer`，graph 虽然也能跑，但每次都是一次性执行；只有加入检查点后，状态才能跨多次调用延续。

这里要明确一个边界：**短期记忆并不等于永久记忆**。它只是某条线程上的连续上下文，生命周期通常受线程、存储策略和保留时长约束。

---

## 3. 自定义短期记忆：不只是消息，还包括业务状态

实际项目里，消息历史往往只是状态的一部分。更有价值的是把流程中的结构化信息也放入 state，比如用户名、任务阶段、意图识别结果、工具输出、待确认参数等。这样 graph 不再只是“聊天上下文容器”，而是“完整工作流状态机”。

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

这段代码的重点不在规则抽取，而在于说明 **state 可以同时承载对话数据和流程数据**。其中 `messages: Annotated[list[BaseMessage], add]` 表示消息字段在节点返回更新时采用“追加”而不是覆盖；`task_stage` 则体现流程推进状态，它不会自动变化，而是由节点返回值显式更新，再由 LangGraph 合并进当前 state。

如果把这类设计抽象一下，可以得到一个很重要的实践判断：**消息历史负责“保留上下文”，结构化字段负责“保留可计算信息”。** 前者面向模型理解，后者面向流程控制。

---

## 4. 长期记忆：不要把聊天记录当记忆本身

长期记忆的关键不在于“保存更多历史”，而在于 **从历史中提炼长期有效的信息并独立存储**。原始聊天记录只是原材料，不是长期记忆本体。真正值得长期保留的，通常是用户画像、偏好、稳定事实、历史总结、任务阶段性成果等。

例如：用户叫小王、是 Python 工程师、偏好简洁回答、正在做 RAG 项目，这些信息都适合跨会话持久化；而“今天下午三点我先去开会”就未必值得长期保留。

因此长期记忆一般不直接依赖 `checkpointer`，而是采用外部存储，比如字典、SQLite、Redis、Postgres、向量库或自定义 memory store。它的基本模式是：**从对话中抽取 → 写入外部存储 → 新会话按用户或主题检索 → 注入当前 state 或 prompt。**

### 最小示例：长期记忆读取

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

这个例子说明了长期记忆的最基础模式：**长期信息不跟着线程自然流转，而是在每次需要时按 `user_id` 主动取回，再参与当前回答。**

---

## 5. 短期记忆与长期记忆的边界

短期记忆适合放“当前线程必须继续记住的东西”，长期记忆适合放“即使换线程也应该保留的东西”。更工程化一点说：**短期记忆的索引主键通常是 `thread_id`，长期记忆的索引主键通常是 `user_id` 或主题键。**

一个用户可以有很多线程，因此不应把 `thread_id` 和 `user_id` 混为一谈。前者描述“这次对话/任务过程”，后者描述“这个人或这个实体是谁”。如果把两者绑定死，系统就会在会话复用、历史隔离和个性化召回上出现混乱。

---

## 6. 长会话中的记忆管理：为什么必须处理

长会话不是“消息越多越好”，而是“信息越准越好”。如果把所有历史原样塞给模型，会同时遇到三个问题：上下文窗口压力上升、token 成本持续增加、无关旧信息干扰当前推理。因此实际系统里必须对短期记忆做治理。

核心思路不是“保留全部历史”，而是 **保留当前真正有用的信息密度**。常见方法包括定期清理、窗口截断、摘要压缩、主题切片、关键事实抽取和分层存储。

### 6.1 窗口截断：只保留最近 N 轮

这是最简单也最常用的方法。比如只保留最近 10 轮消息，把更早的内容丢掉。优点是实现成本低、运行稳定；缺点是会丢失早期但仍有价值的信息。因此它适合作为默认保底策略，而不适合作为唯一策略。

适用场景：客服、问答助手、低成本聊天机器人。典型思想是“近因信息优先，历史久远信息默认衰减”。

### 6.2 定期摘要：把旧消息压成摘要

当消息轮数或 token 超过阈值时，把较早的一段对话总结成一段摘要，替代原始消息。这样模型保留的是“历史浓缩信息”，而不是“历史全文”。

例如一个 50 轮对话可拆成：最近 8 轮原始消息 + 前 42 轮摘要。这样既保留近期细节，又降低上下文成本。

典型压缩内容包括：用户长期目标、已确认事实、已完成步骤、未解决问题、约束条件、偏好变化。摘要的作用不是复述聊天，而是保留后续推理必须知道的状态。

### 6.3 主题切片：按任务或议题分块保存

长会话往往并不是一个连续主题，而是多个子任务混合在一起。与其按时间线一股脑堆叠，不如按主题拆成多个片段，比如“报错排查”“学习路线”“部署问题”“偏好设置”。后续只召回与当前主题最相关的片段，而不是整条历史。

这类方法特别适合 agent、Copilot、项目助手，因为它们的会话常常跨越多种任务。主题切片的本质是让记忆从“时间驱动”转成“任务驱动”。

### 6.4 关键事实抽取：把会话中的稳定信息沉淀成槽位

不是所有内容都值得总结成自然语言摘要，有些内容更适合直接抽成结构化字段，如：用户名、项目名、语言栈、地区、回答偏好、当前目标、约束条件、已经确认过的步骤。这类信息应该独立于消息历史存在，因为它们后续会频繁参与决策和提示词构造。

可以理解为：**摘要保留语义脉络，槽位保留可计算事实。** 两者配合比单纯保留消息效果更稳。

### 6.5 分层记忆：近期原文 + 中期摘要 + 长期事实

这是比较推荐的长会话设计。把记忆拆成三层：最近几轮保留原始消息，中间历史保留摘要，稳定事实沉淀为长期记忆。这样系统既能保留当前对话细节，又不被全量历史拖垮。

可以把它理解成：

```text
当前回答上下文 = 最近消息 + 历史摘要 + 长期事实
```

这通常比“全部消息拼起来”更便宜、更稳、更接近产品可用方案。

---

## 7. 长会话处理的实现思路示例

下面给几个更接近工程实现的思路，重点看设计，不追求代码复杂度。

### 7.1 示例一：达到轮数阈值后自动总结

思路是维护一段 `summary` 字段和 `messages` 字段。每次新消息进来后，如果 `messages` 超过设定轮数，就调用一个 summarizer 节点，把较早消息压缩进 `summary`，只保留最近几轮原文。

伪代码逻辑：

```python
if len(messages) > 12:
    old_messages = messages[:-6]
    recent_messages = messages[-6:]
    summary = summarize(summary, old_messages)
    messages = recent_messages
```

这里 `summarize(summary, old_messages)` 不是对全部历史重写，而是做 **增量摘要**：旧摘要 + 新增旧消息 → 新摘要。这样避免摘要成本随历史长度持续膨胀。

### 7.2 示例二：事实与摘要分离存储

思路是把会话中识别出的稳定事实单独存进 `profile`，把过程性历史压缩进 `summary`。比如：

- `profile`：姓名=韩梅梅，职业=后端开发，偏好=简洁回答
- `summary`：最近几轮在讨论 LangGraph 短期记忆和长期记忆设计，用户已理解 state/checkpointer，正在排查 structured output 兼容性问题

这种分离方式的好处是：以后就算摘要更新了，用户画像也不会被误删；就算主题切换了，画像仍然能长期有效。

### 7.3 示例三：按主题存历史摘要

可维护一个简单结构：

```python
memory_store = {
    "user_001": {
        "profile": {...},
        "topics": {
            "langgraph": "用户已学习 state、checkpointer、自定义 state，下一步想看长期记忆落地方案",
            "deployment": "用户项目使用 Windows + Anaconda，本地调试为主"
        }
    }
}
```

后续用户再问 LangGraph，就优先取 `topics['langgraph']`；问部署问题，就取 `topics['deployment']`。这比全局一份大摘要可控得多。

### 7.4 示例四：对话过长时先做压缩再调用主模型

在图里加入一个“压缩节点”：如果检测到 token 预计超限，就先把部分历史压缩成摘要，再进入主回答节点。它不是为了记忆持久化，而是为了让本轮回答不炸上下文。

流程可以是：

```text
新消息 -> token估算 -> 若超限则压缩历史 -> 组装上下文 -> 主模型回答
```

这类设计尤其适合工具调用多、消息很长、回答链条复杂的 agent。

---

## 8. 实战中的记忆更新原则

长期记忆和长会话摘要都不是“只追加不维护”的。一个成熟系统至少要考虑覆盖、合并、去重、冲突和时效性。

例如用户先说“我是前端开发”，过一段时间又说“我现在转做 AI 应用开发”，系统就不该无脑保留两条并列事实，而应根据时间和可信度决定是否更新画像。再比如偏好字段“回答简洁”通常应覆盖旧偏好，而不是累积成一长串描述。

所以更推荐的原则是：**稳定事实字段采用覆盖更新，过程性历史采用摘要合并，原始长消息采用窗口淘汰。** 这三种策略混用，才是真正可控的记忆系统。

---

## 9. 针对 DeepSeek + LangGraph 的理解重点

你当前的模型初始化方式：

```python
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get('DEEPSEEK_API_KEY2'),
    base_url="https://api.deepseek.com",
)
```

在 LangGraph 里可以直接继续使用，记忆实现层面与模型品牌关系不大。真正关键的是：state 如何设计、线程如何区分、检查点如何保存、长期记忆如何抽取和注入。

如果后续要让 LLM 提取结构化字段，不要把“结构化输出能力”和“记忆系统”混为一件事。结构化输出只是记忆写入的一种手段，记忆系统本身还涉及存储策略、更新逻辑、召回逻辑和上下文拼装方式。

---

## 10. 学习时最值得抓住的主线

如果只保留一条主线，建议按这个顺序理解：**先理解 state，再理解 checkpointer，再理解 thread_id，再理解长期记忆抽取与检索，最后理解长会话压缩与分层存储。**

这是因为 LangGraph 的本体是状态图，记忆只是状态图在多轮调用和跨会话场景下的延伸。只会“加历史消息”还不算真正理解了 LangGraph；真正掌握它，得能把对话、流程、结构化信息和持久化策略统一到同一个状态设计里。

---

## 11. 总结

LangGraph 里的记忆可以压缩成三个判断：**当前线程的连续性靠 state + checkpointer，跨会话的稳定认知靠外部长期存储，长会话的可用性靠压缩、摘要、抽取和分层管理。**

从工程角度看，最推荐的方案不是“把所有消息都留着”，而是把记忆拆成三部分：**最近消息保留细节，历史摘要保留脉络，长期事实保留稳定认知。** 这套设计兼顾效果、成本和可维护性，也更接近真实产品中的 LangGraph 记忆实现。