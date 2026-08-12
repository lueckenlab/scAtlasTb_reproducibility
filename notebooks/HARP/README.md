# HARP Analysis – Feature Selection Benchmark

Reproduces **Figure 5** using the B plasma cell lineage of the HARP dataset.

## Setup

Install the environment from [lueckenlab/scAtlasTb](https://github.com/lueckenlab/scAtlasTb) and set data paths in `configs/feature_selection/`. Notebooks are run from this directory so that `marker_genes_functions.py` and `misc.py` are importable.

## Notebooks

| Notebook | Figures | Output |
|---|---|---|
| `Fig5_B_plasma.ipynb` | 5A, 5B, 5C, 5D, Ext Fig 5A | `figures/figure5/` |
| `Fig5_Feature_selection_benchmark.ipynb` | Ext Fig 5B, Supp Fig 10 | `figures/figure5/tradeoff/` |

## Output files

**Figure 5** (`figures/figure5/`)
- `5A_default_hvg_harmonized_cellhint.svg` (Fig 5A)
- `5B_extra_hvg_leiden_1.0_1--metrics:harmony--strategy=hvg--n_hvg=3000_<group>.svg` (Fig 5B)
- `5C_marker_genes.svg` (Fig 5C)
- `5D_extra_hvg_harmonized_cellhint.svg` (Fig 5D)
- `Default HVG clustering markers-vs-Curated gene set.svg` (Ext Fig 5A)

**Ext Fig 5B / Supp Fig 10** (`figures/figure5/tradeoff/`)
- `n_hvg_B_tradeoff.svg` (Ext Fig 5B)
- `n_hvg_B_tradeoff_custom.svg`
- `n_hvg_B_metrics_vs_nhvg.svg` (Supp Fig 10)
