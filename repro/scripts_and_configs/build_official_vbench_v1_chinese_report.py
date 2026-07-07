from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


DIMENSION_INFO = [
    ("subject_consistency", "主体一致性", "衡量主要主体在视频前后是否保持稳定一致。"),
    ("background_consistency", "背景一致性", "衡量背景区域在时间维度上是否保持连贯稳定。"),
    ("temporal_flickering", "画面闪烁稳定性", "衡量视频是否存在明显的帧间闪烁和亮度跳变。"),
    ("motion_smoothness", "运动平滑度", "衡量主体和镜头运动是否自然连续。"),
    ("dynamic_degree", "动态程度", "衡量视频是否具有足够的动作变化，而不是接近静态图。"),
    ("aesthetic_quality", "美学质量", "衡量视频整体审美观感、构图和视觉吸引力。"),
    ("imaging_quality", "成像质量", "衡量清晰度、噪声、伪影等基础画面质量。"),
    ("object_class", "物体类别一致性", "衡量生成内容是否包含提示词要求的物体类别。"),
    ("multiple_objects", "多物体一致性", "衡量多个目标同时出现时是否都符合提示词要求。"),
    ("human_action", "人物动作一致性", "衡量人物动作是否符合提示词描述。"),
    ("color", "颜色一致性", "衡量生成结果是否符合提示词中的颜色要求。"),
    ("spatial_relationship", "空间关系一致性", "衡量物体之间的空间位置关系是否符合提示词。"),
    ("scene", "场景一致性", "衡量视频场景是否符合提示词描述。"),
    ("temporal_style", "时序风格一致性", "衡量视频是否符合提示词中的时间或季节风格要求。"),
    ("appearance_style", "外观风格一致性", "衡量视频是否符合提示词中的外观或艺术风格要求。"),
    ("overall_consistency", "整体文本一致性", "综合衡量视频整体内容与文本提示词的一致程度。"),
]


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt_summary = read_json_optional(Path(args.prompt_summary))
    link_report = read_json_optional(Path(args.link_report))
    results = collect_results(Path(args.vbench_output_root))

    rows = []
    for key, zh_name, description in DIMENSION_INFO:
        result = results.get(key, {})
        score = result.get("score")
        status = "已完成" if score is not None else "未完成"
        rows.append(
            {
                "指标": zh_name,
                "得分": "" if score is None else f"{float(score):.6f}",
                "完成状态": status,
                "说明": description,
                "结果文件": result.get("file", ""),
                "_key": key,
            }
        )

    csv_path = output_dir / "ConsisID官方VBench评测结果.csv"
    write_csv(csv_path, ["指标", "得分", "完成状态", "说明", "结果文件"], rows)

    bar_path = output_dir / "ConsisID官方VBench柱状图.svg"
    radar_path = output_dir / "ConsisID官方VBench雷达图.svg"
    write_bar_svg(bar_path, rows)
    write_radar_svg(radar_path, rows)

    report_path = output_dir / "ConsisID官方VBench评测报告.md"
    report_path.write_text(
        build_report(args, rows, prompt_summary, link_report, bar_path.name, radar_path.name),
        encoding="utf-8",
    )

    appendix_path = output_dir / "英文复现映射.csv"
    write_csv(appendix_path, ["英文key", "中文展示名", "结果文件"], [{"英文key": r["_key"], "中文展示名": r["指标"], "结果文件": r["结果文件"]} for r in rows])

    print(json.dumps({"report": str(report_path), "csv": str(csv_path), "bar": str(bar_path), "radar": str(radar_path)}, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Chinese analysis report for official VBench v1 ConsisID results.")
    parser.add_argument("--vbench-output-root", default="outputs/official_vbench_v1_consisid/evaluation")
    parser.add_argument("--output-dir", default="outputs/official_vbench_v1_consisid/report")
    parser.add_argument("--prompt-summary", default="data/test_sets/official_vbench_v1/prompts_summary.json")
    parser.add_argument("--link-report", default="outputs/official_vbench_v1_consisid/link_report.json")
    parser.add_argument("--vbench-version", default="v0.1.5")
    parser.add_argument("--sample-count", default="1")
    parser.add_argument(
        "--reference-image",
        default="/data/zengxin/zwt/face_study/face/CVPR25-ConsisID/source/ConsisID-main/asserts/example_images/3.png",
    )
    return parser.parse_args()


def collect_results(root: Path) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for key, _, _ in DIMENSION_INFO:
        candidates = sorted((root / key).glob("*eval_results.json"))
        if not candidates:
            candidates = sorted((root / key).glob("*.json"))
        if not candidates:
            continue
        path = candidates[-1]
        payload = read_json_optional(path)
        score = extract_score(payload, key)
        results[key] = {"score": score, "file": str(path), "payload": payload}
    return results


def extract_score(payload: Any, key: str) -> float | None:
    if payload is None:
        return None
    value = payload.get(key) if isinstance(payload, dict) else payload
    if value is None and isinstance(payload, dict):
        for candidate in payload.values():
            score = extract_score(candidate, key)
            if score is not None:
                return score
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, list) and value:
        for item in value:
            score = extract_score(item, key)
            if score is not None:
                return score
    if isinstance(value, dict):
        for score_key in ("score", "value", "mean", "avg"):
            if isinstance(value.get(score_key), (int, float, bool)):
                return float(value[score_key])
    return None


def read_json_optional(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def build_report(
    args: argparse.Namespace,
    rows: list[dict[str, Any]],
    prompt_summary: dict[str, Any] | None,
    link_report: dict[str, Any] | None,
    bar_name: str,
    radar_name: str,
) -> str:
    complete = [row for row in rows if row["完成状态"] == "已完成"]
    incomplete = [row for row in rows if row["完成状态"] != "已完成"]
    scored = [(row["指标"], float(row["得分"])) for row in complete if row["得分"]]
    top = sorted(scored, key=lambda item: item[1], reverse=True)[:3]
    bottom = sorted(scored, key=lambda item: item[1])[:3]

    official_records = prompt_summary.get("official_records", "未知") if prompt_summary else "未知"
    unique_prompts = prompt_summary.get("unique_prompts", "未知") if prompt_summary else "未知"
    linked = link_report.get("linked_video_files", "未知") if link_report else "未知"
    missing = link_report.get("missing_count", "未知") if link_report else "未知"

    lines = [
        "# ConsisID 官方 VBench 评测报告",
        "",
        "## 摘要",
        "",
        f"本报告使用官方 VBench 第一代评测框架，对 ConsisID 生成视频进行视频质量分析。评测版本为 `{args.vbench_version}`，样本设置为每条提示词 {args.sample_count} 个视频。",
        "",
        f"本次官方提示词记录数为 {official_records}，去重后实际生成提示词数为 {unique_prompts}，已整理为官方标准命名的视频文件数为 {linked}。缺失文件数为 {missing}。",
        "",
        f"ConsisID 不是纯文本视频模型，本次统一使用固定参考人脸：`{args.reference_image}`。因此，报告结论应理解为固定参考人脸条件下的 ConsisID 表现。",
        "",
        "## 总体结论",
        "",
    ]
    if scored:
        lines.append("已完成指标中，得分较高的维度为：" + "、".join(f"{name}（{score:.3f}）" for name, score in top) + "。")
        lines.append("相对需要关注的维度为：" + "、".join(f"{name}（{score:.3f}）" for name, score in bottom) + "。")
    else:
        lines.append("当前尚未解析到有效得分。请先确认官方 VBench 逐维评测是否完成，并检查原始结果文件。")
    if incomplete:
        lines.append("未完成或未解析出结果的维度包括：" + "、".join(row["指标"] for row in incomplete) + "。")
    lines.extend(
        [
            "",
            "## 指标结果",
            "",
            "| 指标 | 得分 | 完成状态 | 说明 |",
            "|---|---:|---|---|",
        ]
    )
    for row in rows:
        lines.append(f"| {row['指标']} | {row['得分'] or '暂无'} | {row['完成状态']} | {row['说明']} |")
    lines.extend(
        [
            "",
            "## 图表",
            "",
            f"![官方 VBench 中文柱状图]({bar_name})",
            "",
            f"![官方 VBench 中文雷达图]({radar_name})",
            "",
            "## 复现信息",
            "",
            f"- VBench 官方版本：`{args.vbench_version}`",
            f"- 每条提示词样本数：{args.sample_count}",
            f"- 固定参考人脸：`{args.reference_image}`",
            "- 原始结果和技术字段见同目录下的 `英文复现映射.csv` 以及各维度原始 JSON 文件。",
            "",
        ]
    )
    return "\n".join(lines)


def score_values(rows: list[dict[str, Any]]) -> list[tuple[str, float | None]]:
    values = []
    for row in rows:
        try:
            score = float(row["得分"]) if row.get("得分") else None
        except ValueError:
            score = None
        values.append((row["指标"], score))
    return values


def write_bar_svg(path: Path, rows: list[dict[str, Any]]) -> None:
    values = score_values(rows)
    max_score = max([score for _, score in values if score is not None] or [1.0])
    max_score = max(max_score, 1.0)
    width = 1200
    row_h = 34
    height = 80 + row_h * len(values)
    lines = [svg_header(width, height), '<rect width="100%" height="100%" fill="#ffffff"/>']
    lines.append('<text x="40" y="35" font-size="22" font-weight="700">ConsisID 官方 VBench 中文指标柱状图</text>')
    for idx, (name, score) in enumerate(values):
        y = 70 + idx * row_h
        bar_w = 0 if score is None else int(760 * score / max_score)
        lines.append(f'<text x="40" y="{y + 20}" font-size="16">{escape_xml(name)}</text>')
        lines.append(f'<rect x="210" y="{y + 5}" width="760" height="22" fill="#eef2f7"/>')
        lines.append(f'<rect x="210" y="{y + 5}" width="{bar_w}" height="22" fill="#2563eb"/>')
        label = "暂无" if score is None else f"{score:.3f}"
        lines.append(f'<text x="990" y="{y + 21}" font-size="15">{label}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_radar_svg(path: Path, rows: list[dict[str, Any]]) -> None:
    values = score_values(rows)
    scores = [score for _, score in values if score is not None]
    max_score = max(scores or [1.0])
    max_score = max(max_score, 1.0)
    width = 1000
    height = 1000
    cx = cy = 500
    radius = 320
    lines = [svg_header(width, height), '<rect width="100%" height="100%" fill="#ffffff"/>']
    lines.append('<text x="40" y="45" font-size="24" font-weight="700">ConsisID 官方 VBench 中文指标雷达图</text>')
    n = len(values)
    for ring in range(1, 6):
        r = radius * ring / 5
        points = polygon_points(cx, cy, r, n)
        lines.append(f'<polygon points="{points}" fill="none" stroke="#d8dee9" stroke-width="1"/>')
    data_points = []
    for idx, (name, score) in enumerate(values):
        angle = -math.pi / 2 + 2 * math.pi * idx / n
        axis_x = cx + radius * math.cos(angle)
        axis_y = cy + radius * math.sin(angle)
        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{axis_x:.1f}" y2="{axis_y:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
        label_x = cx + (radius + 55) * math.cos(angle)
        label_y = cy + (radius + 55) * math.sin(angle)
        anchor = "middle"
        if label_x < cx - 80:
            anchor = "end"
        elif label_x > cx + 80:
            anchor = "start"
        lines.append(f'<text x="{label_x:.1f}" y="{label_y:.1f}" font-size="14" text-anchor="{anchor}">{escape_xml(name)}</text>')
        normalized = 0 if score is None else float(score) / max_score
        data_points.append((cx + radius * normalized * math.cos(angle), cy + radius * normalized * math.sin(angle)))
    point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in data_points)
    lines.append(f'<polygon points="{point_text}" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="3"/>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def polygon_points(cx: int, cy: int, radius: float, n: int) -> str:
    points = []
    for idx in range(n):
        angle = -math.pi / 2 + 2 * math.pi * idx / n
        points.append(f"{cx + radius * math.cos(angle):.1f},{cy + radius * math.sin(angle):.1f}")
    return " ".join(points)


def svg_header(width: int, height: int) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Arial, Noto Sans CJK SC, Microsoft YaHei, sans-serif">'


def escape_xml(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    raise SystemExit(main())
