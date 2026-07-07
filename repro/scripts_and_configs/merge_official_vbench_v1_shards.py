from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    args = parse_args()
    run_ids = args.run_id or [f"{args.run_prefix}_shard{suffix}" for suffix in args.shards.split(",") if suffix]
    if not run_ids:
        raise ValueError("provide --run-id or --run-prefix with --shards")

    manifest_rows = []
    log_rows = []
    missing = []
    for run_id in run_ids:
        manifest_path = Path(args.manifest_dir) / f"{run_id}.csv"
        log_path = Path(args.manifest_dir) / f"{run_id}.generation_log.csv"
        if not manifest_path.exists():
            missing.append(str(manifest_path))
        else:
            manifest_rows.extend(read_csv(manifest_path))
        if not log_path.exists():
            missing.append(str(log_path))
        else:
            log_rows.extend(read_csv(log_path))

    if missing and args.fail_on_missing:
        raise FileNotFoundError("missing shard files: " + ", ".join(missing))

    output_manifest = Path(args.output_manifest)
    output_log = Path(args.output_log)
    write_csv(output_manifest, manifest_rows)
    write_csv(output_log, log_rows)

    summary = {
        "run_ids": run_ids,
        "manifest_rows": len(manifest_rows),
        "generation_log_rows": len(log_rows),
        "missing_files": missing,
        "output_manifest": str(output_manifest),
        "output_generation_log": str(output_log),
    }
    summary_path = output_log.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge sharded official VBench v1 ConsisID generation CSV outputs.")
    parser.add_argument("--run-prefix", help="Common run prefix, for example consisid_official_vbench_v1_single_YYYYMMDD_HHMMSS")
    parser.add_argument("--shards", default="01,02")
    parser.add_argument("--run-id", action="append", help="Explicit shard run id. Can be passed multiple times.")
    parser.add_argument("--manifest-dir", default="data/manifests")
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--output-log", required=True)
    parser.add_argument("--fail-on-missing", action="store_true")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(fh)]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
