# scAtlasTb Paper - Reproducibility Code

Reproducibility code for **"Building optimized single-cell reference atlases with scAtlasTb"** (Mueller et al.). This repo contains the [Snakemake](https://snakemake.readthedocs.io/) pipeline configfiles and the Jupyter notebooks used to generate every data-driven figure panel in the paper, across the three case-study atlases (HLCA, HRCA, HARP) and the scalability benchmark.

The pipeline itself (the modules `run.sh` calls into) lives in the separate [lueckenlab/scAtlasTb](https://github.com/lueckenlab/scAtlasTb) repo, with shared scalable helper functions (Moran's I, graph dissimilarity, majority-voting) in [lueckenlab/scAtlasTb-py](https://github.com/lueckenlab/scAtlasTb-py). This repo only holds the *configuration* and *analysis* layer on top of those — it has no pipeline code of its own.

## Code overview

| Directory | Contents |
| --- | --- |
| [`configs/`](configs/README.md) | Snakemake configfiles, one subdirectory per atlas/analysis. Running these against the `scAtlasTb` pipeline reproduces every intermediate object (QC'd/integrated/benchmarked AnnData, metrics tables) that the figures are built from. **Start here for "how was the data processed."** |
| [`notebooks/`](notebooks/README.md) | Jupyter notebooks that load the pipeline's output objects and render the actual manuscript panels into `figures/`. **Start here for "how was this panel plotted."** |
| `figures/` | Rendered SVG panels, one subdirectory per main figure (`figure1/` … `figure5/`), written by the notebooks above. |
| `scripts/` | Standalone helper scripts outside the Snakemake pipeline: `storage_compare.sh` (feeds Fig. 1F / Supp. Fig. 1) and `scalability_comparison/` (drivers for the scib-pipeline and HPCell baselines scAtlasTb is compared against for scalability). |
| `.profiles/` | Snakemake cluster-execution profiles (SLURM/`czbiohub`, LSF, local) passed to `run.sh` wrappers. |
| `envs/` | Extra conda environment(s) needed only for the R-based HPCell scalability baseline (`hpcell.yaml`, used with `hpcell.sif`). The main pipeline environment (`scanpy.yaml`) lives in the `scAtlasTb` repo, not here. |
| `data/` | Pipeline inputs/outputs (`input/`, `pipeline/`, `output/`, `images/`). Gitignored — not shipped in this repo; regenerate by running the configs, or point at your own copies (see dataset URLs in the manuscript's Code and data availability section). |

## Setup

1. Clone [`scAtlasTb`](https://github.com/lueckenlab/scAtlasTb) alongside this repo (configs reference it as `../scAtlasTb`) and install its `envs/scanpy.yaml` conda environment — this provides both the pipeline modules and the packages the notebooks import.
2. Pick a Snakemake execution profile under `.profiles/` (or add your own) and adjust cluster resources in `configs/<workflow>/*.yaml` / the profile's `cluster_config.yaml` if you're not on the original SLURM cluster.
3. Set/verify data paths in the relevant `configs/<atlas>/` files (input datasets, `output_dir`, `images`) before running anything — see [`configs/README.md`](configs/README.md) for the general config structure and [`configs/load_data/`](configs/load_data/README.md) for downloading the source CELLxGENE datasets.

## Reproducing a figure

Each figure is reproduced in two steps:

1. **Run the Snakemake pipeline config** for that atlas/analysis to (re)generate the underlying AnnData objects and metrics tables:
   ```bash
   bash configs/<atlas>/<workflow>/run.sh <module>_all -n     # dry run first
   bash configs/<atlas>/<workflow>/run.sh <module>_all -c 10  # execute with 10 cores
   ```
   See [`configs/README.md#picking-a-target`](configs/README.md#picking-a-target) for the full module → target table, and each workflow's own README (linked below) for which `DATASETS` entries to run and in what order.
2. **Run the matching notebook** under `notebooks/<atlas>/`, which reads the pipeline's output `.zarr` objects and writes the manuscript panel(s) as SVGs into `figures/<figureN>/`.

## Figure → code map

This is the fastest way to find the code behind a specific panel. Panels not listed here (e.g. Fig. 1A/B–E schematics, Fig. 2B, Fig. 3A/B schematics/example UMAPs, Extended Fig. 1) are conceptual diagrams or illustrative pipeline output not tied to a dedicated figure-generating notebook.

| Figure | Analysis | Pipeline config | Notebook | Output |
| --- | --- | --- | --- | --- |
| Fig. 1F, Supp. Fig. 1A–B | Storage/scalability benchmark | `scripts/storage_compare.sh` (no Snakemake config) | [`notebooks/Scalability/Fig1F.ipynb`](notebooks/Scalability/README.md) | `figures/figure1/` |
| Fig. 2A | HLCA QC thresholds per study/lineage | [`configs/HLCA/QC/`](configs/HLCA/QC/README.md) | [`notebooks/QC/HLCA_QC_overview.ipynb`](notebooks/QC) | — |
| Fig. 2C, 2D, Extended Fig. 2 | HLCA HighQC vs. original atlas comparison | [`configs/HLCA/QC/`](configs/HLCA/QC/README.md) | [`notebooks/HLCA/Fig2C_marker_gene_comparison.ipynb`](notebooks/HLCA/README.md), [`Fig2D_lowQC_cluster.ipynb`](notebooks/HLCA/README.md) | `figures/figure2/` |
| Fig. 3C–E, Extended Fig. 3 | HRCA integration benchmark (trade-offs, funkyheatmap) | [`configs/HRCA/`](configs/HRCA/README.md) | [`notebooks/HRCA/Fig3CDE_benchmark_evaluation.ipynb`](notebooks/HRCA/README.md) | `figures/figure3/` |
| Fig. 3F, Supp. Fig. 6 | HRCA majority-voting disagreement / doublets (AC lineage) | [`configs/HRCA/`](configs/HRCA/README.md) | [`notebooks/HRCA/Fig3F.ipynb`](notebooks/HRCA/README.md) | `figures/figure3/F/` |
| Fig. 4A, 4B | HLCA `dataset` vs. `sample` batch definition | [`configs/HLCA/batch_analysis/`](configs/HLCA/batch_analysis/README.md) | [`notebooks/HLCA/Fig4_batch_epithelial.ipynb`](notebooks/HLCA/README.md) | `figures/figure4/` |
| Fig. 4C, 4D | HLCA PC regression / Theil's U confounder analysis | [`configs/HLCA/batch_analysis/`](configs/HLCA/batch_analysis/README.md) | — (plotted directly from pipeline SVG/TSV output) | `data/images/HLCAv1/batch_analysis/...` |
| Fig. 5, Extended Fig. 4, Supp. Fig. 10 | HARP feature-selection benchmark (B/Plasma lineage) | [`configs/HARP/`](configs/HARP/README.md) | [`notebooks/HARP/Fig5_B_plasma.ipynb`](notebooks/HARP/README.md), [`Fig5_Feature_selection_benchmark.ipynb`](notebooks/HARP/README.md) | `figures/figure5/` |
