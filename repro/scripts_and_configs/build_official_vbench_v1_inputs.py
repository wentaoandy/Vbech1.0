from __future__ import annotations

import argparse
import csv
import json
from collections import OrderedDict
from pathlib import Path


FIELDS = [
    "prompt_id",
    "official_record_indexes",
    "prompt_en",
    "dimensions",
    "primary_dimension",
    "reference_image",
    "reference_identity",
    "sample_count",
    "source_dataset",
    "source_file",
]


def main() -> int:
    args = parse_args()
    info_path = Path(args.vbench_info)
    rows = json.loads(info_path.read_text(encoding="utf-8"))

    prompts: OrderedDict[str, dict[str, object]] = OrderedDict()
    for index, row in enumerate(rows, start=1):
        prompt = str(row.get("prompt_en", "")).strip()
        if not prompt:
            continue
        dims = [str(dim).strip() for dim in row.get("dimension", []) if str(dim).strip()]
        if prompt not in prompts:
            prompts[prompt] = {
                "record_indexes": [],
                "dimensions": [],
            }
        item = prompts[prompt]
        item["record_indexes"].append(index)
        for dim in dims:
            if dim not in item["dimensions"]:
                item["dimensions"].append(dim)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    csv_rows = []
    for prompt_index, (prompt, item) in enumerate(prompts.items(), start=1):
        dimensions = list(item["dimensions"])
        csv_rows.append(
            {
                "prompt_id": f"ovb{prompt_index:04d}",
                "official_record_indexes": "|".join(str(i) for i in item["record_indexes"]),
                "prompt_en": prompt,
                "dimensions": "|".join(dimensions),
                "primary_dimension": dimensions[0] if dimensions else "",
                "reference_image": args.reference_image,
                "reference_identity": args.reference_identity,
                "sample_count": str(args.sample_count),
                "source_dataset": "VBench v1 official prompt suite",
                "source_file": str(info_path),
            }
        )

    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(csv_rows)

    summary = {
        "vbench_info": str(info_path),
        "official_records": len(rows),
        "unique_prompts": len(csv_rows),
        "duplicate_prompt_records": len(rows) - len(csv_rows),
        "sample_count": args.sample_count,
        "target_video_files": len(csv_rows) * args.sample_count,
        "reference_image": args.reference_image,
        "output": str(output),
    }
    summary_path = output.with_name(output.stem + "_summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ConsisID generation prompts from official VBench v1 metadata.")
    parser.add_argument("--vbench-info", default="/data/zengxin/zwt/external/VBench-v1/vbench/VBench_full_info.json")
    parser.add_argument("--output", default="data/test_sets/official_vbench_v1/prompts.csv")
    parser.add_argument(
        "--reference-image",
        default="/data/zengxin/zwt/face_study/face/CVPR25-ConsisID/source/ConsisID-main/asserts/example_images/3.png",
    )
    parser.add_argument("--reference-identity", default="ConsisID固定参考人脸")
    parser.add_argument("--sample-count", type=int, default=1)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
