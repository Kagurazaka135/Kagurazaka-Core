"""
LLM 供应商预设
每个预设包含 API 类型(base_url + 调用格式)和按节点角色推荐的默认模型名

简单模式下用户只需选一个供应商 + 填一个 API key，
系统自动将各节点路由到该供应商的合适模型。
"""
from typing import Dict, Optional

Preset = Dict[str, object]

PRESETS: Dict[str, Preset] = {
    # ---- OpenAI ----
    "openai": {
        "internal_provider": "openai",
        "base_url": "https://api.openai.com",
        "models": {
            "classifier":         "gpt-4.1-mini",
            "parser":             "gpt-4.1-mini",
            "chat":               "gpt-4.1-mini",
            "code":               "gpt-4.1",
            "logic":              "gpt-4.1",
            "polish":             "gpt-4.1-mini",
            "persona_kagurazaka": "gpt-4.1-mini",
            "persona_custom":     "gpt-4.1-mini",
            "quality_check":      "gpt-4.1-mini",
            "planner":            "gpt-4.1",
            "reviewer":           "gpt-4.1-mini",
            "aggregator":         "gpt-4.1-mini",
            "search_judge":       "gpt-4.1-mini",
            "search_quality_check": "gpt-4.1-mini",
            "task_router":        "gpt-4.1"
        }
    },
    # ---- Google Gemini ----
    "google": {
        "internal_provider": "google",
        "base_url": "https://generativelanguage.googleapis.com",
        "models": {
            "classifier":         "gemini-3.1-flash-lite",
            "parser":             "gemini-3.1-flash-lite",
            "chat":               "gemini-3.5-flash",
            "code":               "gemini-3.5-flash",
            "logic":              "gemini-3.5-flash",
            "polish":             "gemini-3.1-flash-lite",
            "persona_kagurazaka": "gemini-3.1-flash-lite",
            "persona_custom":     "gemini-3.1-flash-lite",
            "quality_check":      "gemini-3.1-flash-lite",
            "planner":            "gemini-3.5-flash",
            "reviewer":           "gemini-3.1-flash-lite",
            "aggregator":         "gemini-3.1-flash-lite",
            "search_judge":       "gemini-3.1-flash-lite",
            "search_quality_check": "gemini-3.1-flash-lite",
            "task_router":        "gemini-3.5-flash"
        }
    },
    # ---- Anthropic Claude ----
    "anthropic": {
        "internal_provider": "anthropic",
        "base_url": "https://api.anthropic.com",
        "models": {
            "classifier":         "claude-sonnet-4-6",
            "parser":             "claude-sonnet-4-6",
            "chat":               "claude-sonnet-4-6",
            "code":               "claude-opus-4-6",
            "logic":              "claude-opus-4-6",
            "polish":             "claude-sonnet-4-6",
            "persona_kagurazaka": "claude-sonnet-4-6",
            "persona_custom":     "claude-sonnet-4-6",
            "quality_check":      "claude-sonnet-4-6",
            "planner":            "claude-opus-4-6",
            "reviewer":           "claude-sonnet-4-6",
            "aggregator":         "claude-sonnet-4-6",
            "search_judge":       "claude-sonnet-4-6",
            "search_quality_check": "claude-sonnet-4-6",
            "task_router":        "claude-opus-4-6"
        }
    },
    # ---- DeepSeek (OpenAI 兼容) ----
    "deepseek": {
        "internal_provider": "openai",
        "base_url": "https://api.deepseek.com",
        "models": {
            "classifier":         "deepseek-v4-flash",
            "parser":             "deepseek-v4-flash",
            "chat":               "deepseek-v4-flash",
            "code":               "deepseek-v4-pro",
            "logic":              "deepseek-v4-pro",
            "polish":             "deepseek-v4-flash",
            "persona_kagurazaka": "deepseek-v4-flash",
            "persona_custom":     "deepseek-v4-flash",
            "quality_check":      "deepseek-v4-flash",
            "planner":            "deepseek-v4-pro",
            "reviewer":           "deepseek-v4-flash",
            "aggregator":         "deepseek-v4-flash",
            "search_judge":       "deepseek-v4-flash",
            "search_quality_check": "deepseek-v4-flash",
            "task_router":        "deepseek-v4-pro"
        }
    },
    # ---- 智谱 GLM (OpenAI 兼容) ----
    "zhipu": {
        "internal_provider": "openai",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": {
            "classifier":         "glm-4.7-flash",
            "parser":             "glm-4.7-flash",
            "chat":               "glm-4.7-flash",
            "code":               "glm-5",
            "logic":              "glm-5",
            "polish":             "glm-4.7-flash",
            "persona_kagurazaka": "glm-4.7-flash",
            "persona_custom":     "glm-4.7-flash",
            "quality_check":      "glm-4.7-flash",
            "planner":            "glm-5",
            "reviewer":           "glm-4.7-flash",
            "aggregator":         "glm-4.7-flash",
            "search_judge":       "glm-4.7-flash",
            "search_quality_check": "glm-4.7-flash",
            "task_router":        "glm-5"
        }
    },
    # ---- 阿里通义千问 (OpenAI 兼容) ----
    "qwen": {
        "internal_provider": "openai",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": {
            "classifier":         "qwen3.6-flash",
            "parser":             "qwen3.6-flash",
            "chat":               "qwen3.6-plus",
            "code":               "qwen3.6-plus",
            "logic":              "qwen3.6-plus",
            "polish":             "qwen3.6-flash",
            "persona_kagurazaka": "qwen3.6-flash",
            "persona_custom":     "qwen3.6-flash",
            "quality_check":      "qwen3.6-flash",
            "planner":            "qwen3.6-plus",
            "reviewer":           "qwen3.6-flash",
            "aggregator":         "qwen3.6-flash",
            "search_judge":       "qwen3.6-flash",
            "search_quality_check": "qwen3.6-flash",
            "task_router":        "qwen3.6-plus"
        }
    },
    # ---- Moonshot (OpenAI 兼容) ----
    "moonshot": {
        "internal_provider": "openai",
        "base_url": "https://api.moonshot.cn/v1",
        "models": {
            "classifier":         "kimi-k2.5",
            "parser":             "kimi-k2.5",
            "chat":               "kimi-k2.5",
            "code":               "kimi-k2.6",
            "logic":              "kimi-k2.6",
            "polish":             "kimi-k2.5",
            "persona_kagurazaka": "kimi-k2.5",
            "persona_custom":     "kimi-k2.5",
            "quality_check":      "kimi-k2.5",
            "planner":            "kimi-k2.6",
            "reviewer":           "kimi-k2.5",
            "aggregator":         "kimi-k2.5",
            "search_judge":       "kimi-k2.5",
            "search_quality_check": "kimi-k2.5",
            "task_router":        "kimi-k2.6"
        }
    },
    # ---- 硅基流动 (OpenAI 兼容，模型广场) ----
    "siliconflow": {
        "internal_provider": "openai",
        "base_url": "https://api.siliconflow.cn/v1",
        "models": {
            "classifier":         "deepseek-ai/DeepSeek-V4-Flash",
            "parser":             "deepseek-ai/DeepSeek-V4-Flash",
            "chat":               "deepseek-ai/DeepSeek-V4-Flash",
            "code":               "deepseek-ai/DeepSeek-V4-Pro",
            "logic":              "deepseek-ai/DeepSeek-V4-Pro",
            "polish":             "deepseek-ai/DeepSeek-V4-Flash",
            "persona_kagurazaka": "deepseek-ai/DeepSeek-V4-Flash",
            "persona_custom":     "deepseek-ai/DeepSeek-V4-Flash",
            "quality_check":      "deepseek-ai/DeepSeek-V4-Flash",
            "planner":            "deepseek-ai/DeepSeek-V4-Pro",
            "reviewer":           "deepseek-ai/DeepSeek-V4-Flash",
            "aggregator":         "deepseek-ai/DeepSeek-V4-Flash",
            "search_judge":       "deepseek-ai/DeepSeek-V4-Flash",
            "search_quality_check": "deepseek-ai/DeepSeek-V4-Flash",
            "task_router":        "deepseek-ai/DeepSeek-V4-Pro"
        }
    },
    # ---- 自定义 (OpenAI 兼容，填你自己的 base_url + 模型名) ----
    "custom": {
        "internal_provider": "openai",
        "base_url": "",
        "models": {
            "classifier":         "",
            "parser":             "",
            "chat":               "",
            "code":               "",
            "logic":              "",
            "polish":             "",
            "persona_kagurazaka": "",
            "persona_custom":     "",
            "quality_check":      "",
            "planner":            "",
            "reviewer":           "",
            "aggregator":         "",
            "search_judge":       "",
            "search_quality_check": "",
            "task_router":        ""
        }
    }
}

# 所有支持的供应商名称（用于校验和提示）
ALL_PROVIDERS = list(PRESETS.keys())


def get_preset(name: str) -> Optional[Preset]:
    """获取指定供应商的预设，不存在返回 None"""
    return PRESETS.get(name, None)


def list_providers() -> str:
    """返回人类可读的供应商列表"""
    lines = []
    for name, preset in PRESETS.items():
        api_type = preset.get("internal_provider", "?")
        url = preset.get("base_url", "")
        model_sample = list(preset.get("models", {}).values())[:2]
        model_str = ", ".join(model_sample) if model_sample else "需自行填写"
        lines.append(f"  {name:<14} api={api_type:<10} 模型示例: {model_str}")
    return "\n".join(lines)
