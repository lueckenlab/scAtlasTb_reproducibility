# HARP Analysis – Feature Selection Benchmark

Notebooks for the feature selection benchmark analysis, producing **Figure 5** of the paper.

The analysis uses the B plasma cell lineage from the Human Atlas of the RNA Pelage (HARP) dataset to evaluate different HVG selection strategies and their effect on integration quality.

## Notebooks

| Notebook | Figures produced | Output directory |
|---|---|---|
| `Fig5_B_plasma.ipynb` | Fig 5A, 5B, 5C, 5D, Ext Fig 5A | `figures/figure5/` |
| `Fig5_Feature_selection_benchmark.ipynb` | Ext Fig 5B, Supp Fig 10 | `figures/figure5/tradeoff/` |

## Reproducing figures

### Prerequisites

1. Ensure the HARP dataset and integration outputs are available. Paths are configured in `configs/feature_selection/`.
2. Install the required environment (see `envs/hpcell.yaml`).
3. The `scatlastb_utils` package must be installed.
4. `marker_genes_functions.py` and `misc.py` (from `notebooks/`) must be on the Python path (notebooks are run from the `notebooks/HARP/` directory).

### Figure 5A, 5B, 5C, 5D – Feature selection in B plasma cells

Run `Fig5_B_plasma.ipynb`.

The notebook loads the integrated B plasma cell object, visualises UMAP embeddings under different HVG strategies, computes cluster marker genes, and compares them against a curated gene set.

Outputs written to `figures/figure5/`:
- `5A_default_hvg_harmonized_cellhint.svg` – UMAP coloured by CellHint harmonised labels using default HVG strategy (Fig 5A)
- `5B_extra_hvg_leiden_1.0_1--metrics:harmony--strategy=hvg--n_hvg=3000_<group>.svg` – UMAPs highlighting individual Leiden clusters under the default HVG strategy (Fig 5B)
- `5C_marker_genes.svg` – dot plot of top marker genes per cluster (Fig 5C)
- `5D_extra_hvg_harmonized_cellhint.svg` – UMAP coloured by CellHint labels using the extra-HVG strategy (Fig 5D)
- `Default HVG clustering markers-vs-Curated gene set.svg` – overlap heatmap comparing cluster markers vs. curated gene set (Ext Fig 5A)

### Ext Fig 5B, Supp Fig 10 – Benchmark tradeoff analysis

Run `Fig5_Feature_selection_benchmark.ipynb`.

The notebook aggregates scib benchmark scores across HVG strategies and number of HVGs, then plots the bio conservation vs. batch correction tradeoff.

Outputs written to `figures/figure5/tradeoff/`:
- `n_hvg_B_tradeoff.svg` – tradeoff scatter for all strategies and HVG counts (Ext Fig 5B)
- `n_hvg_B_tradeoff_custom.svg` – highlighted tradeoff for the extra-HVG strategy at 3 000 HVGs
- `n_hvg_B_metrics_vs_nhvg.svg` – metric scores vs. number of HVGs per strategy (Supp Fig 10)

## Helper modules

- `marker_genes_functions.py` – shared utilities for computing and comparing marker gene sets (symlinked/copied from `notebooks/`)
- `misc.py` – miscellaneous plotting helpers including `back_to_back_barplot`
