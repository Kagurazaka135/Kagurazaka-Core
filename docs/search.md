# search.py — 网络搜索模块

**只有 Search Judge 判定需要搜索时才触发。** Google 主引擎 + Bing fallback。

## 逻辑

```python
def google_search(query: str) -> str:
    # 1. 检查 SERPAPI_KEY 是否配置
    # 2. 主引擎：Google (SerpAPI)
    # 3. 失败 → Bing fallback (同一 SerpAPI key)
    # 4. 取前 5 条结果的摘要
    # 5. 返回 "\n".join(snippets)
```

## 在 core.py 里的位置

```
Search Judge → google_search(query) → 搜索缓存 → 质量检查 → 换词重搜
```

搜索结果和搜索词一起存入 `memory.py` 的缓存（30min TTL）。
质量不足时 LLM 给出新搜索词，自动重搜一次。

## 为什么用 SerpAPI 而不是直接爬 Google

直接爬 Google 需要处理反爬、验证码、IP 封禁。SerpAPI 走 API，稳定。不配 `SERPAPI_KEY` 不影响使用——Search Judge 判定不需要搜索的问题照常走。
