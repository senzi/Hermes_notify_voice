"""minimax-notify Hermes 原生插件：注册 notify_voice 工具。

薄封装：handler 调用**本插件目录内**的 minimax-notify.py（脚本与插件一起分发，
自包含，不依赖任何绝对路径）。可用环境变量 MINIMAX_NOTIFY_SCRIPT 覆盖脚本位置。
"""

import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("MINIMAX_NOTIFY_SCRIPT") or os.path.join(_HERE, "minimax-notify.py")

SCHEMA = {
    "name": "notify_voice",
    "description": (
        "本地语音播报提醒用户（MiniMax TTS 合成 + 提示音，立即出声）。"
        "任务开始/阶段性进展/任务完成/出状况/有好消息/需用户拍板时调用；"
        "任务结束务必调用一次。文本一句话、≤20字。默认同步（播完才返回，约1-4秒）。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "播报文本：发生了什么+要用户做什么，一句话≤20字，如'任务完成，可以查看结果了'",
            },
            "sound": {
                "type": "string",
                "enum": ["ding", "double", "alert", "chime", "none"],
                "description": "提示音：ding 一般 / alert 异常 / double 完成 / chime 进展 / none 无。默认 ding",
            },
            "voice": {
                "type": "string",
                "description": "音色 ID 或别名（news_anchor/announcer/yujie/tianmei/robot/bestie/qingse/jingying），默认取 config.json",
            },
            "sync": {
                "type": "boolean",
                "description": "省略/true=同步播放（播完才返回，保证出声）；false=异步（立即返回，子进程继续播）",
            },
        },
        "required": ["text"],
    },
}


def register(ctx):
    def handle_notify(params, **kwargs):
        del kwargs
        text = (params.get("text") or "").strip()
        if not text:
            return json.dumps({"success": False, "error": "缺少 text 参数"}, ensure_ascii=False)

        if not os.path.isfile(SCRIPT):
            return json.dumps({
                "success": False,
                "error": f"未找到脚本: {SCRIPT}（请把 minimax-notify.py 放在插件目录内，或设置 MINIMAX_NOTIFY_SCRIPT）",
            }, ensure_ascii=False)

        args = [sys.executable, SCRIPT, text]
        if params.get("sound"):
            args += ["-s", params["sound"]]
        if params.get("voice"):
            args += ["-v", params["voice"]]
        if params.get("sync") is False:
            args += ["--async"]

        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"  # 子进程 stdout 统一 UTF-8，避免 GBK 管道乱码
        try:
            proc = subprocess.run(
                args, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=60, env=env,
            )
            return json.dumps({
                "success": proc.returncode == 0,
                "output": proc.stdout.strip(),
                "error": proc.stderr.strip(),
            }, ensure_ascii=False)
        except Exception as e:  # noqa: BLE001
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    ctx.register_tool(
        name="notify_voice",
        toolset="minimax_notify",
        schema=SCHEMA,
        handler=handle_notify,
    )
