import requests
import json
import os
from typing import Any, Dict, Optional

# ==========================================
# 1. 配置中心 (建议通过 .env 文件管理)
# ==========================================
CONFIG = {
    # SerpAPI 配置 (用于 Google 搜索)
    "SERPAPI_KEY": "YOUR_SERPAPI_KEY",

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
    }
}

# ==========================================
# 2. 核心功能函数
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

# ==========================================
# 3. 线性执行逻辑
# ==========================================

def run_workflow(user_input: str):
    print(f"\n[开始处理] 用户输入: {user_input}")

    # --- 步骤1: 问题分类器 ---
    classifier_out = call_dify_workflow("CLASSIFIER", {"text": user_input})
    # 工作流逻辑：根据分类器结果判断
    # 假设分类器输出字段为 'class_name' 或类似，根据 yml 逻辑判断是否包含“需要搜索”
    is_search_needed = "true" in str(classifier_out) 

    # --- 步骤2: 搜索处理 ---
    search_context = ""
    if is_search_needed:
        search_context = google_search(user_input)
    else:
        print("[*] 跳过搜索步骤")

    # --- 步骤3 & 4: 分类 LLM (干饭人) & 代码提取 ---
    combined_input = f"搜索结果：{search_context}\n用户问题：{user_input}"
    parser_out = call_dify_workflow("LLM_PARSER", {"text": combined_input})
    raw_json_text = parser_out.get("text", "") # 假设 Dify 返回的主文本在 text 字段

    # 提取字段
    field_chat = extract_json_field(raw_json_text, "聊天")
    field_code = extract_json_field(raw_json_text, "代码")
    field_logic = extract_json_field(raw_json_text, "需要逻辑推理")

    # --- 步骤5: 补救逻辑 (并行转串行) ---
    final_results = {}

    # 5.1 聊天
    if "未找到聊天字段" in field_chat:
        final_results["chat"] = field_chat
       
    else:
         print("[*] 正在进行聊天...")
        res = call_dify_workflow("LLM_CHAT", {"text": field_chat})
        final_results["chat"] = res.get("text", "")

    # 5.2 码码
    if "未找到聊天字段" in field_code:
        final_results["code"] = field_code
    else:
         print("[*] 正在进行代码...")
        res = call_dify_workflow("LLM_CODE", {"text": field_code})
        final_results["code"] = res.get("text", "")

    # 5.3 来硬的 (逻辑)
    if "未找到聊天字段" in field_logic:
        final_results["logic"] = field_logic
    else:
         print("[*] 正在进行逻辑...")
        res = call_dify_workflow("LLM_LOGIC", {"text": field_logic})
        final_results["logic"] = res.get("text", "")

    # --- 步骤6: 变量聚合 ---
    aggregated_text = json.dumps(final_results, ensure_ascii=False)

    # --- 步骤7: 润色 LLM ---
    print("[*] 正在润色最终回答...")
    polish_out = call_dify_workflow("LLM_POLISH", {"text": aggregated_text})
    final_answer = polish_out.get("text", "润色失败，无结果。")

    # --- 步骤8: 输出 ---
    print("\n" + "="*30 + " 最终输出 " + "="*30)
    print(final_answer)
    print("="*70)

# ==========================================
# 4. 入口
# ==========================================
if __name__ == "__main__":
    while True:
        query = input("\n请输入问题 (输入 exit 退出): ")
        if query.lower() == 'exit':
            break
        if not query.strip():
            continue
        run_workflow(query)