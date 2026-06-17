"""
CLI 入口
纯 Python 版 Kagurazaka Core

用法:
    python main.py              # 启动交互模式
    python main.py --stats      # 查看历史日志统计
    python main.py --providers  # 查看可选LLM供应商列表
"""
import sys
import time
import os

from _path import setup_app_dir
from config import init_config
from memory import SimpleMemorySystem
from logger import init as log_init, show_session_stats, show_historical_stats
from core import run_workflow
from provider_presets import list_providers, ALL_PROVIDERS


def main():
    setup_app_dir()

    if "--stats" in sys.argv:
        init_config()
        show_historical_stats()
        return

    if "--providers" in sys.argv:
        print(f"\n可选 LLM 供应商 ({len(ALL_PROVIDERS)} 个):\n")
        print(list_providers())
        print("\n在 config.json 中设置 LLM_PROVIDER 为其中之一即可")
        return

    init_config()

    user_id = "default_user"
    session_id = f"session_{int(time.time())}"
    log_init(session_id)

    memory_system = SimpleMemorySystem(user_id, session_id)

    print(f"Kagurazaka Core (Pure Python) 已启动")
    print(f"用户: {user_id} | 会话: {session_id}")
    print("输入 --stats 作为参数可查看历史日志统计")
    print("输入 exit 退出\n")

    try:
        while True:
            query = input(">>> ")
            if query.lower() == "exit":
                break
            if not query.strip():
                continue
            run_workflow(query, memory_system)
    except KeyboardInterrupt:
        print("\n[*] 收到中断信号")
    finally:
        show_session_stats()
        if memory_system:
            memory_system._save_memory()
        print("\nじゃね～")


if __name__ == "__main__":
    main()
