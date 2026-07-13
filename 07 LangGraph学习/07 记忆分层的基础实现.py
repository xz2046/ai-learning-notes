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