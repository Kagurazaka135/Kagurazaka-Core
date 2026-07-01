# llm.py — 打电话的人

**所有 LLM 调用都走这里。** 不管你是 OpenAI、Google Gemini 还是 Anthropic Claude，上层只喊一句 `call_node("chat", "你好")`，剩下的它搞定。

## 三个 API 适配器

不同公司的 API 格式不一样，llm.py 做了翻译：

| 供应商 | API 路径 | 特点 |
|---|---|---|
| OpenAI | `/v1/chat/completions` | 标准格式，国产模型基本都兼容这个 |
| Google | `/v1beta/models/{model}:generateContent` | system prompt 单独放，key 走 URL |
| Anthropic | `/v1/messages` | system 是顶层字段，key 走 header |

## 怎么用

```python
# 最常用：按节点名调用
call_node("task_router", "用户说：帮我写个爬虫")

# 直接指定 provider + model
call_llm("openai", "gpt-4.1", system_prompt, user_message)

# 带工具的调用（让 LLM 能搜网页、读文件）
call_llm_with_tools(messages, provider, model)
```

`call_node` 自动做了三件事：
1. 查 config 里这个节点用哪个 provider 和 model
2. 查 prompts 里这个节点用哪套 system prompt
3. 调 `call_llm()`

## 输出清理

LLM 有时候会啰嗦——"我需要分析一下..."、"我打算..."之类的自言自语，还会带 Markdown 格式符号。`clean_llm_output()` 自动摘掉这些废话，只留正文。

## JSON 提取

很多节点要求 LLM 输出 JSON，但 LLM 有时候多套一层 ```json ... ``` 或者格式有小毛病。`safe_extract_json()` 做了多层抢救：

1. 剥掉 ```json 外壳
2. 直接 json.loads
3. 修常见错误（尾随逗号、注释、单引号）再试
4. 正则硬搜 {...} 兜底
5. 全失败返回 None

`extract_and_validate()` 在提取后再校验 schema（比如 search_judge 必须有 search_needed 和 search_query 两个字段），不合格自动重试一次。
