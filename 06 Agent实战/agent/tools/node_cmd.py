"""
节点命令执行工具 — 通过隧道API在指定节点上执行命令
"""
import json

import requests
from langchain_core.tools import tool

from agent.tools.common import tools_conf, logger


CMD_URL = tools_conf.get("tunnel_cmd_url", "")
CMD_COOKIE = tools_conf.get("tunnel_cmd_cookie", "")


@tool(description="在指定SN的节点上执行shell命令，返回命令执行结果")
def node_cmd_execute(sn: str, cmd: str) -> str:
    """
    节点命令执行工具

    入参：
        sn (str) — 设备序列号
        cmd (str) — 要执行的shell命令

    返回：str — 命令执行的标准输出(stdout)或错误信息(stderr)
    """
    logger.info(f"[node_cmd_execute] 在节点 {sn} 上执行命令: {cmd}")

    try:
        resp = requests.post(
            CMD_URL,
            headers={
                "Cookie": CMD_COOKIE,
                "Content-Type": "application/json",
            },
            json={"sn": sn, "cmd": cmd},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        stdout = data.get("stdout", "")
        stderr = data.get("stderr", "")

        if stdout:
            return stdout.strip()
        if stderr:
            return f"[错误] {stderr.strip()}"
        return "(无输出)"

    except requests.Timeout:
        return f"[超时] 节点 {sn} 命令执行超时"
    except requests.RequestException as e:
        return f"[失败] 请求隧道接口失败: {e}"
    except Exception as e:
        logger.error(f"[node_cmd_execute] 解析失败: {e}")
        return f"[错误] 无法解析命令执行结果: {e}"


# if __name__ == "__main__":
#     import sys, os
#     _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     sys.path.insert(0, _root)
#     for k in list(sys.modules.keys()):
#         if k.startswith("agent"):
#             del sys.modules[k]
#     from agent.tools.node_cmd import node_cmd_execute
#     r = node_cmd_execute.func(sn="XRVDC8FC2D925D49", cmd="hostname")
#     print(r)
