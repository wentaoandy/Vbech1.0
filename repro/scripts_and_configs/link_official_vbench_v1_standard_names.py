from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
from pathlib import Path


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    prompts = read_csv_by_key(Path(args.prompts), "prompt_id")
    log_rows = read_csv(Path(args.generation_log))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    linked = []
    missing = []
    skipped = []
    for row in log_rows:
        status = row.get("status", "")
        if status not in {"ok", "skipped_existing"}:
            skipped.append({"prompt_id": row.get("prompt_id", ""), "sample_index": row.get("sample_index", ""), "status": status})
            continue
        prompt_id = row.get("prompt_id", "")
        prompt_row = prompts.get(prompt_id)
        if not prompt_row:
            missing.append({"prompt_id": prompt_id, "sample_index": row.get("sample_index", ""), "reason": "prompt_id not found"})
            continue
        sample_index = row.get("sample_index", "0")
        source = resolve_path(project_dir, row.get("output", ""))
        if not source.exists():
            missing.append({"prompt_id": prompt_id, "sample_index": sample_index, "reason": f"source missing: {source}"})
            continue
        prompt = prompt_row["prompt_en"]
        target = output_dir / f"{prompt}-{sample_index}{source.suffix or '.mp4'}"
        if len(target.name.encode("utf-8")) > 250:
            raise RuntimeError(f"VBench filename is too long for prompt_id={prompt_id}: {target.name}")
        if "/" in target.name or "\x00" in target.name:
            raise RuntimeError(f"VBench filename contains an unsafe character for prompt_id={prompt_id}: {target.name!r}")
        create_link(source, target, args.mode)
        linked.append({"prompt_id": prompt_id, "sample_index": sample_index, "source": str(source), "target": str(target)})

    report = {
        "mode": args.mode,
        "prompts": len(prompts),
        "generation_log_rows": len(log_rows),
        "linked_video_files": len(linked),
        "missing_count": len(missing),
        "skipped_count": len(skipped),
        "output_dir": str(output_dir),
        "missing": missing[:100],
        "skipped": skipped[:100],
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not missing else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create official VBench standard filenames for generated ConsisID videos.")
    parser.add_argument("--project-dir", default="/data/zengxin/zwt/face_study")
    parser.add_argument("--prompts", default="data/test_sets/official_vbench_v1/prompts.csv")
    parser.add_argument("--generation-log", required=True)
    parser.add_argument("--output-dir", default="data/generated_official_vbench/consisid_standard_names")
    parser.add_argument("--report", default="outputs/official_vbench_v1_consisid/link_report.json")
    parser.add_argument("--mode", choices=["symlink", "copy", "hardlink"], default="symlink")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(fh)]


def read_csv_by_key(path: Path, key: str) -> dict[str, dict[str, str]]:
    rows = read_csv(path)
    return {row[key]: row for row in rows if row.get(key)}


def resolve_path(project_dir: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return project_dir / path


def create_link(source: Path, target: Path, mode: str) -> None:
    if target.exists() or target.is_symlink():
        if target.is_symlink() and Path(os.readlink(target)) == source:
            return
        target.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    if mode == "symlink":
        target.symlink_to(source)
    elif mode == "hardlink":
        os.link(source, target)
    else:
        shutil.copy2(source, target)


if __name__ == "__main__":
    raise SystemExit(main())
