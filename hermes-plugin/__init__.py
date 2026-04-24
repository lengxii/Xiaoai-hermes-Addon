"""XiaoAI Cloud Plugin for Hermes Agent — 控制小米小爱音箱"""

import json
import os
import urllib.request
import urllib.error

XIAOAI_API_BASE = os.environ.get("XIAOAI_API_URL", "http://127.0.0.1:18790")


def _api_call(path: str, method: str = "GET", data: dict = None) -> dict:
    """Call the XiaoAI Node.js HTTP API."""
    url = f"{XIAOAI_API_BASE}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {error_body}"}
    except urllib.error.URLError as e:
        return {"error": f"Connection error: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def register(ctx):
    """Register all XiaoAI tools with Hermes."""

    # --- xiaoai_speak ---
    ctx.register_tool(
        "xiaoai_speak",
        {
            "name": "xiaoai_speak",
            "description": "通过小爱音箱播报语音内容。参数 text 是要大声说出的中文文本。",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要播报给用户的中文文本"}
                },
                "required": ["text"],
            },
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/speak", "POST", params)),
    )

    # --- xiaoai_play_audio ---
    ctx.register_tool(
        "xiaoai_play_audio",
        {
            "name": "xiaoai_play_audio",
            "description": "通过小爱音箱播放音频。支持 http/https URL 和本地绝对路径。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "音频 URL 或本地路径"},
                    "title": {"type": "string", "description": "音频标题（可选）"},
                },
                "required": ["url"],
            },
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/play-audio", "POST", params)),
    )

    # --- xiaoai_set_volume ---
    ctx.register_tool(
        "xiaoai_set_volume",
        {
            "name": "xiaoai_set_volume",
            "description": "设置小爱音箱音量。",
            "parameters": {
                "type": "object",
                "properties": {
                    "volume": {"type": "integer", "description": "音量 0-100"}
                },
                "required": ["volume"],
            },
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/set-volume", "POST", params)),
    )

    # --- xiaoai_get_volume ---
    ctx.register_tool(
        "xiaoai_get_volume",
        {
            "name": "xiaoai_get_volume",
            "description": "获取小爱音箱当前音量。",
            "parameters": {"type": "object", "properties": {}},
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/get-volume")),
    )

    # --- xiaoai_wake_up ---
    ctx.register_tool(
        "xiaoai_wake_up",
        {
            "name": "xiaoai_wake_up",
            "description": "远程唤醒小爱音箱。",
            "parameters": {"type": "object", "properties": {}},
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/wake-up", "POST", {})),
    )

    # --- xiaoai_execute ---
    ctx.register_tool(
        "xiaoai_execute",
        {
            "name": "xiaoai_execute",
            "description": "发送指令到小爱音箱执行。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的指令"}
                },
                "required": ["command"],
            },
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/execute", "POST", params)),
    )

    # --- xiaoai_set_mode ---
    ctx.register_tool(
        "xiaoai_set_mode",
        {
            "name": "xiaoai_set_mode",
            "description": "切换拦截模式：wake（唤醒词触发）、proxy（完全接管）、silent（静默）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["wake", "proxy", "silent"],
                        "description": "工作模式"
                    }
                },
                "required": ["mode"],
            },
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/set-mode", "POST", params)),
    )

    # --- xiaoai_new_session ---
    ctx.register_tool(
        "xiaoai_new_session",
        {
            "name": "xiaoai_new_session",
            "description": "重置语音对话上下文，开始新会话。",
            "parameters": {"type": "object", "properties": {}},
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/new-session", "POST", {})),
    )

    # --- xiaoai_get_status ---
    ctx.register_tool(
        "xiaoai_get_status",
        {
            "name": "xiaoai_get_status",
            "description": "获取小爱音箱插件完整状态。",
            "parameters": {"type": "object", "properties": {}},
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/status")),
    )

    # --- xiaoai_set_wake_word ---
    ctx.register_tool(
        "xiaoai_set_wake_word",
        {
            "name": "xiaoai_set_wake_word",
            "description": "设置唤醒词规则（正则表达式）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "唤醒词正则"}
                },
                "required": ["pattern"],
            },
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/set-wake-word", "POST", params)),
    )

    # --- xiaoai_login_begin ---
    ctx.register_tool(
        "xiaoai_login_begin",
        {
            "name": "xiaoai_login_begin",
            "description": "开始小米账号登录流程。",
            "parameters": {
                "type": "object",
                "properties": {
                    "account": {"type": "string", "description": "小米账号"},
                    "password": {"type": "string", "description": "密码（可选）"},
                },
            },
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/login-begin", "POST", params)),
    )

    # --- xiaoai_login_status ---
    ctx.register_tool(
        "xiaoai_login_status",
        {
            "name": "xiaoai_login_status",
            "description": "检查小米账号登录状态。",
            "parameters": {"type": "object", "properties": {}},
        },
        lambda params: json.dumps(_api_call("/api/xiaoai/login-status")),
    )

    # --- xiaoai_console_open ---
    ctx.register_tool(
        "xiaoai_console_open",
        {
            "name": "xiaoai_console_open",
            "description": "获取小爱音箱控制台链接。",
            "parameters": {"type": "object", "properties": {}},
        },
        lambda params: json.dumps({
            "content": [{
                "type": "text",
                "text": f"控制台地址: {XIAOAI_API_BASE}/console"
            }]
        }),
    )

    # --- Hook: log tool calls ---
    def on_tool_call(tool_name, params, result):
        if tool_name.startswith("xiaoai_"):
            print(f"[xiaoai] {tool_name} called")

    ctx.register_hook("post_tool_call", on_tool_call)

    print(f"[xiaoai-cloud] Plugin registered, API: {XIAOAI_API_BASE}")
