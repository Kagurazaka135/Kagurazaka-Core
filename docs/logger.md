# logger.py — 会话日志 & 统计

**每次 LLM 调用都记录，退出时计算统计。**

## 每条日志记什么

```json
{
    "session": "session_1716123456",
    "timestamp": "2026-05-19T14:00:01",
    "node": "task_router",
    "call_type": "llm_call",
    "input_len": 240,
    "output_len": 8,
    "latency_ms": 1234.5,
    "success": true,
    "error": ""
}
```

## 谁在记

`core.py` 和 `llm.py` 在每个 LLM 调用处调 `log.record()`。
每条记录即时写入 `logs/{session_id}.jsonl`。

## 会话退出统计

```
============================ 会话统计 ============================
  会话ID:     session_1716123456
  总调用数:   12
  成功:       12  |  失败: 0
  平均延迟:   2100ms  |  最长: 4500ms
  会话耗时:   45.3s
----------------------------------------
  [search_judge]   2次 | 成功2 | 平均1200ms
  [task_router]    1次 | 成功1 | 平均2800ms
  [chat]           3次 | 成功3 | 平均1500ms
  [polish]         2次 | 成功2 | 平均1800ms
  ...
=================================================================
```

## 历史日志统计

`python main.py --stats` 从 `logs/` 读所有 `*.jsonl`，按会话聚合：
```bash
历史统计 - 5 个日志文件, 12 个会话
  [session_xxx] 12次调用 | 成功率 100% | 平均 2200ms
```
