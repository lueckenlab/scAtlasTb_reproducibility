# Figure 5: HARP feature selection benchmark

[scAtlasTb](https://scatlastb.readthedocs.io/en/latest/index.html) feature-selection benchmark for the Human Cell Atlas Reference for PBMCs (HARP), 8.3M circulating immune cells from healthy and COVID-19 donors. The workflow compares a default, fully data-driven batch-aware HVG strategy against a custom strategy that excludes immunoglobulin/TCR, sex, ribosomal, and mitochondrial genes, sweeping HVG count/flavor (`highly_variable_genes` vs. `extra_hvgs`, 3000-7000 genes) with harmony integration, globally and per lineage (TCD4, TCD8_NK, B_plasma, Myeloid), then scores each with `metrics`/`marker_genes` to quantify the resulting batch/bio-conservation trade-off. This config set only covers the feature-selection sweep — the separate integration-method benchmark (harmony, harmony-unscaled, scVI, scPoli) from `harp_figures/figure2/{C,F}` isn't used here and was dropped.


## Usage

From the repository root:

```bash
bash configs/HARP/run.sh metrics_all -n     # dry run
bash configs/HARP/run.sh metrics_all -c 10  # execute
```

Swap `metrics_all` for another module target (see the [top-level README](../README.md#picking-a-target)) to run just one stage, e.g. `preprocessing_all`, `integration_all`, `clustering_all`, `majority_voting_all`.

## Configfiles loaded (in order)

| File | Purpose |
| --- | --- |
| `.profiles/czbiohub/cluster_config.yaml` | SLURM cluster resources |
| `configs/global.yaml` | OS / GPU / conda channel settings shared by all workflows |
| `configs/HARP/gene_sets/gene_sets.yaml` | Marker/Moran's I gene panels per lineage (`MARKER_GENES:` key) |
| `configs/HARP/defaults.yaml` | `output_dir`; all module defaults shared across `DATASETS` entries (integration, clustering, `label_transfer`, `majority_voting`, metrics, funkyheatmap) |
| `configs/HARP/prepare_data.yaml` | `Benchmark_prepare_data`: filter → split_data → subset/preprocessing |
| `configs/HARP/feature_selection.yaml` | `Benchmark_n_hvg`, `Benchmark_n_hvg_{global,TCD4,TCD8_NK,B_plasma,Myeloid}`: the HVG-count/flavor sweep and its metrics |
| `configs/HARP/config.yaml` | `defaults.datasets` target list (drives the bare `all`/DAG-rendering rule only) |

## `DATASETS` entries

| Name | File | Module chain | What it does |
| --- | --- | --- | --- |
| `Benchmark_prepare_data` | prepare_data.yaml | `filter → split_data → subset, preprocessing` | Removes QC-failed/doublet-flagged cells from the already-relabeled cohort, splits by `lineage_celltypist`, then subsets/preprocesses both the split and unsplit data |
| `Benchmark_n_hvg` | feature_selection.yaml | `preprocessing → integration → clustering → label_transfer` | HVG-count sweep (3000-7000 genes) × HVG-flavor (`highly_variable_genes` vs. `extra_hvgs`) with harmony, per lineage and globally |
| `Benchmark_n_hvg_global` / `_TCD4` / `_TCD8_NK` / `_B_plasma` / `_Myeloid` | feature_selection.yaml | `metrics → collect → majority_voting` (`_B_plasma` also runs `marker_genes`) | Benchmarks the HVG sweep per lineage |

## Required input

`configs/HARP/prepare_data.yaml` expects an already-relabeled checkpoint at:

```
data/input/hca_out/relabel/dataset~Benchmark_prepare_data/file_id~All.zarr
```

`configs/HARP/feature_selection.yaml` also expects `configs/HARP/cell_type_order.txt` for `Benchmark_n_hvg_B_plasma.marker_genes.plot.group_order`; add that file manually before running `marker_genes_all`.

## Output

Running this config, all data lands under `data/pipeline/HARP/<module>/dataset~<name>/...` and plots under `data/images/HARP/<module>/dataset~<name>/...`, per `output_dir`/`images` in `configs/HARP/defaults.yaml`.

Outputs specifically used for the paper's figures (see `../../notebooks/HARP/`) — as published, the figure notebooks read the equivalent objects from the original `harp_figures` pipeline run (different base path, same `DATASETS` entry names) rather than from this ported config; the table gives both:

| Figure | Source output (this config) | Source output (as published) | Consuming notebook |
| --- | --- | --- | --- |
| Fig. 5A–D + Extended Fig. 4A (default vs. custom feature selection, B/Plasma lineage) | Final `majority_voting` output of `Benchmark_n_hvg_B_plasma`: `data/pipeline/HARP/majority_voting/dataset~Benchmark_n_hvg_B_plasma/file_id~collect:Benchmark_n_hvg_B_plasma.zarr` | `data/input/hca_out/marker_genes/dataset~Benchmark_n_hvg_B_plasma/file_id~majority_voting:collect:Benchmark_n_hvg_B_plasma.zarr` | `notebooks/HARP/Fig5_B_plasma.ipynb` → `figures/figure5/` |
| Extended Fig. 4B / Supp. Fig. 10 (n_top_genes batch/bio trade-off, all lineages) | Final `majority_voting` output of `Benchmark_n_hvg_{global,TCD4,TCD8_NK,B_plasma,Myeloid}`: `data/pipeline/HARP/majority_voting/dataset~Benchmark_n_hvg_<lineage>/file_id~collect:Benchmark_n_hvg_<lineage>.zarr` | `data/pipeline/input/hca_out/majority_voting/dataset~Benchmark_n_hvg_<lineage>/file_id~collect:Benchmark_n_hvg_<lineage>.zarr` | `notebooks/HARP/Fig5_Feature_selection_benchmark.ipynb` → `figures/figure5/tradeoff/` |

As with the `metrics → collect → majority_voting` chains in the HRCA config, each lineage's `majority_voting` output already carries the swept models' `metrics` scores in `.uns` alongside the per-cell consensus/disagreement annotations, so a single file per lineage covers both the marker/UMAP panels and the metric trade-off plots. `Benchmark_prepare_data` is upstream/complementary to the feature-selection benchmark above and isn't the direct source of a numbered figure panel.
