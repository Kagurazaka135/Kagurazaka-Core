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
            "task_router":        "gpt-4.1"
        }
    },
    # ---- Google Gemini ----
    "google": {
        "internal_provider": "google",
        "base_url": "https://generativelanguage.googleapis.com",
        "models": {
            "classifier":         "gemini-2.5-flash",
            "parser":             "gemini-2.5-flash",
            "chat":               "gemini-2.5-flash",
            "code":               "gemini-2.5-pro",
            "logic":              "gemini-2.5-pro",
            "polish":             "gemini-2.5-flash",
            "persona_kagurazaka": "gemini-2.5-flash",
            "persona_custom":     "gemini-2.5-flash",
            "quality_check":      "gemini-2.5-flash",
            "planner":            "gemini-2.5-pro",
            "reviewer":           "gemini-2.5-flash",
            "aggregator":         "gemini-2.5-flash",
            "search_judge":       "gemini-2.5-flash",
            "task_router":        "gemini-2.5-pro"
        }
    },
    # ---- Anthropic Claude ----
    "anthropic": {
        "internal_provider": "anthropic",
        "base_url": "https://api.anthropic.com",
        "models": {
            "classifier":         "claude-sonnet-4-20250514",
            "parser":             "claude-sonnet-4-20250514",
            "chat":               "claude-sonnet-4-20250514",
            "code":               "claude-sonnet-4-20250514",
            "logic":              "claude-sonnet-4-20250514",
            "polish":             "claude-sonnet-4-20250514",
            "persona_kagurazaka": "claude-sonnet-4-20250514",
            "persona_custom":     "claude-sonnet-4-20250514",
            "quality_check":      "claude-sonnet-4-20250514",
            "planner":            "claude-sonnet-4-20250514",
            "reviewer":           "claude-sonnet-4-20250514",
            "aggregator":         "claude-sonnet-4-20250514",
            "search_judge":       "claude-sonnet-4-20250514",
            "task_router":        "claude-sonnet-4-20250514"
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
            "task_router":        "deepseek-v4-pro"
        }
    },
    # ---- 智谱 GLM (OpenAI 兼容) ----
    "zhipu": {
        "internal_provider": "openai",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": {
            "classifier":         "glm-4-flash",
            "parser":             "glm-4-flash",
            "chat":               "glm-4-flash",
            "code":               "glm-4-flash",
            "logic":              "glm-4-flash",
            "polish":             "glm-4-flash",
            "persona_kagurazaka": "glm-4-flash",
            "persona_custom":     "glm-4-flash",
            "quality_check":      "glm-4-flash",
            "planner":            "glm-4-flash",
            "reviewer":           "glm-4-flash",
            "aggregator":         "glm-4-flash",
            "search_judge":       "glm-4-flash",
            "task_router":        "glm-4-flash"
        }
    },
    # ---- 阿里通义千问 (OpenAI 兼容) ----
    "qwen": {
        "internal_provider": "openai",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": {
            "classifier":         "qwen-turbo",
            "parser":             "qwen-turbo",
            "chat":               "qwen-plus",
            "code":               "qwen-plus",
            "logic":              "qwen-plus",
            "polish":             "qwen-turbo",
            "persona_kagurazaka": "qwen-turbo",
            "persona_custom":     "qwen-turbo",
            "quality_check":      "qwen-turbo",
            "planner":            "qwen-plus",
            "reviewer":           "qwen-turbo",
            "aggregator":         "qwen-turbo",
            "search_judge":       "qwen-turbo",
            "task_router":        "qwen-plus"
        }
    },
    # ---- Moonshot (OpenAI 兼容) ----
    "moonshot": {
        "internal_provider": "openai",
        "base_url": "https://api.moonshot.cn/v1",
        "models": {
            "classifier":         "moonshot-v1-8k",
            "parser":             "moonshot-v1-8k",
            "chat":               "moonshot-v1-8k",
            "code":               "moonshot-v1-8k",
            "logic":              "moonshot-v1-8k",
            "polish":             "moonshot-v1-8k",
            "persona_kagurazaka": "moonshot-v1-8k",
            "persona_custom":     "moonshot-v1-8k",
            "quality_check":      "moonshot-v1-8k",
            "planner":            "moonshot-v1-8k",
            "reviewer":           "moonshot-v1-8k",
            "aggregator":         "moonshot-v1-8k",
            "search_judge":       "moonshot-v1-8k",
            "task_router":        "moonshot-v1-8k"
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
