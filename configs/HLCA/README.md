# HLCA workflows

Shared config root for the Human Lung Cell Atlas (HLCA) workflows used in the paper. It holds the files common to both HLCA sub-workflows plus one subdirectory per workflow:

| Subdirectory | Figures | What it does |
| --- | --- | --- |
| [`QC/`](QC/README.md) | Fig. 2, Extended Fig. 2 | `scAutoQC`-based per-study/lineage thresholding, the "HighQC" reference build, and reference-mapping comparison against the original HLCA |
| [`batch_analysis/`](batch_analysis/README.md) | Fig. 4 | Covariate variance/confounding analysis (PC regression, Theil's U) and the `dataset`-vs-`sample` batch-definition comparison |

Neither subdirectory's `run.sh` is called from here — see each subdirectory's README for its own `bash configs/HLCA/<QC,batch_analysis>/run.sh ...` invocation.

## Shared files

| File | Purpose |
| --- | --- |
| `defaults.yaml` | HLCA-wide module defaults loaded by both `QC/run.sh` and `batch_analysis/run.sh`: `relabel`, `merge`, `split_data`, `preprocessing`, `integration` (harmony/scVI/scANVI hyperparameters), `clustering`, `label_transfer`, `metrics`, `marker_genes`, `collect`, and the `funkyheatmap` metric ordering |
| `gene_sets.yaml` | `MARKER_GENES:` panels (per lineage, e.g. immune/epithelial/endothelial/stromal cell types) consumed by the `marker_genes` module and Moran's-I gene-set metrics in both sub-workflows |
| `gene_sets_full.yaml` | A larger, per-cell-type marker gene list (e.g. `AT0`, ...); not loaded by either `run.sh` — kept for reference/notebook use |

Both subdirectories additionally load their own `defaults.yaml` (workflow-specific overrides) on top of this shared one — see the configfile-loading order in each subdirectory's README.
