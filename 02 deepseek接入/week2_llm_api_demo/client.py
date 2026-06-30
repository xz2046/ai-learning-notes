import os
import time
from typing import Any, List
from openai import OpenAI

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-pro"
MAX_RETRIES = 3
RETRY_SLEEP_SECONDS = 2
REQUEST_TIMEOUT = 60


def create_client() -> OpenAI:
    # 初始化客户端，并检查 API Key 是否存在
    api_key = os.environ.get("DEEPSEEK_API_KEY2")
    if not api_key:
        raise RuntimeError("Missing environment variable: DEEPSEEK_API_KEY2")
    return OpenAI(api_key=api_key, base_url=BASE_URL, timeout=REQUEST_TIMEOUT)


def create_chat_stream(client: OpenAI, messages: List[dict], tools: List[dict]):
    last_error: Any = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}},
                stream=True,
            )
        except Exception as exc:
            last_error = exc
            if attempt == MAX_RETRIES:
                break
            # 请求失败后简单重试，避免偶发网络波动直接中断
            print(f"接口请求异常，第 {attempt} 次重试: {exc}")
            time.sleep(RETRY_SLEEP_SECONDS)
    raise RuntimeError(f"接口请求失败，已重试 {MAX_RETRIES} 次: {last_error}")
