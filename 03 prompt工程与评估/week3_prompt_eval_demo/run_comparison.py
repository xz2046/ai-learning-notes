"""
入口：加载 prompt + 测试用例，跑对比实验。

用法：
    python run_comparison.py              # 跑所有 prompt 对比
    python run_comparison.py --quick       # 只跑摘要对比（验证代码可用）
    python run_comparison.py --summary     # 只跑摘要对比
    python run_comparison.py --classify    # 只跑分类对比
    python run_comparison.py --ops         # 只跑运维问答对比
"""

import sys

from prompts import ALL_PROMPTS, SUMMARY_PROMPT_A, SUMMARY_PROMPT_B
from prompts import CLASSIFY_PROMPT_A, CLASSIFY_PROMPT_B
from prompts import OPS_QA_PROMPT_A, OPS_QA_PROMPT_B
from test_cases import TEST_CASES
from evaluator import run_single_prompt, print_comparison_report, export_results


def build_summary_messages(prompt: dict, case: dict) -> list:
    """构建摘要任务的 messages。"""
    return [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": f"请摘要以下文本：\\n\\n{case['user']}"},
    ]


def build_classify_messages(prompt: dict, case: dict) -> list:
    """构建分类任务的 messages。"""
    return [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": case["user"]},
    ]


def build_ops_qa_messages(prompt: dict, case: dict) -> list:
    """构建运维问答任务的 messages。"""
    return [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": case["user"]},
    ]


TASK_BUILDERS = {
    "summary": build_summary_messages,
    "classify": build_classify_messages,
    "ops_qa": build_ops_qa_messages,
}


def run_comparison(task: str, prompt_pair: tuple, label: str):
    """跑某类任务的两版对比。"""
    prompt_a, prompt_b = prompt_pair
    cases = [c for c in TEST_CASES if c["task"] == task]

    if not cases:
        print(f"没有找到 {task} 类型的测试用例")
        return

    print(f"\\n{'#'*60}")
    print(f"# {label} 对比实验")
    print(f"# 测试用例数: {len(cases)}")
    print(f"{'#'*60}")

    results_a = run_single_prompt(prompt_a, cases, TASK_BUILDERS[task])
    results_b = run_single_prompt(prompt_b, cases, TASK_BUILDERS[task])

    print_comparison_report({
        prompt_a["label"]: results_a,
        prompt_b["label"]: results_b,
    })

    return {prompt_a["label"]: results_a, prompt_b["label"]: results_b}


def run_all():
    """跑全部对比实验。"""
    all_results = {}

    r = run_comparison("summary", (SUMMARY_PROMPT_A, SUMMARY_PROMPT_B), "摘要")
    if r:
        all_results.update(r)

    r = run_comparison("classify", (CLASSIFY_PROMPT_A, CLASSIFY_PROMPT_B), "分类")
    if r:
        all_results.update(r)

    r = run_comparison("ops_qa", (OPS_QA_PROMPT_A, OPS_QA_PROMPT_B), "运维问答")
    if r:
        all_results.update(r)

    if all_results:
        export_results(all_results, "eval_results.json")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--quick" in args:
        run_comparison("summary", (SUMMARY_PROMPT_A, SUMMARY_PROMPT_B), "摘要（快速验证）")
    elif "--summary" in args:
        run_comparison("summary", (SUMMARY_PROMPT_A, SUMMARY_PROMPT_B), "摘要")
    elif "--classify" in args:
        run_comparison("classify", (CLASSIFY_PROMPT_A, CLASSIFY_PROMPT_B), "分类")
    elif "--ops" in args:
        run_comparison("ops_qa", (OPS_QA_PROMPT_A, OPS_QA_PROMPT_B), "运维问答")
    else:
        run_all()
