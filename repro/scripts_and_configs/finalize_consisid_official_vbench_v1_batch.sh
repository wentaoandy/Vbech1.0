#!/usr/bin/env bash
set -euo pipefail

SERVER_ROOT="${SERVER_ROOT:-/data/zengxin/zwt}"
PROJECT_DIR="${PROJECT_DIR:-$SERVER_ROOT/face_study}"
BATCH="${BATCH:-}"
SHARDS="${SHARDS:-01 02}"
EVAL_GPU="${EVAL_GPU:-2}"
POLL_SECONDS="${POLL_SECONDS:-300}"

cd "$PROJECT_DIR"
if [[ -z "$BATCH" ]]; then
  BATCH="$(cat outputs/official_vbench_v1_consisid/full_single_sharded/latest_batch.txt)"
fi

LOG_DIR="outputs/official_vbench_v1_consisid/full_single_sharded"
FINAL_LOG="$LOG_DIR/${BATCH}_finalize.log"

echo "Finalizer batch: $BATCH" | tee -a "$FINAL_LOG"
while true; do
  running=0
  for shard in $SHARDS; do
    run_id="${BATCH}_shard${shard}"
    pid_file="$LOG_DIR/${run_id}.pid"
    if [[ -f "$pid_file" ]]; then
      pid="$(cat "$pid_file")"
      if kill -0 "$pid" >/dev/null 2>&1; then
        running=1
      fi
    fi
  done
  for shard in $SHARDS; do
    run_id="${BATCH}_shard${shard}"
    count="$(find "data/generated_official_vbench/${run_id}/consisid_official_vbench_v1" -type f -name '*.mp4' 2>/dev/null | wc -l)"
    echo "$(date +%F_%T) ${run_id} videos=${count}" | tee -a "$FINAL_LOG"
  done
  if [[ "$running" == "0" ]]; then
    break
  fi
  sleep "$POLL_SECONDS"
done

echo "Merging shard CSV files" | tee -a "$FINAL_LOG"
"$SERVER_ROOT/conda_envs/face_consisid/bin/python" scripts/merge_official_vbench_v1_shards.py \
  --run-prefix "$BATCH" \
  --shards "$(echo "$SHARDS" | tr ' ' ',')" \
  --output-manifest "data/manifests/${BATCH}.csv" \
  --output-log "data/manifests/${BATCH}.generation_log.csv" \
  --fail-on-missing | tee -a "$FINAL_LOG"

echo "Running official VBench evaluation and Chinese report" | tee -a "$FINAL_LOG"
RUN_ID="$BATCH" \
RUN_MODE=single \
SKIP_SETUP=1 \
SKIP_BUILD_PROMPTS=1 \
SKIP_GENERATE=1 \
CUDA_VISIBLE_DEVICES="$EVAL_GPU" \
bash scripts/run_consisid_official_vbench_v1.sh | tee -a "$FINAL_LOG"

echo "Finalize done: outputs/official_vbench_v1_consisid/${BATCH}/report" | tee -a "$FINAL_LOG"
