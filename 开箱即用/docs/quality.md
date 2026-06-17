# quality.py — 输出质量检查

**润色完的最后一道把关。** 不合格就带修改建议打回重试，最多 3 次。

## 检查什么

```python
# system prompt 里的 5 条标准
1. 语言自然流畅，没有生硬的机翻感或AI口癖
2. 不包含未翻译的英文代码、变量名、函数名或乱码
3. 回答完整、逻辑通顺，没有明显错误或前后矛盾
4. 回答内容准确切题，没有编造虚假信息或答非所问
5. 格式清晰易读，没有多余的JSON结构残留
```

## 重试机制

```python
# core.py 里的调用方逻辑
for attempt in range(3):
    passed, feedback = quality_check(final_answer)
    if passed: break
    
    # 失败了：把原始数据 + 修改建议拼在一起，重新扔给润色节点
    retry_input = json.dumps({
        "原始数据": final_results,
        "修改建议": feedback
    })
    final_answer = call_node("polish", retry_input)
```

质检师的系统 prompt 要求它返回 `{"pass": true/false, "feedback": "具体建议"}`。feedback 会给到润色节点当修改指引。

## 和 POLISH_CHECK_SYSTEM 的区别

`prompts.py` 里还有一个 `POLISH_CHECK_SYSTEM`，那是从原 Dify 工作流 1.6 里提取的简单版审核 prompt：
> 如果文本没问题，原样返回。如果不通过就改为 Kagurazaka不知道哦

`quality.py` 用的是更详细的审核 prompt（原 Python 版 `quality_check_openai` 函数的版本），能做精细反馈和重试。`POLISH_CHECK_SYSTEM` 保留在 `prompts.py` 里作参考，如果想切回简单版可以通过 `call_node("quality_check", text)` 调用。
