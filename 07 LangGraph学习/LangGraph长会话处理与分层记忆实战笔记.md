# LangGraph 长会话处理与分层记忆实战笔记

## 1. 先说结论

长会话记忆如果只靠“把全部历史消息继续往下传”，很快就会遇到三个问题：**上下文膨胀、成本失控、噪音变多**。真正可落地的做法通常不是“保留全部历史”，而是做成 **三层记忆**：

- **近期原文**：保留最近几轮完整消息，保证当前问题细节不丢
- **中期摘要**：把较早但仍有参考价值的过程性内容压成摘要
- **长期事实**：把稳定、可复用的信息抽成结构化字段独立保存

一句话概括：**短期细节看原文，历史脉络看摘要，稳定认知看事实。**

---

## 2. 一个可运行的长会话处理示例

下面这份代码演示一个简化但完整的实现：

- 使用 LangGraph 管理线程内状态
- 每轮对话后自动更新长期事实
- 当消息轮数超过阈值时，自动把旧消息压缩进摘要
- 调用主模型回答时，只带：**近期原文 + 历史摘要 + 长期事实**

这里为了保证你当前 DeepSeek 兼容性，**不使用 `with_structured_output()`**，而采用 **`json_object` + 手动 JSON 解析** 的方式。

---

## 3. 完整代码

```python
import os
import json
from typing import TypedDict, Annotated
from operator import add

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
    model_kwargs={"response_format": {"type": "json_object"}},
)

# 主对话模型，不强制 json 输出
chat_llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

# 用 dict 模拟长期记忆库；生产环境可替换成 Redis / SQLite / Postgres
LONG_TERM_MEMORY_DB = {}

# 近期原文最多保留 6 条消息（约 3 轮）
RECENT_MESSAGE_LIMIT = 6
# 超过这个数量就触发摘要压缩
SUMMARY_TRIGGER_LIMIT = 10


class ChatState(TypedDict):
    user_id: str
    messages: Annotated[list[BaseMessage], add]
    running_summary: str
    task_stage: str


def messages_to_text(messages: list[BaseMessage]) -> str:
    lines = []
    for msg in messages:
        role = "用户"
        if isinstance(msg, AIMessage):
            role = "助手"
        elif isinstance(msg, SystemMessage):
            role = "系统"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


def safe_json_loads(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


def get_long_term_memory(user_id: str) -> dict:
    return LONG_TERM_MEMORY_DB.get(
        user_id,
        {
            "user_name": "",
            "profession": "",
            "preference": "",
            "current_goal": "",
        },
    )


def save_long_term_memory(user_id: str, memory: dict):
    LONG_TERM_MEMORY_DB[user_id] = memory


def extract_long_term_facts(state: ChatState):
    user_id = state["user_id"]
    last_user_msg = state["messages"][-1].content
    old_memory = get_long_term_memory(user_id)

    system_prompt = SystemMessage(
        content=(
            "你是一个用户事实抽取器。"
            "请从用户最新输入中抽取可能值得长期保存的稳定信息。"
            "输出 JSON 对象，字段只有：user_name, profession, preference, current_goal。"
            "如果某字段无法确定，返回空字符串。"
            "不要输出解释，只输出 JSON。"
        )
    )

    user_prompt = HumanMessage(
        content=(
            f"已有长期事实：{json.dumps(old_memory, ensure_ascii=False)}\n"
            f"用户最新输入：{last_user_msg}"
        )
    )

    response = llm.invoke([system_prompt, user_prompt])

    try:
        new_data = safe_json_loads(response.content)
    except Exception:
        new_data = {}

    merged_memory = {
        "user_name": new_data.get("user_name") or old_memory.get("user_name", ""),
        "profession": new_data.get("profession") or old_memory.get("profession", ""),
        "preference": new_data.get("preference") or old_memory.get("preference", ""),
        "current_goal": new_data.get("current_goal") or old_memory.get("current_goal", ""),
    }

    save_long_term_memory(user_id, merged_memory)
    return {"task_stage": "facts_updated"}


def compress_history_if_needed(state: ChatState):
    messages = state["messages"]
    running_summary = state.get("running_summary", "")

    if len(messages) <= SUMMARY_TRIGGER_LIMIT:
        return {"task_stage": "skip_compress"}

    old_messages = messages[:-RECENT_MESSAGE_LIMIT]
    recent_messages = messages[-RECENT_MESSAGE_LIMIT:]

    summary_prompt = [
        SystemMessage(
            content=(
                "你是对话摘要器。"
                "请把旧对话总结成一段高信息密度摘要，保留后续回答真正需要的信息。"
                "重点保留：用户目标、已确认事实、已完成步骤、未解决问题、偏好、限制条件。"
                "不要逐句复述，不要写废话。"
            )
        ),
        HumanMessage(
            content=(
                f"已有摘要：\n{running_summary or '无'}\n\n"
                f"需要压缩的旧消息：\n{messages_to_text(old_messages)}"
            )
        ),
    ]

    summary_response = chat_llm.invoke(summary_prompt)
    new_summary = summary_response.content.strip()

    return {
        "messages": recent_messages,
        "running_summary": new_summary,
        "task_stage": "compressed",
    }


def reply_with_layered_memory(state: ChatState):
    user_id = state["user_id"]
    long_term_memory = get_long_term_memory(user_id)
    running_summary = state.get("running_summary", "")
    recent_messages = state["messages"]

    long_term_text = (
        f"用户姓名：{long_term_memory.get('user_name', '') or '未知'}\n"
        f"用户职业/方向：{long_term_memory.get('profession', '') or '未知'}\n"
        f"回答偏好：{long_term_memory.get('preference', '') or '未知'}\n"
        f"当前目标：{long_term_memory.get('current_goal', '') or '未知'}"
    )

    summary_text = running_summary if running_summary else "暂无历史摘要"

    system_prompt = SystemMessage(
        content=(
            "你是一个中文助手。请结合三层记忆回答用户问题：\n\n"
            "【长期事实】\n"
            f"{long_term_text}\n\n"
            "【历史摘要】\n"
            f"{summary_text}\n\n"
            "回答要求：优先利用近期原文理解当前问题，必要时参考历史摘要保持上下文连续性，"
            "再利用长期事实进行个性化和稳定认知补充。回答保持准确、简洁。"
        )
    )

    response = chat_llm.invoke([system_prompt] + recent_messages)
    return {
        "messages": [response],
        "task_stage": "replied",
    }


builder = StateGraph(ChatState)
builder.add_node("extract_long_term_facts", extract_long_term_facts)
builder.add_node("compress_history_if_needed", compress_history_if_needed)
builder.add_node("reply_with_layered_memory", reply_with_layered_memory)

builder.add_edge(START, "extract_long_term_facts")
builder.add_edge("extract_long_term_facts", "compress_history_if_needed")
builder.add_edge("compress_history_if_needed", "reply_with_layered_memory")
builder.add_edge("reply_with_layered_memory", END)

app = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "layered-memory-thread-001"}}
    user_id = "user_001"

    rounds = [
        "我叫韩梅梅，是做 Python 后端开发的，回答尽量简洁一点。",
        "我最近在学习 LangGraph，重点关注短期记忆和长期记忆。",
        "我已经理解了 state 和 checkpointer 的基本作用。",
        "我还想知道长会话里历史消息太多时怎么处理。",
        "比如定期摘要、窗口截断、长期事实抽取该怎么结合？",
        "你再顺便记住，我现在的目标是做一个可以多轮对话的学习助手。",
        "如果后面我继续问实现方案，你要结合这些背景。",
    ]

    for i, text in enumerate(rounds, 1):
        result = app.invoke(
            {
                "user_id": user_id,
                "messages": [HumanMessage(content=text)],
                "running_summary": "",
                "task_stage": "start",
            },
            config=config,
        )
        print(f"\n--- 第 {i} 轮 ---")
        print("AI:", result["messages"][-1].content)
        print("当前摘要:", result.get("running_summary", ""))
        print("长期事实:", LONG_TERM_MEMORY_DB.get(user_id, {}))
```

---

## 4. 这份代码在做什么

这份代码每轮执行都走三步：

1. **抽取长期事实**：从用户最新输入里识别值得长期保存的信息，比如姓名、职业、偏好、当前目标，并写入 `LONG_TERM_MEMORY_DB`
2. **按需压缩历史**：如果线程里的消息数量超过阈值，就把较早消息压缩成 `running_summary`，只保留最近 `RECENT_MESSAGE_LIMIT` 条原文
3. **带分层记忆回答**：把长期事实、历史摘要、近期原文一起作为上下文，让主模型生成回答

整个图里，`messages` 是短期线程状态，`running_summary` 是中期压缩记忆，`LONG_TERM_MEMORY_DB` 是长期事实存储。它们合起来就是一个最小可实现的 **三层记忆系统**。

---

## 5. 为什么这是“分层记忆”而不是“单纯摘要”

很多人会把长会话处理理解成“超过长度就做一次 summary”。这只是摘要机制，不是完整分层记忆。真正的分层记忆是把不同性质的信息放进不同层：

- **近期原文** 保存“当前轮推理必须依赖的细节”
- **中期摘要** 保存“较长历史中的过程脉络”
- **长期事实** 保存“跨会话也应稳定存在的结构化认知”

如果不分层，就会出现两个典型问题：一是摘要里混进大量不稳定细节，越写越乱；二是长期事实被埋在自然语言摘要里，后续很难稳定召回和复用。

---

## 6. 详细解释 6.5：分层记忆中的三层边界到底怎么划

这是最关键的部分。很多系统做不稳，不是因为没做摘要，而是 **三层边界没划清**。

### 6.1 第一层：近期原文

近期原文保存的是 **高保真、低压缩、强时效** 的内容。它直接参与当前一轮模型推理，最重要的作用是防止细节损失。

这层一般包含：

- 最近几轮用户消息与助手回复
- 当前问题的上下文依赖
- 最近一次工具调用结果
- 当前任务中的短期约束

例如：用户刚刚发了一大段报错日志、刚刚补充了一个筛选条件、刚刚确认“不要用 Redis，先用 SQLite”。这些信息都应保留原文，而不是立刻被压缩。因为一旦压缩，很多关键细节会丢。

**边界判断标准**：凡是“当前回答必须精确读取细节”的内容，都优先留在近期原文层。

常见实现方式：

- 保留最近 N 条消息，如 6~12 条
- 或按 token 保留最近 1000~3000 token
- 工具输出过长时可保留摘要 + 原文引用 ID，而非全文硬塞

这层的本质不是“永远最新”，而是“对当前回答最关键的高分辨率上下文”。

### 6.2 第二层：中期摘要

中期摘要保存的是 **过程性历史**，它的价值不在细节，而在脉络。它回答的是：“前面发生过什么、做到了哪一步、哪些结论已经确认、还有什么没解决。”

这层一般包含：

- 已讨论过的主题脉络
- 已完成的推理或操作步骤
- 已明确的中间结论
- 尚未解决的问题或待办
- 对当前主题仍有影响的约束条件

例如：

- 用户前几轮已经理解了 `state` 和 `checkpointer`
- 正在从短期记忆过渡到长期记忆设计
- 遇到过 DeepSeek `structured_output` 兼容性问题
- 当前希望把学习文档升级成可实战的代码模板

这些内容对后续回答有帮助，但没必要保留逐字逐句原文，因此适合进入摘要层。

**边界判断标准**：凡是“后续需要知道这件事发生过，但不需要逐字阅读细节”的内容，进入中期摘要层。

常见实现方式：

- 轮数超过阈值后，把早期消息增量总结进 `running_summary`
- 每个主题维护单独摘要，而不是一份全局大摘要
- 摘要内容尽量按字段组织：目标、已知事实、已完成步骤、未解问题、约束条件

中期摘要最怕两件事：**一是写成流水账，二是把长期事实也揉进去。** 流水账没信息密度，长期事实混进去又难维护。

### 6.3 第三层：长期事实

长期事实保存的是 **稳定、可复用、跨线程依然成立** 的内容。它和中期摘要最大的区别在于：摘要是“发生过什么”，长期事实是“这个用户/任务长期是什么”。

这层一般包含：

- 用户姓名、职业、技能方向
- 表达或回答偏好
- 固定业务属性，如公司、地区、角色
- 稳定目标，如“准备转做 AI 应用开发”
- 反复出现且后续持续有效的项目背景

例如：

- 用户叫韩梅梅
- 做 Python 后端开发
- 喜欢简洁回答
- 当前长期目标是做多轮对话学习助手

这些信息不依赖当前线程，哪怕用户新开一个 thread，它们通常依然有效，因此应该单独存成结构化数据，而不是只埋在摘要里。

**边界判断标准**：凡是“下次新开会话也应该记得”的内容，进入长期事实层。

常见实现方式：

- 用 `user_id` 作为主键保存一份画像/偏好/目标结构
- 新会话开始时先读取长期事实，再注入系统提示词或 state
- 采用覆盖更新而不是无限追加，避免画像越存越乱

长期事实最怕两件事：**一是保存太多瞬时信息，二是完全不做更新。** 前者会污染画像，后者会让画像过期。

---

## 7. 三层之间的划分界限：一个业务判断模板

如果你在项目里拿不准某条信息该放哪层，可以用这三个问题判断：

### 问题 1：这条信息对“当前一轮精确回答”是不是必须看原文？

- 是 → 放 **近期原文**
- 否 → 继续问问题 2

### 问题 2：这条信息后续还需要知道，但不需要保留逐字细节吗？

- 是 → 放 **中期摘要**
- 否 → 继续问问题 3

### 问题 3：这条信息跨会话、跨线程也仍然成立吗？

- 是 → 放 **长期事实**
- 否 → 多半不需要长期保留，可只留在摘要或直接淘汰

举几个例子：

- “报错堆栈全文” → 近期原文
- “已经排查过依赖版本冲突” → 中期摘要
- “用户是 Python 后端开发” → 长期事实
- “今天下午我先去开会” → 多半不值得长期保存
- “当前项目目标是做多轮对话学习助手” → 如果是阶段性持续目标，可放长期事实；如果只是本线程临时目标，也可先放摘要

所以三层不是按时间死分，而是按 **信息性质、时效性、复用价值** 来分。

---

## 8. 业务落地时通常怎么实现

真实系统里，三层记忆一般不会只靠一个 `messages` 字段，而是拆成几个独立存储面。

### 8.1 近期原文的落地方式

这层通常直接跟线程状态绑定，最常见的方式就是：

- LangGraph `state["messages"]`
- 配合 `checkpointer` 做线程级恢复
- 设置固定窗口或 token 阈值

如果是多工具 agent，还会把关键工具结果短期挂在 state 中，比如：`tool_result`、`retrieved_docs`、`current_plan`。这些都是短期工作区内容，不建议直接长期化。

### 8.2 中期摘要的落地方式

这层一般有两种方案：

- **线程内单摘要**：每个 thread 维护一个 `running_summary`
- **主题级摘要**：每个 thread 下按 topic 维护多个摘要片段

简单业务用单摘要就够，高复杂业务更推荐主题级摘要。因为一个 thread 里往往不是只聊一个主题，全挤到一份摘要里会越来越糊。

更新策略通常是：

- 达到轮数阈值或 token 阈值触发压缩
- 摘要采用增量更新：旧摘要 + 新压缩消息 → 新摘要
- 保留最近几轮原文，不压缩最新区间

### 8.3 长期事实的落地方式

这层一般独立于 LangGraph 线程状态，存到外部存储，例如：

- SQLite：单机应用、学习项目、小规模服务
- Redis：低延迟 KV 场景，适合用户画像缓存
- Postgres/MySQL：正式业务系统，便于管理和查询
- 向量库：更适合存语义片段和检索型记忆，不适合纯结构化画像字段

长期事实通常会有一个稳定 schema，例如：

```json
{
  "user_id": "user_001",
  "profile": {
    "name": "韩梅梅",
    "profession": "Python后端开发",
    "preference": "简洁回答",
    "current_goal": "做多轮对话学习助手"
  },
  "updated_at": "2026-07-06T18:00:00"
}
```

它和摘要最大的不同是：**长期事实最好结构化、可更新、可查询。**

---

## 9. 一套更像生产方案的组合方式

如果你要做一个真正可用的 LangGraph 多轮系统，比较推荐的组合是：

- `thread_id` 管近期原文和线程内摘要
- `user_id` 管长期事实
- 每轮进入 graph 时，先恢复线程状态，再读取长期事实
- 每轮回答前，按需压缩消息
- 每轮回答后，抽取新的长期事实并覆盖更新

上下文拼装时，建议按优先级排列：

```text
系统规则 > 长期事实 > 历史摘要 > 近期原文 > 当前用户输入
```

为什么这样排：

- 系统规则优先级最高
- 长期事实提供稳定认知
- 历史摘要补上下文脉络
- 近期原文保细节
- 当前输入是最终触发点

当然，具体顺序可以按业务调，但这个默认顺序比较稳。

---

## 10. 三层记忆在不同业务中的划分参考

### 学习助手 / Copilot

- **近期原文**：最近几轮追问、代码片段、报错内容
- **中期摘要**：已经学过的知识点、未理解的问题、当前学习阶段
- **长期事实**：用户背景、技术栈、回答风格偏好、长期学习目标

### 客服系统

- **近期原文**：当前投诉内容、订单号、最新处理结果
- **中期摘要**：本工单已沟通经过、已确认责任、待处理事项
- **长期事实**：客户等级、历史偏好、常见问题模式

### 销售/顾问助手

- **近期原文**：本次咨询细节、预算、时间安排
- **中期摘要**：沟通进展、已推荐方案、客户反馈
- **长期事实**：客户行业、职位、偏好、决策周期

你会发现不同行业实现方式不同，但三层判断逻辑基本相通：**细节留原文，脉络进摘要，稳定信息进画像。**

---

## 11. 设计时的几个坑

### 11.1 把摘要当成垃圾桶

什么都往摘要里塞，最后摘要会又长又乱，反而取代不了原始消息。摘要应该是信息浓缩，不是历史堆积。

### 11.2 把长期事实写成自然语言大段文本

长期事实如果只是一段自然语言描述，后续更新、检索、覆盖都很难做。能结构化就尽量结构化。

### 11.3 没有压缩触发条件

如果不设轮数阈值或 token 阈值，摘要机制就很难稳定工作。最好明确：多少条消息压缩一次，压缩后保留多少近期原文。

### 11.4 不区分 `thread_id` 和 `user_id`

线程上下文和用户长期画像不是一回事。一个用户可以有多个会话线程，这两个键必须分开设计。

### 11.5 新事实不更新旧事实

长期事实不是“只记第一次”。用户职业、目标、偏好都可能变化，需要有覆盖更新机制。

---

## 12. 最后总结

长会话记忆的关键不是“怎么保存更多消息”，而是 **怎么把不同性质的信息放到正确层里**。分层记忆中：

- **近期原文** 解决当前回答的精确性
- **中期摘要** 解决历史脉络连续性
- **长期事实** 解决跨会话稳定认知

真正落地时，可以把它理解成一句话：**最近细节留在线程里，历史过程压成摘要，稳定信息沉到用户档案。**

如果你后面要继续往实战走，最值得补的一步是把上面示例里的：

- `LONG_TERM_MEMORY_DB` 换成 SQLite / Redis / Postgres
- `running_summary` 从单摘要升级成主题摘要
- 压缩触发条件从“消息条数”升级成“token 预算控制”

这三步做完，基本就从学习版跨到可用版了。