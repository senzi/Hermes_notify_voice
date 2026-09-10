# 粤语学习者版（cantonese）

默认音色 **`Cantonese_GentleLady`**（温柔女声），`language_boost: "Chinese,Yue"` 强制走粤语读音通道。
播报文本用**粤语词**，并在回复正文附**普通话对照** —— 适合想把自己泡在粤语里的使用者。

## 与普通话版的区别

| 项 | 普通话版 | **粤语版** |
| --- | --- | --- |
| 音色 | `Chinese (Mandarin)_Southern_Young_Man` | **`Cantonese_GentleLady`** |
| `config.json` | 无 `language_boost` | **`"language_boost": "Chinese,Yue"`** |
| 播报用词 | 普通话 | **粤语词**（做嘢 / 睇 / 搞掂 / 而家…） |
| 回复正文 | — | **每条播报附 `🔊 粤语 → 普通话` 对照** |
| skill 名 | `minimax-notify` | `minimax-notify-yue` |
| 插件 id | `minimax-notify` | `minimax-notify-yue` |
| 额外文件 | — | **`SOUL_SNIPPET.md`（触发层，必做）** |

## ⚠️ 必做第一步：补触发层

先把 [`SOUL_SNIPPET.md`](SOUL_SNIPPET.md) 里那段追加进你的 `$HERMES_HOME/SOUL.md`。
**不做这一步，Agent 不会主动用粤语播报**（skill 是按需加载的，工具描述也只是能力说明）。

## 装什么

结构与普通话版相同：插件形态（`plugin.yaml` / `__init__.py` / `minimax-notify.py` / `config.json` / `key.txt`）+ Skill 形态（`skill/`）。
安装步骤见 [`../AGENT_SETUP.md`](../AGENT_SETUP.md)。

```text
cantonese/
├── SOUL_SNIPPET.md        ★ 触发层（先做这个）
├── key.txt.example        ← 密钥模板（key.txt 要放两处，见「密钥」）
├── plugin.yaml            ┐
├── __init__.py            │ 插件形态（提供 notify_voice 工具）
├── minimax-notify.py      │
├── config.json            │
└── skill/                 Skill 形态
    ├── SKILL.md           （含粤语用词对照表 + 三条硬规则）
    └── scripts/{py, config.json}
```

## 密钥

本仓库**不含密钥**。到 platform.minimaxi.com → 账户管理 → 接口密钥 申请，
然后写进 `key.txt`（一行，`#` 开头为注释）。

`key.txt` 要放到**两个位置** —— 两种形态各读自己目录的：

| 装的形态 | key.txt 放哪 |
| --- | --- |
| 插件形态 | `cantonese/key.txt`（跟着 5 个插件文件一起拷进 `plugins/minimax-notify-yue/`） |
| Skill 形态 | `cantonese/skill/scripts/key.txt` |

格式模板见 [`key.txt.example`](key.txt.example)（复制改名即可）。也支持环境变量 `MINIMAX_API_KEY`（优先级更高）。

## 快速验证

```bash
# 在版本目录内执行（cd cantonese）
# 1) 听到的是粤语（不是普通话），stdout 显示 voice=Cantonese_GentleLady
python minimax-notify.py -s ding "开始做嘢喇，等几分钟"

# 2) language_boost 真的在起作用：同一句走两条不同读音通道，音频时长不同
python minimax-notify.py --no-play -o t.wav --lang "" "开始做嘢喇，等几分钟"
python minimax-notify.py --no-play -o t.wav --lang "Chinese,Yue" "开始做嘢喇，等几分钟"
```

## 可用粤语音色（本账号实测 6 个）

| 别名 | voice_id | 说明 |
| --- | --- | --- |
| `yue_kind` | `Cantonese_KindWoman` | 善良女声 |
| **`yue_gentle`** | **`Cantonese_GentleLady`** | **温柔女声（当前默认）** |
| `yue_cute` | `Cantonese_CuteGirl` | 可爱女孩 |
| `yue_playful` | `Cantonese_PlayfulMan` | 活泼男声 |
| `yue_host_f` | `Cantonese_ProfessionalHost（F)` | 专业女主持 |
| `yue_host_m` | `Cantonese_ProfessionalHost（M)` | 专业男主持 |

⚠️ 括号是全角「（」+ 半角「)」，复制时别改。
其它粤语 id（`Cantonese_Male_1`、`Cantonese_News_Anchor`、`female-yue-1`…）**一律报 2054 不存在**。

## 常见坑

见 [`skill/SKILL.md`](skill/SKILL.md) 的 Pitfalls：2054 音色不存在 / 2013 `language_boost` 写错 /
两个 `config.json` 必须一起改（只改一个会出现「命令行粤语、工具调用普通话」）。
