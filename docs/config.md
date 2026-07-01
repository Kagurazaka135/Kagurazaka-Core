# config.py — 配置中心

**管所有设置的。** 读 `config.json`，支持两种配置方式：简单模式和高级模式。

## 简单模式（推荐）

适合"我不想折腾，填个 key 就能用"的情况。

`config.json` 里只填这几项：

```json
{
    "LLM_PROVIDER": "deepseek",
    "LLM_API_KEY": "sk-xxxxxxxx",
    "LLM_BASE_URL": ""
}
```

系统自动从 `provider_presets.py` 里查到 deepseek 的所有默认模型，把所有 15 个节点配好。如果你想覆盖某个节点的模型，加个 `MODEL_OVERRIDES`：

```json
{
    "LLM_PROVIDER": "deepseek",
    "LLM_API_KEY": "sk-xxxxxxxx",
    "MODEL_OVERRIDES": {
        "code": "deepseek-v4-pro"
    }
}
```

这样除了 code 节点用 v4-pro，其他节点还是用预设的默认模型。

## 高级模式

适合"我要每个节点手动指定 provider 和 model"的情况。

`config.json` 里不填 `LLM_PROVIDER`（或留空），手动填 `PROVIDERS` 和 `MODELS`：

```json
{
    "PROVIDERS": {
        "google": {"api_key": "...", "base_url": "..."},
        "anthropic": {"api_key": "...", "base_url": "..."}
    },
    "MODELS": {
        "chat": {"provider": "google", "model": "gemini-3.5-flash"},
        "code": {"provider": "anthropic", "model": "claude-opus-4-6"}
    }
}
```

## 自动识别

系统看到 `LLM_PROVIDER` 有值 → 简单模式，没有 → 高级模式。不用手动切换。

## 校验

- `MODEL_OVERRIDES` 里节点名拼错了 → 提示"你是指 xxx 吗？"
- 高级模式里 provider 不在 (openai, google, anthropic) 里 → 警告
- 旧版 config.json 缺字段 → 自动补齐，不用手动改
