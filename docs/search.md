# search.py — Google 搜索

**只有被分类器判定"需要搜索"时才触发。**

## 逻辑

```python
def google_search(query: str) -> str:
    serpapi_key = CONFIG.get("SERPAPI_KEY", "")
    if not serpapi_key:  return ""    # 没配就不搜

    # 调 SerpAPI
    response = requests.get("https://serpapi.com/search", params={...})

    # 取前 5 条结果的摘要
    snippets = [res["snippet"] for res in results["organic_results"][:5]]
    return "\n".join(snippets)
```

## 搜索结果去哪了

`core.py` 里拼到解析器的输入里：

```python
combined_input = f"搜索结果：{search_context}\n用户问题：{enhanced_input}"
```

所以"干饭人"（解析器）看到的是带搜索上下文的完整问题，能做出更准确的分类。

## 为什么用 SerpAPI 而不是直接爬 Google

直接爬 Google 需要处理反爬、验证码、IP 封禁。SerpAPI 付费用 API 调，稳定省心。免费套餐 100 次/月，够开发用。

不配 `SERPAPI_KEY` 也不影响使用——分类器判定不需要搜索的问题照常走。
