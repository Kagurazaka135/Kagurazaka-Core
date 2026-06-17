"""
会话日志系统
记录每次 LLM 调用的输入输出长度、延迟、成功状态
"""
import json
import os
import time
from datetime import datetime
from collections import defaultdict
from typing import Dict, List

import config as cfg


_session_log: List[Dict] = []
_session_id: str = ""
_session_start: float = 0.0


def init(session_id: str):
    global _session_log, _session_id, _session_start
    _session_log = []
    _session_id = session_id
    _session_start = time.time()
    log_dir = cfg.CONFIG.get("LOGGING", {}).get("DIR", "./logs/")
    os.makedirs(log_dir, exist_ok=True)


def record(node: str, call_type: str, input_len: int, latency_ms: float,
           success: bool, output_len: int = 0, error: str = ""):
    entry = {
        "session": _session_id,
        "timestamp": datetime.now().isoformat(),
        "node": node,
        "call_type": call_type,
        "input_len": input_len,
        "output_len": output_len,
        "latency_ms": round(latency_ms, 1),
        "success": success,
        "error": error
    }
    _session_log.append(entry)
    if cfg.CONFIG.get("LOGGING", {}).get("ENABLED", True):
        log_dir = cfg.CONFIG.get("LOGGING", {}).get("DIR", "./logs/")
        log_file = os.path.join(log_dir, f"{_session_id}.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def show_session_stats():
    if not _session_log:
        print("\n[统计] 本次会话无日志记录")
        return
    total = len(_session_log)
    success = sum(1 for e in _session_log if e["success"])
    latencies = [e["latency_ms"] for e in _session_log]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    elapsed = time.time() - _session_start

    print("\n" + "=" * 30 + " 会话统计 " + "=" * 30)
    print(f"  会话ID:     {_session_id}")
    print(f"  总调用数:   {total}")
    print(f"  成功:       {success}  |  失败: {total - success}")
    print(f"  平均延迟:   {avg_latency:.0f}ms  |  最长: {max(latencies) if latencies else 0:.0f}ms")
    print(f"  会话耗时:   {elapsed:.1f}s")
    print("-" * 40)
    by_node = defaultdict(lambda: {"calls": 0, "success": 0, "total_latency": 0.0})
    for e in _session_log:
        n = e["node"]
        by_node[n]["calls"] += 1
        if e["success"]:
            by_node[n]["success"] += 1
        by_node[n]["total_latency"] += e["latency_ms"]
    for node, stats in sorted(by_node.items()):
        avg = stats["total_latency"] / stats["calls"] if stats["calls"] else 0
        print(f"  [{node}] {stats['calls']}次 | 成功{stats['success']} | 平均{avg:.0f}ms")
    print("=" * 70)


def show_historical_stats(log_dir: str = None):
    import glob
    if log_dir is None:
        log_dir = cfg.CONFIG.get("LOGGING", {}).get("DIR", "./logs/")
    files = glob.glob(os.path.join(log_dir, "*.jsonl"))
    if not files:
        print("无历史日志")
        return

    all_entries = []
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    all_entries.append(json.loads(line))

    sessions = defaultdict(list)
    for e in all_entries:
        sessions[e["session"]].append(e)

    print(f"\n历史统计 - {len(files)} 个日志文件, {len(sessions)} 个会话\n")
    for sid, entries in sessions.items():
        total = len(entries)
        success = sum(1 for e in entries if e["success"])
        latencies = [e["latency_ms"] for e in entries]
        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        print(f"  [{sid}] {total}次调用 | 成功率 {success/total*100:.0f}% | 平均 {avg_lat:.0f}ms")
