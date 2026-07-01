# tools.py — 工具箱

**让 LLM 能干活，不只是聊天。** 注册工具 → LLM 决定用哪个 → 执行 → 把结果还给 LLM。

## 5 个内置工具

| 工具 | 干啥的 | 参数 |
|---|---|---|
| `search_web` | 搜网页 | query（搜什么） |
| `read_file` | 读本地文件 | path（文件路径） |
| `write_file` | 写本地文件 | path + content |
| `get_datetime` | 拿当前日期时间 | 无参数 |
| `http_get` | 发 HTTP GET 请求 | url（必须 https） |

## 是怎么工作的

```
LLM 收到你的问题 + 搜到的信息
  → LLM 判断：我需要用工具吗？
  → 需要 → 返回 tool_calls（比如 "我要 search_web，搜 XXX"）
  → core.py 执行这个工具，拿到结果
  → 把结果追加到对话历史，再问 LLM：还需要什么吗？
  → 最多 5 轮
  → 最后一轮强制 LLM 出最终回答（不能再要工具了）
```

## 文件安全

读写文件不是随便哪个路径都能碰的。只允许在项目目录、用户目录、当前工作目录范围内操作。越界的直接拒绝。

## 怎么加新工具

```python
register_tool(
    name="my_tool",
    description="这个工具干什么",
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "参数说明"}
        },
        "required": ["param1"]
    },
    function=my_tool_function  # 实际执行的 Python 函数
)
```

注册完 LLM 就能自动发现和调用它了。
