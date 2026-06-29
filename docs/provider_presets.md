# provider_presets.py — LLM 供应商预设

**选一个供应商，自动配好 7 个节点的模型。**

## 预设结构

每个供应商是一个 dict：

```python
"openai": {
    "internal_provider": "openai",    # 走哪个 API 协议
    "base_url": "https://api.openai.com",
    "models": {
        "classifier":    "gpt-4.1-mini",   # 轻活：便宜模型
        "parser":        "gpt-4.1-mini",
        "chat":          "gpt-4.1-mini",   # 聊天：中等
        "code":          "gpt-4.1",         # 重活：强模型
        "logic":         "gpt-4.1",
        "polish":        "gpt-4.1-mini",   # 轻活
        "quality_check": "gpt-4.1-mini"    # 轻活
    }
}
```

## internal_provider 的含义

| 值 | API 格式 | 适用供应商 |
|---|---|---|
| `"openai"` | `/v1/chat/completions` | OpenAI、DeepSeek、智谱、千问、Moonshot、硅基流动、自定义 |
| `"google"` | `/v1beta/models/{model}:generateContent` | Google Gemini |
| `"anthropic"` | `/v1/messages` | Anthropic Claude |

**大部分国产模型走 `"openai"` 协议**（兼容 OpenAI API 格式），所以 `internal_provider: "openai"` 的覆盖面最广。

## 当前内置的 9 个供应商

| 供应商 | 协议 | 轻活模型 | 重活模型 |
|---|---|---|---|
| `openai` | 原生 | gpt-4.1-mini | gpt-4.1 |
| `google` | 原生 | gemini-2.5-flash | gemini-2.5-pro |
| `anthropic` | 原生 | claude-sonnet-4 | claude-sonnet-4 |
| `deepseek` | OpenAI兼容 | deepseek-v4-flash | deepseek-v4-pro |
| `zhipu` | OpenAI兼容 | glm-4-flash | glm-4-flash |
| `qwen` | OpenAI兼容 | qwen-turbo | qwen-plus |
| `moonshot` | OpenAI兼容 | moonshot-v1-8k | moonshot-v1-8k |
| `siliconflow` | OpenAI兼容 | DeepSeek-V4-Flash | DeepSeek-V4-Pro |
| `custom` | OpenAI兼容 | (需自行填写) | (需自行填写) |

## 如何添加新供应商

只需在 `PRESETS` 字典加一项，`webui.py` 的下拉列表会自动出现：

```python
"新供应商": {
    "internal_provider": "openai",       # 大概率是这个
    "base_url": "https://api.xxx.com",
    "models": {
        "classifier": "model-light",
        ...
        "code": "model-strong",
        "logic": "model-strong",
    }
}
```

## 为什么 DeepSeek 区分轻活重活

DeepSeek V4 有 Flash（轻量）和 Pro（强推理）两个版本。轻活（classifier/parser/chat/polish/persona/quality/reviewer/aggregator/search_judge）走 `deepseek-v4-flash`，重活（code/logic/planner/task_router）走 `deepseek-v4-pro`。如需开启 reasoning，仅在 Pro 模型上启用。
