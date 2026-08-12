# HRCA Analysis

Notebooks for the Human Retinal Cell Atlas (HRCA) analysis, producing **Figures 3C–F** of the paper.

## Notebooks

### Preprocessing (run in order)

| Notebook | Description |
|---|---|
| `00_explore_data.ipynb` | Initial exploration of the raw HRCA dataset (snRNA-seq). Inspect obs columns and cell-type distributions. |
| `01_harmonise_finest_labels.ipynb` | Harmonises finest-resolution cell-type labels across datasets for Amacrine cells (AC), Bipolar cells (BC), and Retinal Ganglion cells (RGC). Saves unified annotations. |
| `02a_explore_integrations_AC.ipynb` | Explores integration results for Amacrine cells. Visualises embeddings, computes cell-cycle effects, and investigates cluster-level metrics. |
| `02b_explore_integrations_BC.ipynb` | Analogous exploration for Bipolar cells and confirms AC results. |
| `03_export_data.ipynb` | Exports final integrated objects and prepares additional outputs (e.g. scimilarity input for RGC). Compresses and uploads data. |

### Figure notebooks

| Notebook | Figures produced | Output directory |
|---|---|---|
| `Fig3CDE_benchmark_evaluation.ipynb` | Fig 3C, 3D, 3E (tradeoff plots, boxplots) | `figures/figure3/` |
| `Fig3F.ipynb` | Fig 3F, Supp Fig 6 | `figures/figure3/F/` |

## Reproducing figures

### Prerequisites

1. Ensure the HRCA dataset and benchmark results are available. Paths are configured in `configs/HRCA/`.
2. Install the required environment (see `envs/hpcell.yaml`).
3. Run preprocessing notebooks `00` → `01` → `02a`/`02b` → `03` before running figure notebooks.

### Figures 3C, 3D, 3E – Integration benchmark evaluation

Run `Fig3CDE_benchmark_evaluation.ipynb`.

The notebook loads scib benchmark metrics across methods, HVG strategies, and resolutions, and generates:

Outputs written to `figures/figure3/`:
- `tradeoff_scatter_all_hue=lineage.svg` – Bio conservation vs. Batch correction, coloured by lineage cell count (Fig 3C)
- `tradeoff_scatter_all_hue=resolution.svg` – same tradeoff coloured by clustering resolution (Fig 3D)
- `tradeoff_scatter_all_hue=n_hvgs.svg` – same tradeoff coloured by number of HVGs
- `tradeoff_scatter_lineage_hue=resolution.svg` – per-lineage tradeoff faceted plots
- `tradeoff_scatter_lineage_hue=n_hvg.svg` – per-lineage tradeoff coloured by HVG count
- `global_vs_lineage_boxplot.svg` – boxplot comparing global vs. lineage-specific integration scores (Fig 3E)

### Figure 3F – UMAP embeddings and doublet/disagreement scores

Run `Fig3F.ipynb`.

The notebook visualises the best-performing integration embeddings and highlights cells with high label disagreement or doublet scores.

Outputs written to `figures/figure3/F/`:
- UMAP SVGs coloured by `cell_type`, `majority_consensus_disagreement`, and `scrublet_score` for each integration method and parameter set (e.g. `Fig3F_scvi--strategy=lineage--batch=sample_id--n_hvgs=3000_cell_type.svg`)
- `Supp6_back_to_back_disagreement_scrublet.svg` – back-to-back bar plot comparing label disagreement and scrublet scores per cluster (Supp Fig 6)
