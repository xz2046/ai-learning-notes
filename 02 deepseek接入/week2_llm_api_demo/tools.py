import json
from datetime import datetime
from typing import Any, Dict, Tuple

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "获取当前日期",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取某个地点在指定日期的天气，用户需要提供地点和日期。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名称"},
                    "date": {
                        "type": "string",
                        "description": "日期，格式为 YYYY-mm-dd",
                    },
                },
                "required": ["location", "date"],
            },
        },
    },
]


def get_date_mock() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_weather_mock(location: str, date: str) -> str:
    return f"{location} {date}: 多云 7~13°C"


TOOL_CALL_MAP = {
    "get_date": get_date_mock,
    "get_weather": get_weather_mock,
}


def _validate_date_str(date_str: str) -> None:
    datetime.strptime(date_str, "%Y-%m-%d")


def validate_tool_args(func_name: str, args: Dict[str, Any]) -> Tuple[bool, str]:
    # 对工具参数做基础校验，避免模型传错参数直接导致程序异常
    if func_name == "get_date":
        return True, ""

    if func_name == "get_weather":
        if not isinstance(args, dict):
            return False, "arguments must be a JSON object"
        if "location" not in args or not isinstance(args["location"], str) or not args["location"].strip():
            return False, "location is required and must be a non-empty string"
        if "date" not in args or not isinstance(args["date"], str):
            return False, "date is required and must be a string in YYYY-mm-dd format"
        try:
            _validate_date_str(args["date"])
        except ValueError:
            return False, "date must be in YYYY-mm-dd format"
        return True, ""

    return False, f"unsupported tool: {func_name}"


def execute_tool_call(func_name: str, args_str: str) -> str:
    if func_name not in TOOL_CALL_MAP:
        return f"Tool {func_name} error: unsupported tool"

    try:
        args = json.loads(args_str) if args_str else {}
    except json.JSONDecodeError as exc:
        return f"Tool {func_name} error: invalid JSON arguments: {exc}"

    is_valid, err = validate_tool_args(func_name, args)
    if not is_valid:
        return f"Tool {func_name} error: {err}"

    try:
        tool_func = TOOL_CALL_MAP[func_name]
        return str(tool_func(**args))
    except Exception as exc:
        return f"Tool {func_name} error: {exc}"
