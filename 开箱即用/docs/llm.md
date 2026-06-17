# llm.py — 统一 LLM 客户端

**所有 LLM 调用的唯一出口。** 不管是要调 OpenAI、Gemini 还是 Claude，都走这里。

## 对外接口

```python
# 方式一：指定 provider + model（最灵活）
call_llm("openai", "gpt-4", system_prompt, user_message)

# 方式二：按节点名调（最常用，自动匹配 system prompt）
call_node("classifier", "用户输入")
```

`call_node` 做了两件事：
1. 从 `config.py` 的 `MODELS` 里查到该节点的 provider 和 model
2. 从 `prompts.py` 里拿到对应的 system prompt
3. 转调 `call_llm()`

## 三个 API 适配器

```python
call_llm(provider, model, ...)
    │
    ├─ provider == "openai"    → _call_openai()
    │     POST /v1/chat/completions
    │     {"model":"gpt-4","messages":[...]}
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
- **OpenAI**: 标准 chat completions，system 和 user 都放 `messages` 数组
- **Gemini**: system prompt 要单独放 `system_instruction` 字段，API key 走 URL query 参数
- **Claude**: system 是顶层字段，API key 走 `x-api-key` header

## 为什么 Gemini 和 Claude 不用统一格式

很多中转 API 也支持 OpenAI 格式调 Gemini/Claude，但：
- 原生 API 更快（少一层转发）
- 某些参数（如 Claude 的 extended thinking、Gemini 的 safety settings）只在原生 API 暴露
- 这个架构下加新 API 也只需加一个适配函数

## JSON 提取工具

```python
safe_extract_json(text: str) -> dict
```

LLM 吐 JSON 时经常多嘴（前面加"好的，结果是："、外面包 markdown 代码块），这个函数做多轮抢救：
1. 先试直接 `json.loads`
2. 失败 → 去掉 markdown ``` 包裹重试
3. 再失败 → 正则搜 `{...}` 重试
4. 全失败 → 返回空 `{}`

调用方不需要关心清洗逻辑，拿到 dict 直接用。
