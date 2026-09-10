# Changelog

## [1.3.2] - 2026-09-10

- **回退**：toolset 归属改回自建的 `minimax_notify`。改挂内置 `tts` 不可行 ——
  `ctx.register_tool(toolset="tts")` 塞不进静态 toolset（`tts` 在 `TOOLSETS` 里写死为 `text_to_speech`），
  改了反而**连桌面端也拿不到工具**。
- **已知限制（重要）**：`notify_voice` 在 **CLI / TUI 会话里不可见**。这些入口走
  `platform_toolsets.<platform>` 白名单，而 **user 插件的自建 toolset 不被该列表承认**
  （写进去会判 `unknown toolset` 并在 update 时告警）。**桌面端正常** —— 它走平台复合 toolset
  （`hermes-desktop`），不经过这份白名单。
- 已试过但**无效**的两种修法：① 把自建 toolset 名加进 `platform_toolsets.cli`；
  ② 在 `plugin.yaml` 声明 `provides_tools: [notify_voice]`（doctor 的 WARN 会消失，但 CLI/TUI 仍不可见）。
- 源码给出的契约：要让插件工具在 CLI/TUI 可见，需把注册放进 **`tools.py` 的 `register_tools(ctx)`**
  （`hermes_cli/plugins_loader.py`："declares provides_tools … but has no tools.py; those tools will not be
  available in CLI/TUI sessions"）。本包尚未按该形态重构。
- 变通：CLI/TUI 下改用命令行直接跑脚本（等于 skill 形态的行为）。

## [1.3.1] - 2026-09-10（已回退）

- 插件的 toolset 归属从自建的 `minimax_notify` 改为 **`tts`**。
  原因：Hermes 按入口维护 `platform_toolsets` 白名单，**自建 toolset 名不在其中** ——
  结果就是"插件 enable 了、`notify_voice` 却看不见"。桌面端能用的假象来自它走平台复合 toolset
  （`hermes-desktop`），而 TUI / CLI 走 `platform_toolsets.cli` 就看不到。
  挂到已有的 `tts` 后，各界面一致可用。
- 副作用：`hermes tools disable tts` 会连带禁用 `notify_voice`。
- （此前试过把自建名加进 `platform_toolsets.cli`，运行时仍判为 unknown toolset，**无效**。）

## [1.3.0] - 2026-09-10

- `notify_voice` 改为**默认后台**：发起即返回（实测 ~4 ms），合成与播放在后台子进程完成，
  **不阻塞 Agent 的思考与输出**
- 需要回执时传 `sync=true`（等播完才返回，含成功/失败与 `[ok:sync]` 输出）
- 后台输出落到 `%TEMP%\minimax-notify.log`，便于排查密钥/余额类故障
- 命令行直接调用**行为不变**（默认同步，`--async` 异步）

## [1.2.0] - 2026-09-10

- 仓库拆分为两个版本目录：`mandarin/`（普通话）与 `cantonese/`（粤语学习者版）
- 新增 `--lang` 参数与 `config.json` 的 `language_boost` 字段
  （粤语必须传 `Chinese,Yue`，否则按普通读音念；只认 `Chinese` / `Chinese,Yue` / `auto`）
- 内置 **6 个粤语音色别名**：`yue_gentle`（默认）/ `yue_kind` / `yue_cute` / `yue_playful` / `yue_host_f` / `yue_host_m`
- **粤语版**：音色 `Cantonese_GentleLady`；skill 三条硬规则（粤语播报 / 粤语用词 / 普通话对照）
  + 粤语用词对照表；插件工具描述同步带上要求；新增 `SOUL_SNIPPET.md` 触发层
- `AGENT.md` 更名为 **`AGENT_SETUP.md`**（涵盖两版安装与触发机制补全）

## [1.1.0] - 2026-09-10

- 首次开源发布：脚本 + Skill + Hermes 原生插件（`notify_voice` 工具）
- 单文件、零第三方依赖（Windows `winsound`）
- 默认音色 `Chinese (Mandarin)_Southern_Young_Man`，音量 1.5
- 支持同步 / 异步播放、五种提示音、任意 MiniMax 音色
- `AGENT.md`：给 Agent 的安装与配置指南，含**触发机制补全**（把播报规范写进 `SOUL.md`）

## [1.0.0] - 2026-08-26

- 内部首版：MiniMax TTS 同步语音播报 + 本地提示音
