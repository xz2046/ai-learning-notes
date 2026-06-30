from typing import Any, Dict, List

from client import create_chat_stream, create_client
from tools import TOOLS, execute_tool_call

# 最大子轮次，避免模型反复调用工具进入死循环
MAX_SUB_TURN = 10


def _merge_tool_call(full_tool_calls: List[Dict[str, Any]], tc: Any) -> None:
    # 流式返回时，一个工具调用可能被拆成多段，这里按 index 合并
    while len(full_tool_calls) <= tc.index:
        full_tool_calls.append(
            {
                "id": "",
                "type": "function",
                "function": {"name": "", "arguments": ""},
            }
        )

    target = full_tool_calls[tc.index]

    if getattr(tc, "id", None):
        target["id"] = tc.id
    if getattr(tc, "type", None):
        target["type"] = tc.type
    if getattr(tc, "function", None):
        if getattr(tc.function, "name", None):
            target["function"]["name"] = tc.function.name
        if getattr(tc.function, "arguments", None):
            target["function"]["arguments"] += tc.function.arguments


def run_turn(client, turn: int, messages: List[dict]):
    sub_turn = 1
    while sub_turn <= MAX_SUB_TURN:
        print(f"\n===== 第 {turn}.{sub_turn} 轮开始请求 =====")

        try:
            # 发起流式对话请求
            stream = create_chat_stream(client, messages, TOOLS)
        except Exception as exc:
            print(str(exc))
            break

        full_reasoning = ""
        full_content = ""
        full_tool_calls: List[Dict[str, Any]] = []

        print("【流式输出】", end="", flush=True)

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 实时输出模型思考内容
            reasoning_piece = getattr(delta, "reasoning_content", None)
            if reasoning_piece:
                full_reasoning += reasoning_piece
                print(reasoning_piece, end="", flush=True)

            # 实时输出模型正文内容
            content_piece = getattr(delta, "content", None)
            if content_piece:
                full_content += content_piece
                print(content_piece, end="", flush=True)

            # 收集并合并工具调用分片
            tool_calls = getattr(delta, "tool_calls", None)
            if tool_calls:
                for tc in tool_calls:
                    _merge_tool_call(full_tool_calls, tc)

        print("\n\n【完整思考内容】:\n", full_reasoning or "<empty>")
        print("【完整回答内容】:\n", full_content or "<empty>")

        # assistant 消息回填上下文，供下一子轮继续推理
        assistant_message: Dict[str, Any] = {
            "role": "assistant",
            "content": full_content or "",
        }
        if full_tool_calls:
            assistant_message["tool_calls"] = full_tool_calls
        messages.append(assistant_message)

        # 没有工具调用，说明本轮已完成
        if not full_tool_calls:
            print("✅ 本轮无工具调用，对话结束")
            break

        print("\n🔧 开始执行工具调用...")
        for tool in full_tool_calls:
            func_name = tool["function"]["name"]
            args_str = tool["function"]["arguments"]
            tool_id = tool["id"]

            print(f"- 工具名: {func_name}")
            print(f"- 参数: {args_str or '{}'}")
            tool_result = execute_tool_call(func_name, args_str)
            print(f"- 结果: {tool_result}")

            # 工具执行结果回填上下文，让模型继续生成最终答案
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": tool_result,
                }
            )

        sub_turn += 1
    else:
        print(f"⚠️ 达到最大子轮次 {MAX_SUB_TURN}，强制终止")


def main():
    # 初始化 DeepSeek 客户端
    client = create_client()
    # 在 messages 最前面增加 system 提示词 + Few-Shot 样例
    messages = [
        {
            "role": "system",
            "content": """
    你是专业天气查询助手，请严格遵守规则：
    1. 查询天气必须先获取日期，再调用天气工具；
    2. get_weather 必须传入 location 和 date 两个参数；
    3. 不要编造天气数据，全部依赖工具返回结果。
    4. 输出全部使用英文

    ===== 参考样例 =====
    用户：杭州明天天气？
    流程：调用 get_date → 调用 get_weather(location="杭州", date="xxxx-xx-xx")

    用户：今天几号？
    流程：调用 get_date
        """,
        },
        {"role": "user", "content": "How's the weather in Hangzhou Tomorrow"},
    ]

    turn = 1
    messages.append({"role": "user", "content": "杭州明天天气怎么样？"})
    run_turn(client, turn, messages)

    turn = 2
    messages.append({"role": "user", "content": "那广州明天天气怎么样？"})
    run_turn(client, turn, messages)


if __name__ == "__main__":
    main()
