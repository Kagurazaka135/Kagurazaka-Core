"""
配置管理模块
支持两种模式:
  【简单模式】选一个供应商 + 填一个 API key → 自动配好所有节点
  【高级模式】手动为每个节点指定 provider 和 model
"""
import json
import os
import copy
from typing import Dict

from provider_presets import get_preset, list_providers, ALL_PROVIDERS

_DEFAULT_CONFIG: Dict = {
    "SERPAPI_KEY": "",
    "PERSONA_MODE": "none",
    "MEMORY": {
        "WORKING_CAPACITY": 7,
        "SESSION_CAPACITY": 10,
        "SAVE_PATH": "./memory_store/"
    },
    "PROVIDERS": {
        "google":    {"api_key": "", "base_url": "https://generativelanguage.googleapis.com"},
        "openai":    {"api_key": "", "base_url": "https://api.openai.com"},
        "anthropic": {"api_key": "", "base_url": "https://api.anthropic.com"}
    },
    "MODELS": {
        "classifier":         {"provider": "google",    "model": "gemini-3.1-flash-lite", "fallback_provider": None, "fallback_model": None},
        "parser":             {"provider": "google",    "model": "gemini-3.1-flash-lite", "fallback_provider": None, "fallback_model": None},
        "chat":               {"provider": "google",    "model": "gemini-3.5-flash",      "fallback_provider": None, "fallback_model": None},
        "code":               {"provider": "anthropic", "model": "claude-opus-4-6",       "fallback_provider": None, "fallback_model": None},
        "logic":              {"provider": "openai",    "model": "gpt-4.1",               "fallback_provider": None, "fallback_model": None},
        "polish":             {"provider": "google",    "model": "gemini-3.1-flash-lite", "fallback_provider": None, "fallback_model": None},
        "persona_kagurazaka": {"provider": "openai",    "model": "deepseek-v4-flash",     "fallback_provider": None, "fallback_model": None},
        "persona_custom":     {"provider": "openai",    "model": "deepseek-v4-flash",     "fallback_provider": None, "fallback_model": None},
        "quality_check":      {"provider": "openai",    "model": "gpt-4.1-mini",          "fallback_provider": None, "fallback_model": None},
        "planner":            {"provider": "anthropic", "model": "claude-opus-4-6",       "fallback_provider": None, "fallback_model": None},
        "reviewer":           {"provider": "google",    "model": "gemini-3.1-flash-lite", "fallback_provider": None, "fallback_model": None},
        "aggregator":         {"provider": "google",    "model": "gemini-3.1-flash-lite", "fallback_provider": None, "fallback_model": None},
        "search_judge":       {"provider": "google",    "model": "gemini-3.1-flash-lite", "fallback_provider": None, "fallback_model": None},
        "search_quality_check":{"provider": "google",   "model": "gemini-3.1-flash-lite", "fallback_provider": None, "fallback_model": None},
        "task_router":        {"provider": "anthropic", "model": "claude-opus-4-6",       "fallback_provider": None, "fallback_model": None}
    },
    "LOGGING": {"ENABLED": True, "DIR": "./logs/"}
}

CONFIG: Dict = {}


def _generate_template():
    template = {
        "_说明": (
            "=== 简单模式（推荐！只填下面几项就能跑）===\n"
            "选一个供应商，填API key。可选供应商:\n"
            f"{list_providers()}\n"
            "如有特殊需求才用高级模式（填 PROVIDERS + MODELS 覆盖）"
        ),
        "搜寻说明_1": "=== LLM 配置 ===",
        "LLM_PROVIDER": "openai",
        "LLM_API_KEY": "sk-",
        "LLM_BASE_URL": "",
        "搜寻说明_2": "=== 可选功能 ===",
        "SERPAPI_KEY": "你的SerpAPI key，不需要搜索就留空（支持Google和Bing）",
        "PERSONA_MODE": "none",
        "_persona_mode说明": "人格注入模式: none(不注入) | kagurazaka(神楽坂人格) | custom(自定义人格)",
        "搜寻说明_3": "=== 高级（可不填）===",
        "MODEL_OVERRIDES": {
            "_说明": "可选，覆盖单个节点的模型名。如 {\"code\": \"gpt-4.1\"}",
        },
    }
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=4)
    print(f"\n[*] 已生成 config.json 模板")
    print(f"[*] 可选供应商: {', '.join(ALL_PROVIDERS)}")
    print(f"[*] 填好 LLM_PROVIDER + LLM_API_KEY 后重新运行\n")


VALID_NODE_NAMES = set(_DEFAULT_CONFIG["MODELS"].keys())


def _validate_overrides(overrides: dict, preset_models: dict):
    """校验 MODEL_OVERRIDES：防拼写错误、防空值"""
    issues = []
    for node_name, model_name in overrides.items():
        if node_name.startswith("_"):
            continue
        if node_name not in VALID_NODE_NAMES:
            close = [n for n in VALID_NODE_NAMES if node_name[:3] in n or n[:3] in node_name]
            hint = f"（你是指 {'/'.join(close)} 吗？）" if close else ""
            issues.append(f"未知节点 '{node_name}' {hint}")
        elif not str(model_name).strip():
            issues.append(f"节点 '{node_name}' 模型名为空，将使用预设默认值")

    # 检查有没有写了对的节点但拼错 model 名的 (不在预设里的模型名给提示)
    if preset_models:
        for node_name, model_name in overrides.items():
            if node_name in VALID_NODE_NAMES and str(model_name).strip():
                preset_val = preset_models.get(node_name, "")
                if preset_val and str(model_name).strip() == preset_val:
                    pass  # 和预设一样，不需要提示
                # 无法验证模型名是否存在（不同供应商不同），只做格式检查
                if "/" not in str(model_name) and " " in str(model_name):
                    issues.append(f"节点 '{node_name}' 模型名包含空格: '{model_name}'")

    if issues:
        print("[!] MODEL_OVERRIDES 校验:")
        for i in issues:
            print(f"    ⚠ {i}")


def _validate_advanced_models(models: dict):
    """高级模式 MODELS 校验"""
    valid_providers = {"openai", "google", "anthropic"}
    for node_name, node_cfg in models.items():
        if node_name.startswith("_"):
            continue
        if isinstance(node_cfg, dict):
            p = node_cfg.get("provider", "")
            m = node_cfg.get("model", "")
            if p and p not in valid_providers:
                print(f"[!] 节点 '{node_name}' 的 provider '{p}' 无效，可选: {valid_providers}")
            if m and " " in str(m) and "/" not in str(m):
                print(f"[!] 节点 '{node_name}' 模型名包含空格: '{m}'（拼写错误？）")


def _apply_simple_mode(config: Dict, user_cfg: Dict):
    """简单模式：根据 LLM_PROVIDER 自动填充 PROVIDERS 和 MODELS"""
    provider_name = user_cfg["LLM_PROVIDER"]
    preset = get_preset(provider_name)

    if preset is None:
        print(f"[!] 未知供应商 '{provider_name}'，可选: {', '.join(ALL_PROVIDERS)}")
        return

    api_key = user_cfg.get("LLM_API_KEY", "")
    base_url = user_cfg.get("LLM_BASE_URL", "") or preset.get("base_url", "")
    internal_provider = preset["internal_provider"]
    preset_models: dict = preset.get("models", {})
    overrides: dict = user_cfg.get("MODEL_OVERRIDES", {})
    if isinstance(overrides, dict):
        overrides = {k: v for k, v in overrides.items() if not k.startswith("_")}
    else:
        overrides = {}
    _validate_overrides(overrides, preset_models)

    # 填充 PROVIDERS：只填用户选的那个供应商slot
    config["PROVIDERS"][internal_provider] = {
        "api_key": api_key,
        "base_url": base_url
    }

    # 填充 MODELS：所有节点路由到同一供应商，模型名取 preset + override
    empty_nodes = []
    for node_name in config["MODELS"]:
        model_name = overrides.get(node_name) or preset_models.get(node_name, "")
        config["MODELS"][node_name] = {
            "provider": internal_provider,
            "model": model_name
        }
        if not model_name:
            empty_nodes.append(node_name)

    print(f"[*] 简单模式: 供应商={provider_name}, API协议={internal_provider}")
    if empty_nodes:
        print(f"[!] 以下节点模型名未填写: {', '.join(empty_nodes)}，请在 MODEL_OVERRIDES 中指定")


def _apply_advanced_mode(config: Dict, user_cfg: Dict):
    """高级模式：手动合并 PROVIDERS 和 MODELS（兼容旧版 config.json）"""
    if "PROVIDERS" in user_cfg and isinstance(user_cfg["PROVIDERS"], dict):
        for pname, pcfg in user_cfg["PROVIDERS"].items():
            if pname.startswith("_"):
                continue
            if pname in config["PROVIDERS"] and isinstance(pcfg, dict):
                for key in ("api_key", "base_url"):
                    if key in pcfg and pcfg[key]:
                        config["PROVIDERS"][pname][key] = pcfg[key]

    if "MODELS" in user_cfg and isinstance(user_cfg["MODELS"], dict):
        _validate_advanced_models(user_cfg["MODELS"])
        for nname, ncfg in user_cfg["MODELS"].items():
            if nname.startswith("_"):
                continue
            if nname in config["MODELS"] and isinstance(ncfg, dict):
                for key in ("provider", "model"):
                    if key in ncfg and ncfg[key]:
                        config["MODELS"][nname][key] = ncfg[key]


def _migrate_config(cfg: dict):
    """补全旧版 config.json 缺失的字段，写回文件"""
    updated = False
    missing = []

    if "SERPAPI_KEY" not in cfg:
        cfg["SERPAPI_KEY"] = "你的SerpAPI key，不需要搜索就留空"
        missing.append("SERPAPI_KEY")
    if "PERSONA_MODE" not in cfg:
        cfg["PERSONA_MODE"] = "none"
        missing.append("PERSONA_MODE")
    if "MODEL_OVERRIDES" not in cfg:
        cfg["MODEL_OVERRIDES"] = {}
        missing.append("MODEL_OVERRIDES")

    if missing:
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)
        print(f"[*] config.json 已补齐缺失字段: {', '.join(missing)}")


def _load_config() -> Dict:
    config = copy.deepcopy(_DEFAULT_CONFIG)
    config_file = "config.json"

    if not os.path.exists(config_file):
        _generate_template()
        return config

    with open(config_file, "r", encoding="utf-8") as f:
        user_cfg = json.load(f)

    # ---- 迁移：补齐旧 config.json 缺失的字段 ----
    _migrate_config(user_cfg)

    # ---- SERPAPI_KEY ----
    if "SERPAPI_KEY" in user_cfg and user_cfg["SERPAPI_KEY"] and not str(user_cfg["SERPAPI_KEY"]).startswith("你的"):
        config["SERPAPI_KEY"] = user_cfg["SERPAPI_KEY"]

    # ---- PERSONA_MODE ----
    if "PERSONA_MODE" in user_cfg and user_cfg["PERSONA_MODE"] in ("none", "kagurazaka", "custom"):
        config["PERSONA_MODE"] = user_cfg["PERSONA_MODE"]

    # ---- LOGGING ----
    if "LOGGING" in user_cfg and isinstance(user_cfg["LOGGING"], dict):
        for key in ("ENABLED", "DIR"):
            if key in user_cfg["LOGGING"]:
                config["LOGGING"][key] = user_cfg["LOGGING"][key]

    # ---- LLM 配置: 简单模式优先，否则高级模式 ----
    if "LLM_PROVIDER" in user_cfg and user_cfg["LLM_PROVIDER"]:
        _apply_simple_mode(config, user_cfg)
    else:
        _apply_advanced_mode(config, user_cfg)

    return config


def init_config():
    global CONFIG
    CONFIG = _load_config()
