"""
Kagurazaka Core - Gradio Web UI
启动: python webui.py
"""
import asyncio
import json
import os
import sys
import time

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

import gradio as gr
from _path import setup_app_dir
from config import init_config, CONFIG
from core import run_workflow
from memory import SimpleMemorySystem
from provider_presets import get_preset, ALL_PROVIDERS
from llm import call_llm
import logger as log

setup_app_dir()
init_config()
log.init("webui")

NODE_NAMES = ["classifier", "parser", "search_judge", "task_router", "chat", "code", "logic",
              "polish", "quality_check", "planner", "reviewer", "aggregator"]
NODE_LABELS = {"classifier": "分类器(旧)", "parser": "解析器(旧)", "search_judge": "搜索审判官",
               "task_router": "任务路由器", "chat": "聊天", "code": "代码",
               "logic": "逻辑推理", "polish": "润色", "quality_check": "质量检查",
               "planner": "规划器", "reviewer": "评审器", "aggregator": "汇总器"}

# ---- 设置读取 ----

def _read_config_json():
    if not os.path.exists("config.json"):
        return {}
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def _get_current_provider(cfg: dict) -> str:
    p = cfg.get("LLM_PROVIDER", "")
    if p and p in ALL_PROVIDERS:
        return p
    if "PROVIDERS" in cfg:
        for pname, pcfg in cfg["PROVIDERS"].items():
            if pname.startswith("_"):
                continue
            if isinstance(pcfg, dict) and pcfg.get("api_key", ""):
                if pname == "google":
                    return "google"
                elif pname == "anthropic":
                    return "anthropic"
                elif pname == "openai":
                    return "openai"
    return "openai"


def _mask_api_key(key: str) -> str:
    if not key or key in ("sk-", "app-") or key.startswith("填你的"):
        return ""
    return key


def _get_initial_settings():
    cfg = _read_config_json()
    provider = _get_current_provider(cfg)
    api_key = ""
    base_url = ""
    if "LLM_API_KEY" in cfg:
        api_key = _mask_api_key(cfg["LLM_API_KEY"])
    elif "PROVIDERS" in cfg:
        pname = {"openai": "openai", "google": "google", "anthropic": "anthropic"}.get(provider, "openai")
        pcfg = cfg["PROVIDERS"].get(pname, {})
        api_key = _mask_api_key(pcfg.get("api_key", ""))
    if "LLM_BASE_URL" in cfg:
        base_url = cfg["LLM_BASE_URL"]
    overrides = cfg.get("MODEL_OVERRIDES", {})
    if isinstance(overrides, dict):
        overrides = {k: v for k, v in overrides.items() if not k.startswith("_")}
    else:
        overrides = {}
    models = {}
    preset = get_preset(provider)
    preset_models = preset.get("models", {}) if preset else {}
    for node in NODE_NAMES:
        models[node] = overrides.get(node, preset_models.get(node, ""))
    return provider, api_key, base_url, models

# ---- 交互逻辑 ----

def on_provider_change(provider: str):
    preset = get_preset(provider)
    if not preset:
        return [gr.update(value="") for _ in NODE_NAMES] + [gr.update(value="")]
    models = preset.get("models", {})
    updates = [gr.update(value=models.get(node, "")) for node in NODE_NAMES]
    updates.append(gr.update(value=preset.get("base_url", "")))
    return updates


def save_settings(provider, api_key, base_url, *model_values):
    overrides = {}
    preset = get_preset(provider)
    preset_models = preset.get("models", {}) if preset else {}
    for i, node in enumerate(NODE_NAMES):
        if i < len(model_values):
            preset_val = preset_models.get(node, "")
            user_val = str(model_values[i]).strip()
            if user_val and user_val != preset_val:
                overrides[node] = user_val

    cfg = _read_config_json()
    cfg["LLM_PROVIDER"] = provider
    cfg["LLM_API_KEY"] = api_key.strip()
    cfg["LLM_BASE_URL"] = base_url.strip()
    cfg["MODEL_OVERRIDES"] = overrides

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)

    init_config()
    return "✅ 设置已保存"


def test_connection():
    """快速测试当前配置能否正常调用"""
    try:
        models = CONFIG.get("MODELS", {})
        node = models.get("classifier", {})
        result = call_llm(
            node.get("provider", "openai"),
            node.get("model", ""),
            "",
            "你好，请回复 OK",
            temperature=0.1,
            max_tokens=32
        )
        if result:
            return f"✅ 连接成功 → 返回: {result[:80]}"
        return "❌ API 返回为空，请检查 API key 和模型名"
    except Exception as e:
        return f"❌ 连接失败: {str(e)[:100]}"


# ---- 聊天 ----

def chat_fn(message: str, history: list, memory_state):
    if not message.strip():
        return "", history, memory_state
    if memory_state is None:
        memory_state = SimpleMemorySystem("web_user", f"web_{int(time.time())}")
    try:
        log.record("chat", "input", len(message), 0, True, 0)
        response = run_workflow(message, memory_state)
        log.record("chat", "output", 0, 0, True, len(response))
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        return "", history, memory_state
    except Exception as e:
        import traceback
        err_msg = f"chat_fn crashed: {e}\n{traceback.format_exc()}"
        log.record("chat", "crash", 0, 0, False, 0, err_msg[:200])
        with open("crash.log", "a", encoding="utf-8") as f:
            f.write(f"\n{'='*40}\n{err_msg}\n")
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"[错误] 处理消息时发生异常: {e}"})
        return "", history, memory_state


def clear_chat(memory_state):
    memory_state = SimpleMemorySystem("web_user", f"web_{int(time.time())}")
    return [], memory_state

# ---- UI ----

_CSS = """
.avatar-img { width: 56px; height: 56px; border-radius: 50%; object-fit: cover; border: 2px solid #e0c0d0; }
.header-row { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
"""

def build_ui():
    provider_0, api_key_0, base_url_0, models_0 = _get_initial_settings()

    with gr.Blocks(title="神楽坂") as demo:
        memory_state = gr.State(None)

        # ---- 顶栏 ----
        with gr.Row(elem_classes="header-row"):
            gr.HTML('<div class="avatar-img" style="background:linear-gradient(135deg,#f0c0d0,#d0a0c0);'
                    'display:flex;align-items:center;justify-content:center;color:#fff;font-size:24px;">🌸</div>')
            with gr.Column(scale=10):
                gr.Markdown("## 神楽坂\n*はい、神楽坂ですよ♡*")

        # ---- 聊天区 ----
        chatbot = gr.Chatbot(height=520, buttons=["copy"])

        with gr.Row():
            msg = gr.Textbox(placeholder="输入消息，按 Enter 发送...",
                             scale=5, show_label=False, container=False)
            send_btn = gr.Button("发送", variant="primary", scale=1)
            clear_btn = gr.Button("🗑️", scale=0, min_width=40)

        # ---- 设置面板 ----
        with gr.Accordion("⚙️ 设置", open=False):
            with gr.Row():
                provider_dd = gr.Dropdown(choices=ALL_PROVIDERS, value=provider_0,
                                          label="LLM 供应商", scale=1)
                api_key_tb = gr.Textbox(value=api_key_0, label="API Key",
                                        type="password", placeholder="sk-...", scale=2)
            base_url_tb = gr.Textbox(value=base_url_0, label="Base URL",
                                     placeholder="留空则用默认地址，选 custom 时必填")

            with gr.Accordion("🔧 模型覆盖（留空则用预设默认值）", open=False):
                model_inputs = {}
                nodes_iter = iter(NODE_NAMES)
                for _ in range(5):
                    with gr.Row():
                        for _ in range(2):
                            node = next(nodes_iter, None)
                            if node is None:
                                break
                            val = models_0.get(node, "")
                            model_inputs[node] = gr.Textbox(
                                value=val, label=NODE_LABELS[node],
                                placeholder=get_preset(provider_0).get("models", {}).get(node, "") if get_preset(provider_0) else ""
                            )

            with gr.Row():
                save_btn = gr.Button("💾 保存设置", variant="primary")
                test_btn = gr.Button("🔍 测试连接")
            status_tb = gr.Textbox(label="", interactive=False, container=False)

        # ---- 事件绑定 ----
        msg.submit(chat_fn, [msg, chatbot, memory_state], [msg, chatbot, memory_state])
        send_btn.click(chat_fn, [msg, chatbot, memory_state], [msg, chatbot, memory_state])
        clear_btn.click(clear_chat, [memory_state], [chatbot, memory_state])

        provider_dd.change(
            on_provider_change, [provider_dd],
            [*model_inputs.values(), base_url_tb]
        )

        save_btn.click(
            save_settings,
            [provider_dd, api_key_tb, base_url_tb, *model_inputs.values()],
            [status_tb]
        )
        test_btn.click(test_connection, None, [status_tb])

    return demo


if __name__ == "__main__":
    # 修复 Windows 代理劫持 localhost 导致 Gradio 503 的问题
    for _k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(_k, None)
    os.environ["no_proxy"] = "localhost,127.0.0.1,0.0.0.0"

    try:
        ui = build_ui()
        ui.launch(server_name="127.0.0.1", server_port=7860, share=False, inbrowser=True,
                  theme=gr.themes.Soft(), css=_CSS)
    except Exception:
        import traceback
        with open("crash.log", "a", encoding="utf-8") as _f:
            _f.write(f"\n{'='*40}\n")
            traceback.print_exc(file=_f)
        raise
