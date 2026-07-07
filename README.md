# ConsisID 官方 VBench v1 中文评测资料库（GitHub 干净版）

这个仓库是 `B:\vbench_struct` 的 GitHub 干净版。它面向网页 ChatGPT 和人工快速分析，保留报告、结果、日志、环境说明和复现信息，不上传完整环境目录和视频文件。

## 本仓库包含

- 中文评测报告和图表
- 中文结果 CSV
- VBench 原始 JSON 结果
- 16 个维度的评测日志
- ConsisID 生成 manifest 和 prompt
- 环境说明、环境问题记录、依赖清单
- 未上传视频文件清单
- 运行命令和复现说明

## 本仓库不包含

- mp4 视频文件
- Conda/venv 环境目录
- site-packages
- tar/tar.gz/zip 大归档
- Git 历史里的旧大对象

## 快速入口

- 总说明：`docs/给AI看的说明.md`
- 中文报告：`reports/中文报告/ConsisID_official_VBench_report_zh.md`
- 中文结果表：`reports/中文报告/ConsisID_official_VBench_results_zh.csv`
- 环境说明：`docs/环境说明.md`
- 环境问题：`docs/环境问题记录.md`
- 视频未上传说明：`docs/视频文件未上传说明.md`
- 视频清单：`manifest/视频文件清单_未上传.csv`
- GitHub 上传说明：`docs/GitHub上传说明.md`

## 原始整理版说明摘录

```text
﻿# README_先读我：ConsisID 官方 VBench v1 整理版

## 0. 这个目录是什么

这是从原始目录 `B:\vbench_current_official_consisid_v1` 重新整理出来的浅层版本。

整理目标：把本次 ConsisID 官方 VBench v1 评测材料按 4 类放好，方便人工和 AI 快速分析。

四类目录：

1. `01_VBench评测`：官方 VBench v1 代码、评测入口、环境压缩包、官方元数据。
2. `02_Consis生成`：ConsisID 生成用 prompts、manifest、脚本配置、生成日志。
3. `03_视频目录`：生成视频和标准命名视频。
4. `04_评测结果`：中文报告、维度日志、原始 JSON、运行日志、环境错误日志。

除 `01_VBench评测\VBench-v1` 需要保留 GitHub 仓库原始结构外，其它常用目录都控制在浅层结构：分类目录 -> 子目录 -> 文件。

## 1. AI 最短读取顺序

1. 先读本文件：`B:\vbench_整理版\README_先读我.md`
2. 看中文报告：`B:\vbench_整理版\04_评测结果\中文报告\ConsisID_official_VBench_report_zh.md`
3. 看中文结果表：`B:\vbench_整理版\04_评测结果\中文报告\ConsisID_official_VBench_results_zh.csv`
4. 看维度失败原因：`B:\vbench_整理版\04_评测结果\维度日志_16\*.log`
5. 核验生成视频：`B:\vbench_整理版\03_视频目录\shard01_原始视频_472\` 和 `B:\vbench_整理版\03_视频目录\shard02_原始视频_472\`
6. 要找官方标准命名视频，优先看：`B:\vbench_整理版\03_视频目录\std安全名_944\`

## 2. 每个目录是什么

### `01_VBench评测`

- `VBench-v1\`
  - 官方 VBench v1 本地代码，按 GitHub 仓库原始结构保留。
  - 重要文件：`evaluate.py`、`vbench\VBench_full_info.json`、`vbench\*.py`。
  - 这是唯一允许保留深层结构的目录。

- `环境压缩包\`
  - `vbench_v1_linux_env_extracted_from_server.tar.gz`：服务器 VBench v1 Python 环境压缩包。
  - `vbench_v1_env_filelist.csv`：环境文件清单。
  - 环境不展开，避免目录层级混乱。

- `版本与命令\`
  - `official_evaluate.py`：官方评测入口副本。
  - `VBench_full_info.json`：官方 prompt 元数据副本。

### `02_Consis生成`

- `prompts\`
  - `official_vbench_v1_prompts.csv`：本次生成使用的官方 prompt 表。
  - `official_vbench_v1_prompts_summary.json`：prompt 摘要。
  - `prompt_*.csv`：生成分片 prompt。

- `manifests\`
  - 本次 ConsisID 官方 VBench v1 的 manifest 和 generation log。
  - 重点看：`consisid_official_vbench_v1_single_20260705_155651.generation_log.csv`。

- `脚本配置\`
  - 本次准备、生成、合并、标准命名、中文报告相关脚本和配置。

- `生成日志\`
  - shard01、shard02、finalizer 的运行日志。
  - `link_report.json` 记录标准命名整理情况。

### `03_视频目录`

- `shard01_原始视频_472\`
  - 第 1 个生成分片，472 个 mp4。

- `shard02_原始视频_472\`
  - 第 2 个生成分片，472 个 mp4。

- `std官方名\`
  - 尽量保留官方 VBench 标准文件名的视频目录。
  - Windows 大小写不敏感，所以这里有 943 个 mp4。

- `std安全名_944\`
  - 推荐用于本地核验的标准命名替代目录。
  - 文件名格式：`prompt_id__sample0__prompt摘要.mp4`。
  - 这里完整包含 944 个 mp4，不受大小写冲突影响。

- `std命名说明_异常.csv`
  - 记录官方标准名无法完整落到 Windows 文件系统的原因。
  - 当前只有 1 条：`A fantasy landscape-0.mp4` 与 `a fantasy landscape-0.mp4` 大小写冲突。

- `smoke_测试视频\`
  - 前期 smoke test 视频，3 个 mp4。

### `04_评测结果`

- `中文报告\`
  - 中文 Markdown 报告、中文 CSV、柱状图、雷达图、英文 key 映射表。

- `维度日志_16\`
  - 16 个 VBench 维度的原始日志。
  - 失败原因主要在这些日志里。

- `原始JSON\`
  - 扁平化后的原始 VBench JSON。
  - 文件名带维度前缀，格式类似：`temporal_flickering__results_..._eval_results.json`。

- `运行日志\`
  - finalizer、shard、下载状态、标准命名文件列表等运行日志。

- `环境错误日志\`
  - detectron2 安装失败等环境日志。

- `图表和映射\`
  - 报告图表和英文 key 映射副本。

## 3. 核心结论

- 本次生成完成：944 个视频。
- 原始生成视频：`shard01_原始视频_472` + `shard02_原始视频_472`。
- VBench 官方标准名在 Windows 下无法 100% 原样共存，使用 `std安全名_944` 可完整核验全部视频。
- 本次评测只成功出分“画面闪烁稳定性”：0.969873。
- 其它维度失败主要是环境依赖和模型下载问题，不是视频生成失败。
- 总耗时约 39 小时 34 分钟。

## 4. 不要再优先看旧目录

旧目录 `B:\vbench_current_official_consisid_v1` 是原始下载和解压结构，层级很深。后续分析优先使用本整理版：`B:\vbench_整理版`。

```

## 中文结果表预览

```csv
﻿指标,得分,完成状态,说明,结果文件
主体一致性,,未完成,衡量主要主体在视频前后是否保持稳定一致。,outputs/official_vbench_v1_consisid/consisid_official_vbench_v1_single_20260705_155651/evaluation/subject_consistency/results_2026-07-07-07:16:10_full_info.json
背景一致性,,未完成,衡量背景区域在时间维度上是否保持连贯稳定。,outputs/official_vbench_v1_consisid/consisid_official_vbench_v1_single_20260705_155651/evaluation/background_consistency/results_2026-07-07-07:16:18_full_info.json
画面闪烁稳定性,0.969873,已完成,衡量视频是否存在明显的帧间闪烁和亮度跳变。,outputs/official_vbench_v1_consisid/consisid_official_vbench_v1_single_20260705_155651/evaluation/temporal_flickering/results_2026-07-07-07:16:22_eval_results.json
运动平滑度,,未完成,衡量主体和镜头运动是否自然连续。,
动态程度,,未完成,衡量视频是否具有足够的动作变化，而不是接近静态图。,outputs/official_vbench_v1_consisid/consisid_official_vbench_v1_single_20260705_155651/evaluation/dynamic_degree/results_2026-07-07-07:18:59_full_info.json
美学质量,,未完成,衡量视频整体审美观感、构图和视觉吸引力。,outputs/official_vbench_v1_consisid/consisid_official_vbench_v1_single_20260705_155651/evaluation/aesthetic_quality/results_2026-07-07-07:21:20_full_info.json
成像质量,,未完成,衡量清晰度、噪声、伪影等基础画面质量。,outputs/official_vbench_v1_consisid/consisid_official_vbench_v1_single_20260705_155651/evaluation/imaging_quality/results_2026-07-07-07:21:24_full_info.json
物体类别一致性,,未完成,衡量生成内容是否包含提示词要求的物体类别。,
多物体一致性,,未完成,衡量多个目标同时出现时是否都符合提示词要求。,
人物动作一致性,,未完成,衡量人物动作是否符合提示词描述。,
颜色一致性,,未完成,衡量生成结果是否符合提示词中的颜色要求。,
空间关系一致性,,未完成,衡量物体之间的空间位置关系是否符合提示词。,
场景一致性,,未完成,衡量视频场景是否符合提示词描述。,
时序风格一致性,,未完成,衡量视频是否符合提示词中的时间或季节风格要求。,
外观风格一致性,,未完成,衡量视频是否符合提示词中的外观或艺术风格要求。,outputs/official_vbench_v1_consisid/consisid_official_vbench_v1_single_20260705_155651/evaluation/appearance_style/results_2026-07-07-07:28:41_full_info.json
整体文本一致性,,未完成,综合衡量视频整体内容与文本提示词的一致程度。,

```
