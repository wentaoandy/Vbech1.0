#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/data/zengxin/zwt/face_study}"
cd "$PROJECT_DIR"

BATCH="${BATCH:-$(cat outputs/official_vbench_v1_consisid/full_single_sharded/latest_batch.txt)}"
SNAP="${SNAP:-official_vbench_v1_snapshot_${BATCH}_$(date +%Y%m%d_%H%M%S)}"
SNAP_ROOT="outputs/official_vbench_v1_consisid/download_snapshots"
SNAPDIR="$SNAP_ROOT/$SNAP"
TAR="$SNAP_ROOT/${SNAP}.tar.gz"

mkdir -p "$SNAPDIR"

{
  echo "批次: $BATCH"
  echo "快照时间: $(date +%F_%T)"
  echo "状态: 仍在运行，尚未完成正式16维VBench评测"
  for i in 01 02; do
    run="${BATCH}_shard${i}"
    count="$(find "data/generated_official_vbench/${run}/consisid_official_vbench_v1" -type f -name '*.mp4' 2>/dev/null | wc -l)"
    echo "${run} 视频数: ${count} / 472"
    pid_file="outputs/official_vbench_v1_consisid/full_single_sharded/${run}.pid"
    if [[ -f "$pid_file" ]]; then
      pid="$(cat "$pid_file")"
      echo "${run} 进程: $(ps -p "$pid" -o pid=,etime=,stat= 2>/dev/null || echo not_running)"
    fi
  done
  finalizer_pid_file="outputs/official_vbench_v1_consisid/full_single_sharded/${BATCH}_finalizer.pid"
  if [[ -f "$finalizer_pid_file" ]]; then
    pid="$(cat "$finalizer_pid_file")"
    echo "finalizer 进程: $(ps -p "$pid" -o pid=,etime=,stat= 2>/dev/null || echo not_running)"
  fi
  echo "说明: 正式评测结果目录 outputs/official_vbench_v1_consisid/${BATCH}/ 当前尚未生成；已包含 smoke 评测结果和当前日志。"
} > "$SNAPDIR/STATUS.txt"

cat > "$SNAPDIR/filelist.txt" <<EOF
$SNAPDIR/STATUS.txt
data/test_sets/official_vbench_v1/prompts.csv
data/test_sets/official_vbench_v1/prompts_summary.json
data/test_sets/official_vbench_v1/shards
data/generated_official_vbench/${BATCH}_shard01
data/generated_official_vbench/${BATCH}_shard02
data/generated_official_vbench/consisid_official_vbench_v1_smoke_20260705_153741
data/generated_official_vbench/consisid_official_vbench_v1_smoke_20260705_153741_standard_names
data/manifests/consisid_official_vbench_v1_smoke_20260705_153741.csv
data/manifests/consisid_official_vbench_v1_smoke_20260705_153741.generation_log.csv
outputs/official_vbench_v1_consisid/consisid_official_vbench_v1_smoke_20260705_153741
outputs/official_vbench_v1_consisid/full_single_sharded
outputs/official_vbench_v1_consisid/setup
scripts/build_official_vbench_v1_inputs.py
scripts/link_official_vbench_v1_standard_names.py
scripts/build_official_vbench_v1_chinese_report.py
scripts/merge_official_vbench_v1_shards.py
scripts/run_consisid_official_vbench_v1.sh
scripts/finalize_consisid_official_vbench_v1_batch.sh
scripts/package_official_vbench_v1_snapshot.sh
configs/model_generation.consisid_official_vbench_v1.json
EOF

tar --ignore-failed-read -czf "$TAR" -T "$SNAPDIR/filelist.txt"
du -h "$TAR"
echo "$TAR"
