"""
节点跑量查询工具 — 通过 Grafana Prometheus API 查询前一完整24小时上行跑量数据
"""
import json
from datetime import datetime

import requests
from langchain_core.tools import tool

from agent.tools.common import (
    query_prometheus, get_previous_day_ms, make_error, logger,
)


def _calc_95th(values: list[float]) -> float:
    """计算降序第95百分位值"""
    if not values:
        return 0.0
    sorted_vals = sorted(values, reverse=True)
    idx = int(len(sorted_vals) * 0.05)
    return sorted_vals[idx]


@tool(description="查询指定SN节点的前一完整24小时上行跑量数据，返回JSON（含晚高峰18-24点95值、晚高峰20-22点均值、峰值及分钟级时序）")
def node_traffic_query(sn: str) -> str:
    """
    节点跑量查询工具

    入参：sn (str) — 设备序列号（即Grafana监控的hostname）
    返回：JSON格式
        - sn / date: 设备标识与数据日期
        - summary: { peak_Mbps, evening_95th_Mbps, evening_peak_avg_Mbps, total_traffic_GB }
        - traffic_data: "HH:MM: value_Mbps" 每行一个数据点，5分钟粒度
    """
    logger.info(f"[node_traffic_query] 开始查询跑量数据，SN={sn}")
    try:
        from_ms, to_ms = get_previous_day_ms()
        from_dt = datetime.fromtimestamp(from_ms / 1000)
        to_dt = datetime.fromtimestamp(to_ms / 1000)
        date_str = from_dt.strftime("%Y-%m-%d")

        expr = f'datacollect_net_out{{instance=~"{sn}"}} < 100*1000*1000*1000'
        series = query_prometheus(expr, from_ms, to_ms, step="5m")

        if not series:
            return json.dumps({
                "sn": sn, "date": date_str,
                "error": "未查询到跑量数据",
                "note": "请检查SN是否正确，或该节点可能暂无监控数据",
            }, ensure_ascii=False)

        all_points = sorted(
            (p for s in series for p in s["points"]),
            key=lambda x: x[0],
        )
        if not all_points:
            return json.dumps({
                "sn": sn, "date": date_str,
                "error": "查询到时间序列但无有效数据点",
            }, ensure_ascii=False)

        # ============ 分时段数据 ============
        # 注意：datacollect_net_out 返回单位为 bytes/sec
        full_values = [v for _, v in all_points]
        peak_bytes = max(full_values)
        # 5min = 300s；总流量 = sum(bytes/sec × 300s) / 1024³ → GB
        total_gb = sum(full_values) * 300 / (1024 ** 3)

        # 晚高峰 18:00~24:00
        evening_start = from_ms + 18 * 3600 * 1000
        evening_end = from_ms + 24 * 3600 * 1000
        evening_points = [v for t, v in all_points if evening_start <= t < evening_end]
        evening_95th = _calc_95th(evening_points)

        # 20:00~22:00 均值
        peak_start = from_ms + 20 * 3600 * 1000
        peak_end = from_ms + 22 * 3600 * 1000
        peak_points = [v for t, v in all_points if peak_start <= t < peak_end]
        peak_avg = sum(peak_points) / len(peak_points) if peak_points else 0.0

        # bytes/sec → Mbps: ×8 ÷ 1_000_000
        def _to_mbps(val: float) -> float:
            return round(val * 8 / 1_000_000, 2)

        # ============ 时序数据（简化为 "时间: 跑量Mbps"） ============
        traffic_lines = []
        for t_ms, v in all_points:
            ts = datetime.fromtimestamp(t_ms / 1000).strftime("%H:%M")
            traffic_lines.append(f"{ts}: {_to_mbps(v)}")

        return json.dumps({
            "sn": sn,
            "date": date_str,
            "summary": {
                "peak_Mbps": _to_mbps(peak_bytes),
                "evening_95th_Mbps": _to_mbps(evening_95th),
                "evening_peak_avg_Mbps": _to_mbps(peak_avg),
                "total_traffic_GB": round(total_gb, 2),
            },
            "traffic_data": traffic_lines,
        }, ensure_ascii=False, indent=2)

    except requests.RequestException as e:
        logger.error(f"[node_traffic_query] Grafana请求失败，SN={sn}，错误：{e}")
        return make_error(sn, f"Grafana查询失败：{e}")
    except Exception as e:
        logger.error(f"[node_traffic_query] 解析失败，SN={sn}，错误：{e}")
        return make_error(sn, f"查询跑量数据出错：{e}")


# if __name__ == "__main__":
#     import sys, os
#     _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     sys.path.insert(0, _root)
#     for key in list(sys.modules.keys()):
#         if key.startswith("agent"):
#             del sys.modules[key]
#     from agent.tools.node_traffic import node_traffic_query
#     res = node_traffic_query.func(sn="XYBM99E704C76B0B39")
#     print(res)
