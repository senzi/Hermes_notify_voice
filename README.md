# Hermes_notify_voice

给 AI Agent 用的**本地语音播报** CLI（命令与包名：`minimax-notify`）。
MiniMax TTS 合成一句话 + 系统提示音，在任务开始 / 进展 / 完成 / 出状况时喊你一声 —— 不用一直盯着屏幕。

**Windows · 单文件 · 零第三方依赖**（只用 Python 标准库）

---

## 两个版本，选一个装

| 版本 | 目录 | 默认音色 | 适合谁 |
| --- | --- | --- | --- |
| **普通话版** | [`mandarin/`](mandarin/) | `Chinese (Mandarin)_Southern_Young_Man` | 日常「干活报进度」 |
| **粤语学习者版** | [`cantonese/`](cantonese/) | `Cantonese_GentleLady` + `language_boost: Chinese,Yue` | 想把语音提醒变成粤语输入、顺便泡耳朵 |

粤语版除了音色与语言，还要求播报**用粤语词**（讲「做嘢」唔讲「干活」），并在回复正文附**普通话对照**。

> ⚠️ 两版**二选一安装** —— skill 名、插件 id、工具名（`notify_voice`）都会重名，同时装会互相覆盖。

---

## 特性

- 一句话就能播报：`python minimax-notify.py "任务完成，可以看结果了"`
- 先响提示音再说话（`ding` / `double` / `alert` / `chime` / `none`）
- 默认**同步**播放（播完才返回，保证出声）；`--async` 可切异步不阻塞
- 音色任选（任意 MiniMax `voice_id` 或内置别名），音量 / 语速 / 语言可配
- 两种 Agent 集成：**Skill**（行为规则）+ **Hermes 原生插件**（`notify_voice` 工具）
- 成本极低：约 0.006 元/次（speech-2.8-turbo，2 元/万字符）

---

## 安装

两个版本目录里是同一套结构：

```text
<版本>/
├── plugin.yaml            ┐
├── __init__.py            │ 插件形态（notify_voice 工具）
├── minimax-notify.py      │   ——这 5 个文件必须同处一个目录
├── config.json            │
├── key.txt.example        ┘
└── skill/                 Skill 形态（行为规则）
    ├── SKILL.md
    └── scripts/{minimax-notify.py, config.json, key.txt.example}
```

### 方式 A：Hermes 原生插件

把该版本目录里的 5 个插件文件复制到 `$HERMES_HOME/plugins/<插件名>/`：

| 版本 | 插件名 |
| --- | --- |
| 普通话版 | `minimax-notify` |
| 粤语版 | `minimax-notify-yue` |

```bash
hermes plugins enable minimax-notify       # 粤语版换成 minimax-notify-yue
```

### 方式 B：Hermes Skill

```powershell
# 普通话版
$dst = "$env:LOCALAPPDATA\hermes\skills\hermes\minimax-notify"
New-Item -ItemType Directory -Force "$dst\scripts" | Out-Null
Copy-Item mandarin\skill\SKILL.md $dst
Copy-Item mandarin\skill\scripts\* "$dst\scripts"
```

粤语版把 `mandarin\` 换成 `cantonese\`、改 `minimax-notify` 为 `minimax-notify-yue`。

### ⚠️ 方式 C（必做）：补全触发机制

只装上面两样，Agent **基本不会主动播报** —— skill 是"按需加载"的（想不起来读就等于不存在），
工具描述也只是"能力说明"。

真正稳定的触发靠**每轮都注入**的常驻指令 —— 把这段**追加**进 `%LOCALAPPDATA%\hermes\SOUL.md`
（**追加，不要覆盖**原有内容）：

```markdown
- **出声提醒**：干活会主动用 minimax-notify 报进度——任务开始、阶段性进展、完成、出状况、有好消息，都值得喊一声提示音+一句话语音。**任务结束务必发语音提醒**，除非是简单回复这类秒完成的小事；默认多喊，安静需要理由
```

**粤语版**改用 [`cantonese/SOUL_SNIPPET.md`](cantonese/SOUL_SNIPPET.md) 里那段
（多了两条硬要求：播报必须用粤语词 + 每条都要附普通话对照）。

> 详细步骤见 **[`AGENT_SETUP.md`](AGENT_SETUP.md)** —— 可以直接把这份文件丢给你的 Agent，让它自己装。

---

## 配置

### 密钥

本仓库**不含密钥**。到 platform.minimaxi.com → 账户管理 → 接口密钥 申请，
写进脚本同目录的 `key.txt`（一行，`#` 开头为注释）。模板见 `key.txt.example`。
也支持环境变量 `MINIMAX_API_KEY`（优先级更高）。

### 默认参数

`config.json`（与脚本同目录）：

| 字段 | 普通话版 | 粤语版 | 说明 |
| --- | --- | --- | --- |
| `voice` | `Chinese (Mandarin)_Southern_Young_Man` | `Cantonese_GentleLady` | 音色 id 或内置别名 |
| `language_boost` | *(无)* | `"Chinese,Yue"` | 语言增强；粤语不传就是普通读音 |
| `sound` | `ding` | `ding` | 默认提示音 |
| `model` | `speech-2.8-turbo` | 同 | TTS 模型 |
| `vol` | `1.5` | 同 | 音量 0–10 |
| `speed` | `1.0` | 同 | 语速 |

优先级：**命令行参数 > `config.json` > 代码默认值**。

---

## 用法

```bash
python minimax-notify.py "文本"                  # 默认同步：播完才返回（保证出声）
python minimax-notify.py --async "文本"          # 异步：立即返回，子进程播放
python minimax-notify.py -s alert "出状况了"      # 提示音
python minimax-notify.py -v yue_gentle "换个音色" # 音色（别名或任意 voice_id）
python minimax-notify.py --lang "Chinese,Yue" "粤语一句"
python minimax-notify.py --voices                # 列出预置音色与提示音
python minimax-notify.py --no-play -o out.wav "只合成不播放"
```

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `text` | 播报文本（必填） | - |
| `-s/--sound` | `ding` / `double` / `alert` / `chime` / `none` | ding |
| `-v/--voice` | 音色 id 或内置别名 | `config.json` |
| `-m/--model` | TTS 模型 | speech-2.8-turbo |
| `--lang` | `Chinese` / `Chinese,Yue` / `auto`（留空不传） | `config.json` |
| `--vol` | 音量 0–10 | 1.5 |
| `--speed` | 语速 | 1.0 |
| `-o/--out` | 保存音频到指定路径 | - |
| `--no-play` | 只合成不播放 | - |
| `--async` | 异步播放（默认同步） | - |

**普通话音色别名**：`news_anchor` / `announcer` / `yujie` / `tianmei` / `robot` / `bestie` / `qingse` / `jingying`

**粤语音色别名**：`yue_gentle`（默认）/ `yue_kind` / `yue_cute` / `yue_playful` / `yue_host_f` / `yue_host_m`

---

## 目录结构

```text
Hermes_notify_voice/
├── mandarin/                  普通话版
│   ├── README.md
│   ├── plugin.yaml / __init__.py / minimax-notify.py / config.json / key.txt.example
│   └── skill/{SKILL.md, scripts/…}
├── cantonese/                 粤语学习者版
│   ├── README.md
│   ├── SOUL_SNIPPET.md        ★ 触发层（必做）
│   ├── plugin.yaml / __init__.py / minimax-notify.py / config.json / key.txt.example
│   └── skill/{SKILL.md, scripts/…}
├── AGENT_SETUP.md             给 Agent 的安装与配置指南
├── CHANGELOG.md
└── LICENSE
```

---

## 工作原理

1. `synthesize()` 调 MiniMax 同步 TTS 接口 `POST /v1/t2a_v2`，拿回 hex 音频
   （主地址失败自动试备用 `api-bj.minimaxi.com`；粤语需带 `language_boost: "Chinese,Yue"`）
2. `play_wav()` 写临时 wav → Windows `winsound` 阻塞播放 → 删除临时文件
3. 播放前先 `play_sound()` 用 `winsound.Beep` 生成提示音（零成本、零延迟）
4. 合成失败时降级为"只响提示音"并以 exit 2 报错，不静默失败

文档：https://platform.minimaxi.com/docs/api-reference/speech-t2a-http

---

## 许可

MIT License —— 见 [`LICENSE`](LICENSE)。
