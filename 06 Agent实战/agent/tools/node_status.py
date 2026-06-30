"""
节点运行状态查询工具 — 从 Grafana Prometheus 获取设备运行指标并判断健康状态
"""
import time

import requests
from langchain_core.tools import tool

from agent.tools.common import (
    query_prometheus, make_error, logger,
)


def _query_latest(expr: str) -> float | None:
    """查询最近5分钟的最近一个数据点"""
    now_ms = int(time.time() * 1000)
    five_min_ago = now_ms - 5 * 60 * 1000
    series = query_prometheus(expr, five_min_ago, now_ms, step="5m")
    if series and series[0]["points"]:
        return series[0]["points"][-1][1]
    return None


def _query_disk_max(expr: str) -> float | None:
    """查询各磁盘指标，返回最大值"""
    now_ms = int(time.time() * 1000)
    five_min_ago = now_ms - 5 * 60 * 1000
    series = query_prometheus(expr, five_min_ago, now_ms, step="5m")
    if not series:
        return None
    vals = [s["points"][-1][1] for s in series if s["points"]]
    return max(vals) if vals else None


def _status_label(value: float | None, thresholds: list[tuple[float, str]], default: str = "未知") -> str:
    """根据阈值判定状态标签"""
    if value is None:
        return default
    for threshold, label in thresholds:
        if value <= threshold:
            return label
    return thresholds[-1][1] if thresholds else default


@tool(description="查询指定SN节点的运行状态，返回简洁中文描述（如：cpu正常，负载正常，运行2.9天，ping正常，磁盘使用96.4%）")
def node_status_query(sn: str) -> str:
    """
    节点运行状态查询工具

    入参：sn (str) — 设备序列号
    返回：str — 中文逗号分隔的状态描述
    """
    logger.info(f"[node_status_query] 开始查询运行状态，SN={sn}")

    try:
        cpu = _query_latest(f'datacollect_cpu_used{{instance=~"{sn}"}}')
        load_1m = _query_latest(f'datacollect_load.1min{{instance=~"{sn}"}}')
        uptime = _query_latest(f'datacollect_uptime{{instance=~"{sn}"}}')
        mem = _query_latest(f'datacollect_mem_used{{instance=~"{sn}"}}')
        ping4 = _query_latest(f'datacollect_basics_ping_packetLoss{{instance=~"{sn}"}}')
        ping6 = _query_latest(f'datacollect_basics_ping_packetLoss_ipv6{{instance=~"{sn}"}}')
        # 磁盘读写等待时间（取各盘中最大的）
        disk_r = _query_disk_max(f'datacollect_disk_r_await{{instance=~"{sn}"}}')
        disk_w = _query_disk_max(f'datacollect_disk_w_await{{instance=~"{sn}"}}')

        parts = []

        # CPU（CDN服务器阈值适当调高）
        label = _status_label(cpu, [(75, "正常"), (90, "偏高"), (100, "过高")])
        parts.append(f"cpu{label}")

        # Load（48核参考，CDN日常负载较高）
        label = _status_label(load_1m, [(48, "正常"), (72, "偏高"), (96, "过高")])
        parts.append(f"负载{label}")

        # 内存
        if mem is not None:
            mem_gb = mem / (1024 ** 3)
            label = _status_label(mem_gb, [(48, "正常"), (56, "偏高"), (100, "过高")])
            parts.append(f"内存{label}({mem_gb:.0f}GB)")
        else:
            parts.append("内存未知")

        # 磁盘读写负载（取r_await和w_await中最大值，单位ms）
        disk_max = max(v for v in [disk_r, disk_w] if v is not None) if any(v is not None for v in [disk_r, disk_w]) else None
        label = _status_label(disk_max, [(5, "正常"), (20, "偏高"), (999, "过高")])
        parts.append(f"磁盘{label}")

        # Uptime
        if uptime is not None:
            days = uptime / 86400
            parts.append(f"运行{days:.1f}天")
        else:
            parts.append("运行未知")

        # Ping丢包 (取IPv4和IPv6中较差的)
        ping_max = max(p for p in [ping4, ping6] if p is not None) if any(p is not None for p in [ping4, ping6]) else None
        label = _status_label(ping_max, [(0, "正常"), (3, "轻微丢包"), (100, "严重丢包")])
        parts.append(f"ping{label}")

        return "，".join(parts)

    except requests.RequestException as e:
        logger.error(f"[node_status_query] 请求失败，SN={sn}，错误：{e}")
        return f"查询失败：{e}"
    except Exception as e:
        logger.error(f"[node_status_query] 解析失败，SN={sn}，错误：{e}")
        return f"查询失败：{e}"


if __name__ == "__main__":
    import sys, os
    _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, _root)
    for key in list(sys.modules.keys()):
        if key.startswith("agent"):
            del sys.modules[key]
    from agent.tools.node_status import node_status_query
    res = node_status_query.func(sn="XYBM99E704C76B0B39")
    print(res)
