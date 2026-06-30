"""
模型 API 客户端封装。

直接从 week2_llm_api_demo/client.py 复用，
保持一致的 API Key 管理、重试、超时机制。
"""

import os
import time
from typing import Any, List, Optional
from openai import OpenAI

BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-v4-pro"
MAX_RETRIES = 3
RETRY_SLEEP_SECONDS = 2
REQUEST_TIMEOUT = 60


def create_client() -> OpenAI:
    """初始化 DeepSeek 客户端，检查 API Key 是否存在。"""
    api_key = os.environ.get("DEEPSEEK_API_KEY2")
    if not api_key:
        raise RuntimeError(
            "Missing environment variable: DEEPSEEK_API_KEY2\\n"
            "请先在 .env 或环境变量中设置你的 API Key。"
        )
    return OpenAI(api_key=api_key, base_url=BASE_URL, timeout=REQUEST_TIMEOUT)


def chat_completion(
    client: OpenAI,
    messages: List[dict],
    temperature: float = 0.3,
    max_tokens: Optional[int] = None,
    response_format: Optional[dict] = None,
) -> str:
    """发送非流式对话请求，返回文本内容。"""
    kwargs: dict = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if response_format is not None:
        kwargs["response_format"] = response_format

    last_error: Any = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as exc:
            last_error = exc
            if attempt == MAX_RETRIES:
                break
            print(f"  请求异常，第 {attempt} 次重试: {exc}")
            time.sleep(RETRY_SLEEP_SECONDS)

    raise RuntimeError(f"请求失败，已重试 {MAX_RETRIES} 次: {last_error}")


def chat_completion_with_log(
    client: OpenAI,
    messages: List[dict],
    case_id: str,
    temperature: float = 0.3,
    max_tokens: Optional[int] = None,
    response_format: Optional[dict] = None,
) -> dict:
    """带日志的包装，返回结果和相关元数据。"""
    import time as time_module
    start = time_module.time()
    try:
        content = chat_completion(client, messages, temperature, max_tokens, response_format)
        elapsed = time_module.time() - start
        return {"case_id": case_id, "success": True, "content": content, "elapsed": round(elapsed, 2), "error": None}
    except Exception as exc:
        elapsed = time_module.time() - start
        return {"case_id": case_id, "success": False, "content": None, "elapsed": round(elapsed, 2), "error": str(exc)}
