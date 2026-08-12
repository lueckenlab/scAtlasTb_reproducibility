# Scalability Analysis

Notebook for the scalability and storage benchmark, producing **Figure 1F** of the paper.

## Notebooks

| Notebook | Figures produced | Output directory |
|---|---|---|
| `Fig1F.ipynb` | Fig 1F, Supp Figs 1A, 1B | `figures/figure1/` |

## Reproducing the figure

### Prerequisites

1. Run the storage benchmark script to collect per-format file sizes:
   ```bash
   bash scripts/storage_compare.sh
   ```
   This generates the size data read by the notebook.
2. Install the required environment (see `envs/hpcell.yaml`).

### Figure 1F – Storage size comparison across formats

Run `Fig1F.ipynb`.

The notebook reads storage benchmark results (file sizes in bytes for different AnnData serialisation formats) and plots a bar chart comparing storage requirements across formats and dataset sizes.

Outputs written to `figures/figure1/`:
- `F.svg` – bar chart comparing storage size across formats (Fig 1F)
- `supp_A.svg` – supplementary storage comparison, variant A (Supp Fig 1A)
- `supp_B.svg` – supplementary storage comparison, variant B (Supp Fig 1B)
