"""
输出质量检查模块
通过 LLM 对最终输出进行质量审核
"""
import json
import re
from typing import Tuple

import config as cfg
from llm import call_llm


def quality_check(text: str) -> Tuple[bool, str]:
    """返回 (是否通过, 反馈/修改建议)"""
    models_cfg = cfg.CONFIG.get("MODELS", {}).get("quality_check", {})
    provider = models_cfg.get("provider", "openai")
    model = models_cfg.get("model", "gpt-4.1-mini")

    provider_cfg = cfg.CONFIG.get("PROVIDERS", {}).get(provider, {})
    api_key = provider_cfg.get("api_key", "")
    if not api_key or api_key.startswith("sk-"):
        print("[!] Quality check provider API key 未配置，跳过质量检查")
        return True, ""

    system_prompt = (
        "你是一个专业的输出质量审核员。请严格检查以下文本是否满足所有质量要求。\n\n"
        "质量检查标准：\n"
        "1. 语言自然流畅，没有生硬的机翻感或AI口癖（如\"总的来说\"、\"综上所述\"等）\n"
        "2. 不包含未翻译的英文代码、变量名、函数名或乱码（日语原文除外，特殊符号除外）\n"
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

    try:
        raw = call_llm(provider, model, system_prompt, text, temperature=0.3)
        raw = re.sub(r"```\w*\n?", "", raw).replace("```", "").strip()
        result = json.loads(raw)
        return result.get("pass", False), result.get("feedback", "")
    except Exception as e:
        print(f"[!] 质检调用或解析失败: {e}")
        return True, ""
