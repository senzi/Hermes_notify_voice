# Changelog

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
