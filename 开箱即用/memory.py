"""
轻量级记忆系统
支持工作记忆、会话历史、主题关键词跟踪、长期记忆持久化
"""
import json
import os
import re
import time
from collections import deque
from typing import Any, Dict, Optional

import config as cfg


_STOP_WORDS = {
    "这个", "那个", "这些", "那些", "什么", "怎么", "如何", "为什么",
    "可以", "能够", "应该", "需要", "不要", "不能", "有没有", "是不是",
    "就是", "还是", "的话", "然后", "所以", "因为", "但是", "不过",
    "一个", "一下", "一些", "一种", "一次", "这个问", "的问题",
    "可能", "已经", "还是", "或者", "如果", "虽然", "而且", "以及",
    "吗", "呢", "吧", "啊", "哦", "嗯", "哈", "呀",
    "的", "了", "是", "在", "我", "你", "他", "她", "它", "们",
    "这", "那", "很", "都", "就", "也", "还", "要", "会", "能",
    "有", "和", "与", "对", "把", "被", "从", "到", "让", "给",
    "用", "做", "去", "来", "看", "说", "想", "知道", "觉得",
    "的问题", "帮我", "请问", "有没有人", "一下"
}


def _extract_keywords(text: str) -> set:
    phrases = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
    freq = {}
    for p in phrases:
        if p not in _STOP_WORDS and not p.isdigit():
            freq[p] = freq.get(p, 0) + 1
    return set(sorted(freq, key=freq.get, reverse=True)[:5])


class SimpleMemorySystem:
    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id

        mem_cfg = cfg.CONFIG.get("MEMORY", {})
        self.working_memory = deque(maxlen=mem_cfg.get("WORKING_CAPACITY", 7))
        self.session_history = deque(maxlen=mem_cfg.get("SESSION_CAPACITY", 10))
        self.topic_keywords = deque(maxlen=mem_cfg.get("SESSION_CAPACITY", 10))
        self.search_cache = deque(maxlen=20)  # [{query, results, timestamp}]

        self.task_context = {
            "active": False,
            "type": None,
            "steps": []
        }

        self.save_path = os.path.join(mem_cfg.get("SAVE_PATH", "./memory_store/"), user_id)
        os.makedirs(self.save_path, exist_ok=True)
        self.long_term_memory = self._load_memory()

    def _load_memory(self) -> Dict:
        memory_file = os.path.join(self.save_path, "memory.json")
        if os.path.exists(memory_file):
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"chat": [], "code": [], "logic": []}

    def _save_memory(self):
        memory_file = os.path.join(self.save_path, "memory.json")
        try:
            with open(memory_file, "w", encoding="utf-8") as f:
                json.dump(self.long_term_memory, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_search_cache(self, query: str, results: str):
        self.search_cache.append({
            "query": query,
            "results": results[:3000],
            "timestamp": time.time()
        })

    def find_in_cache(self, query: str, max_age_seconds: int = 1800):
        """精确或模糊匹配缓存，返回 (result, age_seconds) 或 (None, 0)"""
        if not query:
            return None, 0
        qwords = _extract_keywords(query)
        now = time.time()
        for entry in reversed(list(self.search_cache)):
            entry_qwords = _extract_keywords(entry["query"])
            age = now - entry["timestamp"]
            if qwords == entry_qwords and age < max_age_seconds:
                return entry["results"], age
        for entry in reversed(list(self.search_cache)):
            age = now - entry["timestamp"]
            if qwords & _extract_keywords(entry["query"]) and age < max_age_seconds:
                return entry["results"], age
        return None, 0

    def search_cache_summary(self) -> str:
        if not self.search_cache:
            return "（无历史搜索缓存）"
        lines = []
        for i, entry in enumerate(list(self.search_cache)[-10:]):
            age_sec = time.time() - entry["timestamp"]
            age_str = f"{int(age_sec)}秒" if age_sec < 60 else f"{int(age_sec/60)}分钟"
            preview = entry["results"][:120].replace("\n", " ")
            lines.append(f"  [{i+1}] 查询={entry['query']} | {age_str}前 | 摘要={preview}...")
        return "\n".join(lines)

    def detect_references(self, text: str) -> bool:
        reference_patterns = [
            r'刚才|刚刚|上面|之前|前面',
            r'这个|那个|它|这些|那些',
            r'基于.*的|根据.*的|继续'
        ]
        return any(re.search(pattern, text) for pattern in reference_patterns)

    def _topic_overlap(self, text: str) -> bool:
        if not self.topic_keywords:
            return False
        current_kw = _extract_keywords(text)
        if not current_kw:
            return False
        for hist_kw in list(self.topic_keywords)[-5:]:
            if current_kw & hist_kw:
                return True
        return False

    def enhance_input(self, user_input: str) -> str:
        need_context = self.detect_references(user_input) or self._topic_overlap(user_input)
        if need_context:
            context_parts = []
            if self.session_history:
                recent = list(self.session_history)[-3:]
                for item in recent:
                    context_parts.append(f"[历史] 用户: {item['user']}\n助手: {item['assistant'][:100]}...")
            if self.task_context["active"]:
                context_parts.append(
                    f"[当前任务] {self.task_context['type']}, "
                    f"已完成 {len(self.task_context['steps'])} 步"
                )
            if context_parts:
                return f"相关上下文:\n{chr(10).join(context_parts)}\n\n当前问题: {user_input}"
        return user_input

    def add_to_history(self, user_input: str, ai_output: str, task_type: Optional[str] = None):
        entry = {
            "user": user_input,
            "assistant": ai_output,
            "timestamp": time.time(),
            "task_type": task_type
        }
        self.session_history.append(entry)
        self.topic_keywords.append(_extract_keywords(user_input))

        if len(ai_output) > 200 or (task_type and task_type != "chat"):
            self._add_to_long_term(user_input, ai_output, task_type)

    def _add_to_long_term(self, user_input: str, ai_output: str, task_type: Optional[str]):
        if not task_type:
            task_type = "chat"
        if task_type not in self.long_term_memory:
            self.long_term_memory[task_type] = []

        memory_item = {
            "input": user_input,
            "output": ai_output[:500],
            "timestamp": time.time()
        }
        self.long_term_memory[task_type].append(memory_item)

        max_items = {"chat": 50, "code": 20, "logic": 15}
        limit = max_items.get(task_type, 30)
        if len(self.long_term_memory[task_type]) > limit:
            self.long_term_memory[task_type] = self.long_term_memory[task_type][-limit:]

        self._save_memory()

    def update_task_context(self, task_type: str, step_info: Any):
        if not self.task_context["active"] or self.task_context["type"] != task_type:
            self.task_context = {"active": True, "type": task_type, "steps": []}
        self.task_context["steps"].append(step_info)
