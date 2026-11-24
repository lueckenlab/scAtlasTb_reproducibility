#!/usr/bin/env bash
# scAtlasTb arm: run scAtlasTb.yaml on one subsample with local execution inside the
# current allocation (no cluster submission, so no queueing time in the measurement).
# Per-rule timings come from scAtlasTb's own Snakemake benchmark files.
#
# Usage (from the repo root, snakemake env active):
#   bash scripts/scalability_comparison/workflow_comparison/run_scAtlasTb.sh <size> <rep> <jobs>
#   <jobs>=1 runs one job at a time (isolates Dask/I/O); <jobs>=N lets Snakemake run up to N jobs in parallel.
#   Either way Snakemake gets all $OMP_NUM_THREADS cores, so a single job (e.g. scVI) can use as many
#   threads as in the brute-force arm.
set -euo pipefail

SIZE=$1
REP=$2
JOBS=$3
CORES=${OMP_NUM_THREADS:-$JOBS}

pipeline="$(realpath "${SCATLASTB:-../scAtlasTb}")"  # override with SCATLASTB=/path/to/scAtlasTb
HERE=scripts/scalability_comparison/workflow_comparison
BASE=data/pipeline/scalability/workflow_comparison
INPUT=$BASE/input/HLCA_${SIZE}.h5ad
OUT=$BASE/scAtlasTb_j${JOBS}/${SIZE}/rep${REP}

mkdir -p "$OUT"

# per-run settings layered on top of scAtlasTb.yaml
cat > "$OUT/run_config.yaml" <<EOF
output_dir: $OUT/pipeline
images: $OUT/images
DATASETS:
  HLCA:
    input:
      preprocessing:
        HLCA_${SIZE}: $INPUT
    integration:
      threads: $CORES  # scVI sets torch threads from this; Snakemake caps it at --cores
EOF

snakemake \
  --snakefile "$pipeline/workflow/Snakefile" \
  --configfile "$HERE/scAtlasTb.yaml" "$OUT/run_config.yaml" \
  --cores "$CORES" \
  --resources parallel_jobs="$JOBS" \
  --default-resources parallel_jobs=1 \
  --use-conda \
  --rerun-incomplete \
  --printshellcmds \
  --nolock \
  metrics_merge_all \
  "${@:4}" \
  2> >(tee "$OUT/snakemake.log" >&2)  # per-job timings for plot_runtime.py
