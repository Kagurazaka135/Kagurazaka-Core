# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Kagurazaka Core

import os, sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

_block_cipher = None
SRC = '../new core'

# ---- 项目模块 ----
PROJECT_MODULES = [
    'config', 'prompts', 'llm', 'memory', 'search',
    'quality', 'logger', 'core', 'provider_presets', '_path',
]

# ---- 额外隐藏导入 ----
EXTRA_HIDDEN = [
    'numpy', 'PIL', 'PIL.Image',
    'urllib3', 'charset_normalizer', 'certifi',
    'httpx', 'safehttpx', 'httpcore',
    'pygments', 'markdown_it', 'mdit_py_plugins',
    'pydantic', 'pydantic_core',
    'typing_extensions', 'semver', 'orjson',
    'aiofiles', 'fsspec',
    'json', 're', 'time', 'os', 'copy', 'typing',
    'datetime', 'collections', 'hashlib', 'glob',
    'asyncio', 'asyncio.events', 'asyncio.base_events',
    'asyncio.windows_events', 'asyncio.selector_events',
    'inspect', 'tempfile',
    'importlib.metadata', 'importlib.resources',
    'tomllib', 'pathlib',
    'starlette', 'starlette.routing', 'starlette.applications',
]

# =============================================
# 核心：gradio + gradio_client 全量收集 + 双保险
# =============================================
ALL_DATAS = []
ALL_BINARIES = []
ALL_HIDDEN = list(PROJECT_MODULES)

# 第1层：collect_submodules（确保子模块作为 hidden import，不依赖 collect_all）
print("[spec] Collecting gradio submodules...")
GRADIO_HIDDEN = collect_submodules('gradio')
ALL_HIDDEN += GRADIO_HIDDEN
print(f"[spec]   gradio: {len(GRADIO_HIDDEN)} submodules")

print("[spec] Collecting gradio_client submodules...")
GC_HIDDEN = collect_submodules('gradio_client')
ALL_HIDDEN += GC_HIDDEN
print(f"[spec]   gradio_client: {len(GC_HIDDEN)} submodules")

# 第2层：collect_all（数据文件 + 二进制 + 可能漏掉的子模块）
for _pkg_name, _label in [('gradio', 'gradio'), ('gradio_client', 'gradio_client')]:
    print(f"[spec] collect_all({_pkg_name})...")
    try:
        _d, _b, _h = collect_all(_pkg_name)
        ALL_DATAS += _d
        ALL_BINARIES += _b
        ALL_HIDDEN += _h
        print(f"[spec]   {_label}: +{len(_d)} datas, +{len(_b)} bins, +{len(_h)} imports")
    except Exception as _e:
        print(f"[spec]   {_label}: collect_all failed — {_e}")

# 第3层：补其他依赖的数据文件
for _pkg in ('safehttpx', 'httpx', 'groovy',
             'starlette', 'uvicorn', 'websockets', 'fastapi',
             'h11', 'anyio', 'httpcore', 'packaging', 'shellingham',
             'markdown_it', 'mdit_py_plugins', 'mdurl'):
    try:
        ALL_DATAS += collect_data_files(_pkg)
    except Exception:
        pass

# 第4层：核弹兜底 — gradio/gradio_client 安装目录全文件遍历
for _mod_name in ('gradio', 'gradio_client'):
    try:
        _mod = __import__(_mod_name)
        _mod_dir = os.path.dirname(_mod.__file__)
        _parent = os.path.dirname(_mod_dir)
        for _root, _dirs, _files in os.walk(_mod_dir):
            _dirs[:] = [d for d in _dirs if d != '__pycache__']
            for _f in _files:
                _src = os.path.join(_root, _f)
                _rel = os.path.relpath(_root, _parent)
                ALL_DATAS.append((_src, _rel))
        print(f"[spec]   {_mod_name} walk: included all files")
    except Exception as _e:
        print(f"[spec]   {_mod_name} walk failed: {_e}")

ALL_HIDDEN += EXTRA_HIDDEN

# 去重（PyInstaller 会处理，但先预去重减少数量）
ALL_HIDDEN = list(set(ALL_HIDDEN))

print(f"\n[spec] Summary: {len(ALL_HIDDEN)} hiddenimports, {len(ALL_DATAS)} datas, {len(ALL_BINARIES)} binaries")

a = Analysis(
    [f'{SRC}/webui.py'],
    pathex=[SRC],
    binaries=ALL_BINARIES,
    datas=ALL_DATAS,
    hiddenimports=ALL_HIDDEN,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'scipy',
        'notebook', 'jupyter', 'IPython',
        'tkinter', 'turtle',
        'PyQt5', 'PySide2', 'wx',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Kagurazaka',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon=None,
)
