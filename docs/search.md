# search.py — 上网搜东西

**当 Search Judge 判定需要搜索时才触发。** 调 SerpAPI 搜 Google，Google 挂了就切 Bing。

## 流程

```
Search Judge 说"需要搜，搜 XXX"
  → 先查缓存（30 分钟内搜过直接用）
  → 没缓存 → 调 SerpAPI
    → Google 主引擎
    → Google 挂了 → 自动切 Bing
  → 取前 5 条结果的摘要
  → 返回给 core.py
  → 搜到的结果质量够不够？→ 不够就换词重搜
```

## 为什么不直接爬 Google

直接爬要处理反爬、验证码、IP 封禁。SerpAPI 走正规 API，稳定不折腾。

## 不配 SERPAPI_KEY 也能用

Search Judge 判定不需要搜索的问题（比如闲聊、问代码）照常走。只是不能搜网页而已。
