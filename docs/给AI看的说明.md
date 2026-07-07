# 给 AI 看的说明

这是 ConsisID 官方 VBench v1 评测资料的 GitHub 干净版。目标是让网页 ChatGPT 能直接读取仓库内容，理解评测过程、结果、失败原因和复现路径。

## 评测对象

- 模型：ConsisID
- 评测：官方 VBench v1，`Vchitect/VBench`，版本 `v0.1.5`
- 评测模式：`vbench_standard`
- 样本：官方 prompt suite，946 条 prompt，单样本版本
- 本次生成视频：944 个，分为 shard01 472 个、shard02 472 个
- 参考图：固定参考人脸图，因此报告口径是“固定参考人脸条件下的 ConsisID 评测”

## 读仓库时优先看

1. `README.md`
2. `reports/中文报告/ConsisID_official_VBench_report_zh.md`
3. `reports/中文报告/ConsisID_official_VBench_results_zh.csv`
4. `docs/环境问题记录.md`
5. `logs/维度日志_16/`
6. `results/原始JSON/`
7. `manifest/视频文件清单_未上传.csv`

## 重要说明

- 本仓库不上传视频文件。视频文件数量多，完整本地归档在 `B:\vbench_struct`。
- 本仓库不上传环境目录。环境问题通过 `docs/环境说明.md`、`docs/环境问题记录.md` 和日志体现。
- 正文指标统一使用中文展示名；英文 key 只用于复现映射和原始 JSON。

## 已知结果状态

- `画面闪烁稳定性` 有成功结果，分数约为 0.969873。
- 其他维度多数受环境、依赖或模型下载问题影响，没有全部完成。
- 具体失败原因看 `docs/环境问题记录.md` 和 `logs/维度日志_16/`。
