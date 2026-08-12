# HLCA Analysis

Notebooks for the Human Lung Cell Atlas (HLCA) analysis, producing **Figures 2C, 2D, and 4** of the paper.

## Notebooks

### Preprocessing (run first)

| Notebook | Description |
|---|---|
| `HLCA_prepare_metadata.ipynb` | Transfers cell type annotations between filtered and unfiltered AnnData objects. Run this before the figure notebooks. |
| `HLCA_wrangle_marker_genes.ipynb` | Computes and formats marker genes for HLCA cell types. Outputs are consumed by `Fig2C_marker_gene_comparison.ipynb`. |

### Figure notebooks

| Notebook | Figures produced | Output directory |
|---|---|---|
| `Fig2C_marker_gene_comparison.ipynb` | Fig 2C, Ext Fig 2B | `figures/figure2/C/` |
| `Fig2D_lowQC_cluster.ipynb` | Fig 2D, Supp UMAPs, graph dissimilarity plots | `figures/figure2/D/` |
| `Fig4_batch_epithelial.ipynb` | Fig 4A, Fig 4B | `figures/figure4/` |

## Reproducing figures

### Prerequisites

1. Ensure the HLCA dataset is available and paths are set in the config files under `configs/HLCA/`.
2. Install the required environment (see `envs/hpcell.yaml`).
3. Run the preprocessing notebooks in order before the figure notebooks.

### Figure 2C – Marker gene comparison

Run `HLCA_wrangle_marker_genes.ipynb` then `Fig2C_marker_gene_comparison.ipynb`.

The notebook compares marker genes between:
- High-QC filtered cells
- HLCA v1 reference annotations

Outputs written to `figures/figure2/C/`:
- Heatmaps of marker gene overlap per cell type
- Per-lineage marker overlap plots (one per `ann_level_1` category)
- `supp_table_markers.tsv` – supplementary table of marker gene overlaps
- `Ext2_B_curated_markers.svg` – extended figure with curated gene sets

### Figure 2D – Low-QC cluster UMAPs and graph dissimilarity

Run `Fig2D_lowQC_cluster.ipynb`.

The notebook embeds cells with multiple integration methods and computes graph dissimilarity between integration pairs.

Outputs written to `figures/figure2/D/`:
- `umaps/` – UMAP embeddings coloured by annotation and QC metrics for each integration
- `graph_dissimilarity/` – graph dissimilarity UMAP overlays comparing integration pairs
- Bar plots of clusters with highest graph dissimilarity

### Figure 4 – Batch effect analysis in epithelial cells

Run `Fig4_batch_epithelial.ipynb`.

The notebook compares sample-level vs. dataset-level batch correction in epithelial cells using graph dissimilarity metrics.

Outputs written to `figures/figure4/`:
- `4A_graph_dissim.svg` – graph dissimilarity per cell type (sample vs. dataset batch)
- `4B_scanvi_dataset_ann_finest_level.svg`, `4B_scanvi_sample_ann_finest_level.svg`, etc. – UMAP embeddings coloured by finest annotation level
- `Fig4B_scanvi_dataset--avg_distance_diff.svg`, `Fig4B_scanvi_sample--avg_distance_diff.svg` – average distance difference overlaid on UMAP

## Helper modules

- `batch_analysis_utils.py` – utility functions for graph dissimilarity computation and plotting
- `marker_genes_functions.py` – functions for computing and comparing marker gene sets (also used by `Fig2C_marker_gene_comparison.ipynb`)
