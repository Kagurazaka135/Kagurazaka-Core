import requests
import json
import os
import time
import math
import pickle
import re
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import deque, defaultdict
import hashlib

# ==========================================
# 1. 配置中心 
# ==========================================
CONFIG = {
    # SerpAPI 配置 (用于 Google 搜索)
    "SERPAPI_KEY": "YOUR_SERPAPI_KEY",
    
    # 记忆系统配置
    "MEMORY": {
        "WORKING_CAPACITY": 7,
        "SESSION_CAPACITY": 10,
        "SAVE_PATH": "./memory_store/"
    },

    # Dify 节点配置 (每个节点对应独立的 Dify Workflow 应用)
    "NODES": {
        "CLASSIFIER": { # 问题分类器
            "API_KEY": "app-xxxx",
            "BASE_URL": "https://api.dify.ai"
        },
        "LLM_PARSER": { # 分类逻辑 
            "API_KEY": "app-xxxx",
            "BASE_URL": "https://api.dify.ai"
        },
        "LLM_CHAT": { # 聊天
            "API_KEY": "app-xxxx",
            "BASE_URL": "https://api.dify.ai"
        },
        "LLM_CODE": { # 码码
            "API_KEY": "app-xxxx",
            "BASE_URL": "https://api.dify.ai"
        },
        "LLM_LOGIC": { # 来硬的 (逻辑)
            "API_KEY": "app-xxxx",
            "BASE_URL": "https://api.dify.ai"
        },
        "LLM_POLISH": { # 润色
            "API_KEY": "app-xxxx",
            "BASE_URL": "https://api.dify.ai"
        }
    },
    "OPENAI": {
        "API_KEY": "sk-xxxx",
        "BASE_URL": "https://api.openai.com",
        "MODEL": "gpt-4.1-mini"
    }
    }

# ==========================================
# 2. 轻量级记忆系统
# ==========================================

class SimpleMemorySystem:
    """轻量级记忆系统，最小化对原有逻辑的影响"""
    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        
        # 工作记忆：保存当前会话的关键信息
        self.working_memory = deque(maxlen=CONFIG["MEMORY"]["WORKING_CAPACITY"])
        
        # 会话历史：保存最近的对话
        self.session_history = deque(maxlen=CONFIG["MEMORY"]["SESSION_CAPACITY"])
        
        # 任务上下文：用于多步骤任务
        self.task_context = {
            'active': False,
            'type': None,
            'steps': []
        }
        
        # 长期记忆存储路径
        self.save_path = os.path.join(CONFIG["MEMORY"]["SAVE_PATH"], user_id)
        os.makedirs(self.save_path, exist_ok=True)
        
        # 加载历史记忆
        self.long_term_memory = self._load_memory()
        
    def _load_memory(self) -> Dict:
        """加载持久化的记忆"""
        memory_file = os.path.join(self.save_path, 'memory.json')
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {'chat': [], 'code': [], 'logic': []}
        
    def _save_memory(self):
        """保存记忆到文件"""
        memory_file = os.path.join(self.save_path, 'memory.json')
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.long_term_memory, f, ensure_ascii=False, indent=2)
            
    def detect_references(self, text: str) -> bool:
        """检测是否有引用之前的内容"""
        reference_patterns = [
            r'刚才|刚刚|上面|之前|前面',
            r'这个|那个|它|这些|那些',
            r'基于.*的|根据.*的|继续'
        ]
        return any(re.search(pattern, text) for pattern in reference_patterns)
        
    def enhance_input(self, user_input: str) -> str:
        """增强输入，添加必要的上下文"""
        # 如果检测到引用，添加相关上下文
        if self.detect_references(user_input):
            context_parts = []
            
            # 添加最近的会话历史
            if self.session_history:
                recent = list(self.session_history)[-3:]  # 最近3轮
                for item in recent:
                    context_parts.append(f"[历史] 用户: {item['user']}\n助手: {item['assistant'][:100]}...")
                    
            # 如果在任务中，添加任务上下文
            if self.task_context['active']:
                context_parts.append(f"[当前任务] {self.task_context['type']}, 已完成 {len(self.task_context['steps'])} 步")
                
            if context_parts:
                return f"相关上下文:\n{chr(10).join(context_parts)}\n\n当前问题: {user_input}"
                
        return user_input
        
    def add_to_history(self, user_input: str, ai_output: str, task_type: str = None):
        """添加到会话历史"""
        entry = {
            'user': user_input,
            'assistant': ai_output,
            'timestamp': time.time(),
            'task_type': task_type
        }
        
        self.session_history.append(entry)
        
        # 如果输出较重要，保存到长期记忆
        if len(ai_output) > 200 or (task_type and task_type != 'chat'):
            self._add_to_long_term(user_input, ai_output, task_type)
            
    def _add_to_long_term(self, user_input: str, ai_output: str, task_type: str):
        """添加到长期记忆"""
        if task_type not in self.long_term_memory:
            self.long_term_memory[task_type] = []
            
        memory_item = {
            'input': user_input,
            'output': ai_output[:500],  # 只保存前500字符
            'timestamp': time.time()
        }
        
        self.long_term_memory[task_type].append(memory_item)
        
        # 限制每类记忆的数量
        max_items = {'chat': 50, 'code': 20, 'logic': 15}
        limit = max_items.get(task_type, 30)
        
        if len(self.long_term_memory[task_type]) > limit:
            # 保留最新的
            self.long_term_memory[task_type] = self.long_term_memory[task_type][-limit:]
            
        self._save_memory()
        
    def update_task_context(self, task_type: str, step_info: Any):
        """更新任务上下文"""
        if not self.task_context['active'] or self.task_context['type'] != task_type:
            self.task_context = {
                'active': True,
                'type': task_type,
                'steps': []
            }
        self.task_context['steps'].append(step_info)

# 全局记忆系统实例
memory_system = None

# ==========================================
# 3. 核心功能函数 
# ==========================================

def call_dify_workflow(node_key: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """通用 Dify Workflow API 调用函数"""
    node_cfg = CONFIG["NODES"].get(node_key)
    if not node_cfg:
        raise ValueError(f"Node {node_key} config not found.")

    url = f"{node_cfg['BASE_URL'].rstrip('/')}/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {node_cfg['API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": inputs,
        "response_mode": "blocking",
        "user": "script-runner"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        res_json = response.json()
        if "data" in res_json and "outputs" in res_json["data"]:
            return res_json["data"]["outputs"]
        else:
            print(f"警告: 节点 {node_key} 返回结构异常: {res_json}")
            return {}
    except Exception as e:
        print(f"错误: 调用 {node_key} 失败: {e}")
        return {}

def google_search(query: str) -> str:
    """使用 SerpAPI 实现 Google 搜索"""
    print(f"[*] 正在执行 Google 搜索: {query}")
    params = {
        "q": query,
        "api_key": CONFIG["SERPAPI_KEY"],
        "engine": "google",
        "hl": "zh-cn"
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=20)
        results = response.json()
        # 提取摘要信息
        snippets = []
        if "organic_results" in results:
            for res in results["organic_results"][:5]: # 取前5条
                snippets.append(res.get("snippet", ""))
        return "\n".join(snippets)
    except Exception as e:
        return f"搜索失败: {str(e)}"

def extract_json_field(raw_text: str, field_name: str) -> str:
    """对应工作流中的 code 节点逻辑: 从 JSON 文本中提取特定字段"""
    try:
        # 处理可能的 Markdown 代码块包裹
        clean_text = raw_text.strip().replace("```json", "").replace("```", "")
        data = json.loads(clean_text)
        return data.get(field_name, "未找到聊天字段")
    except:
        return "未找到聊天字段"

def quality_check_openai(text: str) -> Tuple[bool, str]:
    """直接调用 OpenAI API 进行输出质量检查，返回 (是否通过, 修改建议)"""
    cfg = CONFIG["OPENAI"]
    url = f"{cfg['BASE_URL'].rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg['API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": cfg["MODEL"],
        "temperature": 0.3,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一个专业的输出质量审核员。请严格检查以下文本是否满足所有质量要求。\n\n"
                    "质量检查标准：\n"
                    "1. 语言自然流畅，没有生硬的机翻感或AI口癖（如\"总的来说\"、\"综上所述\"等）\n"
                    "2. 不包含未翻译的英文代码、变量名、函数名或乱码（日语原文除外，♡等特殊符号除外）\n"
                    "3. 回答完整、逻辑通顺，没有明显的逻辑错误、事实错误或前后矛盾\n"
                    "4. 回答内容准确切题，没有编造虚假信息或答非所问\n"
                    "5. 格式清晰易读，没有多余的JSON结构残留\n\n"
                    "请严格按照以下JSON格式输出检查结果（只输出JSON，不要包含markdown代码块标记）：\n"
                    '{"pass":true,"feedback":""}\n\n'
                    "如果文本未通过检查（pass为false），feedback必须包含：\n"
                    "- 具体指出哪里有问题\n"
                    "- 明确说明应该如何修改\n\n"
                    "注意：\n"
                    "- pass为true时feedback必须为空字符串\"\"\n"
                    "- pass为false时feedback必须包含具体、可操作的修改建议\n"
                    "- 只输出JSON，不要输出任何其他内容"
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        body = response.json()
        raw = body["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = re.sub(r"```\w*\n?", "", raw).replace("```", "").strip()
        result = json.loads(raw)
        passed = result.get("pass", False)
        feedback = result.get("feedback", "")
        return passed, feedback
    except Exception as e:
        print(f"[!] 质检API调用或解析失败: {e}")
        return True, ""

# ==========================================
# 3. 线性执行逻辑 
# ==========================================

def run_workflow(user_input: str):
    global memory_system
    
    print(f"\n[开始处理] 用户输入: {user_input}")
    
    # 记忆增强：如果检测到引用，增强输入
    enhanced_input = user_input
    if memory_system:
        enhanced_input = memory_system.enhance_input(user_input)
        if enhanced_input != user_input:
            print("[*] 检测到上下文引用，已增强输入")

    # --- 步骤1: 问题分类器 (使用增强后的输入) ---
    classifier_out = call_dify_workflow("CLASSIFIER", {"text": enhanced_input})
    # 工作流逻辑：根据分类器结果判断 (保持原判定逻辑)
    is_search_needed = "true" in str(classifier_out)

    # --- 步骤2: 搜索处理 (保持原逻辑) ---
    search_context = ""
    if is_search_needed:
        search_context = google_search(user_input)  # 注意：搜索仍使用原始输入
    else:
        print("[*] 跳过搜索步骤")

    # --- 步骤3 & 4: 分类 LLM (干饭人) & 代码提取 ---
    # 如果有上下文，在这里加入
    combined_input = f"搜索结果：{search_context}\n用户问题：{enhanced_input}"
    parser_out = call_dify_workflow("LLM_PARSER", {"text": combined_input})
    raw_json_text = parser_out.get("text", "")

    # 提取字段 (保持原逻辑)
    field_chat = extract_json_field(raw_json_text, "聊天")
    field_code = extract_json_field(raw_json_text, "代码")
    field_logic = extract_json_field(raw_json_text, "需要逻辑推理")

    # --- 步骤5: 补救逻辑 (并行转串行) (保持原判定逻辑) ---
    final_results = {}
    task_type = 'chat'  # 默认任务类型

    # 5.1 聊天 (保持原判定)
    if "未找到聊天字段" in field_chat:
        final_results["chat"] = field_chat
    else:
        print("[*] 正在进行聊天...")
        res = call_dify_workflow("LLM_CHAT", {"text": field_chat})
        final_results["chat"] = res.get("text", "")
        task_type = 'chat'

    # 5.2 码码 (保持原判定)
    if "未找到聊天字段" in field_code:
        final_results["code"] = field_code
    else:
        print("[*] 正在进行代码...")
        res = call_dify_workflow("LLM_CODE", {"text": field_code})
        final_results["code"] = res.get("text", "")
        task_type = 'code'
        # 记忆增强：记录代码任务
        if memory_system:
            memory_system.update_task_context('code', {'input': field_code, 'output': res.get("text", "")})

    # 5.3 来硬的 (逻辑) (保持原判定)
    if "未找到聊天字段" in field_logic:
        final_results["logic"] = field_logic
    else:
        print("[*] 正在进行逻辑...")
        res = call_dify_workflow("LLM_LOGIC", {"text": field_logic})
        final_results["logic"] = res.get("text", "")
        task_type = 'logic'

    # --- 步骤6: 变量聚合 (保持原逻辑) ---
    aggregated_text = json.dumps(final_results, ensure_ascii=False)

    # --- 步骤7: 润色 LLM ---
    print("[*] 正在润色最终回答...")
    polish_out = call_dify_workflow("LLM_POLISH", {"text": aggregated_text})
    final_answer = polish_out.get("text", "润色失败，无结果。")

    # --- 步骤7.5: 质检 & 打回重试---
    MAX_RETRY = 3
    for attempt in range(MAX_RETRY):
        print(f"[*] 正在进行第{attempt+1}次质量检查...")
        passed, feedback = quality_check_openai(final_answer)

        if passed:
            print("[*] 质量检查通过！")
            break
        else:
            print(f"[!] 质量检查未通过: {feedback}")
            if attempt < MAX_RETRY - 1:
                retry_input = json.dumps({
                    "原始数据": final_results,
                    "修改建议": feedback
                }, ensure_ascii=False)
                print("[*] 根据反馈重新润色...")
                polish_out = call_dify_workflow("LLM_POLISH", {"text": retry_input})
                final_answer = polish_out.get("text", "润色失败，无结果。")
            else:
                print(f"[!] 已达最大重试次数（{MAX_RETRY}），使用当前结果。")

    # --- 步骤8: 输出 ---
    print("\n" + "="*30 + " 最终输出 " + "="*30)
    print(final_answer)
    print("="*70)
    
    # 记忆增强：保存到历史
    if memory_system:
        memory_system.add_to_history(user_input, final_answer, task_type)

# ==========================================
# 4. 入口 
# ==========================================
if __name__ == "__main__":
    # 初始化记忆系统
    user_id = "default_user"
    session_id = f"session_{int(time.time())}"
    memory_system = SimpleMemorySystem(user_id, session_id)
    
    print(f"系统已启动 (用户: {user_id})")
    
    while True:
        query = input("\n请输入问题 (输入 exit 退出): ")
        if query.lower() == 'exit':
            break
        if not query.strip():
            continue
        run_workflow(query)
