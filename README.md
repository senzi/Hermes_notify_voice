# minimax-notify

给 AI Agent 用的**本地语音播报** CLI：MiniMax TTS 合成一句话 + 系统提示音，
在任务开始 / 进展 / 完成 / 出状况时喊你一声 —— 不用一直盯着屏幕。

**Windows · 单文件 · 零第三方依赖**（只用 Python 标准库）

---

## 特性

- 一句话就能播报：`python minimax-notify.py "任务完成，可以看结果了"`
- 先响提示音再说话（`ding` / `double` / `alert` / `chime` / `none`）
- 默认**同步**播放（播完才返回，保证出声）；`--async` 可切异步不阻塞
- 音色任选（任意 MiniMax `voice_id` 或内置别名），音量 / 语速可配
- 两种 Agent 集成：**Skill**（行为规则）+ **Hermes 原生插件**（`notify_voice` 工具）
- 成本极低：约 0.006 元/次（speech-2.8-turbo，2 元/万字符）

---

## 安装

### 方式 A：作为 Hermes 原生插件（推荐）

```bash
hermes plugins install <owner>/<repo> --enable
```

手动安装：把**仓库根目录**整体复制到 `$HERMES_HOME/plugins/minimax-notify/`，
然后 `hermes plugins enable minimax-notify`。

装完提供 `notify_voice` 工具（模型可直接调用，不必绕 terminal）。

### 方式 B：作为 Hermes Skill

把 `skill/` 拷进 `$HERMES_HOME/skills/hermes/minimax-notify/`：

```powershell
$dst = "$env:LOCALAPPDATA\hermes\skills\hermes\minimax-notify"
New-Item -ItemType Directory -Force "$dst\scripts" | Out-Null
Copy-Item skill\SKILL.md $dst
Copy-Item skill\scripts\* "$dst\scripts"
```

### ⚠️ 装完必须做的一步：补全触发机制

只装上面两样，Agent **基本不会主动播报** —— skill 是"按需加载"的（想不起来读就等于不存在），
工具描述也只是"能力说明"。

真正稳定的触发靠**每轮都注入**的常驻指令：把下面这段**追加**进 `%LOCALAPPDATA%\hermes\SOUL.md`
（**追加，不要覆盖**原有内容）：

```markdown
- **出声提醒**：干活会主动用 minimax-notify 报进度——任务开始、阶段性进展、完成、出状况、有好消息，都值得喊一声提示音+一句话语音。**任务结束务必发语音提醒**，除非是简单回复这类秒完成的小事；默认多喊，安静需要理由
```

- SOUL.md 是英文默认模板 → 用 `AGENT.md` §3 的英文版
- 只想在某个项目启用 → 写进该项目的 `AGENTS.md` / `.hermes.md`

**详细步骤见 [`AGENT.md`](AGENT.md)** —— 可以把这份文件直接丢给你的 Agent，让它自己装。

---

## 配置

### 密钥

本仓库**不含密钥**。到 platform.minimaxi.com → 账户管理 → 接口密钥 申请，
然后写进脚本同目录的 `key.txt`（一行，`#` 开头为注释）：

```
sk-xxxxxxxx...
```

也支持环境变量 `MINIMAX_API_KEY`（优先级更高）。模板见 `key.txt.example`。

### 默认参数

`config.json`（与脚本同目录）：

| 字段 | 默认值 | 说明 |
| --- | --- | --- |
| `voice` | `Chinese (Mandarin)_Southern_Young_Man` | 音色 id，或内置别名 |
| `sound` | `ding` | 默认提示音 |
| `model` | `speech-2.8-turbo` | TTS 模型 |
| `vol` | `1.5` | 音量 0–10 |
| `speed` | `1.0` | 语速 |

优先级：**命令行参数 > `config.json` > 代码默认值**。

---

## 用法

```bash
python minimax-notify.py "文本"                  # 默认同步：播完才返回（保证出声）
python minimax-notify.py --async "文本"          # 异步：立即返回，子进程播放
python minimax-notify.py -s alert "出状况了"      # 提示音
python minimax-notify.py -v yujie "换个音色"      # 音色（别名或任意 voice_id）
python minimax-notify.py --voices                # 列出预置音色与提示音
python minimax-notify.py --no-play -o out.wav "只合成不播放"
```

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `text` | 播报文本（必填） | - |
| `-s/--sound` | `ding` / `double` / `alert` / `chime` / `none` | ding |
| `-v/--voice` | 音色 id 或内置别名 | `config.json` |
| `-m/--model` | TTS 模型 | speech-2.8-turbo |
| `--vol` | 音量 0–10 | 1.5 |
| `--speed` | 语速 | 1.0 |
| `-o/--out` | 保存音频到指定路径 | - |
| `--no-play` | 只合成不播放 | - |
| `--async` | 异步播放（默认同步） | - |

内置音色别名：`news_anchor` / `announcer` / `yujie` / `tianmei` / `robot` / `bestie` / `qingse` / `jingying`

---

## 目录结构

```text
.
├── plugin.yaml           Hermes 原生插件清单（仓库根即插件目录）
├── __init__.py           注册 notify_voice 工具
├── minimax-notify.py     实现脚本（唯一实现）
├── config.json           默认参数
├── key.txt.example       密钥模板
├── skill/                Skill 形态（可选安装）
│   ├── SKILL.md
│   └── scripts/…
├── AGENT.md              给 Agent 的安装与配置指南（含触发机制补全）
└── LICENSE
```

---

## 工作原理

1. `synthesize()` 调 MiniMax 同步 TTS 接口 `POST /v1/t2a_v2`，拿回 hex 音频
2. （主地址失败自动试备用 `api-bj.minimaxi.com`）
3. `play_wav()` 写临时 wav → Windows `winsound` 阻塞播放 → 删除临时文件
4. 播放前先 `play_sound()` 用 `winsound.Beep` 生成提示音（零成本、零延迟）
5. 合成失败时降级为"只响提示音"并以 exit 2 报错，不静默失败

文档：https://platform.minimaxi.com/docs/api-reference/speech-t2a-http

---

## 许可

MIT License —— 见 [`LICENSE`](LICENSE)。
