# Figure 2: HLCA QC Analysis

Evaluating different QC decisions for the Human Lung Cell Atlas (HLCA) core (49 datasets) and its disease-mapped extension cohort. The workflow runs `scAutoQC`-based thresholding per study and lineage (immune, epithelial, endothelial, stroma) to build a more stringently filtered "HighQC" reference, re-integrates it with scANVI, and reference-maps the extension datasets onto both the original HLCA and HighQC embeddings.

## Usage

From the repository root:

```bash
bash configs/HLCA/QC/run.sh qc_all -n     # dry run
bash configs/HLCA/QC/run.sh qc_all -c 10  # execute
```

Swap `qc_all` for another module target (see the [top-level README](../../README.md#picking-a-target)) to run just one stage, e.g. `doublets_all`, `preprocessing_all`, `integration_all`, `clustering_all`, `metrics_all`.

## Configfiles loaded (in order)

| File | Purpose |
| --- | --- |
| `.profiles/czbiohub/cluster_config.yaml` | SLURM cluster resources |
| `configs/global.yaml` | OS / GPU / conda channel settings shared by all workflows |
| `configs/HLCA/gene_sets.yaml` | Marker gene panels for `marker_genes` |
| `configs/HLCA/defaults.yaml` | HLCA-wide module defaults (relabel, merge, split_data, preprocessing, ...) |
| `configs/HLCA/QC/defaults.yaml` | QC-specific defaults (`doublets`: scrublet + doubletdetection) |
| `configs/HLCA/QC/core.yaml` | Core cohort: `prepare_data`, `QC`, `highQC`, `Benchmark_highQC` |
| `configs/HLCA/QC/extended.yaml` | Extended cohort: `QC_extended`, `HLCAv1_extended` |
| `configs/HLCA/QC/followup_qc.yaml` | Follow-up analysis on a QC subset: `follow_up_immune` |

## `DATASETS` entries

| Name | File | Module chain | What it does |
| --- | --- | --- | --- |
| `prepare_data` | core.yaml | `relabel → preprocessing`, `relabel → split_data` | Relabels the raw core cohort and splits it per study |
| `QC` | core.yaml | `doublets → split_data`, `split_data → qc → merge` | Runs doublet detection and QC thresholding per study, merges back |
| `highQC` | core.yaml | `split_data → preprocessing → integration → reference_mapping → merge → relabel → clustering → label_transfer → marker_genes` | Builds the high-QC reference: integrates the passing cells and annotates clusters |
| `Benchmark_highQC` | core.yaml | `clustering → metrics` | Benchmarks clustering/integration quality on the high-QC subset |
| `QC_extended` | extended.yaml | `relabel → filter → split_data → doublets → qc → merge → preprocessing` | Same QC procedure applied to the HLCA extended cohort |
| `HLCAv1_extended` | extended.yaml | `reference_mapping → merge → preprocessing → integration → clustering → metrics → label_transfer → collect → majority_voting → marker_genes` | Maps the extended cohort onto the HLCA reference and re-annotates it |
| `follow_up_immune` | followup_qc.yaml | `filter → relabel → qc`, `relabel → marker_genes` | Zooms into one study's immune compartment to inspect a low-QC cluster found in `highQC` |

Uncomment the `follow_up_AT2` block at the bottom of `followup_qc.yaml` for the analogous AT2-compartment follow-up (kept as a template, not run by default).

## Output

All data lands under `data/pipeline/HLCAv1/QC/<module>/dataset~<name>/...` and plots under `data/images/HLCAv1/QC/<module>/dataset~<name>/...`, per `output_dir`/`images` in `configs/HLCA/QC/defaults.yaml`.

Outputs specifically used for the paper's figures (see `../../../notebooks/HLCA/` for the downstream figure notebooks):

| Figure | Source output | Consuming notebook |
| --- | --- | --- |
| Fig. 2A (per-study/lineage QC thresholds) | `qc` module's `thresholds.tsv` / `qc_stats.tsv` and joint/summary plots under `data/images/HLCAv1/QC/qc/dataset~{QC,QC_extended}/...` | — |
| Fig. 2C (marker gene overlap, HighQC vs. HLCA), Fig. 2D + Extended Fig. 2 (low-QC cluster, graph dissimilarity) | `marker_genes` output of `HLCAv1_extended`: `data/pipeline/HLCAv1/QC/marker_genes/dataset~HLCAv1_extended/file_id~majority_voting:collect:HLCAv1_extended.zarr` — this single AnnData carries both the HLCA- and HighQC-mapped embeddings/annotations for the extension cohort | `notebooks/HLCA/Fig2C_marker_gene_comparison.ipynb` → `figures/figure2/C/`, `notebooks/HLCA/Fig2D_lowQC_cluster.ipynb` → `figures/figure2/D/` |

The `highQC` and `QC` entries' intermediate `integration`/`reference_mapping`/`merge` outputs (the de novo scANVI reference and the query-mapped low-QC cells) are the upstream inputs that `HLCAv1_extended` (in `extended.yaml`) re-maps and re-annotates into the single file above; they aren't consumed directly by a figure notebook.
