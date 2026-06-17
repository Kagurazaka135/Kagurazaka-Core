# Kagurazaka Core

A pure-Python multi-model task orchestration framework.  
User input → search decision → routing (chat/code/logic) → LLM execution → aggregation & polish → quality check.

## Quick Start

```bash
pip install -r requirements.txt
cp config.example.json config.json
# Edit config.json with your LLM provider and API key
python main.py
```

## Configuration

### Simple Mode (Recommended)

```json
{
    "LLM_PROVIDER": "openai",
    "LLM_API_KEY": "sk-...",
    "LLM_BASE_URL": ""
}
```

Once a provider is selected, the system automatically assigns models to all nodes from `provider_presets.py`.

Supported providers: `openai` / `google` / `anthropic` / `deepseek` / `zhipu` / `qwen` / `moonshot` / `siliconflow` / `custom`

### Advanced Mode

Manually control which model each node uses. See `docs/config.md`.

## CLI Usage

```bash
python main.py              # Interactive mode
python main.py --stats      # Session log statistics
python main.py --providers  # List available providers
```

## Architecture

```
User Input
  │
  ├─ L1 Whitelist (trivial reject, zero-cost)
  ├─ L2 Regex (strong signal match, zero-cost)
  ├─ Search Judge (LLM) → {search_needed, search_query}
  ├─ Search + Cache (30min TTL, fuzzy match)
  ├─ Task Router (LLM) → simple or complex
  │
  ├─ simple: chat/code/logic → polish → quality_check
  └─ complex: steps[] → aggregate → reviewer loop (≤3 rounds)
```

See `docs/README.md` for detailed architecture.

## File Responsibilities

| File | Responsibility |
|------|---------------|
| `main.py` | CLI entry point |
| `core.py` | Workflow orchestration |
| `llm.py` | Unified LLM client (OpenAI/Google/Anthropic) |
| `prompts.py` | All system prompts |
| `config.py` | Configuration (simple/advanced mode) |
| `provider_presets.py` | 9 provider presets |
| `memory.py` | Session memory + search cache |
| `search.py` | SerpAPI search |
| `quality.py` | Quality check for simple path |
| `logger.py` | Session logging + statistics |

---

# Kagurazaka Core

纯 Python 多模型任务编排框架 —— 用户输入 → 判断要不要搜索 → 拆成聊天/代码/逻辑三类 → 分别交给 LLM → 聚合润色 → 质检打回。

## 快速开始

```bash
pip install -r requirements.txt
cp config.example.json config.json
# 编辑 config.json，填你的 LLM provider 和 API key
python main.py
```

## 配置

### 简单模式（推荐）

```json
{
    "LLM_PROVIDER": "openai",
    "LLM_API_KEY": "sk-...",
    "LLM_BASE_URL": ""
}
```

选了供应商后，系统自动从 `provider_presets.py` 给所有节点配模型。

支持 9 个供应商：`openai` / `google` / `anthropic` / `deepseek` / `zhipu` / `qwen` / `moonshot` / `siliconflow` / `custom`

### 高级模式

手动控制每个节点用什么模型，详见 `docs/config.md`。

## CLI 用法

```bash
python main.py              # 交互模式
python main.py --stats      # 历史日志统计
python main.py --providers  # 查看可选供应商
```

## 架构

```
用户输入
  │
  ├─ L1 白名单（废话拦截器，零成本）
  ├─ L2 正则（强信号匹配，零成本）
  ├─ Search Judge (LLM) → {search_needed, search_query}
  ├─ 搜索 + 缓存（30min TTL，模糊匹配）
  ├─ Task Router (LLM) → simple 或 complex
  │
  ├─ simple: chat/code/logic → polish → quality_check
  └─ complex: 按 steps[] 执行 → aggregate → reviewer 循环（≤3轮）
```

详细架构见 `docs/README.md`。

## 文件职责

| 文件 | 职责 |
|------|------|
| `main.py` | CLI 入口 |
| `core.py` | 工作流编排 |
| `llm.py` | 统一 LLM 客户端（OpenAI/Google/Anthropic 协议） |
| `prompts.py` | 全部 system prompt |
| `config.py` | 配置管理（简单/高级模式） |
| `provider_presets.py` | 9 个供应商预设 |
| `memory.py` | 会话记忆 + 搜索缓存 |
| `search.py` | SerpAPI 搜索 |
| `quality.py` | simple 路径质检 |
| `logger.py` | 会话日志 + 统计 |

## License

MIT
