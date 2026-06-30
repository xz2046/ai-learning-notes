from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import AgentMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.runtime import Runtime
import os


@tool(description="查询天气，传入城市名称字符串，返回字符串天气信息")
def get_weather(city: str) -> str:
    return f"{city}天气：晴天"


class MyMiddleware(AgentMiddleware):
    def before_agent(self, state: AgentState, runtime: Runtime) -> None:
        print(f"[before_agent] agent启动，并附带 {len(state['messages'])} 条消息")

    def after_agent(self, state: AgentState, runtime: Runtime) -> None:
        print(f"[after_agent] agent结束，并附带 {len(state['messages'])} 条消息")

    def before_model(self, state: AgentState, runtime: Runtime) -> None:
        print(f"[before_model] 模型即将调用，并附带 {len(state['messages'])} 条消息")

    def after_model(self, state: AgentState, runtime: Runtime) -> None:
        print(f"[after_model] 模型调用结束，并附带 {len(state['messages'])} 条消息")

    def wrap_model_call(self, request, handler):
        print("模型调用啦")
        return handler(request)

    def wrap_tool_call(self, request, handler):
        print(f"工具执行：{request.tool_call['name']}")
        print(f"工具执行传入参数：{request.tool_call['args']}")
        return handler(request)


agent = create_agent(
    model=ChatOpenAI(
        model="deepseek-v4-flash",
        api_key=os.environ.get("DEEPSEEK_API_KEY2"),
        base_url="https://api.deepseek.com",
        temperature=0.2,
    ),
    tools=[get_weather],
    middleware=[MyMiddleware()],
    system_prompt="你是一个聊天助手,回答用户问题。",
)

res = agent.invoke({
    "messages": [
        {"role": "user", "content": "深圳今天的天气如何呀，如何穿衣"}
    ]
})

print("​**********​")
print(res)
