# Kagurazaka Core

A pure-Python multi-model orchestration framework — user input → search intent → tool calling → task routing → dual-path execution → persona injection → output.

---

## 简介

纯 Python 多模型任务编排框架 —— 用户输入 → 搜索意图判断 → 工具调用 → 任务路由 → 简单/复杂双路径 → 人格注入 → 输出。

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

### 可选功能

| 功能 | 配置项 | 说明 |
|------|--------|------|
| 联网搜索 | `SERPAPI_KEY` | SerpAPI key，不填则跳过搜索 |
| 人格注入 | `PERSONA_MODE` | `none` / `kagurazaka` / `custom` |
| 模型覆盖 | `MODEL_OVERRIDES` | 覆盖单个节点的模型名 |

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
  ├─ Search Judge (LLM) → 搜索意图判断 + 搜索词生成
  ├─ 搜索 + 缓存（30min TTL，模糊匹配）+ 质量检查 + 换词重搜
  ├─ 工具调用循环（≤5 轮）：search_web / read_file / write_file / get_datetime / http_get
  │     └─ 有最终答案 → 跳过 Task Router，直接人格注入
  ├─ Task Router (LLM) → simple 或 complex
  │
  ├─ simple: chat / code / logic → polish → quality_check（≤3 轮）
  └─ complex: 按 steps[] 多步执行 → aggregator → reviewer 循环（≤3 轮）
  │
  └─ 人格注入（可选）→ 最终输出
```

详细架构见 `docs/README.md`。

## 14 个 LLM 节点

| 节点 | 职责 | 轻/重 |
|------|------|-------|
| `search_judge` | 判断要不要搜索、生成搜索词 | 轻 |
| `search_quality_check` | 评估搜索结果质量 | 轻 |
| `task_router` | 判断复杂度 + 拆解任务 | 重 |
| `chat` | 聊天回复 | 轻 |
| `code` | 代码生成 | 重 |
| `logic` | 逻辑推理 | 重 |
| `polish` | 聚合结果润色为自然语言 | 轻 |
| `quality_check` | 输出质量审核 | 轻 |
| `planner` | 复杂路径拆步骤 | 重 |
| `reviewer` | 复杂路径评审 | 轻 |
| `aggregator` | 多步骤结果整合 | 轻 |
| `persona_kagurazaka` | 神楽坂人格注入 | 轻 |
| `persona_custom` | 自定义人格注入 | 轻 |
| `classifier` / `parser` | 旧版兼容（不再使用） | - |

## 文件职责

| 文件 | 职责 |
|------|------|
| `main.py` | CLI 入口 |
| `core.py` | 工作流编排 |
| `llm.py` | 统一 LLM 客户端（OpenAI/Google/Anthropic 协议 + JSON 提取 + 输出清理） |
| `prompts.py` | 全部 system prompt |
| `config.py` | 配置管理（简单/高级模式） |
| `provider_presets.py` | 9 个供应商预设 |
| `memory.py` | 会话记忆 + 搜索缓存 |
| `search.py` | SerpAPI 搜索（Google + Bing fallback） |
| `quality.py` | simple 路径质检 |
| `logger.py` | 会话日志 + 统计 |
| `tools.py` | Function Calling 工具注册表（5 个内置工具） |
| `fallback.py` | 指数退避重试 + Fallback 模型切换 + 优雅降级 |

## License

MIT
