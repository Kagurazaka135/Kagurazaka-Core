# prompts.py — Prompt 模板库

**7 个节点的 system prompt 全在这里。** `[PLACEHOLDER]` 标记的地方等你后面填。

## 每个 Prompt 的作用

| 常量 | 对应节点 | 来源 | 状态 |
|---|---|---|---|
| `CLASSIFIER_SYSTEM` | 分类器 | 自己写的 | 有 PLACEHOLDER |
| `PARSER_SYSTEM` | 解析器(干饭人) | 从 1.2分类逻辑.yml 提取 | **完整**（原版 prompt） |
| `CHAT_SYSTEM` | 聊天 | 原 Dify 只有"以json输出" | 有 PLACEHOLDER |
| `CODE_SYSTEM` | 代码 | 原 Dify 只有"以json输出" | 有 PLACEHOLDER |
| `LOGIC_SYSTEM` | 逻辑推理 | 原 Dify 只有"以json输出" | 有 PLACEHOLDER |
| `POLISH_SYSTEM` | 润色 | 从 1.6润色.yml 提取 | 有 PLACEHOLDER |
| `POLISH_CHECK_SYSTEM` | 润色质检 | 从 1.6润色.yml 提取 | **完整**（原版 prompt） |

## 为什么聊天/代码/逻辑是空的

原 Dify 工作流里这三个节点的 system prompt 就一行"以json输出"。Dify 的 LLM 节点靠节点名称和上下文来区分功能，prompt 本身是极简的。

现在纯 Python 版把这三个节点接到了一般的 LLM，只写"以json输出"肯定不够——你需要按神楽坂的人设去填。比如聊天节点的 prompt 可以写：

> 你是神楽坂，一个哥特系傲娇AI少女。说话带日语口癖，会撒娇也会毒舌...

## PARSER_SYSTEM（干饭人）为什么是完整的

这是整个系统的核心 prompt，原版就写得很详细。摘一段看看：

> 你是一个名为"干饭人"的系统核心，没有显性人格，没有预设情绪，
> 只负责一件事：接收输入，拆解逻辑，输出最优解。
> 将问题分为"代码，需要逻辑推理，聊天"三大类...

这个 prompt 被完整从 `1.2分类逻辑.yml` 提取出来，没做任何改动。

## 如何关联到 llm.py

`llm.py` 里的 `call_node("chat", ...)` 会自动拿 `CHAT_SYSTEM` 当 system prompt：

```python
# llm.py
SYSTEM_MAP = {
    "classifier":    CLASSIFIER_SYSTEM,
    "parser":        PARSER_SYSTEM,
    "chat":          CHAT_SYSTEM,
    ...
}
```

所以你改了 prompts.py 的 prompt，重启就能生效，不用动 `core.py` 或 `llm.py`。
