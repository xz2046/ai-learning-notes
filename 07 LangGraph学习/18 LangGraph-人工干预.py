import os
import json
from typing import TypedDict, Literal
 
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
 
 
# =========================
# 模型配置
# =========================
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
    model_kwargs={"response_format": {"type": "json_object"}},
)
 
 
# =========================
# 状态定义
# =========================
class State(TypedDict):
    user_request: str
    ssh_command: str
    review_json: str
    review_reason: str
    risk_level: Literal["low", "medium", "high"]
    need_human_review: bool
    human_decision: str
    execution_result: str
 
 
# =========================
# 工具函数
# =========================
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
 
 
# =========================
# 节点1：命令生成（这里简化为直接用用户输入）
# =========================
def prepare_command_node(state: State):
    return {
        "ssh_command": state["user_request"],
    }
 
 
# =========================
# 节点2：LLM 风险审查
# =========================
def review_command_node(state: State):
    command = state["ssh_command"]
 
    system_prompt = SystemMessage(
        content=(
            "你是一个 Linux/SSH 命令安全审查器。"
            "请判断给定命令是否存在执行风险，并只返回 JSON。"
            "JSON 字段必须包含："
            "risk_level（low/medium/high）, "
            "need_human_review（true/false）, "
            "review_reason（字符串）。"
            "判断原则："
            "删除文件、修改系统配置、停止服务、网络下载执行、权限变更、批量覆盖、"
            "数据库删除、rm -rf、mkfs、shutdown、reboot、userdel、chmod/chown 大范围修改等，"
            "都应视为高风险或至少需要人工复核。"
            "只返回 JSON，不要输出解释。"
        )
    )
 
    user_prompt = HumanMessage(content=f"待审查命令：{command}")
    response = llm.invoke([system_prompt, user_prompt])
 
    try:
        data = safe_json_loads(response.content)
    except Exception:
        data = {
            "risk_level": "high",
            "need_human_review": True,
            "review_reason": "模型审查结果解析失败，按高风险处理。",
        }
 
    risk_level = data.get("risk_level", "high")
    need_human_review = bool(data.get("need_human_review", True))
    review_reason = data.get("review_reason", "未提供原因")
 
    return {
        "review_json": json.dumps(data, ensure_ascii=False),
        "risk_level": risk_level,
        "need_human_review": need_human_review,
        "review_reason": review_reason,
    }
 
 
# =========================
# 路由1：是否需要人工审批
# =========================
def route_after_review(state: State):
    if state["need_human_review"]:
        return "human_confirm_node"
    return "execute_ssh_node"
 
 
# =========================
# 节点3：人工审批（interrupt）
# =========================
def human_confirm_node(state: State):
    decision = interrupt(
        {
            "type": "ssh_command_review",
            "message": "该 SSH 命令存在风险，请人工确认是否继续执行。",
            "ssh_command": state["ssh_command"],
            "risk_level": state["risk_level"],
            "review_reason": state["review_reason"],
            "review_json": state["review_json"],
            "allowed_values": ["approve", "reject"],
        }
    )
    return {"human_decision": decision}
 
 
# =========================
# 路由2：人工审批后走向
# =========================
def route_after_human(state: State):
    if state["human_decision"].strip().lower() == "approve":
        return "execute_ssh_node"
    return "reject_node"
 
 
# =========================
# 节点4：执行 SSH 命令（安全起见，这里只做模拟执行）
# =========================
def execute_ssh_node(state: State):
    command = state["ssh_command"]
 
    # 为了学习和测试安全，这里不真的连 SSH，也不真的执行危险命令
    # 只模拟一份结果
    simulated_output = (
        "[SIMULATED EXECUTION]\n"
        f"命令已进入执行阶段：{command}\n"
    )
 
    return {
        "execution_result": simulated_output
    }
 
 
# =========================
# 节点5：人工拒绝
# =========================
def reject_node(state: State):
    return {
        "execution_result": (
            f"命令被人工拒绝，未执行。\n"
            f"命令：{state['ssh_command']}\n"
            f"风险等级：{state['risk_level']}\n"
            f"风险说明：{state['review_reason']}"
        )
    }
 
 
# =========================
# 构建图
# =========================
builder = StateGraph(State)
 
builder.add_node("prepare_command_node", prepare_command_node)
builder.add_node("review_command_node", review_command_node)
builder.add_node("human_confirm_node", human_confirm_node)
builder.add_node("execute_ssh_node", execute_ssh_node)
builder.add_node("reject_node", reject_node)
 
builder.add_edge(START, "prepare_command_node")
builder.add_edge("prepare_command_node", "review_command_node")
builder.add_conditional_edges("review_command_node", route_after_review)
builder.add_conditional_edges("human_confirm_node", route_after_human)
builder.add_edge("execute_ssh_node", END)
builder.add_edge("reject_node", END)
 
graph = builder.compile(checkpointer=InMemorySaver())
 
 
# =========================
# 测试入口
# =========================
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "ssh-review-demo-001"}}
 
    initial_state = {
        "user_request": "rm -rf /var/log/myapp",
        "ssh_command": "",
        "review_json": "",
        "review_reason": "",
        "risk_level": "low",
        "need_human_review": False,
        "human_decision": "",
        "execution_result": "",
    }
 
    print("=== 第一次执行：LLM 先审查命令 ===")
    result = graph.invoke(initial_state, config=config)
    print(result)
 
    snapshot = graph.get_state(config)
    print("\n=== 当前图状态（已在人工审批点中断）===")
    print(snapshot)
 
    human_input = input("\n请输入人工审批结果 approve/reject: ").strip()
 
    print("\n=== 恢复执行 ===")
    resumed_result = graph.invoke(Command(resume=human_input), config=config)
    print(resumed_result)
 
    print("\n=== 最终执行结果 ===")
    print(resumed_result["execution_result"])
 
