# Figure 3: HRCA Benchmark

Targeted integration benchmark for the Human Retina Cell Atlas (HRCA), a >3M-nucleus snRNA dataset from 9 studies and >120 donors with lineage-level annotations for amacrine (AC), bipolar (BC), and retinal ganglion (RGC) cells (>1.6M nuclei, >130 cell types). The workflow sweeps feature-selection strategy, integration method (harmony, scVI, DRVI, scPoli, plus scimilarity reference mapping), and global vs. lineage-specific integration scope (64 integration models, 96 lineage-specific representations), then scores each with `metrics`/`marker_genes` to identify the best strategy per lineage.

## Usage

From the repository root:

```bash
bash configs/HRCA/run.sh integration_all -n     # dry run
bash configs/HRCA/run.sh integration_all -c 10  # execute
```

Swap `integration_all` for another module target (see the [top-level README](../README.md#picking-a-target)) to run just one stage, e.g. `doublets_all`, `qc_all`, `clustering_all`, `metrics_all`, `marker_genes_all`.

## Configfiles loaded (in order)

| File | Purpose |
| --- | --- |
| `configs/global.yaml` | OS / GPU / conda channel settings shared by all workflows |
| `configs/HRCA/defaults.yaml` | HRCA-wide module defaults (integration methods, clustering, metrics, funkyheatmap) |
| `configs/HRCA/marker_genes.yaml` | Marker gene panels for `AC`, `BC`, `RGC` (`MARKER_GENES:` key) |
| `configs/HRCA/integration.yaml` | Main entries: `PREPARE_DATA`, `INTEGRATION_GLOBAL`, `INTEGRATION_LINEAGE`, `AC`, `BC`, `RGC` |

## `DATASETS` entries

| Name | Module chain | What it does |
| --- | --- | --- |
| `PREPARE_DATA` | `relabel → doublets → qc → merge → split_data` | Relabels the raw snRNA cohort, removes doublets, runs QC, splits by `majorclass` (AC/BC/RGC) |
| `INTEGRATION_GLOBAL` | `preprocessing → integration → reference_mapping → split_data → clustering → label_transfer` | Integrates the whole retina (all lineages together) with harmony/scVI/scANVI/DRVI/scPoli plus scimilarity reference mapping, batch key and HVG count swept |
| `INTEGRATION_LINEAGE` | `preprocessing → integration → clustering → label_transfer` | Same integration sweep run independently within each of AC, BC, RGC |
| `AC` | `metrics → collect → majority_voting` | Benchmarks every global- and lineage-strategy integration result for amacrine cells against `gene_sets: AC` |
| `BC` | `metrics → collect → majority_voting` | Same benchmark for bipolar cells |
| `RGC` | `metrics → collect → majority_voting` | Same benchmark for retinal ganglion cells |

`AC`/`BC`/`RGC` each compare integration runs swept over method (harmony, scvi, drvi, scpoli, scimilarity), strategy (`global` vs `lineage`), batch key (`None` vs `sample_id`) and HVG count (1000 vs 3000) — see the `metrics.input` block in `configs/HRCA/integration.yaml` for the full file-ID matrix.

## Output

All data lands under `data/pipeline/HRCA/<module>/dataset~<name>/...` and plots under `data/images/HRCA/<module>/dataset~<name>/...`, per `output_dir`/`images` in `configs/HRCA/defaults.yaml`.

Outputs specifically used for the paper's figures (see `../../notebooks/HRCA/`):

| Figure | Source output | Consuming notebook |
| --- | --- | --- |
| Fig. 3C–E (batch/bio trade-off scatter, lineage-vs-global boxplot) | Final `majority_voting` output of each of `AC`/`BC`/`RGC`: `data/pipeline/HRCA/majority_voting/dataset~{AC,BC,RGC}/file_id~collect:{AC,BC,RGC}.zarr` — the preceding `collect` step merges every swept model's `metrics` scores into that object's `.uns` (keys matching `metrics--*`), which the notebook concatenates into `metrics_df.tsv` before plotting | `notebooks/HRCA/Fig3CDE_benchmark_evaluation.ipynb` → `figures/figure3/` |
| Fig. 3F + Extended Fig. 3B–C (majority-voting disagreement / doublet overlap, AC lineage) | Same file for `AC`: `data/pipeline/HRCA/majority_voting/dataset~AC/file_id~collect:AC.zarr` (per-cell majority-consensus disagreement score + Scrublet score alongside the embeddings) | `notebooks/HRCA/Fig3F.ipynb` → `figures/figure3/F/` |
| Extended Fig. 3A (funkyheatmap of summarized scores per lineage) | `metrics` module's `funkyheatmap` rule, run per dataset: `data/images/HRCA/dataset~{AC,BC,RGC}/funky_heatmap.svg` (+ `.tsv` with the underlying table) | — (rendered directly by the pipeline) |

`PREPARE_DATA`, `INTEGRATION_GLOBAL`, and `INTEGRATION_LINEAGE` produce the upstream QC'd/integrated objects that `AC`/`BC`/`RGC` benchmark against — they feed the figures above but aren't read directly by a figure notebook.
