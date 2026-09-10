# AGENT_SETUP.md —— 给 Hermes Agent 的安装与配置指南

> 本文件写给**另一个 Hermes Agent** 看：用户把 Hermes_notify_voice 交给你，让你在这台机器上装好它。
> 照下面的步骤执行即可，**不要反问用户本文件已经写明的内容**。只有遇到真实歧义（选哪个版本、密钥从哪来）才停下来问。

---

## 0. 目标

在本机装好语音播报，使 Agent 能在「任务开始 / 阶段性进展 / 任务完成 / 出状况 / 有好消息」时，用一句话语音提醒用户。

装完应满足：

- 命令行能出声：`python <脚本> -s ding "测试"`
- Agent **每一轮都记得**该播报 —— 这靠 §3 的补全，光装文件做不到

---

## 1. 前置检查（先跑，别跳）

```bash
python --version      # 需 3.8+
```

| 项 | 要求 |
| --- | --- |
| 平台 | **Windows**（播放走系统自带的 `winsound`，无需额外安装任何软件） |
| Python | 3.8+，只用标准库（`urllib` / `subprocess` / `winsound`） |

**密钥**：

- 脚本同目录的 `key.txt`（一行，`#` 开头为注释）
- **若来源是分发包**：包内通常已带 `key.txt`，开箱即用，无需额外配置
- **若来源是本开源仓库**：**不含密钥**，需自己申请（platform.minimaxi.com → 账户管理 → 接口密钥）后写进 `key.txt`
- 也支持环境变量 `MINIMAX_API_KEY`（优先级更高）

**不要把密钥提交到 git、贴到聊天里或写进日志。**

---

## 2. 选版本 + 安装

### 2.0 先选版本（二选一，别都装）

| 版本 | 目录 | 默认音色 | 特点 |
| --- | --- | --- | --- |
| **普通话版** | `mandarin/` | `Chinese (Mandarin)_Southern_Young_Man` | 日常「干活报进度」 |
| **粤语学习者版** | `cantonese/` | `Cantonese_GentleLady` + `language_boost: Chinese,Yue` | 粤语播报，要求用**粤语词**并在回复正文附**普通话对照** |

**两版二选一**：skill 名（`minimax-notify` / `minimax-notify-yue`）、插件 id、工具名 `notify_voice`
都会重名，同时装会互相覆盖。**问用户要哪版**；用户没偏好就选普通话版。

下面用 `<版本>` 表示选定的目录（`mandarin` 或 `cantonese`）。

### 2.1 插件形态（提供 `notify_voice` 工具）

把 `<版本>/` 里这 **5 个文件**复制到 `$HERMES_HOME/plugins/<插件名>/`（**必须同处一个目录**）：

| 版本 | `<插件名>` |
| --- | --- |
| 普通话版 | `minimax-notify` |
| 粤语版 | `minimax-notify-yue` |

```text
plugin.yaml
__init__.py
minimax-notify.py     # 脚本必须和插件放在一起（插件按自身目录解析路径）
config.json
key.txt
```

然后**必须启用**（第三方插件默认不加载）：

```bash
hermes plugins enable minimax-notify        # 粤语版：minimax-notify-yue
```

`hermes plugins list` 显示 `enabled` 才算装好；`config.yaml` 里会出现 `plugins.enabled: [..., minimax-notify]`。

脚本路径可用环境变量 `MINIMAX_NOTIFY_SCRIPT` 覆盖（默认取插件目录下的 `minimax-notify.py`）。

### 2.2 Skill 形态

目标路径：`$HERMES_HOME/skills/<分类>/<skill名>/`（Windows 默认 `%LOCALAPPDATA%\hermes\skills\`）

| 版本 | `<skill名>` |
| --- | --- |
| 普通话版 | `minimax-notify` |
| 粤语版 | `minimax-notify-yue` |

```powershell
# 普通话版示例
$dst = "$env:LOCALAPPDATA\hermes\skills\hermes\minimax-notify"
New-Item -ItemType Directory -Force "$dst\scripts" | Out-Null
Copy-Item mandarin\skill\SKILL.md $dst
Copy-Item mandarin\skill\scripts\* "$dst\scripts"
```

密钥随包带上（`scripts/key.txt`），复制时已一并就位。

**生效方式**：不需要重启，新会话里 Agent 读到 SKILL.md 就会按节奏调用。

---

## 3. 补全触发机制（**必做**，不做的话基本不会播报）

装完上面两样**还不够** —— 关键问题是：**谁来触发播报？**

| 路径 | 加载时机 | 可靠性 |
| --- | --- | --- |
| `skill/SKILL.md` | **按需加载**（Agent 主动读才进上下文） | 低 —— 想不起来读，规则等于不存在 |
| `notify_voice` 工具描述 | 工具列表里一行 | 低 —— 属"能力说明"，模型注意力低 |
| **`$HERMES_HOME/SOUL.md`** | **每轮都注入身份槽位** | **高** |

所以要补上第三层：**把播报规范追加进 `$HERMES_HOME/SOUL.md`**
（Windows 默认 `%LOCALAPPDATA%\hermes\SOUL.md`）。

**追加，不要覆盖原有内容。** 没有"工作规范"这一节就在末尾新建。

**普通话版**追加这段：

```markdown
## 工作规范

- **出声提醒**：干活会主动用 minimax-notify 报进度——任务开始、阶段性进展、完成、出状况、有好消息，都值得喊一声提示音+一句话语音。**任务结束务必发语音提醒**，除非是简单回复这类秒完成的小事；默认多喊，安静需要理由
```

**粤语版**改用 `cantonese/SOUL_SNIPPET.md` 里那段（多两条硬要求：播报必须用粤语词 + 每条附普通话对照）：

```markdown
- **粤语播报 + 粤语用词 + 普通话对照（硬要求）**：语音提醒一律用粤语（白话）说……**每条播报都必须在回复正文里写出它的普通话意思**，一条一行，格式 `🔊 粤语原文 → 普通话`；收尾那条也要写。只说粤语不给对照 = 没做到。
```

SOUL.md 还是英文默认模板的话，可按上面语义写一版英文，或直接在中文段落后追加。

**只想在某个项目里启用的替代方案**：写进该项目的 `AGENTS.md` 或 `.hermes.md`。

**写入后确认**（用 Hermes 自己的加载器验）：

```bash
python -c "from agent.prompt_builder import load_soul_md; s=load_soul_md(); print(len(s))"
# 期望：非 0
```

> 原理：`SOUL.md` 由 `agent/prompt_builder.py: load_soul_md()` 读取，注入系统提示的**身份槽位**
> （替换默认身份，不是追加在末尾），因此**每一轮都在场**。skill 只在被主动加载时进上下文。

---

## 4. 配置

`config.json` 与脚本同目录：

| 字段 | 普通话版 | 粤语版 | 说明 |
| --- | --- | --- | --- |
| `voice` | `Chinese (Mandarin)_Southern_Young_Man` | `Cantonese_GentleLady` | 音色 id 或内置别名 |
| `language_boost` | *(无)* | `"Chinese,Yue"` | 语言增强（只认 `Chinese` / `Chinese,Yue` / `auto`） |
| `sound` | `ding` | `ding` | 提示音 |
| `model` | `speech-2.8-turbo` | 同 | TTS 模型 |
| `vol` | `1.5` | 同 | 音量 0–10 |
| `speed` | `1.0` | 同 | 语速 |

优先级：**命令行参数 > `config.json` > 代码默认值**。
要改默认音色 / 音量 / 语言，**只改 `config.json`，不要改代码**。

⚠️ **两个 `config.json` 要一起改**：skill 形态走 `skill/scripts/config.json`，插件形态走插件目录的 `config.json`。
只改一个会出现「命令行是粤语、工具调用还是普通话」。

---

## 5. 验证

**播放链路**：

```bash
# 普通话版
python <脚本路径> -s ding "安装测试，能听到吗"

# 粤语版（应听到粤语，stdout 显示 voice=Cantonese_GentleLady）
python <脚本路径> -s ding "开始做嘢喇，等几分钟"
```

成功标志：先听到"叮"，再听到一句话；stdout 出现 `[ok:sync] ...` 且带 `trace` 字段。

**粤语版额外验证 `language_boost` 生效**（同一句走两条读音通道，音频时长不同）：

```bash
python <脚本路径> --no-play -o t.wav --lang "" "开始做嘢喇，等几分钟"
python <脚本路径> --no-play -o t.wav --lang "Chinese,Yue" "开始做嘢喇，等几分钟"
```

**触发是否补全** —— 开一个**新会话**，让它干一件多步的活，观察：

- [ ] 开场有播报
- [ ] 过程中有进展播报
- [ ] 任务结束必有一条
- [ ] 每次回复收尾有声音
- [ ] （粤语版）每条播报在回复正文里都有 `🔊 粤语 → 普通话` 对照

---

## 6. 故障排查

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 没声音，但 stdout 有 `[ok:sync]` | 系统静音 / 输出设备不对 | 检查系统音量与默认播放设备 |
| `错误: 未找到 API key` | 脚本目录没有 `key.txt`，也没设环境变量 | 放 `key.txt` 或设 `MINIMAX_API_KEY` |
| `合成失败，仅播了提示音`（exit 2） | 密钥无效 / 余额不足 / 网络不通 | 核对密钥与 MiniMax 账户余额 |
| 工具 `notify_voice` 不存在 | 插件未启用 | `hermes plugins enable <插件名>` |
| 插件加载报错 | 脚本没和插件放一起 | 把 `minimax-notify.py` 放进插件目录，或设 `MINIMAX_NOTIFY_SCRIPT` |
| 提示 `当前环境不支持 winsound` | 不是 Windows 环境 | 本包仅支持 Windows |
| **装好了但从不播报** | **§3 没做**（缺 SOUL.md 常驻指令） | 回 §3 补上，再开新会话验证 |
| **粤语版发音是普通话** | 没传 `language_boost` | `config.json` 里加 `"language_boost": "Chinese,Yue"` |
| `接口错误 2013: invalid params: language_boost` | 值写错 | 只认 `Chinese` / `Chinese,Yue` / `auto` |
| `接口错误 2054: voice id not exist` | 用了不存在的粤语音色 | 本账号只有 6 个可用（`yue_gentle` / `yue_kind` / `yue_cute` / `yue_playful` / `yue_host_f` / `yue_host_m`） |
| 工具调用是普通话、命令行是粤语 | 只改了一个 `config.json` | 两个都改（见 §4） |

补了 SOUL.md 还不播时的排查顺序：

1. SOUL.md 确实非空、且这段落在文件内（`load_soul_md()` 读的就是 `$HERMES_HOME/SOUL.md`）
2. SOUL.md 过大 → 按上下文长度截断；`strip_legacy_protocol` 会清掉旧的 Bot Mode 段落
3. cron / `hermes chat -q` 一次性会话可能走 `skip_context_files`，身份槽位行为不同
4. 播放链路：key 有效？系统音量？`notify_voice` 返回 `success: true`？

---

## 7. 做完之后

- 向用户汇报：装了**哪个版本**、装到哪个路径、验证输出、当前音色、**§3 是否已补**
- 如果你是 Hermes 且装了 Skill：以后干活按对应 `SKILL.md` 的播报节奏执行
  （每条用户消息最多 2 条，收尾必播一条；粤语版还要附普通话对照）
- `key.txt` 不进 git、不贴聊天、不写日志
