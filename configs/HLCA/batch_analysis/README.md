# Figure 4: HLCA Batch Analysis

Batch covariate analysis for the HLCA core dataset. The workflow quantifies each covariate's variance contribution (principal component regression) and pairwise confounding (Theil's U) across ~20 technical and biological covariates, then re-integrates the core cohort under two batch definitions — `dataset` (as used by HLCA) vs. the finer-grained `sample` — comparing the resulting embeddings with the graph-dissimilarity score. This shows that `sample`-level batching merges spatially resolved nasal/non-nasal multiciliated cell states that `dataset`-level batching keeps separate, and that a study-level covariate flagged as significant (`Processing site`) is confounded with tissue, supporting HLCA's decision not to split that study further.

## Usage

From the repository root:

```bash
bash configs/HLCA/batch_analysis/run.sh batch_analysis_all -n     # dry run
bash configs/HLCA/batch_analysis/run.sh batch_analysis_all -c 10  # execute
```

Swap `batch_analysis_all` for another module target (see the [top-level README](../../README.md#picking-a-target)) to run just one stage, e.g. `integration_all`, `clustering_all`, `metrics_all`, `sample_representation_all`.

## Configfiles loaded (in order)

| File | Purpose |
| --- | --- |
| `.profiles/czbiohub/cluster_config.yaml` | SLURM cluster resources |
| `configs/global.yaml` | OS / GPU / conda channel settings shared by all workflows |
| `configs/HLCA/gene_sets.yaml` | Marker gene panels for `marker_genes` |
| `configs/HLCA/defaults.yaml` | HLCA-wide module defaults |
| `configs/HLCA/batch_analysis/defaults.yaml` | Batch-analysis-specific defaults (preprocessing, batch_analysis, sample_representation, clustering, label_transfer, majority_voting) |
| `configs/HLCA/batch_analysis/workflow.yaml` | Main entries: `batch_analysis_all`, `batch_analysis_per_study`, `batch_correction`, `batch_correction_pseudobulk` |
| `configs/HLCA/batch_analysis/followup.yaml` | Follow-up entry: `Reintegration_new_batch_covariate` |

## `DATASETS` entries

| Name | File | Module chain | What it does |
| --- | --- | --- | --- |
| `batch_analysis_all` | workflow.yaml | `relabel → preprocessing → batch_analysis` | Runs Theil's U / PCR-based covariate-variance analysis on the full cohort (~20 covariates: study, assay, donor, tissue, sex, age, disease, ...) |
| `batch_analysis_per_study` | workflow.yaml | `split_data → preprocessing → batch_analysis` | Repeats the covariate analysis within each of 4 selected studies (edit the commented-out studies in `split_data.values` to add more) |
| `batch_correction` | workflow.yaml | `preprocessing → integration → clustering → label_transfer → marker_genes → metrics → collect → majority_voting` | Benchmarks integration methods/batch keys (harmony, scVI, scANVI at dataset vs. sample level) on the QC-passing HLCA cohort |
| `batch_correction_pseudobulk` | workflow.yaml | `sample_representation → collect` | Builds pseudobulk sample representations from each `batch_correction` embedding for downstream comparison |
| `Reintegration_new_batch_covariate` | followup.yaml | `relabel → preprocessing → integration → clustering → metrics → collect`, `preprocessing → filter → split_data → marker_genes` | Re-runs integration (harmony/scVI/scANVI) with a new/refined batch covariate and inspects per-cell-type effects of `Processing_site` |

## Output

All data lands under `data/pipeline/HLCAv1/batch_analysis/<module>/dataset~<name>/...` and plots under `data/images/HLCAv1/batch_analysis/<module>/dataset~<name>/...`, per `output_dir`/`images` in `configs/HLCA/batch_analysis/defaults.yaml`.

Outputs specifically used for the paper's figures (see `../../../notebooks/HLCA/`):

| Figure | Source output | Consuming notebook |
| --- | --- | --- |
| Fig. 4C (PC regression variance contribution) | `batch_analysis`'s `batch_pcr` output for the `batch_analysis_per_study` entry (`Banovich_Kropski_2020` split): `batch_pcr.tsv` and `batch_pcr_bar.svg`/`batch_pcr_violin.svg` under `data/{pipeline,images}/HLCAv1/batch_analysis/batch_analysis/dataset~batch_analysis_per_study/...` | — (plotted directly from the pipeline SVG/TSV) |
| Fig. 4D (Theil's U confounding heatmap) | `batch_analysis`'s `theils_u` output for the same `batch_analysis_per_study` entry: `theils_u.tsv` and `theils_u_heatmap.svg` | — (plotted directly from the pipeline SVG/TSV) |
| Fig. 4A/4B (`dataset` vs. `sample` batch, graph dissimilarity + epithelial UMAP) | Final `majority_voting` output of `batch_correction`: `data/pipeline/HLCAv1/batch_analysis/majority_voting/dataset~batch_correction/file_id~collect:batch_correction.zarr` — carries the harmony/scVI/scANVI × {dataset, sample} embeddings collected side by side | `notebooks/HLCA/batch_analysis/HLCA_global_batch_comparison.ipynb` (graph dissimilarity), `notebooks/HLCA/Fig4_batch_epithelial.ipynb` → `figures/figure4/` |

`batch_correction_pseudobulk` (pseudobulk PCA per embedding) and `Reintegration_new_batch_covariate` (the `Processing_site` follow-up) support the discussion around Fig. 4 but aren't the direct source of a numbered figure panel.
