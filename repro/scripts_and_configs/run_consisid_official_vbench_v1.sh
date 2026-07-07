#!/usr/bin/env bash
set -euo pipefail

SERVER_ROOT="${SERVER_ROOT:-/data/zengxin/zwt}"
PROJECT_DIR="${PROJECT_DIR:-$SERVER_ROOT/face_study}"
VBENCH_DIR="${VBENCH_DIR:-$SERVER_ROOT/external/VBench-v1}"
VBENCH_ENV="${VBENCH_ENV:-$SERVER_ROOT/conda_envs/vbench_v1}"
CONSISID_PY="${CONSISID_PY:-$SERVER_ROOT/conda_envs/face_consisid/bin/python}"
VBENCH_PY="${VBENCH_PY:-$VBENCH_ENV/bin/python}"
CONSISID_CKPT_DIR="${CONSISID_CKPT_DIR:-$SERVER_ROOT/models/consisid/ConsisID-preview}"
REFERENCE_IMAGE="${REFERENCE_IMAGE:-$PROJECT_DIR/face/CVPR25-ConsisID/source/ConsisID-main/asserts/example_images/3.png}"
RUN_MODE="${RUN_MODE:-smoke}"
RUN_ID="${RUN_ID:-consisid_official_vbench_v1_${RUN_MODE}_$(date +%Y%m%d_%H%M%S)}"
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-1}"
LINK_MODE="${LINK_MODE:-symlink}"
INSTALL_DETECTRON2="${INSTALL_DETECTRON2:-1}"
STRICT_SETUP="${STRICT_SETUP:-0}"
SKIP_SETUP="${SKIP_SETUP:-0}"
SKIP_BUILD_PROMPTS="${SKIP_BUILD_PROMPTS:-0}"
SKIP_GENERATE="${SKIP_GENERATE:-0}"
SKIP_LINK="${SKIP_LINK:-0}"
SKIP_EVALUATE="${SKIP_EVALUATE:-0}"
SKIP_REPORT="${SKIP_REPORT:-0}"

case "$RUN_MODE" in
  smoke)
    MAX_PROMPTS="${MAX_PROMPTS:-3}"
    SAMPLES_PER_PROMPT="${SAMPLES_PER_PROMPT:-1}"
    EVAL_DIMENSIONS="${EVAL_DIMENSIONS:-temporal_flickering}"
    ;;
  single)
    MAX_PROMPTS="${MAX_PROMPTS:-}"
    SAMPLES_PER_PROMPT="${SAMPLES_PER_PROMPT:-1}"
    EVAL_DIMENSIONS="${EVAL_DIMENSIONS:-subject_consistency background_consistency temporal_flickering motion_smoothness dynamic_degree aesthetic_quality imaging_quality object_class multiple_objects human_action color spatial_relationship scene temporal_style appearance_style overall_consistency}"
    ;;
  full5)
    MAX_PROMPTS="${MAX_PROMPTS:-}"
    SAMPLES_PER_PROMPT="${SAMPLES_PER_PROMPT:-5}"
    EVAL_DIMENSIONS="${EVAL_DIMENSIONS:-subject_consistency background_consistency temporal_flickering motion_smoothness dynamic_degree aesthetic_quality imaging_quality object_class multiple_objects human_action color spatial_relationship scene temporal_style appearance_style overall_consistency}"
    ;;
  *)
    echo "RUN_MODE must be smoke, single, or full5" >&2
    exit 2
    ;;
esac

mkdir -p "$SERVER_ROOT"/{tmp,pip_cache,hf_cache,cache/torch,external} "$PROJECT_DIR/outputs/official_vbench_v1_consisid"
export TMPDIR="${TMPDIR:-$SERVER_ROOT/tmp}"
export TEMP="${TEMP:-$SERVER_ROOT/tmp}"
export TMP="${TMP:-$SERVER_ROOT/tmp}"
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-$SERVER_ROOT/pip_cache}"
export HF_HOME="${HF_HOME:-$SERVER_ROOT/hf_cache}"
export HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-$HF_HOME/hub}"
export TORCH_HOME="${TORCH_HOME:-$SERVER_ROOT/cache/torch}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-$HF_HOME/transformers}"
export DEEPFACE_HOME="${DEEPFACE_HOME:-$SERVER_ROOT/cache/deepface}"
export PATH="$(cd "$(dirname "$CONSISID_PY")" && pwd):$PATH"
export PYTHON_BIN="$CONSISID_PY"

PROMPTS_CSV="${PROMPTS_CSV:-data/test_sets/official_vbench_v1/prompts.csv}"
PROMPT_SUMMARY="${PROMPT_SUMMARY:-${PROMPTS_CSV%.csv}_summary.json}"
MANIFEST="data/manifests/${RUN_ID}.csv"
GEN_LOG="data/manifests/${RUN_ID}.generation_log.csv"
GEN_ROOT="data/generated_official_vbench/${RUN_ID}"
STANDARD_DIR="data/generated_official_vbench/${RUN_ID}_standard_names"
OUT_ROOT="outputs/official_vbench_v1_consisid/${RUN_ID}"
EVAL_ROOT="$OUT_ROOT/evaluation"
REPORT_DIR="$OUT_ROOT/report"
LINK_REPORT="$OUT_ROOT/link_report.json"

setup_vbench() {
  cd "$SERVER_ROOT/external"
  if [[ ! -d "$VBENCH_DIR" ]]; then
    curl -L -o VBench-v0.1.5.tar.gz https://github.com/Vchitect/VBench/archive/refs/tags/v0.1.5.tar.gz
    tar -xzf VBench-v0.1.5.tar.gz
    mv VBench-0.1.5 "$VBENCH_DIR"
  fi
  if [[ ! -x "$VBENCH_PY" ]]; then
    "$CONSISID_PY" -m venv --system-site-packages "$VBENCH_ENV"
  fi
  "$VBENCH_PY" -m pip install -U pip wheel setuptools
  "$VBENCH_PY" -m pip install -r "$VBENCH_DIR/requirements.txt"
  "$VBENCH_PY" -m pip install -e "$VBENCH_DIR"
  if [[ "$INSTALL_DETECTRON2" == "1" ]]; then
    if ! "$VBENCH_PY" -c "import detectron2" >/dev/null 2>&1; then
      if ! "$VBENCH_PY" -m pip install "detectron2@git+https://github.com/facebookresearch/detectron2.git"; then
        echo "detectron2 install failed; dimensions that require it may fail." >&2
        [[ "$STRICT_SETUP" == "1" ]] && exit 1
      fi
    fi
  fi
  "$VBENCH_PY" "$VBENCH_DIR/evaluate.py" --help >/dev/null
}

build_prompts() {
  cd "$PROJECT_DIR"
  "$CONSISID_PY" scripts/build_official_vbench_v1_inputs.py \
    --vbench-info "$VBENCH_DIR/vbench/VBench_full_info.json" \
    --output "$PROMPTS_CSV" \
    --reference-image "$REFERENCE_IMAGE" \
    --sample-count "$SAMPLES_PER_PROMPT"
}

generate_videos() {
  cd "$PROJECT_DIR"
  args=(
    scripts/generate_videos_manifest.py
    --model consisid_official_vbench_v1
    --config configs/model_generation.consisid_official_vbench_v1.json
    --prompts "$PROMPTS_CSV"
    --samples-per-prompt "$SAMPLES_PER_PROMPT"
    --output-root "$GEN_ROOT"
    --output-name-template "{prompt_id}_{model_name}_{sample_index}.mp4"
    --manifest-output "$MANIFEST"
    --log-output "$GEN_LOG"
    --skip-existing
    --stop-on-failure
  )
  if [[ -n "$MAX_PROMPTS" ]]; then
    args+=(--max-prompts "$MAX_PROMPTS")
  fi
  CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES" CONSISID_CKPT_DIR="$CONSISID_CKPT_DIR" "$CONSISID_PY" "${args[@]}"
}

link_standard_names() {
  cd "$PROJECT_DIR"
  "$CONSISID_PY" scripts/link_official_vbench_v1_standard_names.py \
    --prompts "$PROMPTS_CSV" \
    --generation-log "$GEN_LOG" \
    --output-dir "$STANDARD_DIR" \
    --report "$LINK_REPORT" \
    --mode "$LINK_MODE"
}

evaluate_vbench() {
  cd "$VBENCH_DIR"
  mkdir -p "$PROJECT_DIR/$EVAL_ROOT"
  for dim in $EVAL_DIMENSIONS; do
    mkdir -p "$PROJECT_DIR/$EVAL_ROOT/$dim"
    echo "Evaluating $dim"
    CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES" "$VBENCH_PY" evaluate.py \
      --videos_path "$PROJECT_DIR/$STANDARD_DIR" \
      --dimension "$dim" \
      --output_path "$PROJECT_DIR/$EVAL_ROOT/$dim" \
      --mode vbench_standard \
      > "$PROJECT_DIR/$EVAL_ROOT/$dim.log" 2>&1 || true
  done
}

build_report() {
  cd "$PROJECT_DIR"
  "$CONSISID_PY" scripts/build_official_vbench_v1_chinese_report.py \
    --vbench-output-root "$EVAL_ROOT" \
    --output-dir "$REPORT_DIR" \
    --prompt-summary "$PROMPT_SUMMARY" \
    --link-report "$LINK_REPORT" \
    --vbench-version "v0.1.5" \
    --sample-count "$SAMPLES_PER_PROMPT" \
    --reference-image "$REFERENCE_IMAGE"
}

echo "RUN_ID=$RUN_ID"
echo "RUN_MODE=$RUN_MODE"
if [[ "$SKIP_SETUP" == "1" ]]; then
  echo "Skipping VBench setup"
else
  setup_vbench
fi
if [[ "$SKIP_BUILD_PROMPTS" == "1" ]]; then
  echo "Skipping prompt build"
else
  build_prompts
fi
if [[ "$SKIP_GENERATE" == "1" ]]; then
  echo "Skipping video generation"
else
  generate_videos
fi
if [[ "$SKIP_LINK" == "1" ]]; then
  echo "Skipping VBench standard-name linking"
else
  link_standard_names
fi
if [[ "$SKIP_EVALUATE" == "1" ]]; then
  echo "Skipping VBench evaluation"
else
  evaluate_vbench
fi
if [[ "$SKIP_REPORT" == "1" ]]; then
  echo "Skipping Chinese report build"
else
  build_report
fi
echo "Report: $PROJECT_DIR/$REPORT_DIR/ConsisID官方VBench评测报告.md"
