# prompts.py — Prompt 模板库

**14 个 LLM 节点的 system prompt 全在这里。**

## 当前 Prompt 清单

| 常量 | 对应节点 | 状态 |
|------|---------|------|
| `SEARCH_JUDGE_SYSTEM` | 搜索意图判断 | 完整 |
| `SEARCH_QUALITY_CHECK_SYSTEM` | 搜索结果质量评估 | 完整 |
| `TASK_ROUTER_SYSTEM` | 复杂度判断 + 任务拆解 | 完整 |
| `CHAT_SYSTEM` | 聊天回复 | 完整 |
| `CODE_SYSTEM` | 代码生成 | 完整 |
| `LOGIC_SYSTEM` | 逻辑推理 | 完整 |
| `POLISH_SYSTEM` | 聚合结果润色 | 完整 |
| `POLISH_CHECK_SYSTEM` | 润色质检 | 完整 |
| `PLANNER_SYSTEM` | 复杂路径步骤规划 | 完整 |
| `REVIEWER_SYSTEM` | 复杂路径评审 | 完整 |
| `AGGREGATOR_SYSTEM` | 多步骤结果整合 | 完整 |
| `PERSONA_KAGURAZAKA_SYSTEM` | 神楽坂人格注入 | 有 PLACEHOLDER |
| `PERSONA_CUSTOM_SYSTEM` | 自定义人格注入 | 有 PLACEHOLDER |
| `CLASSIFIER_SYSTEM` | 旧版兼容（= SEARCH_JUDGE_SYSTEM） | - |
| `PARSER_SYSTEM` | 旧版解析器（"干饭人"） | 完整但不使用 |

## PARSER_SYSTEM（干饭人）为什么保留

这是原 Dify 工作流的核心 prompt，从 `1.2分类逻辑.yml` 完整提取：

> 你是一个名为"干饭人"的系统核心，没有显性人格，没有预设情绪，
> 只负责一件事：接收输入，拆解逻辑，输出最优解。

新版 Task Router 取代了 Parser 的拆解+路由职责，但 Parser 的 prompt 保留作为低层解析器的 fallback 参考。

## 如何关联到 llm.py

`llm.py` 里的 `SYSTEM_MAP` 字典将节点名映射到 prompt 常量：

```python
SYSTEM_MAP = {
    "search_judge":       SEARCH_JUDGE_SYSTEM,
    "task_router":        TASK_ROUTER_SYSTEM,
    "chat":               CHAT_SYSTEM,
    ...
}
```

改 prompts.py 的 prompt，重启即生效，不用动 `core.py` 或 `llm.py`。

## LLM 输出要求

大部分 prompt 要求输出 JSON（只输出 JSON，不要 markdown 代码块）。
`llm.py` 的 `safe_extract_json()` 负责从 LLM 的啰嗦输出中提取 JSON。
