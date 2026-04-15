Kagurazaka-Core
Kagurazaka-Core is a logic processing framework driven by task deconstruction and multi-model cascading. The system dismantles complex instructions into specialized dimensions—Code, Logic, and Chat—routing them to dedicated sub-engines for execution, followed by an automated audit and polishing layer before final output.

Key Features
Multi-Dimensional Deconstruction
The core "Parser" node transforms ambiguous user input into structured instruction sets, acting as the primary filter for all incoming data.

Cascaded Remediation Mechanism

Code (码码): Powered by Claude-3.5-Sonnet for high-intensity programming and algorithmic tasks.

Logic (来硬的): Driven by GPT-4 for rigorous reasoning and complex instruction following.

Chat (聊天): Utilizes Gemini for rapid interaction and stable JSON formatting.

Automated Auditing
A final "Polish" node performs compliance checks, tone adjustment, and multi-language cleanup, with specific handling for Japanese/English mixing.

Search Integration
Pre-emptive intent classification determines if real-time web data via SerpAPI is required before the main logic triggers.

System Architecture
The workflow follows a robust, linear pipeline designed for maximum stability:

Intent Classification (Node 1.1)
Identifies if the query requires real-time web access or specific search intervention.

Parser Logic (Node 1.2)
The "Brain" of the system. It performs task decomposition and logic modeling, outputting a structured JSON that defines the path for subsequent nodes.

Remediation Layer (Nodes 1.3 - 1.5)
Serial dispatching to specialized models (Chat, Code, or Hard Logic) based on the parsed fields from the previous step.

Polish & Audit (Node 1.6)
Final natural language refinement, artifact cleaning, and a safety fallback check.

Setup & Deployment
Prerequisites
Python 3.8+

SerpAPI Key (Optional, for search integration)

Dify Workflow API Keys for each specialized node.

Installation
Bash
pip install requests
Usage
Configure your API keys and base URLs in the CONFIG dictionary within 1の码码.py.

Execute the orchestrator:

Bash
python "1の码码.py"
Design Philosophy
Rationality First
The system prioritizes the granularity of logic deconstruction over emotional engagement. It is built to analyze, not just to react.

Defensive Output
Stability is paramount. If the audit node detects an unrecoverable logical deviation or formatting error, the system defaults to a safe-stop response: "Kagurazaka不知道哦" (Kagurazaka doesn't know).

"The world is a deconstructible system; optimal solutions reside at the intersection of the most direct path and the most efficient laziness."

Kagurazaka-Core
Kagurazaka-Core 是一款基于任务解构与多模型级联（Cascading）驱动的逻辑处理框架。该系统通过将复杂的指令拆解为代码、逻辑推理与常规对话三个专项维度，分发至对应的子引擎执行补救，最后通过自动化审计与润色层输出结果。

核心特性
多维逻辑解构
核心“分类逻辑”节点负责将模糊的用户输入转化为结构化的指令集。它是所有信息进入系统后的首要过滤器。

级联补救机制

码码 (Code)：由 Claude-3.5-Sonnet 驱动，专门处理高强度的编程、算法及技术调试任务。

来硬的 (Logic)：由 GPT-4 驱动，应对严密的逻辑推导、数学计算或复杂的长指令遵循。

聊天 (Chat)：基于 Gemini 构建，负责快速交互处理及确保 JSON 格式的稳定性。

自动化审计与润色
最终输出由“润色”节点把关，负责文案修饰、乱码清洗（特别是中英日混合环境的处理）以及最终的合规审计。

外部检索集成
系统在进入主逻辑前，会前置判断是否需要通过 SerpAPI 获取实时搜索数据作为背景补充。

系统架构
系统遵循一套稳固的线性流水线设计，以确保处理过程的可追溯性：

检索意图识别 (Node 1.1)
识别输入是否包含实时性需求，决定是否介入外部搜索。

分类建模 (Node 1.2)
系统“大脑”所在。执行任务拆解，输出定义后续路径的结构化 JSON。

补救执行层 (Nodes 1.3 - 1.5)
根据 1.2 节点的拆解结果，将任务分发给专项模型（聊天、码码、或来硬的）。

润色与终审 (Node 1.6)
执行自然语言优化，剔除处理过程中的冗余信息，并进行最后的逻辑合规检查。

部署与运行
环境要求
Python 3.8+

SerpAPI Key（可选，用于搜索集成）

Dify Workflow API Keys（对应各专项节点）

依赖安装
Bash
pip install requests
快速开始
在 1の码码.py 的 CONFIG 字典中配置各节点的 API Key 与 Base URL。

启动调度脚本：

Bash
python "1の码码.py"
设计哲学
理性至上
系统设计优先考虑任务拆解的粒度，而非情绪化的反馈。它被构建用于“分析”，而非简单的“反应”。

防御性输出
稳定性是系统的首要目标。若审计节点检测到不可修复的逻辑偏差或格式错误，系统将触发安全停机回执：“Kagurazaka不知道哦”。

“世界是一套可以拆解的系统；最优解往往藏在最直接的路径与最高效的‘偷懒’之间。”
