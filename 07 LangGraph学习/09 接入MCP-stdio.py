import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
import asyncio
os.environ['AMAP_MAPS_API_KEY'] = "2be5adb3a47e9c16df44e657e3a71c18"

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.environ.get("DEEPSEEK_API_KEY2"),
    base_url="https://api.deepseek.com",
)

client = MultiServerMCPClient(
    {
        "amap-maps": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@amap/amap-maps-mcp-server"],
            "env": {
                "AMAP_MAPS_API_KEY": os.environ.get("AMAP_MAPS_API_KEY")
            }
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
                    "content": "帮我查一下西安钟楼附近的咖啡店，并给出通俗一点的出行建议"
                }
            ]
        }
    )

    print(result)


asyncio.run(main())