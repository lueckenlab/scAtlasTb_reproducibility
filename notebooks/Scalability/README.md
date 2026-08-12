# Scalability Analysis

Reproduces **Figure 1F** from the storage and scalability benchmark.

## Setup

Install the environment from [lueckenlab/scAtlasTb](https://github.com/lueckenlab/scAtlasTb). Before running the notebook, collect per-format file sizes with:

```bash
bash scripts/storage_compare.sh
```

## Notebooks

| Notebook | Figures | Output |
|---|---|---|
| `Fig1F.ipynb` | 1F, Supp Figs 1A–B | `figures/figure1/` |

## Output files

**Figure 1F** (`figures/figure1/`)
- `F.svg` (Fig 1F)
- `supp_A.svg` (Supp Fig 1A)
- `supp_B.svg` (Supp Fig 1B)
