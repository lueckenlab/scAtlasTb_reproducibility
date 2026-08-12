# Notebooks

This directory contains analysis notebooks that reproduce all figures in the paper. Each subdirectory corresponds to one dataset or analysis context.

## Directory structure

| Directory | Dataset / Analysis | Figures |
|---|---|---|
| [`HLCA/`](HLCA/README.md) | Human Lung Cell Atlas (HLCA) | 2C, 2D, 4A, 4B |
| [`HRCA/`](HRCA/README.md) | Human Retinal Cell Atlas (HRCA) | 3C, 3D, 3E, 3F |
| [`HARP/`](HARP/README.md) | HARP B plasma – feature selection benchmark | 5A, 5B, 5C, 5D |
| [`Scalability/`](Scalability/README.md) | Storage & scalability benchmark | 1F |

## Shared helper modules

| File | Description |
|---|---|
| `marker_genes_functions.py` | Functions for computing and comparing marker gene sets across cell types |
| `misc.py` | Miscellaneous plotting utilities (e.g. `back_to_back_barplot`) |

## General setup

1. **Install the environment** – use the conda environment defined in `envs/hpcell.yaml`:
   ```bash
   conda env create -f envs/hpcell.yaml
   conda activate hpcell
   ```
2. **Configure data paths** – edit the YAML files under `configs/` to point to your local copies of the datasets (HLCA, HRCA, HARP) and integration outputs.
3. **Run notebooks** – open each notebook in JupyterLab or VSCode and run all cells sequentially. See the per-analysis READMEs for the recommended execution order.

## Figure map

| Figure panel | Notebook | Output file(s) |
|---|---|---|
| Fig 1F | `Scalability/Fig1F.ipynb` | `figures/figure1/F.svg` |
| Fig 2C | `HLCA/Fig2C_marker_gene_comparison.ipynb` | `figures/figure2/C/` |
| Fig 2D | `HLCA/Fig2D_lowQC_cluster.ipynb` | `figures/figure2/D/` |
| Fig 3C–E | `HRCA/Fig3CDE_benchmark_evaluation.ipynb` | `figures/figure3/tradeoff_scatter_*.svg`, `global_vs_lineage_boxplot.svg` |
| Fig 3F | `HRCA/Fig3F.ipynb` | `figures/figure3/F/` |
| Fig 4A–B | `HLCA/Fig4_batch_epithelial.ipynb` | `figures/figure4/` |
| Fig 5A–D | `HARP/Fig5_B_plasma.ipynb` | `figures/figure5/5A_*.svg`, `5B_*.svg`, `5C_*.svg`, `5D_*.svg` |
| Ext Fig 5A | `HARP/Fig5_B_plasma.ipynb` | `figures/figure5/Default HVG clustering markers-vs-Curated gene set.svg` |
| Ext Fig 5B | `HARP/Fig5_Feature_selection_benchmark.ipynb` | `figures/figure5/tradeoff/n_hvg_B_tradeoff.svg` |
| Supp Fig 1A–B | `Scalability/Fig1F.ipynb` | `figures/figure1/supp_A.svg`, `supp_B.svg` |
| Supp Fig 6 | `HRCA/Fig3F.ipynb` | `figures/figure3/F/Supp6_back_to_back_disagreement_scrublet.svg` |
| Supp Fig 10 | `HARP/Fig5_Feature_selection_benchmark.ipynb` | `figures/figure5/tradeoff/n_hvg_B_metrics_vs_nhvg.svg` |
