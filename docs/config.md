# config.py — 配置管理

**整个系统的配置中心。** 读 `config.json`，支持简单模式和高级模式。

## 简单模式 vs 高级模式

| | 简单模式 | 高级模式 |
|---|---|---|
| 触发条件 | config.json 里有 `LLM_PROVIDER` | 没有 `LLM_PROVIDER`（或为空） |
| 用户填什么 | 3 项：供应商名 + API key + 可选 base_url | 每个供应商的 api_key + 每个节点的 provider/model |
| 模型分配 | 自动从 `provider_presets.py` 预设 | 手动指定 |
| 适合谁 | 普通用户、打包分发 | 开发者、需要精细化控制 |

## 自动识别逻辑

```python
if "LLM_PROVIDER" in user_cfg and user_cfg["LLM_PROVIDER"]:
    _apply_simple_mode(config, user_cfg)   # 走简单模式
else:
    _apply_advanced_mode(config, user_cfg)  # 走高级模式
```

## 简单模式做了什么

1. 查 `provider_presets.py` 获取预设（`get_preset(provider_name)`）
2. 将用户的一个 API key 填进 `PROVIDERS`
3. 将全部 14 个节点指向该供应商，模型名从预设拿
4. `MODEL_OVERRIDES` 可覆盖单个节点的模型名

本质：**把 3 行配置展开成高级模式的完整结构**。下游代码看到的 `CONFIG` 结构一致。

## 高级模式做了什么

手动合并 `PROVIDERS` 和 `MODELS` 字段，无自动推断。

## 配置校验

- `MODEL_OVERRIDES` 校验：检查节点名拼写（不在 `VALID_NODE_NAMES` 里的提示"你是指 xxx 吗？"）
- 高级模式 `MODELS` 校验：检查 provider 是否在 `(openai, google, anthropic)` 中，模型名是否包含空格（拼写错误？）

## 配置迁移

`_migrate_config()` 自动补齐旧版 config.json 缺失的字段（`SERPAPI_KEY`、`PERSONA_MODE`、`MODEL_OVERRIDES`），无需手动改。

## 模板生成

首次运行没有 `config.json` 时，生成带中文注释的模板，默认简单模式格式。
