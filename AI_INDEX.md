# AI_INDEX：ConsisID 官方 VBench v1 评测资料索引

这个文件用于帮助 GitHub / ChatGPT / Codex 快速定位本仓库内容。仓库主题是 ConsisID 官方 VBench v1 中文评测资料库。

## 仓库核心关键词

ConsisID, VBench, VBench v1, official VBench, video generation evaluation, text-to-video evaluation, T2V benchmark, ConsisID evaluation, temporal flickering, subject consistency, background consistency, dynamic degree, aesthetic quality, imaging quality, appearance style, 16 dimensions, 中文报告, 中文结果表, 维度日志, 原始 JSON, 生成 manifest, prompt, generation log, evaluation log, clean report package.

## 最重要入口

- 总说明：`README.md`
- 给 AI 看的说明：`docs/给AI看的说明.md`
- 中文评测报告：`reports/中文报告/ConsisID_official_VBench_report_zh.md`
- 中文结果表：`reports/中文报告/ConsisID_official_VBench_results_zh.csv`
- 环境说明：`docs/环境说明.md`
- 环境问题记录：`docs/环境问题记录.md`
- 视频文件未上传说明：`docs/视频文件未上传说明.md`
- 视频文件清单：`manifest/视频文件清单_未上传.csv`
- GitHub 上传说明：`docs/GitHub上传说明.md`

## 评测核心结论

- 生成任务：ConsisID 官方 VBench v1 prompt suite。
- 生成视频数量：944 个视频。
- 原始视频分片：shard01 472 个，shard02 472 个。
- GitHub 干净版不上传 mp4、环境目录、site-packages、模型权重和大压缩包。
- 当前成功出分维度：画面闪烁稳定性 temporal_flickering。
- 当前成功分数：0.969873。
- 其它维度主要失败于环境依赖、模型下载、detectron2 / 评测模型等问题，不是视频生成失败。
- 总耗时约 39 小时 34 分钟。

## 适合搜索的问题

### 想看总览

搜索：

```text
ConsisID VBench 中文报告
```

优先读：

```text
README.md
reports/中文报告/ConsisID_official_VBench_report_zh.md
```

### 想看指标结果

搜索：

```text
temporal_flickering 0.969873
```

优先读：

```text
reports/中文报告/ConsisID_official_VBench_results_zh.csv
reports/中文报告/ConsisID_official_VBench_report_zh.md
```

### 想看为什么只有一个维度成功

搜索：

```text
维度日志 失败原因 detectron2 模型下载
```

优先读：

```text
logs/维度日志_16/
docs/环境问题记录.md
```

### 想看视频为什么没上传

搜索：

```text
视频文件未上传 mp4 944 std安全名
```

优先读：

```text
docs/视频文件未上传说明.md
manifest/视频文件清单_未上传.csv
```

### 想复现或重新跑

搜索：

```text
VBench_full_info evaluate.py official_evaluate 运行命令
```

优先读：

```text
docs/环境说明.md
docs/GitHub上传说明.md
```

## 中文指标关键词映射

- 主体一致性：subject_consistency
- 背景一致性：background_consistency
- 画面闪烁稳定性：temporal_flickering
- 运动平滑度：motion_smoothness
- 动态程度：dynamic_degree
- 美学质量：aesthetic_quality
- 成像质量：imaging_quality
- 物体类别一致性：object_class
- 多物体一致性：multiple_objects
- 人物动作一致性：human_action
- 颜色一致性：color
- 空间关系一致性：spatial_relationship
- 场景一致性：scene
- 时序风格一致性：temporal_style
- 外观风格一致性：appearance_style
- 整体文本一致性：overall_consistency

## 给 ChatGPT / Codex 的读取顺序

1. 先读 `README.md`。
2. 再读 `docs/给AI看的说明.md`。
3. 然后读 `reports/中文报告/ConsisID_official_VBench_report_zh.md`。
4. 核对表格读 `reports/中文报告/ConsisID_official_VBench_results_zh.csv`。
5. 追失败原因读 `logs/维度日志_16/` 和 `docs/环境问题记录.md`。
6. 追视频对应关系读 `manifest/视频文件清单_未上传.csv`。

## 注意

当前仓库依赖 GitHub / ChatGPT 的代码搜索索引刷新。即使搜索暂时不可用，也可以通过明确路径直接读取文件。
