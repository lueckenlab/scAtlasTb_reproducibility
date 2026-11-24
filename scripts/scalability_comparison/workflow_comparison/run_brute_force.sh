#!/usr/bin/env bash
# Brute-force arm: run brute_force.py stage by stage, each stage in the same pre-existing
# conda env scAtlasTb uses for that step, and record each stage with measure.py.
#
# Usage (from the repo root): bash scripts/scalability_comparison/workflow_comparison/run_brute_force.sh <size> <rep>
set -euo pipefail

SIZE=$1
REP=$2

HERE=scripts/scalability_comparison/workflow_comparison
BASE=data/pipeline/scalability/workflow_comparison
INPUT=$BASE/input/HLCA_${SIZE}.h5ad
OUT=$BASE/brute_force/${SIZE}/rep${REP}
SUMMARY=$OUT/measure_steps.tsv
MEASURE_PY="$(conda info --base)/envs/scanpy/bin/python"

# integration method -> conda env (same as scAtlasTb's workflow/integration/params.tsv on CPU)
declare -A METHOD_ENV=(
  [unintegrated]=scanpy
  [combat]=scanpy
  [harmonypy]=scanpy
  [scvi]=scvi-tools
  [bbknn]=bbknn
)

mkdir -p "$OUT"

# measure <step> <env> <brute_force.py args...>
measure() {
  local step=$1 env=$2
  shift 2
  "$MEASURE_PY" "$HERE/measure.py" \
    --summary "$SUMMARY" \
    --label arm=brute_force size="$SIZE" rep="$REP" step="$step" \
    --disk-dir "$OUT" \
    -- conda run -n "$env" --no-capture-output python "$HERE/brute_force.py" "$@"
}

measure preprocess scanpy preprocess "$INPUT" "$OUT/preprocessed.h5ad"

for method in unintegrated combat harmonypy scvi bbknn; do
  measure "integrate:$method" "${METHOD_ENV[$method]}" \
    integrate "$method" "$OUT/preprocessed.h5ad" "$OUT/integrated_${method}"
done

# one metrics run per method and output type (7 in total, as in scAtlasTb)
for file in "$OUT"/integrated_*.h5ad; do
  name=$(basename "$file" .h5ad)
  name=${name#integrated_}
  measure "metrics:$name" scib \
    metrics "$file" "$OUT/metrics_${name}.tsv"
done

# one table with all scores
head -n1 "$OUT/metrics_unintegrated_embed.tsv" > "$OUT/metrics.tsv"
tail -q -n+2 "$OUT"/metrics_*.tsv >> "$OUT/metrics.tsv"
