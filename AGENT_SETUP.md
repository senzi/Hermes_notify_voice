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

## 1. 开工前：先问用户 + 查环境（别跳）

### 1.1 环境检查

```bash
python --version      # 需 3.8+
```

| 项 | 要求 |
| --- | --- |
| 平台 | **Windows**（播放走系统自带的 `winsound`，无需额外安装任何软件） |
| Python | 3.8+，只用标准库（`urllib` / `subprocess` / `winsound`） |

### 1.2 先问用户四件事（**交互**：合并成一次问，别挤牙膏）

> 装这个语音播报，先确认四件事：
> 1. 要**哪个版本**？普通话版（日常报进度）/ 粤语学习者版（粤语播报 + 附普通话对照）
> 2. 你有 MiniMax 的 API key 吗？
> 3. 注册过 MiniMax 开放平台账号吗？
> 4. 账户充过钱吗（余额够不够）？

**Q1 · 选版本**：

| 版本 | 目录 | 默认音色 | 适合谁 |
| --- | --- | --- | --- |
| **普通话版** | `mandarin/` | `Chinese (Mandarin)_Southern_Young_Man` | 日常「干活报进度」—— **用户没偏好就选这个** |
| **粤语学习者版** | `cantonese/` | `Cantonese_GentleLady` + `language_boost: Chinese,Yue` | 想把语音提醒变成粤语输入、顺便泡耳朵 |

- 粤语版额外要求：播报**用粤语词**（讲「做嘢」唔讲「干活」），且每条都在回复正文附 `🔊 粤语 → 普通话` 对照
- **两版二选一**：skill 名 / 插件 id / 工具名（`notify_voice`）都会重名，同时装会互相覆盖
- 选定后记下：`<版本>` = `mandarin` 或 `cantonese`，对应插件名 / skill 名见 §2 开头

**Q2~Q4 · 账号与余额**，按回答分流：

| 情况 | 你要做的 |
| --- | --- |
| 三样都齐 | 直接进 §2 安装 |
| **没注册** | 给注册入口 https://platform.minimaxi.com/ ，说明「手机号注册，免费」 |
| **没 key** | 指路：登录后 →「账户管理」→「接口密钥」→ 创建密钥 → **当场复制保存**（只显示一次）。直达 https://platform.minimaxi.com/user-center/basic-information/interface-key |
| **没充值 / 不确定余额** | 充值 https://platform.minimaxi.com/user-center/payment/balance ；消费与充值记录 https://platform.minimaxi.com/console/recharge-records |
| 来源是**分发包**（已带 key） | Q1/Q2 可跳过，只需确认 Q3（余额） |

**开 key 三步**（可以直接念给用户听）：

1. 打开 https://platform.minimaxi.com/ → 手机号注册 / 登录
2. 左侧「账户管理」→「接口密钥」→ 创建密钥 → 命名 → 复制（**只显示一次，务必当场保存**）
3. 左侧「账户管理」→「余额」→ 充值（按量计费，充一点就够）

### 1.3 费率（先说清楚，别让人以为很贵）

**按字符计费**，本项目默认模型 `speech-2.8-turbo` = **2 元/万字符**
（官方定价页 https://platform.minimaxi.com/docs/guides/pricing-paygo 的「语音合成（TTS）」表）

计费口径：**1 个汉字 = 2 个字符**；英文字母、标点、空格、回车各算 1 个字符。

| 用量 | 花费 |
| --- | --- |
| 一句播报（~15 汉字 = 30 字符） | ≈ **0.006 元** |
| 一天 20 句 | ≈ 0.12 元 / 天（一个月 ≈ 3.6 元） |
| 一天 100 句 | ≈ 0.6 元 / 天（一个月 ≈ 18 元） |
| 充 10 元 | ≈ **1600 句**播报 |

模型选择：`speech-2.8-turbo`（2 元/万字符，本项目默认）；`speech-2.8-hd`（3.5 元/万字符，音质更好、一般用不上）。

> **不用买套餐**：语音套餐（¥360 起 / 200 万字符）是给每天几万句的量准备的，
> 按量充一点就够用很久 —— https://platform.minimaxi.com/docs/guides/pricing-speech

### 1.4 工具箱（按需把这些链接丢给用户）

| 用途 | 链接 |
| --- | --- |
| 开放平台首页 / 注册 | https://platform.minimaxi.com/ |
| 接口密钥（创建 / 查看） | https://platform.minimaxi.com/user-center/basic-information/interface-key |
| 充值 | https://platform.minimaxi.com/user-center/payment/balance |
| 充值 / 消费记录 | https://platform.minimaxi.com/console/recharge-records |
| 按量计费定价（含 TTS 费率表） | https://platform.minimaxi.com/docs/guides/pricing-paygo |
| 语音资源包（大用量才考虑） | https://platform.minimaxi.com/docs/guides/pricing-speech |
| TTS 接口文档 | https://platform.minimaxi.com/docs/api-reference/speech-t2a-http |

### 1.5 密钥放哪

- `key.txt`（一行，`#` 开头为注释）要放到**两个位置** —— 两种形态各读自己目录的：
  - 插件形态：`<版本>/key.txt`（跟着 5 个插件文件拷进 `plugins/<插件名>/`）
  - Skill 形态：`<版本>/skill/scripts/key.txt`
- 格式模板：`<版本>/key.txt.example`
- **若来源是分发包**：两处 `key.txt` 通常已内置，开箱即用
- **若来源是本开源仓库**：**不含密钥**，需按 §1.2 申请后放进上述两处
- 也支持环境变量 `MINIMAX_API_KEY`（优先级更高）

**不要把密钥提交到 git、贴到聊天里或写进日志。**

---

## 2. 安装（版本已在 §1.2 选定）

| 选定的版本 | `<版本>` 目录 | 插件名 / skill 名 |
| --- | --- | --- |
| 普通话版 | `mandarin` | `minimax-notify` |
| 粤语学习者版 | `cantonese` | `minimax-notify-yue` |

> ⚠️ 两版**只装一个**（skill 名 / 插件 id / 工具名重名会互相覆盖）。
> 粤语版装完还要在 §3 用 `cantonese/SOUL_SNIPPET.md` 那段补触发层。

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
**若来源是开源仓库**（不含密钥），需自己把 `key.txt` 放进这里的 `scripts/`。

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
