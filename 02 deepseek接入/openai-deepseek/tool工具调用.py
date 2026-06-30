import os
import json
from openai import OpenAI
from datetime import datetime

# ===================== 工具定义 =====================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "Get the current date",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply the location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city name"},
                    "date": {
                        "type": "string",
                        "description": "The date in format YYYY-mm-dd",
                    },
                },
                "required": ["location", "date"],
            },
        },
    },
]


# ===================== 模拟工具实现 =====================
def get_date_mock():
    return datetime.now().strftime("%Y-%m-%d")


def get_weather_mock(location, date):
    return f"{location} {date}: Cloudy 7~13°C"


TOOL_CALL_MAP = {"get_date": get_date_mock, "get_weather": get_weather_mock}

# ===================== 初始化客户端 =====================
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY2"), base_url="https://api.deepseek.com"
)

# 最大子轮次，防止死循环
MAX_SUB_TURN = 10


def run_turn(turn: int, messages: list):
    sub_turn = 1
    while sub_turn <= MAX_SUB_TURN:
        print(f"\n===== Turn {turn}.{sub_turn} 开始请求 =====")

        try:
            # 开启流式输出 stream=True
            stream = client.chat.completions.create(
                model="deepseek-v4-pro",
                messages=messages,
                tools=tools,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}},
                stream=True,  # 核心：开启流式
            )
        except Exception as e:
            print(f"接口请求异常: {str(e)}")
            break

        # 用于拼接流式分片
        full_reasoning = ""  # 思考过程
        full_content = ""  # 普通回答内容
        full_tool_calls = []  # 收集工具调用信息

        print("【模型思考过程】", end="", flush=True)

        # 遍历流式分片
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 1. 实时输出 & 拼接 思考链 reasoning_content
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                reasoning_piece = delta.reasoning_content
                full_reasoning += reasoning_piece
                print(reasoning_piece, end="", flush=True)

            # 2. 实时输出 & 拼接 普通回答内容
            if delta.content:
                content_piece = delta.content
                full_content += content_piece
                print(content_piece, end="", flush=True)

            # 3. 收集流式分片里的 tool_calls
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    # 合并分片工具调用
                    if len(full_tool_calls) <= tc.index:
                        full_tool_calls.append(tc)
                    else:
                        full_tool_calls[
                            tc.index
                        ].function.arguments += tc.function.arguments

        print("\n\n【完整思考内容】:\n", full_reasoning)
        print("【完整回答内容】:\n", full_content)

        # 构造完整消息，加入上下文
        final_msg = {
            "role": "assistant",
            "content": full_content,
            "reasoning_content": full_reasoning,
        }
        if full_tool_calls:
            final_msg["tool_calls"] = full_tool_calls
        messages.append(final_msg)

        # 判断是否有工具调用
        if not full_tool_calls:
            print("✅ 本轮无工具调用，对话结束")
            break

        # 执行所有工具调用
        print("\n🔧 开始执行工具调用...")
        for tool in full_tool_calls:
            func_name = tool.function.name
            args_str = tool.function.arguments

            try:
                args = json.loads(args_str)
                tool_func = TOOL_CALL_MAP[func_name]
                tool_result = tool_func(**args)
                print(f"工具 {func_name} 执行结果: {tool_result}")
            except Exception as e:
                print(f"工具 {func_name} 执行失败: {str(e)}")
                tool_result = f"Tool {func_name} error: {str(e)}"

            # 工具结果回填上下文
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool.id,
                    "content": tool_result,
                }
            )

        sub_turn += 1
    else:
        print(f"⚠️ 达到最大子轮次 {MAX_SUB_TURN}，强制终止")


# ===================== 执行对话 =====================
if __name__ == "__main__":
    # 第一轮提问：杭州明天天气
    turn = 1
    messages = [
        {"role": "system", "content": "回答均用中文回答。"},
        {"role": "user", "content": "How's the weather in Hangzhou Tomorrow"},
    ]
    run_turn(turn, messages)

    # 第二轮提问：广州明天天气（复用上下文）
    turn = 2
    messages.append(
        {"role": "user", "content": "How's the weather in Guangzhou Tomorrow"}
    )
    run_turn(turn, messages)
