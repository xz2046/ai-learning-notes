import os
from typing import TypedDict
 
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
 
 
# =========================
# 1. 定义 State
# =========================
class State(TypedDict):
    topic: str
    author: str
    joke: str
 
 
# =========================
# 2. 初始化模型
# =========================
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
    temperature=1.1,
)
 
 
# =========================
# 3. 定义节点
# =========================
def author_node(state: State):
    """第一步：让大模型推荐一个有名作家"""
    response = llm.invoke(
        "请随机推荐一位世界知名作家。"
        "只返回作家姓名，不要解释，不要加标点。"
    )
    author = response.content.strip().splitlines()[0]
    return {"author": author}
 
 
def joke_node(state: State):
    """第二步：让大模型模仿该作家的风格写一个 100 字以内笑话"""
    author = state["author"]
    topic = state.get("topic", "日常生活")
 
    response = llm.invoke(
        f"请模仿作家「{author}」的语言风格，"
        f"围绕「{topic}」写一个中文笑话。"
        "要求：100字以内，只输出笑话正文。"
    )
    return {"joke": response.content.strip()}
 
 
# =========================
# 4. 构建图
# =========================
builder = StateGraph(State)
 
builder.add_node("author_node", author_node)
builder.add_node("joke_node", joke_node)
 
builder.add_edge(START, "author_node")
builder.add_edge("author_node", "joke_node")
builder.add_edge("joke_node", END)
 
# 时间回溯必须依赖 checkpointer
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
 
 
# =========================
# 5. 工具函数：打印 checkpoint 历史
# =========================
def print_checkpoints(config):
    history = list(graph.get_state_history(config))
 
    print("\n========== Checkpoint 历史 ==========")
    print("说明：get_state_history 通常按时间倒序返回；下面按执行顺序打印。\n")
 
    for index, snapshot in enumerate(reversed(history), start=1):
        checkpoint_id = snapshot.config["configurable"].get("checkpoint_id")
        step = snapshot.metadata.get("step") if snapshot.metadata else None
        source = snapshot.metadata.get("source") if snapshot.metadata else None
        writes = snapshot.metadata.get("writes") if snapshot.metadata else None
 
        print(f"[{index}] checkpoint_id: {checkpoint_id}")
        print(f"    step   : {step}")
        print(f"    source : {source}")
        print(f"    next   : {snapshot.next}")
        print(f"    values : {snapshot.values}")
        print(f"    writes : {writes}")
        print("-" * 60)
 
    return history
 
 
# =========================
# 6. 主流程：首次执行 + 时间回溯
# =========================
if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "time-travel-author-joke-demo-001"
        }
    }
 
    initial_state = {
        "topic": "程序员加班",
        "author": "",
        "joke": "",
    }
 
    print("========== 第一次执行 ==========")
    first_result = graph.invoke(initial_state, config=config)
    print("第一次推荐作家：", first_result["author"])
    print("第一次生成笑话：", first_result["joke"])
 
    # 查看所有 checkpoint
    history = print_checkpoints(config)
 
    # =========================
    # 7. 选择 checkpoint：回到 author_node 执行前
    # =========================
    # 注意：如果想让 author_node 重新推荐作家，应该选择 next 里包含 author_node 的 checkpoint。
    # 这代表“下一步将执行 author_node”，也就是 author_node 执行前的状态。
    author_checkpoint = None
    for snapshot in history:
        if "author_node" in snapshot.next:
            author_checkpoint = snapshot
            break
 
    if author_checkpoint is None:
        raise RuntimeError("没有找到 author_node 执行前的 checkpoint")
 
    author_checkpoint_id = author_checkpoint.config["configurable"].get("checkpoint_id")
    print("\n========== 选定 checkpoint ==========")
    print("准备从 author_node 执行前重新开始")
    print("checkpoint_id:", author_checkpoint_id)
    print("checkpoint values:", author_checkpoint.values)
    print("checkpoint next:", author_checkpoint.next)
 
    # =========================
    # 8. 从该 checkpoint 继续执行
    # =========================
    print("\n========== 时间回溯后重新执行 ==========")
 
    # 关键点：传入历史 checkpoint 的 config。
    # 这会从该 checkpoint 所代表的位置继续执行后续节点。
    second_result = graph.invoke(None, config=author_checkpoint.config)
 
    print("第二次推荐作家：", second_result["author"])
    print("第二次生成笑话：", second_result["joke"])
 
    print("\n========== 对比结果 ==========")
    print("第一次 author:", first_result["author"])
    print("第一次 joke  :", first_result["joke"])
    print("第二次 author:", second_result["author"])
    print("第二次 joke  :", second_result["joke"])
 
    print("\n========== 回溯后新的 checkpoint 历史 ==========")
    print_checkpoints(config)