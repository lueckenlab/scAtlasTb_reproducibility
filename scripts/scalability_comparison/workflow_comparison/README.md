# Workflow comparison: scAtlasTb vs. brute-force script

Compares the same preprocessing → integration → metrics workflow run two ways on HLCA core subsamples:

| Arm | What runs |
|---|---|
| `scAtlasTb_j1` | [`scAtlasTb.yaml`](scAtlasTb.yaml), one Snakemake job at a time, each with all 16 threads: shows the effect of Dask, partial reads and linked zarr outputs only |
| `scAtlasTb_j16` | Same config, up to 16 Snakemake jobs in parallel: realistic use |
| `brute_force` | [`brute_force.py`](brute_force.py): reads the full `.h5ad` into memory at every stage and writes a full `.h5ad` copy per result |

Both arms use the **pre-existing conda environments** (`env_mode: local`): `scanpy` (preprocessing, unintegrated, combat, harmonypy), `scvi-tools` (scVI on CPU), `bbknn`, `scib` (metrics), and `snakemake` to drive scAtlasTb. They call the same functions with the same parameters, evaluate the same 7 method × output-type combinations (unintegrated full/embed/knn, combat full, harmonypy embed, scvi embed, bbknn knn) and compute neighbors and a UMAP for each, as scAtlasTb does.

## Files

| File | Purpose |
|---|---|
| `subsample.py` | Creates the shared inputs `HLCA_{50000,100000,250000,full}.h5ad` (raw counts in `X`, nested subsamples, seed 0). Not timed. |
| `scAtlasTb.yaml` | scAtlasTb config (one dataset). `run_scAtlasTb.sh` layers the input path and output dir on top. |
| `run_scAtlasTb.sh` | Runs Snakemake locally inside the allocation (no queueing in the timings), target `metrics_merge_all`. |
| `brute_force.py` | Brute-force stages: `preprocess`, `integrate <method>`, `metrics`. |
| `run_brute_force.sh` | Runs the brute-force stages in order, each in its matching env and measured separately. |
| `measure.py` | Wraps a command: wall time, CPU time, peak summed RSS of the process tree, bytes read/written, disk use (actual vs. symlink-expanded). |
| `submit.sh` | One exclusive SLURM job per arm × size × replicate (3 × 4 × 3 = 36), on `amd_7h12` nodes with 16 CPUs and 250G. Each job runs in node-local `/tmp` and copies back only tables, logs and metrics. |
| `plot_runtime.py` | Plots wall/CPU time, peak memory and disk per arm and size, time per stage and per integration method. |

## Running (from the repo root)

```bash
conda run -n scanpy python scripts/scalability_comparison/workflow_comparison/subsample.py \
  data/pipeline/load_data/download/HLCAv1_core.h5ad data/pipeline/scalability/workflow_comparison/input \
  50000 100000 250000 full
bash scripts/scalability_comparison/workflow_comparison/submit.sh --dry-run   # print the jobs
bash scripts/scalability_comparison/workflow_comparison/submit.sh             # submit
conda run -n scanpy python scripts/scalability_comparison/workflow_comparison/plot_runtime.py \
  data/pipeline/scalability/workflow_comparison data/pipeline/scalability/workflow_comparison/plots
```

## Outputs

Under `data/pipeline/scalability/workflow_comparison/<arm>/<size>/rep<r>/`:

- `measure_total.tsv`: one row for the whole run (both arms)
- `rss_timeseries.tsv`: memory over time
- brute force only: `measure_steps.tsv` (per stage) and `metrics.tsv` (scores)
- scAtlasTb only: `snakemake.log` (per-job timings) and, under `pipeline/`, per-rule `.benchmark/` TSVs and the metrics tables

The data files themselves are deleted with the node-local working directory.

## Known caveats

- All runs read and write node-local NVMe, not the shared filesystem: shared scratch cannot hold the brute-force
  outputs at full size (~330 GB per run). On fast local disk the brute force arm's extra I/O costs less, so this
  understates rather than overstates scAtlasTb's advantage.
- Leiden clustering for the metrics differs: scAtlasTb uses `flavor='igraph'` with `n_iterations=2`, while
  `brute_force.py` uses scib's `cluster_optimal_resolution` with scanpy's defaults (`leidenalg`, run to
  convergence). This makes the brute-force metrics stage slower (at 50k cells: 84 vs. 33 min) for reasons other than I/O.
- Thread limits (`OMP_NUM_THREADS` etc.) are 16 for every process. In `scAtlasTb_j16`, parallel jobs can therefore oversubscribe the 16 CPUs.
- I/O bytes come from sampling once per second, so very short-lived processes may be missed.
- An out-of-memory crash or timeout is recorded via `exit_code` and counts as a result.
- The brute-force arm does not finish the full HLCA within the 48 h job limit. Replicate 1 had spent 28 h
  (preprocessing and integration in 2.4 h, then 2 of the 7 metrics evaluations in 14 h and 8.6 h), so the runs were
  cancelled and are reported as "> 48 h". Their per-step timings so far are kept in
  `brute_force/full/rep{1,2}/measure_steps.tsv`; with no `measure_total.tsv`, `plot_runtime.py` skips them.
- `pcr_comparison` is not computed in either arm. In scAtlasTb, integrating on HVGs (`var_mask`) leaves the
  combat full output with HVG-only `var` but all-gene `layers`, which breaks the unintegrated PCA that
  `pcr_comparison` needs.
