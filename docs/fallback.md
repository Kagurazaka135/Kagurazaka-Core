# fallback.py — 错误恢复与容错

**LLM 调用挂了怎么办？** 指数退避重试 → Fallback 模型切换 → 优雅降级。

## 三层容错策略

### 1. 指数退避重试
```python
def call_llm_with_retry(provider, model, ..., max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return call_llm(provider, model, ...)
        except Exception as e:
            if not is_retryable_error(e): raise  # 认证错误直接抛
            delay = base_delay * (2 ** attempt) + random(0, 0.3)
            sleep(delay)
```

### 2. Fallback 模型切换
```python
def call_node_with_fallback(node_name, ...):
    try:
        return call_llm(primary_provider, primary_model, ...)
    except:
        # 切到 fallback_provider/fallback_model
        return call_llm(fallback_provider, fallback_model, ...)
```

`llm.py` 的 `call_node` 内置了简单的 fallback（单次重试，无指数退避）。
`fallback.py` 的 `call_node_with_fallback` 提供完整的指数退避 + fallback + 降级。

### 3. 优雅降级
```python
def get_degradation_strategy(node_name, context):
    # 每个节点都有默认值：
    #   search_judge → {"search_needed": false}  ← 不搜
    #   task_router → {"complexity": "simple"}    ← 走简单路径
    #   reviewer    → {"pass": true}              ← 直接通过
    #   chat/code   → "Kagurazaka暂时不在线"      ← 兜底话术
```

全部失败时返回预定义的降级值，而不是 crash。

## 可重试 vs 不可重试

| 可重试 | 不可重试 |
|--------|----------|
| Timeout, ConnectionError | 401 认证失败 |
| 429 rate limit, 5xx server error | 403 权限错误 |
| ProxyError, SSLError | 404 资源不存在 |

`is_retryable_error()` 通过异常类型和错误消息关键字判断。
