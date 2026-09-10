# 普通话版（mandarin）

默认音色 `Chinese (Mandarin)_Southern_Young_Man`，`language_boost` 留空 —— 日常「干活报进度」用这版。

## 装什么

| 用途 | 需要哪些文件 |
| --- | --- |
| **Skill 形态** | `skill/SKILL.md` + `skill/scripts/`（脚本、`config.json`、`key.txt`） |
| **插件形态** | `plugin.yaml` + `__init__.py` + `minimax-notify.py` + `config.json` + `key.txt`（**必须同处一个目录**） |

安装步骤见根目录 [`../AGENT_SETUP.md`](../AGENT_SETUP.md)。

## 目录

```text
mandarin/
├── key.txt.example        ← 密钥模板（key.txt 要放两处，见「密钥」）
├── plugin.yaml            ┐
├── __init__.py            │ 插件形态（提供 notify_voice 工具）
├── minimax-notify.py      │
├── config.json            │
└── skill/                 Skill 形态
    ├── SKILL.md
    └── scripts/{py, config.json}
```

## 密钥

本仓库**不含密钥**。到 platform.minimaxi.com → 账户管理 → 接口密钥 申请，
然后写进 `key.txt`（一行，`#` 开头为注释）。

`key.txt` 要放到**两个位置** —— 两种形态各读自己目录的：

| 装的形态 | key.txt 放哪 |
| --- | --- |
| 插件形态 | `mandarin/key.txt`（跟着 5 个插件文件一起拷进 `plugins/minimax-notify/`） |
| Skill 形态 | `mandarin/skill/scripts/key.txt` |

格式模板见 [`key.txt.example`](key.txt.example)（复制改名即可）。也支持环境变量 `MINIMAX_API_KEY`（优先级更高）。

## 快速验证

```bash
python minimax-notify.py -s ding "安装测试，能听到吗"
# 听到「叮」+ 一句话，stdout 出现 [ok:sync] = 链路正常
```

## 配置

`config.json`：

```json
{
  "voice": "Chinese (Mandarin)_Southern_Young_Man",
  "sound": "ding",
  "model": "speech-2.8-turbo",
  "vol": 1.5,
  "speed": 1.0
}
```

想换成粤语播报 → 用 [`../cantonese/`](../cantonese/) 那一版（`config.json` 里加 `language_boost`）。
