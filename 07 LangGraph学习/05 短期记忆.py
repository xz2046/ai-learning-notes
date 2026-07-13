import os
import json
from typing import TypedDict, Annotated, Optional
from operator import add

from pydantic import BaseModel, Field, ValidationError
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)


class UserProfile(BaseModel):
    user_name: Optional[str] = Field(default=None, description="用户姓名或称呼")
    profession: Optional[str] = Field(default=None, description="用户职业或技能方向")
    preference: Optional[str] = Field(default=None, description="用户回答偏好")


class MyState(TypedDict):
    messages: Annotated[list[BaseMessage], add]
    user_name: str
    profession: str
    preference: str
    task_stage: str


def extract_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]

    return text


def extract_user_info(state: MyState):
    last_user_msg = state["messages"][-1].content

    system_prompt = SystemMessage(
        content=(
            "你是一个信息抽取器。"
            "请从用户输入中提取结构化字段，并严格返回 JSON 对象。"
            "字段只有这三个：user_name, profession, preference。"
            "如果某个字段无法确定，值设为 null。"
            "不要输出解释，不要输出 Markdown，不要输出代码块，只输出 JSON。"
        )
    )

    human_prompt = HumanMessage(
        content=f"用户输入：{last_user_msg}"
    )

    response = llm.invoke([system_prompt, human_prompt])
    raw_text = response.content
    json_text = extract_json_text(raw_text)

    try:
        data = json.loads(json_text)
        extracted = UserProfile.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        extracted = UserProfile()

    return {
        "user_name": extracted.user_name or state.get("user_name", ""),
        "profession": extracted.profession or state.get("profession", ""),
        "preference": extracted.preference or state.get("preference", ""),
        "task_stage": "info_extracted",
    }


def reply_node(state: MyState):
    system_message = SystemMessage(
        content=(
            "你是一个简洁、友好的中文助手。\n"
            f"当前已知用户姓名：{state.get('user_name', '未知') or '未知'}\n"
            f"当前已知用户职业/方向：{state.get('profession', '未知') or '未知'}\n"
            f"当前已知用户偏好：{state.get('preference', '未知') or '未知'}\n"
            "请结合这些信息正常回答用户问题。"
        )
    )

    response = llm.invoke([system_message] + state["messages"])
    return {
        "messages": [response],
        "task_stage": "replied",
    }


builder = StateGraph(MyState)
builder.add_node("extract_user_info", extract_user_info)
builder.add_node("reply_node", reply_node)

builder.add_edge(START, "extract_user_info")
builder.add_edge("extract_user_info", "reply_node")
builder.add_edge("reply_node", END)

app = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "custom-state-llm-extract-001"}}

result = app.invoke(
    {
        "messages": [
            HumanMessage(content="我叫韩梅梅，是做 Python 后端开发的，喜欢编程，回答尽量简洁一点")
        ],
        "user_name": "",
        "profession": "",
        "preference": "",
        "task_stage": "start",
    },
    config=config,
)

print("最终状态：")
print(result)
print("\nAI 回复：")
print(result["messages"][-1].content)

result = app.invoke(
    {
        "messages": [
            HumanMessage(content="我喜欢电影和诗歌")
        ]
    },
    config=config,
)

result = app.invoke(
    {
        "messages": [
            HumanMessage(content="我的职业是什么？")
        ]
    },
    config=config,
)

print("最终状态：")
print(result)
print("\nAI 回复：")
print(result["messages"][-1].content)