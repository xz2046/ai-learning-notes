from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import os


@tool
def get_weather(city: str, date: str) -> dict:
    """查询指定城市指定日期的天气"""
    return {"city": city, "date": date, "weather": "晴天"}


agent = create_agent(
    model=ChatOpenAI(
        model="deepseek-v4-flash",
        api_key=os.environ.get("DEEPSEEK_API_KEY2"),
        base_url="https://api.deepseek.com",
        temperature=0.2,
    ),
    tools=[get_weather],
    system_prompt="""
        你是一个聊天助手。
        回答天气问题时必须基于工具返回结果。
        如果工具返回信息不足，不要猜测，直接说明信息不足。
        如果缺少必要参数，先向用户追问。
        """,
)

res = agent.invoke({"messages": [{"role": "user", "content": "明天西安天气如何？"}]})

for msg in res["messages"]:
    print(type(msg).__name__, msg.content)
