# Kagurazaka Core

A pure-Python multi-model orchestration framework. Pick a provider, fill in an API key, and you're running — the system routes every task to the right model automatically.

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

First run generates `config.json`. Edit it, fill in your provider and API key, run again.

### Simplest config (3 lines)

```json
{
    "LLM_PROVIDER": "deepseek",
    "LLM_API_KEY": "sk-xxxxxxxx"
}
```

That's it. All 15 internal nodes are auto-configured. See `docs/config.md` for advanced per-node control.

### Supported providers

`openai` / `google` / `anthropic` / `deepseek` / `zhipu` / `qwen` / `moonshot` / `siliconflow` / `custom`

```bash
python main.py --providers   # list all with model previews
```

---

## What it does

```
Your input
  → Memory enhancement ("that thing from earlier..." → finds context)
  → L1 whitelist (chitchat like "thanks"/"ok" → skip search, zero cost)
  → L2 regex (strong signals like "today's weather" → skip Search Judge)
  → Search Judge (LLM): should we search? what query?
  → Search + cache (30min TTL) + quality check + auto re-search
  → Tool calling loop (≤5 rounds): search_web / read_file / write_file / get_datetime / http_get
  → Task Router (LLM): simple or complex?
      ├─ simple: chat/code/logic → polish → quality_check (≤3 retries)
      └─ complex: execute steps[] → aggregator → reviewer loop (≤3 retries)
  → Persona injection (optional: kagurazaka / custom / none)
  → Output
```

## Architecture

| Layer | What | Why |
|---|---|---|
| L1 + L2 filters | Pure Python string/regex matching | ~50% of inputs caught with zero LLM cost |
| Search Judge | 1 cheap LLM call | Only fires when L1/L2 miss |
| Search + cache | SerpAPI (Google → Bing fallback), 30min TTL | Avoid redundant API calls |
| Tool calling | 5 built-in tools, ≤5 rounds | LLM can search, read/write files, fetch HTTP |
| Task Router | 1 LLM call → simple or complex path | Simple questions go fast; complex tasks get structured execution |
| Dual path | simple: generate → polish → QC; complex: multi-step → aggregate → review | Right tool for the job |
| Persona injection | Optional post-processing pass | Character consistency without slowing the main pipeline |

## 15 LLM Nodes

| Node | Role | Weight |
|---|---|---|
| `classifier` | Search intent classification | light |
| `parser` | Input parsing (legacy, unused) | light |
| `search_judge` | Search intent + query generation | light |
| `search_quality_check` | Search result quality assessment | light |
| `task_router` | Complexity judgment + task decomposition | heavy |
| `chat` | Conversational response | light |
| `code` | Code generation | heavy |
| `logic` | Logical reasoning | heavy |
| `polish` | Output polishing / natural language conversion | light |
| `quality_check` | Output quality review (simple path) | light |
| `planner` | Step planning (complex path) | heavy |
| `reviewer` | Output review (complex path) | light |
| `aggregator` | Multi-step result aggregation | light |
| `persona_kagurazaka` | Kagurazaka persona injection | light |
| `persona_custom` | Custom persona injection | light |

## File Map

| File | Does what |
|---|---|
| `main.py` | CLI entry point — the front door |
| `core.py` | Workflow brain — the entire pipeline |
| `config.py` | Config loader — simple mode (3 lines) or advanced (per-node) |
| `provider_presets.py` | 9 provider presets with model assignments |
| `llm.py` | Unified LLM client — 3 API protocols + JSON extraction + output cleanup |
| `prompts.py` | All system prompts — change behavior without touching code |
| `memory.py` | Session memory + search cache + long-term storage |
| `search.py` | Web search via SerpAPI (Google + Bing fallback) |
| `quality.py` | Output quality gate (simple path, ≤3 retries) |
| `tools.py` | Function calling — 5 built-in tools, extensible |
| `fallback.py` | Retry + model failover + graceful degradation |
| `logger.py` | Per-call logging + session stats |
| `_path.py` | Working directory resolution (PyInstaller-safe) |

## CLI

```bash
python main.py              # interactive mode
python main.py --stats      # historical call statistics
python main.py --providers  # list supported providers
```

## Docs

Every module has its own doc in `docs/`:
- [core](docs/core.md) — the brain
- [llm](docs/llm.md) — the phone line to every LLM
- [config](docs/config.md) — simple vs advanced mode
- [provider_presets](docs/provider_presets.md) — provider menu
- [memory](docs/memory.md) — how the system remembers
- [search](docs/search.md) — web search with cache
- [quality](docs/quality.md) — the quality inspector
- [tools](docs/tools.md) — how LLMs use tools
- [fallback](docs/fallback.md) — when things go wrong
- [logger](docs/logger.md) — the ledger
- [prompts](docs/prompts.md) — the script library
- [main](docs/main.md) — the front door
- [_path](docs/_path.md) — finding home

## License

MIT

---

# Kagurazaka Core（中文）

纯 Python 多模型任务编排框架。选一个供应商、填一个 API key 就能跑——系统自动把不同任务路由到合适的模型。

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

首次运行生成 `config.json`。编辑它，填好供应商和 API key，再运行。

### 最简配置（3 行）

```json
{
    "LLM_PROVIDER": "deepseek",
    "LLM_API_KEY": "sk-xxxxxxxx"
}
```

完事。15 个内部节点全部自动配好。高级手动控制见 `docs/config.md`。

### 支持的供应商

`openai` / `google` / `anthropic` / `deepseek` / `zhipu` / `qwen` / `moonshot` / `siliconflow` / `custom`

```bash
python main.py --providers   # 列出所有供应商及模型预览
```

## 做了什么

```
你的输入
  → 记忆增强（"刚才那个..."→ 捞出上文拼进去）
  → L1 白名单（"谢谢""好的"→ 零成本跳过搜索）
  → L2 正则（"今天天气""最新新闻"→ 跳过 Search Judge）
  → Search Judge：要不要搜？搜什么？
  → 搜索 + 缓存（30分钟有效）+ 质量检查 + 不行就换词重搜
  → 工具调用循环（最多5轮）：搜索/读文件/写文件/查时间/HTTP请求
  → Task Router：简单还是复杂？
      ├─ 简单：chat/code/logic → 润色 → 质检（最多打回3次）
      └─ 复杂：按计划分步执行 → 整合 → 审查循环（最多3轮）
  → 人格注入（可选：kagurazaka / custom / 不注入）
  → 输出
```

## 架构设计

| 层 | 用什么 | 为什么 |
|---|---|---|
| L1 + L2 过滤 | 纯 Python 字符串/正则匹配 | 约一半输入在这层拦截，零 LLM 成本 |
| Search Judge | 1 次便宜 LLM 调用 | 只有 L1/L2 都 miss 才触发 |
| 搜索 + 缓存 | SerpAPI（Google → Bing），30min TTL | 避免重复调 API |
| 工具调用 | 5 个内置工具，最多 5 轮 | LLM 能搜网页、读写文件、发 HTTP 请求 |
| Task Router | 1 次 LLM 调用 → 简单或复杂路径 | 简单问题快速通道，复杂任务结构化执行 |
| 双路径 | 简单：生成→润色→质检；复杂：多步→聚合→审查 | 不同任务用不同策略 |
| 人格注入 | 可选后处理 | 角色一致性，不影响主流程速度 |

## 15 个 LLM 节点

| 节点 | 职责 | 轻/重 |
|---|---|---|
| `classifier` | 搜索意图分类 | 轻 |
| `parser` | 输入解析（旧版，不再使用） | 轻 |
| `search_judge` | 搜索意图判断 + 搜索词生成 | 轻 |
| `search_quality_check` | 搜索结果质量评估 | 轻 |
| `task_router` | 复杂度判断 + 任务拆解 | 重 |
| `chat` | 聊天回复 | 轻 |
| `code` | 代码生成 | 重 |
| `logic` | 逻辑推理 | 重 |
| `polish` | 结果润色为自然语言 | 轻 |
| `quality_check` | 简单路径输出质检 | 轻 |
| `planner` | 复杂路径步骤规划 | 重 |
| `reviewer` | 复杂路径结果审查 | 轻 |
| `aggregator` | 多步骤结果整合 | 轻 |
| `persona_kagurazaka` | 神楽坂人格注入 | 轻 |
| `persona_custom` | 自定义人格注入 | 轻 |

## 文件地图

| 文件 | 干啥的 |
|---|---|
| `main.py` | 门面——启动、收输入、打印结果、关机收尾 |
| `core.py` | 大脑——整个工作流管线 |
| `config.py` | 配置中心——简单模式 3 行搞定，或高级逐节点控制 |
| `provider_presets.py` | 供应商菜单——9 个预设，模型分配全在这 |
| `llm.py` | 打电话的人——3 种 API 协议 + JSON 提取 + 输出清理 |
| `prompts.py` | 剧本库——所有 system prompt，改行为不用动代码 |
| `memory.py` | 记性——会话记忆 + 搜索缓存 + 长期存储 |
| `search.py` | 上网搜——SerpAPI（Google + Bing 备用） |
| `quality.py` | 质检员——简单路径最后一道关，最多打回 3 次 |
| `tools.py` | 工具箱——5 个内置工具，可扩展 |
| `fallback.py` | 救火队——重试 + 换模型 + 优雅降级 |
| `logger.py` | 账本——每次调用记账，退出算总账 |
| `_path.py` | 找家——不管从哪启动都能找到项目目录 |

## CLI

```bash
python main.py              # 交互模式
python main.py --stats      # 看历史调用统计
python main.py --providers  # 看支持哪些供应商
```

## 模块文档

每个模块都有独立文档在 `docs/`：
- [core](docs/core.md) — 大脑
- [llm](docs/llm.md) — 打给所有 LLM 的电话线
- [config](docs/config.md) — 简单 vs 高级模式
- [provider_presets](docs/provider_presets.md) — 供应商菜单
- [memory](docs/memory.md) — 系统怎么记东西
- [search](docs/search.md) — 带缓存的网页搜索
- [quality](docs/quality.md) — 质检员
- [tools](docs/tools.md) — LLM 怎么用工具
- [fallback](docs/fallback.md) — 出问题的时候
- [logger](docs/logger.md) — 账本
- [prompts](docs/prompts.md) — 剧本库
- [main](docs/main.md) — 门面
- [_path](docs/_path.md) — 找家

## License

MIT
