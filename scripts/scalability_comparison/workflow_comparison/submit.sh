#!/usr/bin/env bash
# Submit every (arm x size x replicate) run as its own exclusive SLURM job on the same
# node type, with identical CPU, memory and thread limits. Each run is wrapped in
# measure.py (step=total), so all arms are measured the same way.
#
# Arms:
#   brute_force   brute_force.py, one stage after another
#   scAtlasTb_j1  scAtlasTb, one Snakemake job at a time with all $THREADS threads (effect of Dask + I/O only)
#   scAtlasTb_jN  scAtlasTb, up to $THREADS Snakemake jobs in parallel (realistic use)
#
# Every job runs in node-local /tmp (NVMe; the node is exclusive): the input is copied there first
# (not timed) and only tables, logs and metrics are copied back. Shared scratch cannot hold the
# brute-force outputs at full size (~330 GB per run), and both arms write to the same kind of disk.
#
# Usage (from the repo root): bash scripts/scalability_comparison/workflow_comparison/submit.sh [--dry-run]
set -euo pipefail

SIZES=(50000 100000 250000 full)
REPS=(1 2 3)
ARMS=(brute_force scAtlasTb_j1 scAtlasTb_jN)

THREADS=16
MEM=250G
TIME=2-00:00:00
PARTITION=cpu
CONSTRAINT=amd_7h12  # one CPU type, so runtimes are comparable

HERE=scripts/scalability_comparison/workflow_comparison
BASE=data/pipeline/scalability/workflow_comparison
LOGS=logs/workflow_comparison
REPO=$(pwd)
SCATLASTB="$(realpath "${SCATLASTB:-../scAtlasTb}")"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

mkdir -p "$LOGS"

for size in "${SIZES[@]}"; do
  for rep in "${REPS[@]}"; do
    for arm in "${ARMS[@]}"; do
      case $arm in
        brute_force)  cmd="bash $HERE/run_brute_force.sh $size $rep"
                      out=$BASE/brute_force/$size/rep$rep ;;
        scAtlasTb_j1) cmd="bash $HERE/run_scAtlasTb.sh $size $rep 1"
                      out=$BASE/scAtlasTb_j1/$size/rep$rep ;;
        scAtlasTb_jN) cmd="bash $HERE/run_scAtlasTb.sh $size $rep $THREADS"
                      out=$BASE/scAtlasTb_j$THREADS/$size/rep$rep ;;
      esac

      job="
set -euo pipefail
eval \"\$(conda shell.bash hook)\"
conda activate snakemake
# same thread limits for every library in both arms
export OMP_NUM_THREADS=$THREADS MKL_NUM_THREADS=$THREADS OPENBLAS_NUM_THREADS=$THREADS NUMBA_NUM_THREADS=$THREADS
export SCATLASTB=$SCATLASTB

# node-local working copy with the same relative layout as the repo
work=/tmp/wfcmp_\$SLURM_JOB_ID
trap 'rm -rf \$work' EXIT
mkdir -p \$work/$BASE/input \$work/$out
ln -s $REPO/scripts \$work/scripts
cp $REPO/$BASE/input/HLCA_$size.h5ad \$work/$BASE/input/
cd \$work

status=0
\$(conda info --base)/envs/scanpy/bin/python $HERE/measure.py \
  --summary $out/measure_total.tsv \
  --label arm=$arm size=$size rep=$rep step=total threads=$THREADS mem=$MEM scatlastb=\$(git -C $SCATLASTB rev-parse --short HEAD) \
  --disk-dir $out \
  --timeseries $out/rss_timeseries.tsv \
  -- $cmd || status=\$?

# keep tables, logs and configs (incl. scAtlasTb metrics and benchmarks), drop the data
rm -rf $REPO/$out && mkdir -p $REPO/$out
rsync -a --prune-empty-dirs --include='*/' --include='*.tsv' --include='*.log' --include='*.yaml' --exclude='*' \
  $out/ $REPO/$out/
exit \$status
"
      if $DRY_RUN; then
        echo "=== $arm size=$size rep=$rep"
        echo "$job"
      else
        sbatch \
          --partition=$PARTITION \
          --constraint=$CONSTRAINT \
          --exclusive \
          --cpus-per-task=$THREADS \
          --mem=$MEM \
          --time=$TIME \
          --job-name="wfcmp_${arm}_${size}_r${rep}" \
          --output="$LOGS/%j-${arm}_${size}_r${rep}.out" \
          --wrap="$job"
      fi
    done
  done
done
