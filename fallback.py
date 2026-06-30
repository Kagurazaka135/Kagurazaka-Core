"""
错误恢复与容错模块
- 指数退避重试
- Fallback 模型切换
- 优雅降级策略
"""
import time
import random


class MaxRetriesExceeded(Exception):
    def __init__(self, provider: str, model: str, attempts: int, last_error: str):
        self.provider = provider
        self.model = model
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"All {attempts} retries exhausted for {provider}/{model}: {last_error}")


def is_retryable_error(exception: Exception) -> bool:
    """判断异常是否值得重试"""
    ex_type = type(exception).__name__
    ex_msg = str(exception).lower()

    # 不可重试：认证/权限错误
    non_retryable = ["401", "403", "unauthorized", "forbidden", "api key not set",
                     "not found", "404", "method not allowed", "405",
                     "invalid_request_error", "invalid api key"]
    for kw in non_retryable:
        if kw in ex_msg:
            return False

    # 可重试
    retryable_types = ["Timeout", "ConnectionError", "HTTPError", "RemoteDisconnected",
                       "ProxyError", "SSLError", "ReadTimeout", "ConnectTimeout"]
    if ex_type in retryable_types:
        return True

    retryable_keywords = ["timeout", "connection", "rate limit", "429", "500", "502", "503",
                          "504", "server error", "too many requests", "service unavailable",
                          "temporarily", "overloaded"]
    for kw in retryable_keywords:
        if kw in ex_msg:
            return True

    return False


def call_llm_with_retry(provider: str, model: str, system_prompt: str, user_message: str,
                        max_retries: int = 3, base_delay: float = 1.0) -> str:
    """带指数退避重试的 LLM 调用"""
    from llm import call_llm

    last_error = None
    for attempt in range(max_retries):
        try:
            return call_llm(provider, model, system_prompt, user_message)
        except Exception as e:
            last_error = e
            if not is_retryable_error(e):
                raise
            if attempt == max_retries - 1:
                raise MaxRetriesExceeded(provider, model, max_retries, str(e))
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.3)
            print(f"[重试] 第{attempt+1}次失败 ({provider}/{model}): {e}，{delay:.1f}秒后重试")
            time.sleep(delay)

    raise MaxRetriesExceeded(provider, model, max_retries, str(last_error))


def call_node_with_fallback(node_name: str, user_message: str,
                            temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """带 fallback 的节点调用：主模型失败自动切备用"""
    import config as cfg
    from llm import call_llm, SYSTEM_MAP

    models_cfg = cfg.CONFIG.get("MODELS", {})
    node_cfg = models_cfg.get(node_name, {})
    if not node_cfg:
        raise ValueError(f"Node '{node_name}' not found in MODELS config")

    primary_provider = node_cfg["provider"]
    primary_model = node_cfg["model"]
    fallback_provider = node_cfg.get("fallback_provider") or None
    fallback_model = node_cfg.get("fallback_model") or None
    system_prompt = SYSTEM_MAP.get(node_name, "")

    # 主模型尝试
    try:
        return call_llm_with_retry(primary_provider, primary_model,
                                   system_prompt, user_message, 3, 1.0)
    except Exception as e:
        print(f"[主模型失败] {node_name}: {primary_provider}/{primary_model} — {e}")

    # 备用模型
    if fallback_provider and fallback_model:
        print(f"[Fallback] {node_name} 切换到备用: {fallback_provider}/{fallback_model}")
        try:
            return call_llm_with_retry(fallback_provider, fallback_model,
                                       system_prompt, user_message, 2, 1.0)
        except Exception as e2:
            print(f"[Fallback失败] {node_name}: {fallback_provider}/{fallback_model} — {e2}")

    # 全部失败 → 降级
    degraded = get_degradation_strategy(node_name, str(user_message)[:200])
    print(f"[降级] {node_name} 使用降级策略")
    return degraded


def get_degradation_strategy(node_name: str, context: str = "") -> str:
    """返回节点的降级默认值"""
    strategies = {
        "search_judge":         '{"search_needed": false}',
        "search_quality_check": '{"quality_ok": true}',
        "task_router":          '{"complexity": "simple", "chat_task": "' + context.replace('"', '\\"') + '", "code_task": null, "logic_task": null}',
        "chat":                 "",
        "code":                 "",
        "logic":                "",
        "polish":               "",
        "planner":              '{"steps": [{"step_id": 1, "node_type": "chat", "user_prompt": "' + context.replace('"', '\\"') + '"}]}',
        "reviewer":             '{"pass": true}',
        "aggregator":           "",
        "classifier":           "",
        "parser":               "",
        "persona_kagurazaka":   "",
        "persona_custom":       "",
        "quality_check":        '{"pass": true}',
    }

    result = strategies.get(node_name, "")
    if result == "" and node_name in ("chat", "code", "logic", "polish", "aggregator",
                                       "persona_kagurazaka", "persona_custom"):
        return "Kagurazaka暂时不在线 [oops] 请稍后再试"
    return result
