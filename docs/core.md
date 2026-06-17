# core.py — 工作流编排（整个系统的大脑）

**7 个步骤把用户输入变成最终回答。** 对应原 Dify 工作流 1.1~1.6 的全部逻辑。

## 核心函数

```python
def run_workflow(user_input: str, memory_system: SimpleMemorySystem) -> str:
```

只有一个入口，一个出口。输入用户消息，输出最终回答。

## 8 个步骤详解

### 步骤 0：记忆增强
```python
enhanced_input = memory_system.enhance_input(user_input)
```
如果用户说"刚才那个..."，自动从历史里捞出上文拼进去。

### 步骤 1：分类器 — 要不要搜索
```python
classifier_result = call_node("classifier", enhanced_input)
is_search_needed = "需要搜索" in classifier_result
```
调 LLM 判断。问天气 → 需要搜索，问什么是递归 → 不需要。

### 步骤 2：搜索
```python
search_context = google_search(user_input)
```
只当步骤 1 判定"需要搜索"时才跑。调 SerpAPI 拿前 5 条摘要。

### 步骤 3：解析器（"干饭人"）
```python
combined_input = f"搜索结果：{search_context}\n用户问题：{enhanced_input}"
raw_json_text = call_node("parser", combined_input)
```
把带搜索结果的输入扔给 LLM，输出 JSON：
```json
{"聊天": "...", "代码": "...", "需要逻辑推理": "..."}
```

### 步骤 4：分类处理
```python
field_chat  = _extract_json_field(raw_json_text, "聊天")
field_code  = _extract_json_field(raw_json_text, "代码")
field_logic = _extract_json_field(raw_json_text, "需要逻辑推理")
```
从 JSON 里拆出三个字段。如果一个字段不存在（`_FIELD_NOT_FOUND`），就跳过那个子节点。

然后分别调三个节点：
```python
call_node("chat",  field_chat)    # 聊天回复
call_node("code",  field_code)    # 代码生成
call_node("logic", field_logic)   # 逻辑推理
```

### 步骤 5：变量聚合
```python
aggregated_text = json.dumps(final_results)
```
三个结果拼成一个 JSON 字符串，例如 `{"chat": "...", "code": "...", "logic": "..."}`。

### 步骤 6：润色
```python
final_answer = call_node("polish", aggregated_text)
```
把生硬的 JSON 变成自然语言。核心 prompt 是"根据json生成一段话"。

### 步骤 7：质量检查 & 重试
```python
for attempt in range(3):          # 最多重试3次
    passed, feedback = quality_check(final_answer)
    if passed: break
    final_answer = call_node("polish", retry_input)  # 带反馈重新润色
```
质检失败 → 把修改建议和原始数据一起塞回润色节点，让它重新生成。

### 步骤 8：输出 & 记忆保存
```python
memory_system.add_to_history(user_input, final_answer, task_type)
```

## 为什么是串行不是并行

Chat/Code/Logic 三个节点绝大多数时候只有一个被触发（Parser 的分类 prompt 写了"没有这一分类就不要生成对应字段"）。三个同时触发的情况极其罕见，没必要为了极端情况加并行复杂度。
