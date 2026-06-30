# llm.py — 统一 LLM 客户端

**所有 LLM 调用的唯一出口。** 支持 OpenAI / Google Gemini / Anthropic Claude 三种原生 API 协议。

## 对外接口

```python
# 按节点名调用（最常用，自动匹配 system prompt 和模型配置）
call_node("task_router", user_message)

# 按 provider + model 直接调用
call_llm("openai", "gpt-4.1", system_prompt, user_message)

# 带工具定义的调用
call_llm_with_tools(messages, provider, model)
```

`call_node` 做了三件事：
1. 从 `config.py` 的 `MODELS` 里查到该节点的 provider 和 model
2. 从 `prompts.py` 的 `SYSTEM_MAP` 拿到对应的 system prompt
3. 转调 `call_llm()`

失败时自动尝试 fallback 模型（`fallback_provider` / `fallback_model`）。

## 三个 API 适配器

```
call_llm(provider, model, ...)
    │
    ├─ provider == "openai"    → _call_openai()
    │     POST /v1/chat/completions
    │     {"model":"gpt-4.1","messages":[...]}
    │
    ├─ provider == "google"    → _call_gemini()
    │     POST /v1beta/models/{model}:generateContent?key=...
    │     {"contents":[...], "system_instruction":{...}}
    │
    └─ provider == "anthropic" → _call_anthropic()
          POST /v1/messages
          {"model":"claude-...", "system":"...", "messages":[...]}
```

每个适配器处理各自 API 的细节差异：
- **OpenAI**：标准 chat completions，system/user 放 `messages`。支持 tool_calls。
- **Gemini**：system prompt 单独放 `system_instruction`，API key 走 URL query。
- **Claude**：system 是顶层字段，API key 走 `x-api-key` header。

## 输出清理 — clean_llm_output()

每轮 LLM 调用后自动执行，剔除碎碎念但保留正文：
- DeepSeek `<think>` XML 标签
- 元分析自言自语（"我需要/我打算/我注意到..."）
- Markdown 格式符号（去壳留肉）
- 步骤标签 + 引导句
- 安全网：若清除量 >80%，退回原文

## JSON 提取与校验

### safe_extract_json(text) → dict | None
多轮抢救提取 JSON：
1. 去除 ```json ... ``` 包裹
2. 直接 `json.loads`
3. 修复常见错误（尾随逗号、注释、单引号）后重试
4. 正则兜底搜 `{...}` 块
5. 全部失败返回 None（不再返回空 dict）

### extract_and_validate(text, schema_name) → (data, error)
提取 JSON 并校验 schema。schema 定义在 `SCHEMAS` 字典中：
- `search_judge`：search_needed (bool) + search_query (str)
- `task_router`：complexity (simple/complex) + tasks + steps
- `quality_check`：pass (bool) + issues + suggestion
- `search_quality_check`：quality_ok (bool) + reason + retry_query
- `reviewer`：pass (bool) + feedback + missing_steps

校验失败时返回默认值，Schema 校验失败时自动重试一次。

## debug.log

每次 LLM 调用写一行 debug.log，包含时间、节点、provider、model、输入长度、结果长度、成功状态。
