# Notebooks

Analysis notebooks for reproducing all figures in the paper. Each subdirectory corresponds to one dataset or analysis.

## Setup

Install the environment from [lueckenlab/scAtlasTb](https://github.com/lueckenlab/scAtlasTb), then configure data paths in `configs/` before running the notebooks.

## Analyses

| Directory | Dataset / Analysis | Figures |
|---|---|---|
| [`HLCA/`](HLCA/README.md) | Human Lung Cell Atlas | 2C, 2D, 4A, 4B |
| [`HRCA/`](HRCA/README.md) | Human Retinal Cell Atlas | 3C, 3D, 3E, 3F |
| [`HARP/`](HARP/README.md) | Feature selection benchmark (B plasma) | 5A–D |
| [`Scalability/`](Scalability/README.md) | Storage & scalability benchmark | 1F |

## Figure map

| Figure | Notebook | Output |
|---|---|---|
| Fig 1F | `Scalability/Fig1F.ipynb` | `figures/figure1/F.svg` |
| Fig 2C | `HLCA/Fig2C_marker_gene_comparison.ipynb` | `figures/figure2/C/` |
| Fig 2D | `HLCA/Fig2D_lowQC_cluster.ipynb` | `figures/figure2/D/` |
| Fig 3C–E | `HRCA/Fig3CDE_benchmark_evaluation.ipynb` | `figures/figure3/` |
| Fig 3F | `HRCA/Fig3F.ipynb` | `figures/figure3/F/` |
| Fig 4A–B | `HLCA/Fig4_batch_epithelial.ipynb` | `figures/figure4/` |
| Fig 5A–D | `HARP/Fig5_B_plasma.ipynb` | `figures/figure5/` |
| Ext Fig 5A | `HARP/Fig5_B_plasma.ipynb` | `figures/figure5/Default HVG clustering markers-vs-Curated gene set.svg` |
| Ext Fig 5B | `HARP/Fig5_Feature_selection_benchmark.ipynb` | `figures/figure5/tradeoff/n_hvg_B_tradeoff.svg` |
| Supp Fig 1A–B | `Scalability/Fig1F.ipynb` | `figures/figure1/supp_A.svg`, `supp_B.svg` |
| Supp Fig 6 | `HRCA/Fig3F.ipynb` | `figures/figure3/F/Supp6_back_to_back_disagreement_scrublet.svg` |
| Supp Fig 10 | `HARP/Fig5_Feature_selection_benchmark.ipynb` | `figures/figure5/tradeoff/n_hvg_B_metrics_vs_nhvg.svg` |
