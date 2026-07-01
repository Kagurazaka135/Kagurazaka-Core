# quality.py — 质检员

**简单路径的最后一道关。** 润色完了，质检员看一眼：合格就放行，不合格打回去改，最多打回 3 次。

## 检查什么

5 条标准：

1. 语言自然流畅，不像机翻、没有 AI 口癖
2. 没有未翻译的英文代码、变量名、乱码混在中文里
3. 回答完整、逻辑通顺、没有前后矛盾
4. 内容切题、没有编造虚假信息
5. 格式清晰、没有残留的 JSON 结构

## 在 core.py 里怎么用

```python
for attempt in range(3):
    passed, feedback = quality_check(答案)
    if passed: break
    # 没通过 → 把原始数据 + 修改建议重新丢给 polish 节点润色
    答案 = call_node("polish", {"原始数据": 结果, "修改建议": feedback})
```

质检师返回 `{"pass": true/false, "feedback": "哪里不好、怎么改"}`。

## 容错

API key 没配的时候自动跳过质检，直接当通过——不能因为没质检员就卡住整个流程。
