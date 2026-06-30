"""
测试用例集。

每类 4 个 case，共 12 个：
- 2 个正常 case
- 1 个边界/模糊 case
- 1 个超出范围 case

每个 case 标注了期望的检查点（check），跑完后可以对比。
"""

TEST_CASES = [
    # ============================================================
    # 摘要测试 (summary)
    # ============================================================
    {
        "id": "summary_01",
        "task": "summary",
        "user": (
            "2026-06-09 14:23:15 [ERROR] [order-service] Failed to process order #12345: "
            "connection to database 'orders_db' timed out after 30s. Retry attempt 1/3 failed. "
            "Stack trace: ... at com.order.service.OrderProcessor.process(OrderProcessor.java:85)\\n"
            "2026-06-09 14:23:20 [WARN] [order-service] Connection pool stats: active=45, idle=5, max=50. "
            "Pool exhausted, queuing requests.\\n"
            "2026-06-09 14:23:25 [ERROR] [order-service] Circuit breaker opened for downstream: payment-service"
        ),
        "check": "应提取关键错误信息（数据库超时、连接池耗尽、熔断）",
        "type": "normal",
    },
    {
        "id": "summary_02",
        "task": "summary",
        "user": (
            "[INFO] Scheduled health check completed. All 12 services healthy. "
            "Average response time: 45ms. No anomalies detected."
        ),
        "check": "应说明一切正常，不要编造异常",
        "type": "normal",
    },
    {
        "id": "summary_03",
        "task": "summary",
        "user": "服务器出了点问题，好像是昨晚开始的，现在还没好。",
        "check": "信息不足时应指出缺乏具体信息，不要编造具体错误",
        "type": "boundary",
    },
    {
        "id": "summary_04",
        "task": "summary",
        "user": (
            "今天天气很好，适合出去散步。顺便说一下，我的服务器好像有点慢，"
            "不过不确定是不是网络问题。数据库那边没人反馈有问题。"
        ),
        "check": "应区分无关信息和技术问题，或者指出信息混杂",
        "type": "boundary",
    },

    # ============================================================
    # 分类测试 (classify)
    # ============================================================
    {
        "id": "classify_01",
        "task": "classify",
        "user": "Nginx 返回 502 Bad Gateway，后端服务日志显示 Connection refused",
        "check": "应分类为网络问题",
        "expected": "网络问题",
        "type": "normal",
    },
    {
        "id": "classify_02",
        "task": "classify",
        "user": "MySQL 慢查询日志显示一条 SQL 执行了 12 秒，表数据量 500 万行，没有走索引",
        "check": "应分类为数据库问题",
        "expected": "数据库问题",
        "type": "normal",
    },
    {
        "id": "classify_03",
        "task": "classify",
        "user": "K8s 集群中某个 Pod 一直 CrashLoopBackOff，可能是 OOM 了",
        "check": "分类可能是服务器问题或应用问题，两者有争议时可接受其中一种",
        "expected": None,
        "type": "boundary",
    },
    {
        "id": "classify_04",
        "task": "classify",
        "user": "中午吃什么比较好？推荐一下公司附近的餐馆",
        "check": "应分类为其他",
        "expected": "其他",
        "type": "out_of_scope",
    },

    # ============================================================
    # 运维问答测试 (ops_qa)
    # ============================================================
    {
        "id": "ops_qa_01",
        "task": "ops_qa",
        "user": "Nginx 502 Bad Gateway 怎么排查？",
        "check": "应给出结构化排查步骤，不应该是空泛的回答",
        "type": "normal",
    },
    {
        "id": "ops_qa_02",
        "task": "ops_qa",
        "user": "磁盘空间满了怎么办？",
        "check": "应给出排查步骤（df -h, du -sh * 等）和清理建议",
        "type": "normal",
    },
    {
        "id": "ops_qa_03",
        "task": "ops_qa",
        "user": "我有一段日志：\"2026-06-09 15:30:00 ERROR: null pointer exception at OrderService.getOrder() line 142\"，这是什么问题？",
        "check": "应分析空指针异常可能的原因，给出排查方向",
        "type": "normal",
    },
    {
        "id": "ops_qa_04",
        "task": "ops_qa",
        "user": "服务器突然特别卡，我也不知道原因，你帮我看一下",
        "check": "应在信息不足时要求补充具体信息（如 CPU/内存/磁盘使用率等），而不是直接给出确定结论",
        "type": "boundary",
    },
]
