"""
网络搜索模块
  - 主引擎: Google (SerpAPI)
  - 备选引擎: Bing (同一 SerpAPI key 切换 engine)
  - 两次都失败 → 返回空
"""
import requests

import config as cfg


def google_search(query: str) -> str:
    serpapi_key = cfg.CONFIG.get("SERPAPI_KEY", "")
    if not serpapi_key or serpapi_key.startswith("你的"):
        print("[*] SERPAPI_KEY 未配置，跳过搜索")
        return ""

    # 主引擎: Google
    result = _serpapi_search(query, serpapi_key, "google")
    if result:
        return result

    # 备选引擎: Bing
    print("[*] Google 搜索无结果，尝试 Bing...")
    result = _serpapi_search(query, serpapi_key, "bing")
    if result:
        return result

    print("[!] 两个搜索引擎均无结果")
    return ""


def _serpapi_search(query: str, api_key: str, engine: str) -> str:
    print(f"[*] 正在执行 {engine} 搜索: {query}")
    params = {
        "q": query,
        "api_key": api_key,
        "engine": engine,
        "hl": "zh-cn"
    }
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=20)
        results = resp.json()
        snippets = []
        if "organic_results" in results:
            for res in results["organic_results"][:5]:
                snippet = res.get("snippet", "")
                if snippet:
                    snippets.append(snippet)
        return "\n".join(snippets) if snippets else ""
    except Exception as e:
        print(f"[!] {engine} 搜索失败: {e}")
        return ""
