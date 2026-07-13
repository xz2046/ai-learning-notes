import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
import asyncio

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

client = MultiServerMCPClient(
    {
        "my-tools": {
            "command": "python",
            "transport": "stdio",
            "args": [r"C:\Users\admin\Desktop\学习\07 LangGraph学习\10 MCP服务实现.py"]
        }
    }
)

async def main():
    tools = await client.get_tools()
    agent = create_agent(llm, tools)

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "帮我查一下北京的天气"
                }
            ]
        }
    )

    print(result)


asyncio.run(main())