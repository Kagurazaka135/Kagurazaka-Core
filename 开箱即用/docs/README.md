# Kagurazaka Core — 纯 Python 版架构说明

## 一句话总结
用户输入 → 判断要不要联网搜索 → 拆成「聊天/代码/逻辑」三类 → 分别交给 LLM 处理 → 聚合结果 → 润色输出 → 质检打回重试

## 文件职责速查

| 文件 | 一句话 | 被谁依赖 |
|---|---|---|
| `main.py` | CLI 入口，命令行交互 | 依赖所有 |
| `core.py` | 工作流编排大管家，串联所有节点 | 依赖 llm/memory/search/quality/logger |
| `config.py` | 读 config.json，支持简单/高级两种模式 | 被几乎所有文件依赖 |
| `provider_presets.py` | 9 个 LLM 供应商的内置模型映射表 | 被 config.py 依赖 |
| `llm.py` | 统一 LLM 调用，对接 OpenAI/Gemini/Claude 三种 API | 被 core.py/quality.py/webui.py 依赖 |
| `prompts.py` | 所有 7 个节点的 system prompt，含 `[PLACEHOLDER]` 标记 | 被 llm.py 依赖 |
| `memory.py` | 会话记忆：上下文追踪 + 话题关联 + 长期记忆持久化 | 被 core.py 依赖 |
| `search.py` | Google 搜索（SerpAPI），为实时问题提供上下文 | 被 core.py 依赖 |
| `quality.py` | 输出质量检查，最多重试 3 次，不合格打回润色 | 被 core.py 依赖 |
| `logger.py` | 会话日志 + 统计，`--stats` 查看历史 | 被 core.py 依赖 |
| `webui.py` | Gradio 网页前端，聊天界面 + 设置面板 | 同 main.py，加 gradio 依赖 |

## 数据流向图

```
用户输入 (main.py / webui.py)
    │
    ▼
[core.py] run_workflow()
    │
    ├─1. 记忆增强 (memory.py)          检测"刚才那个..."等上下文引用
    │
    ├─2. 分类器 (llm.py → classifier)  判断要不要搜索
    │       │
    │       ├─ 需要搜索 → search.py     Google 搜索
    │       └─ 不需要   → 跳过
    │
    ├─3. 解析器 (llm.py → parser)      把输入拆成 JSON:
    │    {聊天:"...", 代码:"...", 逻辑:"..."}
    │
    ├─4. 并行处理
    │   ├─ 聊天 (llm.py → chat)        Gemini (可换)
    │   ├─ 代码 (llm.py → code)        Claude (可换)
    │   └─ 逻辑 (llm.py → logic)       GPT-4  (可换)
    │
    ├─5. 变量聚合                       三个结果拼成 JSON
    │
    ├─6. 润色 (llm.py → polish)         JSON → 自然语言
    │
    └─7. 质检 (quality.py)              不通过 → 带反馈打回步骤6重试
                最多3次
    │
    ▼
  最终输出
```

## config.json 的两种模式

### 简单模式（推荐，只填 3 项）
```json
{
    "LLM_PROVIDER": "openai",
    "LLM_API_KEY": "sk-...",
    "LLM_BASE_URL": ""
}
```
选了供应商后，系统自动从 `provider_presets.py` 给 7 个节点配好模型。

### 高级模式（手动控制每个节点用什么模型）
```json
{
    "PROVIDERS": {
        "google": {"api_key": "...", "base_url": "..."},
        "openai": {"api_key": "...", "base_url": "..."}
    },
    "MODELS": {
        "classifier": {"provider": "google", "model": "gemini-2.5-flash"},
        "code":      {"provider": "openai", "model": "gpt-4"}
    }
}
```

### 两种模式自动识别
`config.py` 启动时检查：有 `LLM_PROVIDER` → 走简单模式；否则走高级模式。可以随时切换，互不冲突。
