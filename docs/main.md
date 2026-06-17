# main.py — CLI 入口

**你运行 `python main.py` 实际就是它在干活。**

## 做了啥

```
1. os.chdir(__file__目录)       ← 保证 config.json 能找到
2. init_config()                ← 读配置
3. 创建 SimpleMemorySystem      ← 这一轮对话的记忆
4. 初始化日志系统               ← 记录这次会话
5. 进入循环:
   >>> 用户输入
   → 调 core.run_workflow()
   → 打印结果
   → 循环
6. Ctrl+C 或 exit → 打印统计 → 保存记忆
```

## 关键代码走读

```python
# 命令行扩展
if "--stats" in sys.argv:       # python main.py --stats → 看历史统计
if "--providers" in sys.argv:   # python main.py --providers → 看可选供应商
```

```python
# 交互循环
while True:
    query = input(">>> ")       # 等待用户输入
    if query.lower() == "exit": break
    run_workflow(query, memory_system)  # 交给核心
```

```python
# 退出时的收尾
finally:
    show_session_stats()        # 本次会话调了多少次LLM、延迟多少
    memory_system._save_memory() # 长期记忆写盘
```

## 为什么这么简单

真正的逻辑全在 `core.py` 里。`main.py` 就是个壳——负责启动、收输入、展示结果、关机收尾。
