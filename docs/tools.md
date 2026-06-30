# tools.py — 工具注册表与 Function Calling 引擎

**让 LLM 能调用外部工具。** 注册 → 暴露 → 执行 → 返回。

## 5 个内置工具

| 工具 | 功能 | 参数 |
|------|------|------|
| `search_web` | 搜索互联网 | `query` (必填) |
| `read_file` | 读取本地文件 | `path` (必填) |
| `write_file` | 写入本地文件 | `path`, `content` (必填) |
| `get_datetime` | 获取当前日期时间 | 无 |
| `http_get` | HTTP GET 请求 | `url` (必填, https://) |

## 如何添加新工具

```python
register_tool(
    name="my_tool",
    description="工具描述",
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "参数说明"}
        },
        "required": ["param1"]
    },
    function=my_tool_function
)
```

## 工具定义暴露

`get_tool_definitions()` 返回 OpenAI 格式的 tools 列表，传给 `call_llm_with_tools()`。

## 文件操作安全

路径必须在白名单范围内：
- 项目目录
- 用户目录
- 当前工作目录

越界路径返回错误。

## 在 core.py 里的工具调用循环

```
LLM 收到用户输入 + 搜索结果
    → 判断是否需要工具
    → 返回 tool_calls 或直接文本回答
    → 有 tool_calls → 执行 → 结果追加到消息历史 → 下一轮
    → 最多 5 轮
    → 最后一轮强制 LLM 给出最终回答
```

如果有工具调用并产生了最终答案，跳过 Task Router，直接进入人格注入。
