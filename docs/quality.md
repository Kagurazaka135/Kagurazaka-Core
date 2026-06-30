# quality.py — 简单路径输出质量检查

**润色后的最后一道把关。** 不合格带修改建议打回重试，最多 3 次。

## 检查什么

```python
# system prompt 5 条标准
1. 语言自然流畅，没有生硬的机翻感或AI口癖
2. 不包含未翻译的英文代码、变量名、函数名或乱码
3. 回答完整、逻辑通顺，没有明显错误或前后矛盾
4. 回答内容准确切题，没有编造虚假信息或答非所问
5. 格式清晰易读，没有多余的JSON结构残留
```

## 在 core.py 里的重试机制

```python
# core.py 简单路径
for attempt in range(3):
    passed, feedback = quality_check(final_answer)
    if passed: break

    # 失败：原始数据 + 修改建议 → 重新润色
    retry_input = json.dumps({
        "原始数据": final_results,
        "修改建议": feedback
    })
    final_answer = call_node("polish", retry_input)
```

质检师返回 `{"pass": bool, "feedback": "具体建议"}`。feedback 给润色节点当修改指引。
API key 未配置时自动跳过质检，返回通过。
