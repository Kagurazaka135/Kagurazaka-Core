# _path.py — 找家

**不管从哪里启动、不管是不是打包成 exe，都能找到项目目录。**

## 问题

Python 程序有个常见坑：你从桌面快捷方式启动、从命令行启动、打包成 exe 后启动，`os.getcwd()` 返回的路径可能不一样。如果代码里用相对路径找 `config.json`，换个启动方式就找不到了。

## 解决

```python
# 不管怎么启动，都以 main.py 所在的目录为基准
import sys, os
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)  # PyInstaller 打包后
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 正常 Python
```

## 谁用它

`main.py` 启动时第一件事就是切到这个目录。之后所有相对路径（`config.json`、`logs/`、`memory_store/`）都能正常工作。
