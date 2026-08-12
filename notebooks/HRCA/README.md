# HRCA Analysis

Reproduces **Figures 3C–F** using the Human Retinal Cell Atlas (HRCA).

## Setup

Install the environment from [lueckenlab/scAtlasTb](https://github.com/lueckenlab/scAtlasTb) and set data paths in `configs/HRCA/`.

## Notebooks

Run preprocessing notebooks before figure notebooks.

| Notebook | Figures | Output |
|---|---|---|
| `00_explore_data.ipynb` | – | – |
| `01_harmonise_finest_labels.ipynb` | – | harmonised annotation files |
| `02a_explore_integrations_AC.ipynb` | – | – |
| `02b_explore_integrations_BC.ipynb` | – | – |
| `03_export_data.ipynb` | – | exported integrated objects |
| `Fig3CDE_benchmark_evaluation.ipynb` | 3C, 3D, 3E | `figures/figure3/` |
| `Fig3F.ipynb` | 3F, Supp Fig 6 | `figures/figure3/F/` |

## Output files

**Figures 3C–E** (`figures/figure3/`)
- `tradeoff_scatter_all_hue=lineage.svg` (Fig 3C)
- `tradeoff_scatter_all_hue=resolution.svg` (Fig 3D)
- `tradeoff_scatter_all_hue=n_hvgs.svg`
- `tradeoff_scatter_lineage_hue=resolution.svg`
- `tradeoff_scatter_lineage_hue=n_hvg.svg`
- `global_vs_lineage_boxplot.svg` (Fig 3E)

**Figure 3F** (`figures/figure3/F/`)
- `Fig3F_<method>--strategy=<strategy>--batch=sample_id--n_hvgs=<n>_cell_type.svg`
- `Fig3F_<method>--strategy=<strategy>--batch=sample_id--n_hvgs=<n>_majority_consensus_disagreement.svg`
- `Fig3F_<method>--strategy=<strategy>--batch=sample_id--n_hvgs=<n>_scrublet_score.svg`
- `Supp6_back_to_back_disagreement_scrublet.svg` (Supp Fig 6)
