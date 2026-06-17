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
def _load_config():
    ...
    if "LLM_PROVIDER" in user_cfg and user_cfg["LLM_PROVIDER"]:
        _apply_simple_mode(config, user_cfg)   # 走简单模式
    else:
        _apply_advanced_mode(config, user_cfg)  # 走高级模式
```

## 简单模式做了什么

```python
def _apply_simple_mode(config, user_cfg):
    preset = get_preset(provider_name)          # 查预设表
    internal_provider = preset["internal_provider"]  # openai/google/anthropic

    # 把用户的一个 API key 填进 PROVIDERS
    config["PROVIDERS"][internal_provider] = {"api_key": ..., "base_url": ...}

    # 把 7 个节点全部指向这个供应商，模型名从预设拿
    for node in ["classifier", "parser", ...]:
        config["MODELS"][node] = {
            "provider": internal_provider,
            "model": preset["models"][node]       # 可被 MODEL_OVERRIDES 覆盖
        }
```

简单模式的本质：**帮用户把 3 行配置展开成高级模式的完整结构**。对下游代码（`llm.py`、`core.py`）来说，不管用户用哪种模式，看到的 `CONFIG` 结构都是一样的。

## 高级模式做了什么

```python
def _apply_advanced_mode(config, user_cfg):
    # 合并用户写的 PROVIDERS（覆盖 api_key 和 base_url）
    # 合并用户写的 MODELS（覆盖每个节点的 provider 和 model）
```

只是简单的字段合并，什么都不自动推断。

## 模板生成

首次运行没有 `config.json` 时，生成一个带中文注释的模板。模板默认是简单模式格式。
