"""
评估器：批量运行测试用例，收集结果，输出对比报告。
"""

import json
from typing import List, Callable

from client import create_client, chat_completion_with_log


def run_single_prompt(
    prompt_config: dict,
    test_cases: list,
    get_messages_fn: Callable,
) -> list:
    """
    对某个 prompt 配置跑所有 test cases。

    Args:
        prompt_config: prompts.py 中的 prompt 配置 dict
        test_cases: test_cases.py 中的 case 列表
        get_messages_fn: 函数，接收 (prompt_config, case) 返回 messages 列表

    Returns:
        result 列表，每个元素是 chat_completion_with_log 的返回
    """
    client = create_client()
    results = []
    prompt_name = prompt_config["name"]
    temperature = prompt_config.get("temperature", 0.3)

    print(f"\\n{'='*60}")
    print(f"  运行: {prompt_config['label']} (temp={temperature})")
    print(f"{'='*60}")

    for case in test_cases:
        case_id = f"{prompt_name}__{case['id']}"
        print(f"  [{case['id']}] ", end="", flush=True)

        messages = get_messages_fn(prompt_config, case)

        result = chat_completion_with_log(
            client=client,
            messages=messages,
            case_id=case_id,
            temperature=temperature,
        )
        results.append(result)

        if result["success"]:
            preview = result["content"][:80].replace("\\n", " ")
            print(f"OK ({result['elapsed']}s) {preview}...")
        else:
            print(f"FAIL: {result['error']}")

    return results


def print_comparison_report(results_by_prompt: dict):
    """
    输出多套 prompt 的对比报告。

    Args:
        results_by_prompt: {prompt_label: [result, ...]}
    """
    print("\\n" + "=" * 70)
    print("  Prompt 对比报告")
    print("=" * 70)

    for label, results in results_by_prompt.items():
        total = len(results)
        success = sum(1 for r in results if r["success"])
        fail = total - success
        avg_time = sum(r["elapsed"] for r in results) / total if total > 0 else 0

        print(f"\\n  [{label}]")
        print(f"    通过: {success}/{total}")
        print(f"    失败: {fail}")
        print(f"    平均耗时: {avg_time:.2f}s")

        if fail > 0:
            print("    失败详情:")
            for r in results:
                if not r["success"]:
                    print(f"      - {r['case_id']}: {r['error']}")

    print("\\n" + "=" * 70)


def export_results(results_by_prompt: dict, filepath: str):
    """将结果导出为 JSON 文件，方便后续分析。"""
    output = {}
    for label, results in results_by_prompt.items():
        output[label] = [
            {
                "case_id": r["case_id"],
                "success": r["success"],
                "content": r["content"],
                "elapsed": r["elapsed"],
                "error": r["error"],
            }
            for r in results
        ]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\\n结果已导出到: {filepath}")
