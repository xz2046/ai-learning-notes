"""
工具模块共享配置与工具函数
"""
import json
import re
from datetime import datetime, timedelta

import requests

from utils.config_handler import tools_conf
from utils.logger_handler import logger

# ==================== 配置（从 config/tools.yaml 读取） ====================
MONITOR_BASE_URL = tools_conf.get("monitor_base_url", "")
MONITOR_COOKIE = tools_conf.get("monitor_cookie", "")
REQUEST_TIMEOUT = 15  # 请求超时（秒）

GRAFANA_BASE_URL = tools_conf.get("grafana_base_url", "")
GRAFANA_COOKIE = tools_conf.get("grafana_cookie", "")
PROMETHEUS_DS_UID = tools_conf.get("prometheus_datasource_uid", "")
PROMETHEUS_DS_TYPE = tools_conf.get("prometheus_datasource_type", "prometheus")

# 省份关键词列表
PROVINCE_KEYWORDS = (
    "河南|广东|北京|上海|浙江|江苏|山东|四川|湖北|湖南|福建|安徽|"
    "河北|陕西|辽宁|江西|重庆|天津|云南|贵州|广西|山西|吉林|"
    "黑龙江|甘肃|内蒙古|新疆|海南|宁夏|青海|西藏"
)


def safe_text(el) -> str:
    """安全提取标签纯文本"""
    return el.get_text(strip=True) if el is not None else ""


def query_prometheus(expr: str, from_ms: int, to_ms: int, step: str = "15m") -> list[dict]:
    """
    通过 Grafana API 执行 PromQL 查询，返回时间序列数据。
    
    :param expr: PromQL 表达式
    :param from_ms: 起始时间（毫秒时间戳）
    :param to_ms: 结束时间（毫秒时间戳）
    :param step: 数据点间隔
    :return: 时间序列列表，每个元素含 labels / points / metric
    """
    url = f"{GRAFANA_BASE_URL}/api/ds/query"
    headers = {
        "Cookie": GRAFANA_COOKIE,
        "Content-Type": "application/json",
    }
    payload = {
        "queries": [{
            "datasource": {"type": PROMETHEUS_DS_TYPE, "uid": PROMETHEUS_DS_UID},
            "rawQuery": True,
            "expr": expr,
            "refId": "A",
            "step": step,
            "maxDataPoints": 300,
        }],
        "from": str(from_ms),
        "to": str(to_ms),
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    series_list = []
    for result in data.get("results", {}).values():
        for frame in result.get("frames", []):
            schema = frame.get("schema", {})
            fields = schema.get("fields", [])
            data_vals = frame.get("data", {}).get("values", [])
            if len(data_vals) < 2:
                continue

            times, values = data_vals[0], data_vals[1]
            labels = {}
            for field in fields:
                if field.get("name") == "Time":
                    continue
                labels = field.get("labels", {})
                break

            points = [(int(t), float(v)) for t, v in zip(times, values) if v is not None]
            series_list.append({"labels": labels, "points": points, "metric": schema.get("name", "")})

    return series_list


def get_previous_day_ms() -> tuple[int, int]:
    """获取前一完整自然日的毫秒时间戳范围 00:00:00 ~ 23:59:59"""
    yesterday = datetime.now() - timedelta(days=1)
    day_start = datetime(yesterday.year, yesterday.month, yesterday.day)
    day_end = day_start + timedelta(days=1) - timedelta(seconds=1)
    return int(day_start.timestamp() * 1000), int(day_end.timestamp() * 1000)


def make_error(sn: str, msg: str) -> str:
    """构造统一错误 JSON 字符串"""
    return json.dumps({"sn": sn, "error": msg}, ensure_ascii=False)
