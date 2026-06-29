# Kagurazaka-Core Roadmap

从聊天机器人到 Agent 框架——10 步落差补齐计划。

## 现状：已经做到的事

1. L1/L2 预过滤（零成本拦截废话）← 大部分框架没这个
2. Search Judge + 搜索质量检查 + 缓存
3. Task Router 按复杂度分流（simple/complex）
4. chat/code/logic 三维度任务拆解
5. 质量检查循环（最多 3 轮打回重来）
6. 人格注入（神楽坂/自定义）← 独特卖点
7. LLM 输出清洗（think 标签、元分析自言自语）
8. 9 个供应商预设 + 每节点独立配模型
9. 会话记忆 + 搜索缓存 + 长期记忆持久化

## 竞品对照

| 框架 | 工具调用 | 流式 | MCP | 代码执行 | 你有它没有的 |
|------|----------|------|-----|----------|-------------|
| LangChain/Graph | 有 | 有 | 有 | 有 | L1/L2预过滤、人格注入 |
| AutoGen | 有 | 有 | 无 | 有 | 搜索质量检查 |
| CrewAI | 有 | 有 | 无 | 有 | 输出清洗 |
| Dify | 有 | 有 | 有 | 无 | per-node模型配置 |
| OpenAI Agents SDK | 有 | 有 | 有 | 有 | 离线兜底 |
| **Kagurazaka-Core** | **无** | **无** | **无** | **无** | **全都有↑** |

结论：独特功能别人没有，基础设施别人都有你没有。补上基础设施 + 保留独特功能 = 市面上没有的东西。

## 优先级 1：做了就质变

### 01 — 工具调用 (Function Calling)

**现状**：用户说话 → LLM 回话。不能读文件、不能调 API、不能操作任何外部系统。本质是高级聊天机器人。

**目标**：LLM 能调用预定义工具函数，从「只能说」变成「能干活」。

**方案**：
- 新建 `tools.py`，工具注册表 + JSON Schema 参数定义
- 修改 `llm.py`，为每个 provider 适配 function calling 格式
- 在 Task Router 后加工具调用循环：LLM 决定调工具 → 执行 → 结果塞回对话 → 继续

**内置工具**：`search_web` / `read_file` / `write_file` / `get_datetime` / `http_get`

**预计**：2-3 天

### 02 — 异步并行

**现状**：chat/code/logic 三个任务串行跑，3+3+3=9 秒。

**目标**：三个任务无依赖，`asyncio.gather` 同时跑，9 秒变 3 秒。

**方案**：
- `requests.post` → `aiohttp`（异步非阻塞）
- `_run_simple_workflow` 中 chat/code/logic 并行
- 保留同步兼容层

**预计**：1 天

## 优先级 2：做了体验飞升

### 03 — 搜索改进

- 修 Windows GBK 编码 bug（emoji 搜索结果崩溃）
- 搜索结果加全文抓取（requests + BeautifulSoup）
- 相关性评分 + Jaccard 去重
- 时效性标注 + 文件缓存持久化（30 分钟过期）

**预计**：1-2 天

### 04 — 结构化输出 (JSON Schema 校验)

- `json_repair` 自动修复格式错误
- 每个 JSON 输出节点定义 schema
- 校验失败自动重试（最多 2 次，带错误信息反馈给 LLM）

**预计**：半天

### 05 — 错误恢复与容错

- 指数退避重试（1s/2s/4s，最多 3 次）
- Fallback 模型：主模型挂了自动切备用
- 优雅降级：每个节点失败有独立兜底策略
- 兜底流程：Search Judge 失败→不搜索 / Router 失败→simple / 全挂→"Kagurazaka 暂时不在线"

**预计**：半天

## 优先级 3：做了才像专业框架

### 06 — 上下文窗口管理

- tiktoken 精确 token 计数
- 预算分配：system prompt → 搜索结果 → 历史记录，超了就裁
- 可进阶：长对话 LLM 摘要压缩

**预计**：1-2 天

### 07 — 流式输出 (Streaming)

- LLM 调用改 SSE 流式，首 token 延迟从 10s 降到 1s
- 中间节点继续非流式（需要完整 JSON），最终输出节点流式
- 流式中过滤 DeepSeek `<think>` 标签

**预计**：1 天

### 08 — MCP 协议支持

- Client 端：连接 MCP Server，获取工具列表，转成 function calling 格式
- Server 端：把 Kagurazaka-Core 的能力暴露给其他框架
- 现成可接：filesystem / github / brave-search MCP Server

**依赖**：需先完成 01 工具调用

**预计**：2-3 天

## 优先级 4：锦上添花

### 09 — 代码执行沙箱

- 方案 A：subprocess + tempfile + timeout 30s（简单，推荐先做）
- 方案 B：Docker 完全隔离（安全，依赖重）
- 注册为 `run_python` 工具 → LLM 写代码 → 执行 → 报错 → 自动修正循环

**预计**：1-2 天

### 10 — 可观测性 (Tracing)

- 每个请求分配 trace_id，全链路追踪
- Token 用量 + 费用统计（按各 provider 定价实时算）
- debug 模式下打印 trace summary 面板

**预计**：半天

---

**暂不做**：Web UI / 可视化工作流编辑器（前端短期来不了）

**总预计工时**：约 10-15 天（全部优先级 1-4）
