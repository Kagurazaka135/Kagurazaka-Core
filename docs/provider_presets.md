# provider_presets.py — 供应商菜单

**每个供应商用哪些模型，全写在这里。** 简单模式下，用户选一个供应商，系统从这里查模型名自动配好。

## 数据结构

```python
"openai": {
    "internal_provider": "openai",        # 走哪个 API 协议
    "base_url": "https://api.openai.com", # API 地址
    "models": {
        "classifier": "gpt-4.1-mini",     # 轻活用便宜模型
        "code":       "gpt-4.1",          # 重活用强模型
        "logic":      "gpt-4.1",
        ...
    }
}
```

## internal_provider 什么意思

不同公司用不同的 API 格式，但大部分国产模型兼容 OpenAI 格式：

| internal_provider | 实际 API 格式 | 哪些供应商用 |
|---|---|---|
| `"openai"` | OpenAI 格式 | OpenAI、DeepSeek、智谱、千问、Moonshot、硅基流动、自定义 |
| `"google"` | Gemini 格式 | Google |
| `"anthropic"` | Claude 格式 | Anthropic |

## 节点分两档

每个供应商的 15 个节点分两档：

- **轻活**（classifier/parser/chat/polish/persona/quality_check/reviewer/aggregator/search_judge/search_quality_check）：用便宜、快的模型
- **重活**（code/logic/planner/task_router）：用强推理模型

## 当前 9 个供应商

| 供应商 | 协议 | 轻活模型 | 重活模型 |
|---|---|---|---|
| openai | 原生 | gpt-4.1-mini | gpt-4.1 |
| google | 原生 | gemini-3.1-flash-lite | gemini-3.5-flash |
| anthropic | 原生 | claude-sonnet-4-6 | claude-opus-4-6 |
| deepseek | OpenAI兼容 | deepseek-v4-flash | deepseek-v4-pro |
| zhipu | OpenAI兼容 | glm-4.7-flash | glm-5 |
| qwen | OpenAI兼容 | qwen3.6-flash | qwen3.6-plus |
| moonshot | OpenAI兼容 | kimi-k2.5 | kimi-k2.6 |
| siliconflow | OpenAI兼容 | DeepSeek-V4-Flash | DeepSeek-V4-Pro |
| custom | OpenAI兼容 | 自己填 | 自己填 |

## 加新供应商

在 `PRESETS` 字典里加一项就行，照着上面的格式抄。
