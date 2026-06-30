# provider_presets.py — LLM 供应商预设

**选一个供应商，自动配好 14 个节点的模型。**

## 预设结构

```python
"openai": {
    "internal_provider": "openai",       # 走哪个 API 协议
    "base_url": "https://api.openai.com",
    "models": {
        "classifier":    "gpt-4.1-mini",  # 轻活：便宜模型
        "chat":          "gpt-4.1-mini",  # 聊天：中等
        "code":          "gpt-4.1",        # 重活：强模型
        "logic":         "gpt-4.1",
        ...
    }
}
```

## internal_provider 的含义

| 值 | API 格式 | 适用供应商 |
|---|---|---|
| `"openai"` | `/v1/chat/completions` | OpenAI、DeepSeek、智谱、千问、Moonshot、硅基流动、自定义 |
| `"google"` | `/v1beta/models/{model}:generateContent` | Google Gemini |
| `"anthropic"` | `/v1/messages` | Anthropic Claude |

大部分国产模型走 `"openai"` 协议（OpenAI API 兼容），覆盖面最广。

## 当前内置的 9 个供应商

| 供应商 | 协议 | 轻活模型 | 重活模型 |
|---|---|---|---|
| `openai` | 原生 | gpt-4.1-mini | gpt-4.1 |
| `google` | 原生 | gemini-2.5-flash | gemini-2.5-pro |
| `anthropic` | 原生 | claude-sonnet-4 | claude-sonnet-4 |
| `deepseek` | OpenAI兼容 | deepseek-chat | deepseek-chat |
| `zhipu` | OpenAI兼容 | glm-4-flash | glm-4-flash |
| `qwen` | OpenAI兼容 | qwen-turbo | qwen-plus |
| `moonshot` | OpenAI兼容 | moonshot-v1-8k | moonshot-v1-8k |
| `siliconflow` | OpenAI兼容 | DeepSeek-V3 | DeepSeek-V3 |
| `custom` | OpenAI兼容 | (需自行填写) | (需自行填写) |

## 如何添加新供应商

在 `PRESETS` 字典加一项即可：

```python
"xxx": {
    "internal_provider": "openai",       # 大概率是这个
    "base_url": "https://api.xxx.com",
    "models": {
        "classifier": "model-light",
        "code": "model-strong",
        "logic": "model-strong",
        ...
    }
}
```

## 模型分配策略

每个供应商的预设区分"轻活"和"重活"：
- **轻活**（search_judge/chat/polish/quality_check/reviewer/aggregator/persona_*)：便宜、快的模型
- **重活**（code/logic/planner/task_router）：强推理模型

DeepSeek/智谱/Moonshot/硅基流动的轻活和重活用同一个模型，因为这些模型的能力足够覆盖轻活。
