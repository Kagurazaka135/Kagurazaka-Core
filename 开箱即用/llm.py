"""
统一 LLM 调用客户端
支持 OpenAI / Google Gemini / Anthropic Claude
"""
import json
import re
import time
import requests

import config as cfg
import logger as log
from prompts import (
    CLASSIFIER_SYSTEM, PARSER_SYSTEM,
    SEARCH_JUDGE_SYSTEM, SEARCH_QUALITY_CHECK_SYSTEM,
    TASK_ROUTER_SYSTEM,
    CHAT_SYSTEM, CODE_SYSTEM, LOGIC_SYSTEM,
    POLISH_SYSTEM, POLISH_CHECK_SYSTEM,
    PLANNER_SYSTEM, REVIEWER_SYSTEM, AGGREGATOR_SYSTEM,
    PERSONA_KAGURAZAKA_SYSTEM, PERSONA_CUSTOM_SYSTEM
)

_DEBUG_LOG = None


def _dbg(msg: str):
    """直接写 debug.log，不依赖 logger 模块"""
    global _DEBUG_LOG
    import datetime
    try:
        if _DEBUG_LOG is None:
            _DEBUG_LOG = open("debug.log", "a", encoding="utf-8")
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        _DEBUG_LOG.write(f"[{ts}] {msg}\n")
        _DEBUG_LOG.flush()
    except Exception:
        pass

SYSTEM_MAP = {
    "classifier":           CLASSIFIER_SYSTEM,
    "parser":               PARSER_SYSTEM,
    "search_judge":         SEARCH_JUDGE_SYSTEM,
    "search_quality_check": SEARCH_QUALITY_CHECK_SYSTEM,
    "task_router":          TASK_ROUTER_SYSTEM,
    "chat":                 CHAT_SYSTEM,
    "code":                 CODE_SYSTEM,
    "logic":                LOGIC_SYSTEM,
    "polish":               POLISH_SYSTEM,
    "planner":              PLANNER_SYSTEM,
    "reviewer":             REVIEWER_SYSTEM,
    "aggregator":           AGGREGATOR_SYSTEM,
    "persona_kagurazaka":   PERSONA_KAGURAZAKA_SYSTEM,
    "persona_custom":       PERSONA_CUSTOM_SYSTEM,
    "quality_check":        POLISH_CHECK_SYSTEM,
}


def call_llm(provider: str, model: str, system_prompt: str, user_message: str,
             temperature: float = 0.7, max_tokens: int = 4096) -> str:
    if provider == "openai":
        return _call_openai(model, system_prompt, user_message, temperature, max_tokens)
    elif provider == "google":
        return _call_gemini(model, system_prompt, user_message, temperature, max_tokens)
    elif provider == "anthropic":
        return _call_anthropic(model, system_prompt, user_message, temperature, max_tokens)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def call_node(node_name: str, user_message: str, temperature: float = 0.7,
              max_tokens: int = 4096) -> str:
    models_cfg = cfg.CONFIG.get("MODELS", {})
    if node_name not in models_cfg:
        raise ValueError(f"Node '{node_name}' not found in MODELS config")

    node_cfg = models_cfg[node_name]
    provider = node_cfg["provider"]
    model = node_cfg["model"]
    system_prompt = SYSTEM_MAP.get(node_name, "")

    log.record(node_name, "llm_call", len(user_message), 0, True, 0,
               f"provider={provider} model={model}")
    _dbg(f"call_node [{node_name}] provider={provider} model={model} msg_len={len(user_message)}")
    result = call_llm(provider, model, system_prompt, user_message, temperature, max_tokens)
    log.record(node_name, "llm_result", 0, 0, bool(result), len(result))
    _dbg(f"call_node [{node_name}] result_len={len(result)} ok={bool(result)}")
    return result


def _get_provider_cfg(provider: str) -> dict:
    providers = cfg.CONFIG.get("PROVIDERS", {})
    _dbg(f"_get_provider_cfg [{provider}] keys={list(providers.keys())}")
    log.record(provider, "get_cfg", 0, 0, True, 0,
               f"providers_keys={list(providers.keys())}")
    if provider not in providers:
        _dbg(f"_get_provider_cfg [{provider}] NOT FOUND in providers")
        log.record(provider, "cfg_err", 0, 0, False, 0,
                   f"provider not in {list(providers.keys())}")
        raise ValueError(f"Provider '{provider}' not configured")
    pcfg = providers[provider]
    api_key = pcfg.get("api_key", "")
    if not api_key or api_key.startswith("填你的") or api_key == "sk-":
        _dbg(f"_get_provider_cfg [{provider}] api_key invalid: {'empty' if not api_key else api_key[:8]}")
        log.record(provider, "cfg_err", 0, 0, False, 0,
                   f"api_key invalid: {'empty' if not api_key else api_key[:8]}...")
        raise ValueError(f"Provider '{provider}' API key not set. Please edit config.json")
    _dbg(f"_get_provider_cfg [{provider}] OK base_url={pcfg.get('base_url', '?')[:50]}")
    return pcfg


# ==========================================
# LLM 输出清理 — 剔除碎碎念 (DeepSeek / 元分析 / 格式残留)
# ==========================================
def clean_llm_output(text: str) -> str:
    """每轮 LLM 调用后自动清理输出中的思考过程、元分析和格式残留
    - 安全设计：只匹配明确的碎碎念模式，不伤正文
    - 安全网：若清除量 >80%，回退原文"""
    if not text or len(text) < 20:
        return text.strip() if text else ""

    original = text

    # --- 1. DeepSeek <think> XML 标签 ---
    text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
    text = re.sub(r'<think>.*$', '', text, flags=re.DOTALL)

    # --- 2. 元分析自言自语（整行匹配，防误删正文） ---
    meta_patterns = [
        r'^.{0,10}(?:我需要|我打算|我准备|我决定|我注意到|我认为应该).{0,80}?(?:来回应|来回答|来思考|来展开)[。]?\s*$',
        r'^.{0,6}(?:可以借鉴|可以引用|可以类比|可以借用).{0,60}?[。]?\s*$',
        r'^.{0,6}(?:关键词在|核心在于|重点在于|难点在于|关键点在于).{0,60}?[。]\s*$',
        r'^.{0,10}(?:这个问题|这个提问|这道题).{0,40}?(?:触及|涉及|关于|围绕).{0,40}?[。]\s*$',
        r'^嗯[，,].{0,30}?(?:这个问题|很有|值得|确实|不错|可以的).{0,60}?[。]?\s*$',
        r'^.{0,6}(?:好的|好)[，,].{0,30}?(?:让我|我先|我来|我试着).{0,60}?[。]?\s*$',
    ]
    for p in meta_patterns:
        text = re.sub(p, '', text, flags=re.MULTILINE)

    # --- 3. 领域选择前缀 ---
    text = re.sub(r'从.{1,6}(?:领域|角度).{0,20}(?:提取|选择|中)[：:，。]?\s*', '', text)
    text = re.sub(r'我选择.{1,6}(?:领域|角度)[。，]?\s*', '', text)
    text = re.sub(r'基于.{1,6}(?:领域|角度).{0,10}[：:]\s*', '', text)

    # --- 4. Markdown 格式符号（去壳留肉） ---
    text = re.sub(r'#{1,6}\s?', '', text)
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
    text = re.sub(r'^[-*+] ', '', text, flags=re.MULTILINE)
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)

    # --- 5. 步骤标签 + 引导句 ---
    text = re.sub(r'(?:第[一二三四五六七八九十\d]+步|步骤\s*\d+)[：:]?\s*', '', text)
    text = re.sub(r'若你愿意.*?再展开[。！]?', '', text)
    text = re.sub(r'【[^】]{1,20}】\s*', '', text)

    # --- 6. 清理多余空行 ---
    text = re.sub(r'\n{3,}', '\n\n', text)

    text = text.strip()

    # 安全网：若清理过头（输出 < 原文 15%），退回原文
    if len(text) < max(10, len(original) * 0.15):
        return original.strip()

    return text


def _call_openai(model: str, system_prompt: str, user_message: str,
                 temperature: float, max_tokens: int) -> str:
    pcfg = _get_provider_cfg("openai")
    url = f"{pcfg['base_url'].rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {pcfg['api_key']}",
        "Content-Type": "application/json"
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        _dbg(f"_call_openai [{model}] POST {url[:80]}...")
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        body = resp.json()
        result = clean_llm_output(body["choices"][0]["message"]["content"])
        _dbg(f"_call_openai [{model}] OK len={len(result)}")
        return result
    except Exception as e:
        _dbg(f"_call_openai [{model}] ERROR: {e}")
        print(f"[!] OpenAI API error ({model}): {e}")
        return ""


# ==========================================
# Google Gemini
# ==========================================
def _call_gemini(model: str, system_prompt: str, user_message: str,
                 temperature: float, max_tokens: int) -> str:
    pcfg = _get_provider_cfg("google")
    url = f"{pcfg['base_url'].rstrip('/')}/v1beta/models/{model}:generateContent?key={pcfg['api_key']}"
    headers = {"Content-Type": "application/json"}

    body: dict = {
        "contents": [{"parts": [{"text": user_message}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }
    if system_prompt:
        body["system_instruction"] = {"parts": [{"text": system_prompt}]}

    try:
        _dbg(f"_call_gemini [{model}] POST {url[:80]}...")
        resp = requests.post(url, headers=headers, json=body, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                result = clean_llm_output(parts[0].get("text", ""))
                _dbg(f"_call_gemini [{model}] OK len={len(result)}")
                return result
        _dbg(f"_call_gemini [{model}] empty response")
        return ""
    except Exception as e:
        _dbg(f"_call_gemini [{model}] ERROR: {e}")
        print(f"[!] Gemini API error ({model}): {e}")
        return ""


# ==========================================
# Anthropic Claude
# ==========================================
def _call_anthropic(model: str, system_prompt: str, user_message: str,
                    temperature: float, max_tokens: int) -> str:
    pcfg = _get_provider_cfg("anthropic")
    url = f"{pcfg['base_url'].rstrip('/')}/v1/messages"
    headers = {
        "x-api-key": pcfg["api_key"],
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    body: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user_message}]
    }
    if system_prompt:
        body["system"] = system_prompt
    if temperature > 0:
        body["temperature"] = temperature

    try:
        _dbg(f"_call_anthropic [{model}] POST {url[:80]}...")
        resp = requests.post(url, headers=headers, json=body, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("content", [])
        for block in content:
            if block.get("type") == "text":
                result = clean_llm_output(block.get("text", ""))
                _dbg(f"_call_anthropic [{model}] OK len={len(result)}")
                return result
        _dbg(f"_call_anthropic [{model}] empty response")
        return ""
    except Exception as e:
        _dbg(f"_call_anthropic [{model}] ERROR: {e}")
        print(f"[!] Anthropic API error ({model}): {e}")
        return ""


# ==========================================
# JSON 提取工具
# ==========================================
def safe_extract_json(text: str) -> dict:
    """从 LLM 输出中安全提取 JSON"""
    if not text:
        return {}
    clean = text.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        clean = "\n".join(lines)
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{[\s\S]*\}', clean)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}
