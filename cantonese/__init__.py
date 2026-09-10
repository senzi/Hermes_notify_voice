"""minimax-notify 粤语版 —— Hermes 原生插件：注册 notify_voice 工具。

薄封装：handler 调用**本插件目录内**的 minimax-notify.py（脚本与插件一起分发，
自包含，不依赖任何绝对路径）。可用环境变量 MINIMAX_NOTIFY_SCRIPT 覆盖脚本位置。

**默认完全后台**：Popen 起子进程后立即返回（几十毫秒），合成与播放在后台继续 ——
不阻塞 Agent 的思考与输出。需要回执时显式传 sync=true。

粤语版差异：默认音色为粤语（`Cantonese_GentleLady`），`language_boost=Chinese,Yue`
强制走粤语读音通道；工具描述要求用**粤语词**播报，并在回复正文给出普通话对照。
"""

import json
import os
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("MINIMAX_NOTIFY_SCRIPT") or os.path.join(_HERE, "minimax-notify.py")
LOG_PATH = os.path.join(tempfile.gettempdir(), "minimax-notify.log")

SCHEMA = {
    "name": "notify_voice",
    "description": (
        "本地语音播报提醒用户（MiniMax TTS 粤语音色 + 提示音，立即出声）。"
        "任务开始/阶段性进展/任务完成/出状况/有好消息/需用户拍板时调用；任务结束务必调用一次。"
        "text 必须用粤语（白话）口语词——讲「做嘢」唔讲「干活」、「睇」唔讲「看」、「搞掂」唔讲「完成」，"
        "净系加句尾「喇/咗/晒」唔算粤语；调用之后记得在回复正文写出佢嘅普通话意思（🔊 粤语 → 普通话）。"
        "发起后立即返回，播报在后台进行，不会阻塞你继续思考或输出。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "粤语播报文本，一句话≤20字，如'搞掂晒，睇得结果喇'。要用粤语词，唔好用普通话词。",
            },
            "sound": {
                "type": "string",
                "enum": ["ding", "double", "alert", "chime", "none"],
                "description": "提示音：ding 一般 / alert 异常 / double 完成 / chime 进展 / none 无。默认 ding",
            },
            "voice": {
                "type": "string",
                "description": "粤语音色 id 或别名（yue_gentle 默认 / yue_kind / yue_cute / yue_playful / yue_host_f / yue_host_m），默认取 config.json",
            },
            "sync": {
                "type": "boolean",
                "description": "默认 false/省略 = 后台播报（立即返回，不阻塞）；true = 等到播完才返回，能拿到成功/失败回执",
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

        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"  # 子进程 stdout 统一 UTF-8，避免 GBK 管道乱码

        # 同步模式（显式要求）：等到播完，能拿到回执
        if params.get("sync") is True:
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

        # 默认：完全后台 —— 立即返回，合成与播放在子进程里继续
        try:
            log = open(LOG_PATH, "wb")
            try:
                subprocess.Popen(
                    args,
                    creationflags=0x08000000 | 0x00000200,  # CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log, close_fds=True, env=env,
                )
            finally:
                log.close()
            return json.dumps({
                "success": True,
                "mode": "background",
                "note": f"播报已在后台发起（不阻塞思考/输出）；最近一次输出见 {LOG_PATH}；记得在回复正文写普通话对照",
            }, ensure_ascii=False)
        except Exception as e:  # noqa: BLE001
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    ctx.register_tool(
        name="notify_voice",
        toolset="minimax_notify",
        schema=SCHEMA,
        handler=handle_notify,
    )
