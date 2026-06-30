# Prompt 评估测试工具

## 目标

对比不同 Prompt 设计的效果，用数据而不是感觉来判断哪个 prompt 更好。

## 项目结构

week3_prompt_eval_demo/
  client.py              # API 客户端（复用 week2_llm_api_demo）
  prompts.py             # 3 套 prompt，每套 2 个版本
  test_cases.py          # 12 个测试用例
  evaluator.py           # 批量运行 + 结果收集 + 对比报告
  run_comparison.py      # 入口
  requirements.txt
  .env.example
  README.md

## 快速开始

1. 设置 API Key
   cp .env.example .env
   编辑 .env，填入你的 DeepSeek API Key

   或者直接设置环境变量：
   ="your-key"

2. 安装依赖
   pip install -r requirements.txt

3. 运行快速验证（只跑摘要，验证代码正常）
   python run_comparison.py --quick

4. 跑全部对比
   python run_comparison.py

5. 跑单项对比
   python run_comparison.py --summary   # 摘要
   python run_comparison.py --classify  # 分类
   python run_comparison.py --ops       # 运维问答

## 实验内容

### 摘要
- 版本 A: 基础摘要（自由格式）
- 版本 B: 增强版（few-shot + JSON 结构化输出）
- 对比: 哪个输出更稳定、信息更完整

### 分类
- 版本 A: 基础分类（只列类别）
- 版本 B: 增强版（few-shot + 类别边界说明）
- 对比: 哪个在边界 case 上更准确

### 运维问答
- 版本 A: 基础回答（自由格式）
- 版本 B: 增强版（结构化模板 + 约束规则）
- 对比: 哪个更完整、更不容易编造

## 提示

- Temperature 统一设为 0.1-0.3（评估场景不需要创造）
- 测试用例覆盖了正常、边界、超出范围三类
- 结果自动保存到 eval_results.json
