# AGENT.md —— 给 Hermes Agent 的安装与配置指南

> 本文件写给**另一个 Hermes Agent** 看：用户把 minimax-notify 交给你，让你在这台机器上装好它。
> 照下面的步骤执行即可，**不要反问用户本文件已经写明的内容**。只有遇到真实歧义（密钥从哪来）才停下来问。

---

## 0. 目标

在本机装好 minimax-notify，使 Agent 能在「任务开始 / 阶段性进展 / 任务完成 / 出状况 / 有好消息」时，用一句话语音提醒用户。

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
- **若来源是开源仓库**：**不含密钥**，需自己申请（platform.minimaxi.com → 账户管理 → 接口密钥）后写进 `key.txt`
- 也支持环境变量 `MINIMAX_API_KEY`（优先级更高）

**不要把密钥提交到 git、贴到聊天里或写进日志。**

---

## 2. 安装（两种形态，建议都装）

| 形态 | 目录 | 作用 |
| --- | --- | --- |
| Skill | `skill/` | 告诉 Agent「什么时候该播报」（行为规则） |
| 原生插件 | `hermes-plugin/` | 提供 `notify_voice` 工具，模型可直接调用 |

**两者配合最好**：skill 定播报节奏，插件给工具。
只装 skill 也能用（Agent 走命令行调脚本），装上插件后模型不必绕 terminal。

### 2A. Skill 形态

目标路径：`$HERMES_HOME/skills/<任意分类>/minimax-notify/`
（Windows 默认 `%LOCALAPPDATA%\hermes\skills\`）

```powershell
$dst = "$env:LOCALAPPDATA\hermes\skills\hermes\minimax-notify\scripts"
New-Item -ItemType Directory -Force $dst | Out-Null
Copy-Item skill\SKILL.md "$env:LOCALAPPDATA\hermes\skills\hermes\minimax-notify\"
Copy-Item skill\scripts\* $dst
```

密钥随包带上（`scripts/key.txt`），复制时已一并就位。

**生效方式**：不需要重启，新会话里 Agent 读到 SKILL.md 就会按节奏调用。

### 2B. 原生插件形态（提供 `notify_voice` 工具）

目标路径：`$HERMES_HOME/plugins/minimax-notify/`，需要这些文件（**必须同处一个目录**）：

```text
plugin.yaml
__init__.py
minimax-notify.py     # 脚本必须和插件放在一起（插件按自身目录解析路径）
config.json
key.txt
```

**若来源是 git 仓库、且仓库根就是插件目录**（开源仓库即如此），可直接一条命令装：

```bash
hermes plugins install <owner>/<repo> --enable
```

**必须启用**（第三方插件默认不加载）：

```bash
hermes plugins enable minimax-notify
```

`hermes plugins list` 显示 `enabled` 才算装好；`config.yaml` 里会出现 `plugins.enabled: [..., minimax-notify]`。

脚本路径可用环境变量 `MINIMAX_NOTIFY_SCRIPT` 覆盖（默认取插件目录下的 `minimax-notify.py`）。

---

## 3. 补全触发机制（**必做**，不做的话基本不会播报）

装完上面两个文件**还不够** —— 关键问题是：**谁来触发播报？**

| 路径 | 加载时机 | 可靠性 |
| --- | --- | --- |
| `skill/SKILL.md` | **按需加载**（Agent 主动读才进上下文） | 低 —— 想不起来读，规则等于不存在 |
| `notify_voice` 工具描述 | 工具列表里一行 | 低 —— 属"能力说明"，模型注意力低 |
| **`$HERMES_HOME/SOUL.md`** | **每轮都注入身份槽位** | **高** |

所以要动手补上第三层：**把播报规范追加进 `$HERMES_HOME/SOUL.md`**
（Windows 默认 `%LOCALAPPDATA%\hermes\SOUL.md`；先确认路径：`python -c "from hermes_cli.config import get_hermes_home; print(get_hermes_home() / 'SOUL.md')"`）。

**追加，不要覆盖原有内容。** 没有"工作规范"这一节就在末尾新建：

```markdown
## 工作规范

- **出声提醒**：干活会主动用 minimax-notify 报进度——任务开始、阶段性进展、完成、出状况、有好消息，都值得喊一声提示音+一句话语音。**任务结束务必发语音提醒**，除非是简单回复这类秒完成的小事；默认多喊，安静需要理由
```

如果 SOUL.md 还是英文默认模板，用这段等效英文版：

```markdown
## Working conventions

- **Voice notifications**: proactively announce progress with minimax-notify — task start, milestones, completion, problems, good news. Always play a voice alert when a task finishes, unless it was a trivial one-line reply. Default to notifying; silence needs a reason.
```

**只想在某个项目里启用的替代方案**：写进该项目的 `AGENTS.md` 或 `.hermes.md`：

```markdown
## 语音提醒

- 任务开始 / 阶段性进展 / 任务完成 / 出状况时，调用 `notify_voice` 工具，
  或运行 `python <skill目录>/scripts/minimax-notify.py "一句话"`
- 每条用户消息最多播 2 条；回复收尾必播一条
```

> 原理：`SOUL.md` 由 `agent/prompt_builder.py: load_soul_md()` 读取，注入系统提示的**身份槽位**
> （替换默认身份，不是追加在末尾），因此**每一轮都在场**。skill 只在被主动加载时进上下文。

---

## 4. 配置

`config.json` 与脚本同目录，字段：

| 字段 | 默认值 | 说明 |
| --- | --- | --- |
| `voice` | `Chinese (Mandarin)_Southern_Young_Man` | 音色 id，或脚本内置别名（`--voices` 查看） |
| `sound` | `ding` | 提示音：ding / double / alert / chime / none |
| `model` | `speech-2.8-turbo` | TTS 模型 |
| `vol` | `1.5` | 音量 0–10 |
| `speed` | `1.0` | 语速 |

优先级：**命令行参数 > `config.json` > 代码默认值**。
要改默认音色或音量，**只改 `config.json`，不要改代码**。

---

## 5. 验证

**播放链路**：

```bash
python <脚本路径> -s ding "安装测试，能听到吗"
```

成功标志：先听到"叮"，再听到这句话；stdout 出现 `[ok:sync] ...` 且带 `trace` 字段。

```bash
python <脚本路径> --voices      # 列出可用音色别名与提示音（不出声）
```

**触发是否补全** —— 开一个**新会话**，让它干一件多步的活，观察：

- [ ] 开场有播报
- [ ] 过程中有进展播报
- [ ] 任务结束必有一条
- [ ] 每次回复收尾有声音

---

## 6. 故障排查

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 没声音，但 stdout 有 `[ok:sync]` | 系统静音 / 输出设备不对 | 检查系统音量与默认播放设备 |
| `错误: 未找到 API key` | 脚本目录没有 `key.txt`，也没设环境变量 | 放 `key.txt` 或设 `MINIMAX_API_KEY` |
| `合成失败，仅播了提示音`（exit 2） | 密钥无效 / 余额不足 / 网络不通 | 核对密钥与 MiniMax 账户余额 |
| 工具 `notify_voice` 不存在 | 插件未启用 | `hermes plugins enable <name>` |
| 插件加载报错 | 脚本没和插件放一起 | 把 `minimax-notify.py` 放进插件目录，或设 `MINIMAX_NOTIFY_SCRIPT` |
| 提示 `当前环境不支持 winsound` | 不是 Windows 环境 | 本包仅支持 Windows |
| **装好了但从不播报** | **§3 没做**（缺 SOUL.md 常驻指令） | 回 §3 补上，再开新会话验证 |
| 补了 SOUL.md 仍不播 | 内容被截断 / 是 cron 等子会话 | 见下 |

补了 SOUL.md 还不播时的排查顺序：

1. SOUL.md 确实非空、且这段落在文件内（`load_soul_md()` 读的就是 `$HERMES_HOME/SOUL.md`）
2. SOUL.md 过大 → 按上下文长度截断；`strip_legacy_protocol` 会清掉旧的 Bot Mode 段落
3. cron / `hermes chat -q` 一次性会话可能走 `skip_context_files`，身份槽位行为不同
4. 播放链路：key 有效？系统音量？`notify_voice` 返回 `success: true`？

---

## 7. 做完之后

- 向用户汇报：装到哪个路径、验证输出、当前音色、**§3 是否已补**
- 如果你是 Hermes 且装了 Skill：以后干活按 `SKILL.md` 的播报节奏执行（每条用户消息最多 2 条，收尾必播一条）
- `key.txt` 不进 git、不贴聊天、不写日志
