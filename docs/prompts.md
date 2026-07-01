# prompts.py — 剧本库

**所有 LLM 节点的 system prompt 全在这里。** 每个节点扮演什么角色、怎么输出、什么格式，都写在对应的 prompt 里。

## 15 个节点的 prompt

| Prompt | 对应节点 | 干什么 |
|---|---|---|
| SEARCH_JUDGE_SYSTEM | search_judge | 判断要不要搜索，生成搜索词 |
| SEARCH_QUALITY_CHECK_SYSTEM | search_quality_check | 评估搜索结果质量，不行就换词 |
| TASK_ROUTER_SYSTEM | task_router | 判断简单/复杂，拆解任务 |
| CHAT_SYSTEM | chat | 日常聊天回复 |
| CODE_SYSTEM | code | 写代码 |
| LOGIC_SYSTEM | logic | 逻辑推理 |
| POLISH_SYSTEM | polish | 把结果润色成自然语言 |
| POLISH_CHECK_SYSTEM | quality_check | 检查润色质量 |
| PLANNER_SYSTEM | planner | 复杂路径的步骤规划 |
| REVIEWER_SYSTEM | reviewer | 审查复杂路径的结果 |
| AGGREGATOR_SYSTEM | aggregator | 把多步结果拼成一篇 |
| PERSONA_KAGURAZAKA_SYSTEM | persona_kagurazaka | 注入神楽坂人格 |
| PERSONA_CUSTOM_SYSTEM | persona_custom | 注入自定义人格 |
| CLASSIFIER_SYSTEM | classifier | 旧版搜索意图判断（兼容） |
| PARSER_SYSTEM | parser | 旧版解析器（保留不用） |

## 怎么关联到 llm.py

`llm.py` 里有个 `SYSTEM_MAP` 字典：

```python
SYSTEM_MAP = {
    "search_judge": SEARCH_JUDGE_SYSTEM,
    "task_router": TASK_ROUTER_SYSTEM,
    "chat": CHAT_SYSTEM,
    ...
}
```

`call_node("chat", ...)` 自动从 `SYSTEM_MAP` 拿 `CHAT_SYSTEM`。

## 改 prompt 不用动代码

prompt 全在 `prompts.py` 里，改完重启即生效。不用碰 `core.py` 或 `llm.py`。

## 输出格式

大部分 prompt 要求 LLM 输出纯 JSON（不要 markdown 代码块）。`llm.py` 的 `safe_extract_json()` 负责从可能啰嗦的输出里把 JSON 抠出来。
