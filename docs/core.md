# core.py — 工作流编排（整个系统的大脑）

**从用户输入到最终回答的完整流水线。** 串联搜索判断、工具调用、任务路由、双路径执行和人格注入。

## 核心函数

```python
def run_workflow(user_input: str, memory_system: SimpleMemorySystem) -> str:
```

只有一个入口，一个出口。

## 完整流程

### 步骤 0：记忆增强
检测"刚才那个..."等上下文引用，从历史里捞出上文拼接。

### L1 白名单 — 废话拦截器（零成本）
纯 Python 字符串匹配。命中则跳过搜索和 Search Judge。
包含 20+ 个闲聊短语：谢谢/好的/再见/ok/嗯/嗨/晚安 等。

### L2 正则 — 强信号匹配（零成本）
5 组正则模式，匹配明显的搜索需求——天气/股价/汇率/热搜/怎么/哪里 等。
命中则直接设置 `search_needed=True`，跳过 Search Judge 的 LLM 调用。

### Search Judge (LLM)
L1/L2 都未命中时，调 LLM 判断是否需要搜索并生成最优搜索词。
输出 JSON：`{"search_needed": bool, "search_query": str}`。
Json schema 校验失败时自动重试一次。

### 搜索 + 缓存
- 先查缓存（30min TTL，关键词模糊匹配）
- 缓存未命中或过期 → SerpAPI 搜索（Google 主引擎 + Bing fallback）
- 搜索结果质量检查：太短/太少自动换词重搜
- 质量检查也用 LLM 评估，不通过时给出新搜索词

### 工具调用循环（≤5 轮）
LLM 可调用 5 个内置工具：`search_web` / `read_file` / `write_file` / `get_datetime` / `http_get`。
每轮检查是否有 `tool_calls`，有则执行工具并继续下一轮。
如果工具调用产生了最终答案，跳过 Task Router，直接进入人格注入。

### Task Router (LLM)
判断任务复杂度并拆解：
- **simple**：单一问答/闲聊/简单代码 → 输出 `chat_task` / `code_task` / `logic_task`
- **complex**：多步推理/跨领域任务 → 输出 `steps[]` 执行计划

### 简单路径 (simple)
```
chat / code / logic（按需并行）
    → polish（润色聚合）
    → quality_check（≤3 轮质检打回）
```

### 复杂路径 (complex)
```
按 steps[] 逐步执行（每步可指定 node_type: search/chat/code/logic/polish）
    → aggregator（整合多步结果）
    → reviewer 循环（≤3 轮，不通过则追加 missing_steps 重新执行）
```

### 人格注入
- `PERSONA_MODE = "kagurazaka"` → 以神楽坂人格改写输出
- `PERSONA_MODE = "custom"` → 以自定义人格改写
- `PERSONA_MODE = "none"` → 跳过

### 异常保护
整个 `run_workflow` 外层有 try/except，崩溃时记录 crash.log 并返回错误提示。

## 为什么 L1+L2 不用 LLM

50% 以上的搜索意图可以由正则和关键词识别。LLM 调用有延迟（500ms~3s），L1+L2 为零成本拦截。
