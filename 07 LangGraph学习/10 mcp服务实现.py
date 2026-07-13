from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")


@mcp.tool()
def get_weather(city: str) -> str:
    """查询某个城市的天气信息"""
    fake_data = {
        "北京": "晴，30度，可能有雷暴阵雨",
        "上海": "多云，28度",
        "广州": "阵雨，32度",
    }
    return fake_data.get(city, f"未找到 {city} 的天气信息")


@mcp.tool()
def add(a: int, b: int) -> int:
    """返回两个整数之和"""
    return a + b


if __name__ == "__main__":
    mcp.run()