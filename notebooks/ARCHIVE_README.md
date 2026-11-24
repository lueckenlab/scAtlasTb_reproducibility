# Archived notebooks (not used for the paper)

This branch keeps exploratory, prototype and export notebooks that are not needed to reproduce any figure of the scAtlasTb manuscript. It is kept for reference only. `main` holds the paper analyses.

| Path | What it is |
|---|---|
| `notebooks/hlca_integrations.ipynb` | Old version of the HLCA batch analysis (superseded by `notebooks/HLCA/batch_analysis/HLCA_global_batch_comparison.ipynb` + `Fig4_batch_epithelial.ipynb`) |
| `notebooks/graph_similarity.py` | Helper imported by `hlca_integrations.ipynb` (copy of `immune-v1-scripts/notebooks/integrations/graph_similarity/graph_similarity.py`; now part of scAtlasTb-utils) |
| `notebooks/misc_bkp.py` | Backup of an older `misc.py` |
| `notebooks/QC/HLCA_QC_overview.ipynb` | Prototype QC ridge plots / removed-cell heatmaps, now produced by the scAtlasTb `qc` module (`plot_summary.py`) |
| `notebooks/QC/HLCA_extended_comparison.ipynb` | Exploration that became `Fig2C_marker_gene_comparison.ipynb` and `Fig2D_lowQC_cluster.ipynb` (plus unused entropy analysis) |
| `notebooks/QC/HLCA_core.ipynb`, `HLCA_epithelial.ipynb` | Graph dissimilarity exploration on HLCA core (not in the paper) |
| `notebooks/QC/HLCA_export.ipynb`, `HLCA_core_export.ipynb`, `HLCA_export_AT2_qc.ipynb` | Data exports for sharing |
| `notebooks/QC/PBMC_QC.ipynb` | PBMC raw data preparation for QC (not in the paper) |
| `notebooks/HARP/HICA_B_plasma.ipynb` | Draft of `Fig5_B_plasma.ipynb` |
| `notebooks/HARP/HICA_DCs.ipynb`, `export_HICA.ipynb`, `export_HICA_remapped.ipynb` | HARP data exports for collaborators |
| `notebooks/HLCA/batch_analysis/export_sample_representation.ipynb` | Pseudobulk export of `batch_correction_pseudobulk` |
| `notebooks/HLCA/batch_analysis/Followup_new_batch_split.ipynb` | `Processing_site` follow-up (discussion of Fig. 4, no figure panel) |
