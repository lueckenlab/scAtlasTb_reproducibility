# HLCA Analysis

Reproduces **Figures 2C, 2D, and 4** using the Human Lung Cell Atlas (HLCA).

## Setup

Install the `scanpy` environment from [lueckenlab/scAtlasTb](https://github.com/lueckenlab/scAtlasTb) (`envs/scanpy.yaml`) and set data paths in `configs/HLCA/`.

## Notebooks

Run preprocessing notebooks before figure notebooks.

| Notebook | Figures | Output |
|---|---|---|
| `HLCA_prepare_metadata.ipynb` | – | metadata files |
| `HLCA_wrangle_marker_genes.ipynb` | – | marker gene tables |
| `Fig2C_marker_gene_comparison.ipynb` | 2C, Ext Fig 2B | `figures/figure2/C/` |
| `Fig2D_lowQC_cluster.ipynb` | 2D | `figures/figure2/D/` |
| `Fig4_batch_epithelial.ipynb` | 4A, 4B | `figures/figure4/` |

## Output files

**Figure 2C** (`figures/figure2/C/`)
- `High QC-vs-HLCAv1.svg`, `HLCAv1-vs-HLCAv1.svg`, `High QC-vs-High QC.svg` – marker gene overlap heatmaps
- Per-lineage overlap plots under `Endothelial/`, `Epithelial/`, `Immune/`, `Stroma/`
- `Ext2_B_curated_markers.svg`
- `supp_table_markers.tsv`

**Figure 2D** (`figures/figure2/D/`)
- `umaps/` – UMAP embeddings per integration
- `graph_dissimilarity/` – graph dissimilarity overlays

**Figure 4** (`figures/figure4/`)
- `4A_graph_dissim.svg`
- `4B_scanvi_dataset_ann_finest_level.svg`, `4B_scanvi_sample_ann_finest_level.svg`, `4B_scanvi_dataset_ann_level_5.svg`, `4B_scanvi_sample_ann_level_5.svg`
- `Fig4B_scanvi_dataset--avg_distance_diff.svg`, `Fig4B_scanvi_sample--avg_distance_diff.svg`
