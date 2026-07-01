# main.py — 门面

**你运行 `python main.py` 时实际执行的文件。** 整个系统最薄的一层——就是个壳。

## 启动流程

```
1. 切到 main.py 所在目录（保证能找到 config.json）
2. 读配置（config.py）
3. 初始化记忆系统（这一轮对话的记忆）
4. 初始化日志（记录这次会话）
5. 进入循环：
   >>> 等你输入
   → 交给 core.run_workflow()
   → 打印结果
   → 回到 >>> 等你下一条
6. 你输入 exit 或 Ctrl+C → 打印统计 → 保存记忆 → 关机
```

## 命令行参数

```bash
python main.py              # 正常启动，进入对话
python main.py --stats      # 看历史调用统计
python main.py --providers  # 看支持哪些供应商
```

## 为什么这么短

真正的逻辑全在 `core.py` 里。`main.py` 就像餐厅门口的服务员——只负责迎客、传菜、买单，不做菜。
