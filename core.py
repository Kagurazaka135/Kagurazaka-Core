"""
核心工作流编排
整合所有 Dify 工作流节点逻辑为纯 Python 实现

新流程:
  L1白名单 → L2正则 → Search Judge(LLM) → 搜索(含缓存) → Task Router(LLM) → simple/complex
"""
import json
import re
import time
from typing import Dict

from llm import call_node, call_llm, safe_extract_json
from memory import SimpleMemorySystem
from search import google_search
from quality import quality_check
import logger as log
import config as cfg


_FIELD_NOT_FOUND = "__FIELD_NOT_FOUND__"

# ==========================================
# L1 白名单 — 废话拦截器
# ==========================================
_SEARCH_WHITELIST = {
    "谢谢", "好的", "再见", "OK", "ok", "拜拜", "哈哈", "牛逼", "太棒了",
    "在吗", "嗯", "哦", "嗨", "你好", "早安", "晚安", "辛苦了",
}

# ==========================================
# L2 正则 — 强信号匹配
# ==========================================
_SEARCH_SIGNAL_PATTERNS = [
    re.compile(p) for p in [
        r'(今天|现在|此刻|实时|最新|刚刚|202\d年).{0,8}(天气|股价|汇率|温度|新闻|热搜|排名|价格)',
        r'(什么|多少|怎么|如何|哪里|哪个|谁|为什么).{0,10}(价格|时间|天气|方法|地方|最新|电话)',
        r'(帮我|给我|我想|帮我查|帮忙)(查|找|搜|了解|看看|搜一下)',
        r'(查一下|搜一下|上网找|检索|百度|谷歌|搜索)',
        r'(天气|新闻|热搜|排名|股价|汇率).{0,5}(怎么|如何|多少|什么|今天)',
    ]
]


def _search_intent_whitelist(text: str):
    t = text.strip()
    if t in _SEARCH_WHITELIST:
        return True
    return False


def _search_intent_regex(text: str):
    t = re.sub(r'[?？?！!。，,、\s]', '', text)
    for pat in _SEARCH_SIGNAL_PATTERNS:
        if pat.search(t):
            return True, text[:60]
    return False, ""


def _extract_json_field(raw_text: str, field_name: str):
    data = safe_extract_json(raw_text)
    return data.get(field_name, _FIELD_NOT_FOUND)


def run_workflow(user_input: str, memory_system: SimpleMemorySystem) -> str:
    try:
        return _run_workflow_impl(user_input, memory_system)
    except Exception as e:
        import traceback
        err_detail = traceback.format_exc()
        print(f"[!!!] run_workflow 未捕获异常: {e}\n{err_detail}")
        log.record("workflow", "crash", len(user_input), 0, False, 0, str(e)[:200])
        with open("crash.log", "a", encoding="utf-8") as f:
            f.write(f"\n{'='*40}\nrun_workflow crash\n{err_detail}\n")
        return f"Kagurazaka出错了: {e}"


def _run_workflow_impl(user_input: str, memory_system: SimpleMemorySystem) -> str:
    print(f"\n[开始处理] 用户输入: {user_input}")

    # ---- 记忆增强 ----
    enhanced_input = user_input
    if memory_system:
        enhanced_input = memory_system.enhance_input(user_input)
        if enhanced_input != user_input:
            print("[*] 检测到上下文引用，已增强输入")

    # ---- L1 白名单 ----
    if _search_intent_whitelist(enhanced_input):
        print("[L1-白名单] 命中，跳过搜索与Search Judge")
        is_search_needed = False
        search_query = ""
    else:
        # ---- L2 正则 ----
        l2_hit, l2_query = _search_intent_regex(enhanced_input)
        if l2_hit:
            print(f"[L2-正则] 命中，关键词={l2_query}，跳过Search Judge")
            is_search_needed = True
            search_query = l2_query
        else:
            # ---- Search Judge ----
            print("[Search Judge] 判断搜索意图...")
            t0 = time.time()
            try:
                judge_raw = call_node("search_judge", enhanced_input)
                judge_data = safe_extract_json(judge_raw)
                is_search_needed = judge_data.get("search_needed", False)
                search_query = judge_data.get("search_query", "") or user_input
                log.record("search_judge", "llm", len(enhanced_input),
                           (time.time() - t0) * 1000, True, len(judge_raw))
                print(f"[Search Judge] search_needed={is_search_needed}, query={search_query}")
            except Exception as e:
                print(f"[!] Search Judge 调用失败: {e}")
                is_search_needed = False
                search_query = ""
                log.record("search_judge", "llm", len(enhanced_input),
                           (time.time() - t0) * 1000, False, 0, str(e))

    # ---- 搜索（含缓存） ----
    search_context = _resolve_search(search_query, memory_system, is_search_needed)

    # ---- Task Router ----
    print("[Task Router] 判断复杂度并拆解任务...")
    router_input = json.dumps({
        "user_request": enhanced_input,
        "search_results": search_context[:2000] if search_context else ""
    }, ensure_ascii=False)
    t0 = time.time()
    try:
        router_raw = call_node("task_router", router_input)
        router_data = safe_extract_json(router_raw)
        complexity = router_data.get("complexity", "simple")
        log.record("task_router", "llm", len(router_input),
                   (time.time() - t0) * 1000, True, len(router_raw))
        print(f"[Task Router] complexity={complexity}")
    except Exception as e:
        print(f"[!] Task Router 调用失败: {e}")
        router_data = {"complexity": "simple", "chat_task": enhanced_input, "code_task": None, "logic_task": None}
        complexity = "simple"
        log.record("task_router", "llm", len(router_input),
                   (time.time() - t0) * 1000, False, 0, str(e))

    # ---- 路由 ----
    if complexity == "complex":
        print("[*] → 走复杂路径")
        final_answer = _run_complex_workflow(enhanced_input, search_context, router_data, memory_system)
        task_type = "complex"
    else:
        print("[*] → 走简单路径")
        final_answer, task_type = _run_simple_workflow(router_data, memory_system)

    # ---- 人格注入 ----
    persona_mode = cfg.CONFIG.get("PERSONA_MODE", "none")
    if persona_mode == "kagurazaka":
        print("[*] 注入神楽坂人格...")
        t0 = time.time()
        try:
            final_answer = call_node("persona_kagurazaka", final_answer)
            log.record("persona_kagurazaka", "llm", len(final_answer),
                       (time.time() - t0) * 1000, True, len(final_answer))
        except Exception as e:
            log.record("persona_kagurazaka", "llm", 0, 0, False, 0, str(e))
    elif persona_mode == "custom":
        print("[*] 注入自定义人格...")
        t0 = time.time()
        try:
            final_answer = call_node("persona_custom", final_answer)
            log.record("persona_custom", "llm", len(final_answer),
                       (time.time() - t0) * 1000, True, len(final_answer))
        except Exception as e:
            log.record("persona_custom", "llm", 0, 0, False, 0, str(e))

    # ---- 输出 ----
    print("\n" + "=" * 30 + " 最终输出 " + "=" * 30)
    print(final_answer)
    print("=" * 70)

    if memory_system:
        memory_system.add_to_history(user_input, final_answer, task_type)

    return final_answer


# ==========================================
# 搜索解析 — 缓存判断 + 实际搜索 + 质量检查
# ==========================================
def _resolve_search(search_query: str, memory_system, is_search_needed: bool) -> str:
    if not is_search_needed:
        print("[*] 无需搜索")
        return ""

    if memory_system:
        cached, age = memory_system.find_in_cache(search_query)
        if cached and age < 1800:
            print(f"[搜索缓存] 命中，{int(age)}秒前的结果")
            return cached
        if cached:
            print(f"[搜索缓存] 命中但过期({int(age)}秒前)，先复用旧缓存")

    print(f"[搜索] 正在搜索: {search_query}")
    results = google_search(search_query)
    if not results:
        print("[!] 搜索结果为空")
        return ""

    # 质量检查 — 结果太短/太乱时换词重搜
    quality_ok = True
    if len(results) < 80 or len(results.split("\n")) < 2:
        quality_ok = False
        retry_reason = "结果太短或太少"
    else:
        # 用 Search Judge 检查质量
        try:
            qc_input = json.dumps({
                "search_query": search_query,
                "search_results": results[:1200]
            }, ensure_ascii=False)
            qc_raw = call_node("search_quality_check", qc_input)
            qc_data = safe_extract_json(qc_raw)
            if not qc_data.get("quality_ok", True):
                quality_ok = False
                retry_reason = qc_data.get("reason", "")
                retry_query = qc_data.get("retry_query", "")
                if retry_query:
                    print(f"[搜索重试] 质量不够({retry_reason})，换词: {retry_query}")
                    results2 = google_search(retry_query)
                    if results2:
                        results = results2
                        quality_ok = True
                        search_query = retry_query
                        print(f"[搜索重试] 第二次搜索结果长度={len(results)}")
                    else:
                        print(f"[搜索重试] 第二次搜索也为空，用第一次结果")
                        quality_ok = True  # 算了就用第一次的
            else:
                print(f"[搜索质量] 通过")
        except Exception as e:
            print(f"[!] 搜索质量检查失败: {e}，默认通过")
            quality_ok = True

    if memory_system:
        memory_system.add_search_cache(search_query, results)

    return results


# ==========================================
# 简单路径 — 用 Task Router 的 task 字段
# ==========================================
def _run_simple_workflow(router_data: dict, memory_system: SimpleMemorySystem):
    field_chat = router_data.get("chat_task") if router_data.get("chat_task") != "null" else None
    field_code = router_data.get("code_task") if router_data.get("code_task") != "null" else None
    field_logic = router_data.get("logic_task") if router_data.get("logic_task") != "null" else None

    final_results: Dict[str, str] = {}
    task_type = "chat"

    if field_chat:
        print("[*] 生成聊天回复...")
        t0 = time.time()
        try:
            res = call_node("chat", field_chat)
            final_results["chat"] = res
            log.record("chat", "llm", len(str(field_chat)),
                       (time.time() - t0) * 1000, True, len(res))
        except Exception as e:
            final_results["chat"] = ""
            log.record("chat", "llm", 0, 0, False, 0, str(e))
        task_type = "chat"

    if field_code:
        print("[*] 生成代码...")
        t0 = time.time()
        try:
            res = call_node("code", field_code)
            final_results["code"] = res
            log.record("code", "llm", len(str(field_code)),
                       (time.time() - t0) * 1000, True, len(res))
        except Exception as e:
            final_results["code"] = ""
            log.record("code", "llm", 0, 0, False, 0, str(e))
        task_type = "code"
        if memory_system:
            memory_system.update_task_context("code", {"input": str(field_code), "output": final_results["code"]})

    if field_logic:
        print("[*] 逻辑推理...")
        t0 = time.time()
        try:
            res = call_node("logic", field_logic)
            final_results["logic"] = res
            log.record("logic", "llm", len(str(field_logic)),
                       (time.time() - t0) * 1000, True, len(res))
        except Exception as e:
            final_results["logic"] = ""
            log.record("logic", "llm", 0, 0, False, 0, str(e))
        task_type = "logic"

    # 如果没有任何 task 字段有值，兜底
    if not any(final_results.values()):
        final_results["chat"] = "Kagurazaka不知道哦"

    aggregated_text = json.dumps(final_results, ensure_ascii=False)

    print("[*] 润色中...")
    t0 = time.time()
    try:
        final_answer = call_node("polish", aggregated_text)
        log.record("polish", "llm", len(aggregated_text),
                   (time.time() - t0) * 1000, True, len(final_answer))
    except Exception as e:
        final_answer = "Kagurazaka不知道哦"
        log.record("polish", "llm", 0, 0, False, 0, str(e))

    # 质量检查
    MAX_RETRY = 3
    qc_passed = False
    for attempt in range(MAX_RETRY):
        print(f"[*] 第{attempt+1}次质量检查...")
        passed, feedback = quality_check(final_answer)
        if passed:
            print("[*] 质量检查通过")
            qc_passed = True
            break
        else:
            print(f"[!] 未通过: {feedback}")
            if attempt < MAX_RETRY - 1:
                retry_input = json.dumps({"原始数据": final_results, "修改建议": feedback}, ensure_ascii=False)
                try:
                    final_answer = call_node("polish", retry_input)
                except Exception:
                    pass
            else:
                print(f"[!] 已达最大重试次数({MAX_RETRY})")

    if not qc_passed:
        final_answer = final_answer + "\n\n（Kagurazaka也不知道这样对不对）"

    return final_answer, task_type


# ==========================================
# 复杂路径 — 执行 Task Router 的 steps
# ==========================================
def _execute_step(step: dict, memory_system=None) -> dict:
    node_type = step.get("node_type", "chat")
    user_prompt = step.get("user_prompt", "")
    system_prompt = step.get("system_prompt", "")
    model_override = step.get("model", "")

    print(f"  [step {step.get('step_id')}] {node_type}: {str(user_prompt)[:60]}...")

    if node_type == "search":
        is_needed = bool(user_prompt)
        result = _resolve_search(user_prompt, memory_system, is_needed) if is_needed else ""
        return {"step_id": step.get("step_id"), "node_type": node_type,
                "user_prompt": user_prompt, "result": result}

    models_cfg = cfg.CONFIG.get("MODELS", {})
    if node_type in models_cfg:
        node_cfg = models_cfg[node_type]
        provider = node_cfg["provider"]
        model = model_override or node_cfg["model"]
    else:
        fallback = models_cfg.get("chat", {"provider": "openai", "model": "gpt-4.1-mini"})
        provider = fallback["provider"]
        model = model_override or fallback["model"]

    try:
        if system_prompt:
            result = call_llm(provider, model, system_prompt, str(user_prompt))
        else:
            result = call_node(node_type, str(user_prompt))
        log.record(f"step_{step.get('step_id')}", "llm", len(str(user_prompt)), 0, True, len(result))
    except Exception as e:
        result = f"[执行失败] {e}"
        log.record(f"step_{step.get('step_id')}", "llm", 0, 0, False, 0, str(e))

    return {"step_id": step.get("step_id"), "node_type": node_type,
            "user_prompt": user_prompt, "result": result}


def _run_complex_workflow(user_input: str, search_context: str,
                           router_data: dict, memory_system: SimpleMemorySystem) -> str:
    MAX_REVIEW_ROUNDS = 3
    step_results = []
    steps = router_data.get("steps", [{"step_id": 1, "node_type": "chat", "user_prompt": user_input}])
    reasoning = router_data.get("reasoning", "")

    print(f"[Task Router] 拆解思路: {reasoning}")
    print(f"[Task Router] 共 {len(steps)} 步")

    for step in steps:
        sr = _execute_step(step, memory_system)
        step_results.append(sr)

    print("[Aggregator] 整合结果...")
    final_answer = _aggregate(step_results)

    for round_idx in range(MAX_REVIEW_ROUNDS):
        print(f"[Reviewer] 第{round_idx+1}轮评审...")
        review_input = json.dumps({
            "user_request": user_input,
            "final_output": final_answer,
            "execution_log": [{"step_id": s.get("step_id"), "node_type": s.get("node_type", ""),
                               "result_preview": str(s.get("result", ""))[:200]}
                              for s in step_results]
        }, ensure_ascii=False)
        t0 = time.time()
        try:
            review_raw = call_node("reviewer", review_input)
            review = safe_extract_json(review_raw)
            log.record("reviewer", "llm", len(review_input),
                       (time.time() - t0) * 1000, True, len(review_raw))
        except Exception as e:
            print(f"[!] 评审器调用失败: {e}")
            log.record("reviewer", "llm", len(review_input),
                       (time.time() - t0) * 1000, False, 0, str(e))
            break

        if review.get("pass", True):
            print("[Reviewer] 通过")
            break
        else:
            feedback = review.get("feedback", "")
            missing = review.get("missing_steps", [])
            print(f"[Reviewer] 未通过: {feedback}")
            if missing and round_idx < MAX_REVIEW_ROUNDS - 1:
                print(f"[Reviewer] 追加 {len(missing)} 个补充步骤")
                for step in missing:
                    step["step_id"] = len(step_results) + 1
                    sr = _execute_step(step, memory_system)
                    step_results.append(sr)
                final_answer = _aggregate(step_results)
            elif round_idx == MAX_REVIEW_ROUNDS - 1:
                print("[Reviewer] 已达最大评审轮数")

    return final_answer


def _aggregate(step_results: list) -> str:
    agg_input = json.dumps(
        [{"step_id": s.get("step_id"), "result": str(s.get("result", ""))[:1500]}
         for s in step_results],
        ensure_ascii=False
    )
    try:
        result = call_node("aggregator", agg_input)
        log.record("aggregator", "llm", len(agg_input), 0, True, len(result))
        return result
    except Exception as e:
        log.record("aggregator", "llm", len(agg_input), 0, False, 0, str(e))
        parts = [str(s.get("result", "")) for s in step_results]
        return "\n\n".join(parts)
