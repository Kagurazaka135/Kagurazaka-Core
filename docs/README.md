# Kagurazaka Core — 纯 Python 版架构详解

## 一句话总结

用户输入 → L1+L2 搜索信号检测 → Search Judge (LLM) → 搜索+缓存+质检 → 工具调用循环 → Task Router → simple/complex 双路径 → 人格注入 → 输出

## 文件职责速查

| 文件 | 一句话 | 被谁依赖 |
|---|---|---|
| `main.py` | CLI 入口，交互循环 | 依赖所有 |
| `core.py` | 工作流编排大管家 | 依赖 llm/memory/search/quality/logger/tools |
| `config.py` | 读 config.json，简单/高级双模式 | 被几乎所有文件依赖 |
| `provider_presets.py` | 9 个供应商的模型映射表 | 被 config.py 依赖 |
| `llm.py` | 统一 LLM 客户端，三协议+JSON提取+输出清理 | 被 core.py/quality.py 依赖 |
| `prompts.py` | 全 14 个节点的 system prompt | 被 llm.py 依赖 |
| `memory.py` | 会话记忆：上下文追踪+话题关联+搜索缓存+长期记忆 | 被 core.py 依赖 |
| `search.py` | SerpAPI 搜索（Google+Bing fallback） | 被 core.py 依赖 |
| `quality.py` | simple 路径质检，≤3 轮打回 | 被 core.py 依赖 |
| `tools.py` | Function Calling 工具注册表，5 个内置工具 | 被 core.py/llm.py 依赖 |
| `logger.py` | 会话日志+统计，`--stats` 查看 | 被 core.py/llm.py 依赖 |
| `fallback.py` | 指数退避重试+模型切换+优雅降级 | 各级调用方 |
| `_path.py` | PyInstaller 打包兼容，工作目录定位 | 被 main.py 依赖 |

## 数据流向图

```
用户输入 (main.py)
    │
    ▼
[core.py] run_workflow()
    │
    ├─ 记忆增强 (memory.py)           "刚才那个..." → 捞出上文
    │
    ├─ L1 白名单                      20+ 闲聊短语，命中跳过搜索
    │
    ├─ L2 正则                        5 组正则，命中跳过 Search Judge
    │
    ├─ Search Judge (llm.py)          判断要不要搜索 + 生成搜索词
    │       │
    │       ├─ 需要 → search.py       Google → 缓存 → 质量检查 → 换词重搜
    │       └─ 不需要 → 跳过
    │
    ├─ 工具调用循环 (tools.py)         ≤5 轮：search_web/read_file/write_file/
    │       │                          get_datetime/http_get
    │       ├─ 有最终答案 → 跳过 Task Router
    │       └─ 无最终答案 → 继续
    │
    ├─ Task Router (llm.py)           判断 simple/complex
    │       │
    │       ├─ simple → chat/code/logic → polish → quality_check (≤3轮)
    │       │
    │       └─ complex → 按 steps[] 执行 → aggregator → reviewer (≤3轮)
    │
    ├─ 人格注入 (llm.py)              可选：kagurazaka / custom
    │
    └─ 记忆保存 (memory.py)           写入会话历史+长期记忆
    │
    ▼
  最终输出
```

## 双路径设计

| | simple | complex |
|---|---|---|
| 触发条件 | Task Router 判定简单 | Task Router 判定需要多步 |
| 执行方式 | 单 chat/code/logic + polish + QC | 多步按 steps[] 顺序执行 |
| 聚合 | polish 直接润色 JSON | aggregator 整合多步结果 |
| 评审 | 无（由 QC 替代） | reviewer ≤3 轮，不通过追加 missing_steps |
| 适用 | 日常对话、短回答、简单代码 | 长报告、多步推理、跨领域任务 |

## 为什么 L1+L2 不用 LLM

50%+ 搜索意图可由正则/关键词识别。LLM 调用有 500ms-3s 延迟，L1+L2 为零成本拦截。
L1 白名单处理"谢谢""好的""再见"等纯闲聊，L2 正则处理"今天天气""最新新闻"等强搜索信号。

## config.json 两种模式

### 简单模式（推荐，只填 3 项）
```json
{
    "LLM_PROVIDER": "openai",
    "LLM_API_KEY": "sk-...",
    "LLM_BASE_URL": ""
}
```
选了供应商后自动从 `provider_presets.py` 配好所有节点。

### 高级模式（手动控制每个节点）
```json
{
    "PROVIDERS": {
        "google": {"api_key": "...", "base_url": "..."},
        "anthropic": {"api_key": "...", "base_url": "..."}
    },
    "MODELS": {
        "chat": {"provider": "google", "model": "gemini-2.5-flash"},
        "code": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"}
    }
}
```

两种模式自动识别：有 `LLM_PROVIDER` → 简单模式；否则 → 高级模式。
