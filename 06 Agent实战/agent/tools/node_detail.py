"""
节点详情查询工具 — 爬取监控平台页面，提取设备配置、运营商、资源标签、业务信息及任务状态
"""
import json
import re

import requests
from bs4 import BeautifulSoup, Tag
from langchain_core.tools import tool

from agent.tools.common import (
    MONITOR_BASE_URL, MONITOR_COOKIE, REQUEST_TIMEOUT,
    PROVINCE_KEYWORDS, safe_text, make_error, logger,
)


# ==================== 页面解析函数 ====================

def _find_card_by_header(soup: BeautifulSoup, keyword: str) -> Tag | None:
    """根据 card-header 中的文字找到对应的 card 元素"""
    for header in soup.find_all(["h5", "div", "span"], string=re.compile(keyword)):
        card = header.find_parent("div", class_="card")
        if card:
            return card
    return None


def _parse_badges(soup: BeautifulSoup) -> dict:
    """解析顶部 badge 栏：设备概要信息 + 资源标签"""
    result = {"设备概要": {}, "资源标签": []}
    for b in soup.select("span.badge"):
        text = safe_text(b)
        if not text:
            continue
        cls_list = b.get("class", [])

        if "badge-primary" in cls_list:
            if "平台架构" not in result["设备概要"]:
                result["设备概要"]["平台架构"] = text
            elif "渠道" in text and text not in result["资源标签"]:
                result["资源标签"].append(text)
        elif "badge-success" in cls_list:
            result["设备概要"]["招募标签"] = text
        elif "badge-light" in cls_list:
            if re.search(r"centos|ubun|debian|kernel|核", text, re.I):
                result["设备概要"]["系统_CPU_内存"] = text
            elif "带宽" in text:
                result["设备概要"]["带宽信息"] = text
            elif "磁盘" in text:
                result["设备概要"]["磁盘信息"] = text
            elif re.search(r"全锥|对称|端口限制|NAT", text):
                result["设备概要"]["网络类型"] = text
            elif re.search(PROVINCE_KEYWORDS, text):
                result["设备概要"]["地理位置_运营商"] = text
        elif "badge-warning" in cls_list and text not in result["资源标签"]:
            result["资源标签"].append(text)
    return result


def _parse_business_info(soup: BeautifulSoup) -> dict:
    """解析定向业务信息"""
    biz = {}
    div = soup.find(string=re.compile("定向业务"))
    if not div:
        return biz
    parent = div.find_parent("div")
    if not parent:
        return biz

    html = str(parent)
    m = re.search(r"(wxy[A-Za-z0-9]{20,})", html)
    if m:
        biz["定向业务APPID"] = m.group(1)
    m = re.search(r"部署业务[：:]\s*([a-f0-9]{32})", html)
    if m:
        biz["部署业务APPID"] = m.group(1)
    m = re.search(r"\[(\d+)\]\[(.+?)\]\[(.+?)\]", html)
    if m:
        biz["定向业务客户UID"] = m.group(1)
        biz["定向业务描述"] = re.sub(r"<[^>]+>", "", m.group(2))
        biz["定向业务时间"] = m.group(3)
    m = re.search(r"部署业务[^]]+\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", html)
    if m:
        biz["部署业务时间"] = m.group(1)
    return biz


def _parse_task_table(soup: BeautifulSoup) -> list:
    """解析「全部任务」表格"""
    tasks = []
    card = _find_card_by_header(soup, "全部任务")
    if not card:
        return tasks
    outer_table = card.find("table", class_=re.compile(r"table"))
    if not outer_table:
        return tasks

    for row in outer_table.find_all("tr")[1:]:
        cols = row.find_all("td", recursive=False)
        if len(cols) < 8:
            continue

        task = {
            "序号": safe_text(cols[0]),
            "UID": safe_text(cols[1]),
            "客户名": safe_text(cols[2]),
            "业务标签": safe_text(cols[3]),
            "APPID": safe_text(cols[4].find("a")) if cols[4].find("a") else safe_text(cols[4]),
            "镜像名称": safe_text(cols[5]),
            "定向业务": safe_text(cols[6]),
            "缓存GB": safe_text(cols[7]),
        }

        detail_col = cols[8] if len(cols) > 8 else cols[-1]
        detail_html = str(detail_col)
        detail_text = safe_text(detail_col)

        m = re.search(r"TaskInfo\?task_id=(\d+)", detail_html)
        if m:
            task["TaskID"] = m.group(1)

        inner_table = detail_col.find("table")
        if inner_table:
            for cell in inner_table.find_all("td"):
                cell_text = safe_text(cell)
                if re.match(r"^v\d+\.\d+\.\d+", cell_text):
                    task["版本号"] = cell_text
                    break
        if "版本号" not in task:
            m = re.search(r"v\d+\.\d+\.\d+[-]?\S*", detail_text)
            if m:
                task["版本号"] = m.group(0)

        m = re.search(r"(\d+/\d+)", detail_text)
        if m:
            task["实例数"] = m.group(1)

        status_span = detail_col.find("span", style=re.compile(r"color"))
        if status_span:
            task["状态"] = safe_text(status_span)

        m = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\[\d+d\d+m\])", detail_html)
        if m:
            task["调度时间"] = m.group(1)

        tasks.append(task)
    return tasks


def _parse_epod_cpod(soup: BeautifulSoup) -> list:
    """解析「任务信息」折叠面板中的 EPod/CPod/TaskInfo 详细数据"""
    items = []
    card = _find_card_by_header(soup, "任务信息")
    if not card:
        return items
    collapse_body = card.find("div", class_="collapse")
    if not collapse_body:
        return items
    main_table = collapse_body.find("table", class_=re.compile(r"table"))
    if not main_table:
        return items

    for row in main_table.find_all("tr")[1:]:
        cols = row.find_all("td", recursive=False)
        if len(cols) < 4:
            continue
        items.append({
            "序号": safe_text(cols[0]),
            "EPod": safe_text(cols[1])[:300],
            "CPod": safe_text(cols[2])[:300],
            "TaskInfo": safe_text(cols[3])[:300],
        })
    return items


def _parse_node_info(sn: str) -> dict:
    """爬取并解析节点详情页面，返回结构化数据字典"""
    url = f"{MONITOR_BASE_URL}/monitor/node/info?&sn={sn}"
    resp = requests.get(url, headers={"Cookie": MONITOR_COOKIE}, timeout=REQUEST_TIMEOUT)
    resp.encoding = "utf-8"
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    result = {}

    badge_data = _parse_badges(soup)
    result["设备概要"] = badge_data["设备概要"]
    result["资源标签"] = badge_data["资源标签"]

    biz = _parse_business_info(soup)
    if biz:
        result["业务信息"] = biz

    tasks = _parse_task_table(soup)
    if tasks:
        result["全部任务"] = tasks

    epod = _parse_epod_cpod(soup)
    if epod:
        result["任务详细状态"] = epod

    return result


# ==================== Agent 工具 ====================

@tool(description="查询指定SN节点的详细信息，返回JSON字符串，包含设备配置、运营商、资源标签、业务信息及各任务运行状态")
def node_detail_query(sn: str) -> str:
    """
    节点详情查询工具

    入参：sn (str) — 设备序列号
    返回：JSON格式的结构化数据
        - 设备概要（平台架构、CPU/内存、磁盘、带宽、系统）
        - 运营商信息（地理位置、运营商、网络类型）
        - 资源标签（异网标签、同省调度、只跑晚4h、渠道设备等）
        - 业务信息（定向业务APPID、部署业务APPID、客户UID、业务描述、部署时间）
        - 全部任务列表（客户名、APPID、镜像、TaskID、版本号、实例数、状态等）
    """
    logger.info(f"[node_detail_query] 开始查询节点信息，SN={sn}")
    try:
        data = _parse_node_info(sn)
        data["sn"] = sn
        return json.dumps(data, ensure_ascii=False, indent=2)
    except requests.ConnectionError:
        return make_error(sn, "连接监控平台失败，请检查网络或配置文件中的 monitor_base_url")
    except requests.Timeout:
        return make_error(sn, "请求监控平台超时，请稍后重试")
    except requests.RequestException as e:
        return make_error(sn, f"请求监控平台失败：{e}")
    except Exception as e:
        logger.error(f"[node_detail_query] 解析失败，SN={sn}，错误：{e}")
        return make_error(sn, f"解析节点信息出错：{e}")


# if __name__ == "__main__":
#     # 用法：从项目根目录执行
#     #   python -m agent.tools.node_detail
#     #   python agent/tools/node_detail.py
#     import sys, os
#     _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     sys.path.insert(0, _root)
#     for key in list(sys.modules.keys()):
#         if key.startswith("agent"):
#             del sys.modules[key]
#     from agent.tools.node_detail import node_detail_query
#     res = node_detail_query.func(sn="XRVD8BF927F82C3B")
#     print(res[:800])
