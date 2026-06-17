"""
应用根目录工具 — 兼容 PyInstaller 打包
在 main.py / webui.py 中 import 并调用 setup_app_dir() 即可
"""
import sys
import os


def get_app_dir() -> str:
    """返回应用根目录（兼容 PyInstaller 打包和直接运行）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))


def setup_app_dir():
    """切换工作目录到应用根目录，保证 config.json / memory_store / logs 等路径正确"""
    os.chdir(get_app_dir())
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')
