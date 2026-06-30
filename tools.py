"""
工具注册表与 Function Calling 引擎
让 LLM 能调用外部工具：搜索、读写文件、HTTP请求、获取时间
"""
import json
import os
import datetime
import requests
from typing import Any, Callable

TOOL_REGISTRY: dict = {}

# 文件操作的安全路径白名单
_SAFE_ROOTS = [
    os.path.abspath(os.path.dirname(__file__)),
    os.path.expanduser("~"),
    os.path.abspath("."),
]


def _is_path_safe(path: str) -> bool:
    """检查目标路径是否在安全范围内"""
    try:
        abs_path = os.path.abspath(os.path.expanduser(path))
    except (ValueError, OSError):
        return False
    for root in _SAFE_ROOTS:
        try:
            if abs_path.startswith(os.path.abspath(root) + os.sep) or abs_path == os.path.abspath(root):
                return True
        except (ValueError, OSError):
            continue
    return False


def register_tool(name: str, description: str, parameters: dict, function: Callable):
    TOOL_REGISTRY[name] = {
        "name": name,
        "description": description,
        "parameters": parameters,
        "function": function,
    }


def get_tool_definitions() -> list:
    """返回 OpenAI 格式的 tools 列表"""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
            }
        }
        for t in TOOL_REGISTRY.values()
    ]


def execute_tool(name: str, arguments: dict) -> str:
    if name not in TOOL_REGISTRY:
        return json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)
    try:
        result = TOOL_REGISTRY[name]["function"](arguments)
        if isinstance(result, str):
            return result
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def has_tool_calls(response: Any) -> bool:
    if isinstance(response, dict):
        msg = response.get("choices", [{}])[0].get("message", {})
        return bool(msg.get("tool_calls"))
    return False


def extract_tool_calls(response: Any) -> list:
    if isinstance(response, dict):
        return response.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
    return []


def format_tool_result(tool_call_id: str, name: str, result: str) -> dict:
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": name,
        "content": result,
    }


def tool_search_web(params: dict) -> str:
    from search import google_search
    query = params.get("query", "")
    if not query:
        return json.dumps({"error": "缺少搜索关键词"}, ensure_ascii=False)
    results = google_search(query)
    if not results:
        return json.dumps({"message": "未找到相关结果"}, ensure_ascii=False)
    return results


def tool_read_file(params: dict) -> str:
    path = params.get("path", "")
    if not path:
        return json.dumps({"error": "缺少文件路径"}, ensure_ascii=False)
    if not _is_path_safe(path):
        return json.dumps({"error": "路径不在允许范围内"}, ensure_ascii=False)
    try:
        with open(os.path.expanduser(path), "r", encoding="utf-8") as f:
            content = f.read(8192)
        return content[:8192]
    except FileNotFoundError:
        return json.dumps({"error": f"文件不存在: {path}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def tool_write_file(params: dict) -> str:
    path = params.get("path", "")
    content = params.get("content", "")
    if not path:
        return json.dumps({"error": "缺少文件路径"}, ensure_ascii=False)
    if not _is_path_safe(path):
        return json.dumps({"error": "路径不在允许范围内"}, ensure_ascii=False)
    try:
        abs_path = os.path.expanduser(path)
        os.makedirs(os.path.dirname(os.path.abspath(abs_path)) or ".", exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return json.dumps({"ok": True, "path": abs_path, "size": len(content)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def tool_get_datetime(params: dict) -> str:
    now = datetime.datetime.now()
    return json.dumps({
        "datetime": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "weekday": now.strftime("%A"),
        "timestamp": int(now.timestamp()),
    }, ensure_ascii=False)


def tool_http_get(params: dict) -> str:
    url = params.get("url", "")
    if not url:
        return json.dumps({"error": "缺少URL"}, ensure_ascii=False)
    if not url.startswith(("http://", "https://")):
        return json.dumps({"error": "URL必须以http或https开头"}, ensure_ascii=False)
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Kagurazaka-Agent/1.0"})
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            text = json.dumps(resp.json(), ensure_ascii=False)[:4096]
        else:
            text = resp.text[:4096]
        return f"[HTTP {resp.status_code}] {text}"
    except requests.Timeout:
        return json.dumps({"error": f"请求超时: {url}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ---- 注册内置工具 ----
register_tool(
    name="search_web",
    description="搜索互联网获取最新信息。用于需要实时数据、新闻、事实查询等场景。",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"}
        },
        "required": ["query"]
    },
    function=tool_search_web
)

register_tool(
    name="read_file",
    description="读取本地文件内容。只能读取项目目录和用户目录下的文件。",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径（相对于项目目录或绝对路径）"}
        },
        "required": ["path"]
    },
    function=tool_read_file
)

register_tool(
    name="write_file",
    description="写入内容到本地文件。只能写入项目目录和用户目录下的文件。",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"},
            "content": {"type": "string", "description": "要写入的内容"}
        },
        "required": ["path", "content"]
    },
    function=tool_write_file
)

register_tool(
    name="get_datetime",
    description="获取当前日期、时间、星期信息。用于需要知道现在是什么时间的场景。",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    },
    function=tool_get_datetime
)

register_tool(
    name="http_get",
    description="发送 HTTP GET 请求获取网页或 API 的内容。",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "请求的URL（必须以http://或https://开头）"}
        },
        "required": ["url"]
    },
    function=tool_http_get
)
