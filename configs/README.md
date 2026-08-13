# Pipeline configs

This directory holds Snakemake configfiles for the [scAtlasTb](https://github.com/lueckenlab/scAtlasTb) pipeline, one subdirectory per atlas or analysis. Each workflow directory ships a `run.sh` wrapper that calls `snakemake` with a fixed set of `--configfile`s plus the SLURM cluster profile, and forwards any extra CLI arguments straight through to `snakemake`.

## Usage

Run wrapper scripts from the repository root (`scAtlasTb_reproducibility/`), **not** from inside the config directory — they resolve `../scAtlasTb` and all configfile paths relative to the current working directory:

```bash
bash configs/<workflow>/run.sh <target> [snakemake-flags]
```

For example:

```bash
bash configs/HLCA/batch_analysis/run.sh batch_analysis_all -n      # dry run
bash configs/HLCA/batch_analysis/run.sh batch_analysis_all -c 10   # execute with 10 cores
bash configs/HLCA/QC/run.sh qc_all -q                               # quiet output
bash configs/HLCA/QC/run.sh preprocessing_all qc_all -nq            # multiple targets at once
```

### Picking a target

Every pipeline module (`qc`, `preprocessing`, `integration`, `metrics`, ...) contributes a `<module>_all` rule that builds that module's output for every dataset in the loaded configfiles which uses it. Which datasets that is comes from each config's `DATASETS.<name>.input` block (see below).

**Calling `run.sh` with no target (or `all`) does not run any computation.** The bare `all` rule [only renders rule-graph/DAG PNGs](https://scatlastb.readthedocs.io/en/latest/getting_started/call_pipeline.html#first-dry-run), so you should always pass an explicit `<module>_all` target (or a concrete output file path) to actually execute the pipeline.

Module → target reference:

| module | target |
| --- | --- |
| load_data | `load_data_all` |
| relabel | `relabel_all` |
| filter | `filter_all` |
| doublets | `doublets_all` |
| qc | `qc_all` |
| merge | `merge_all` |
| split_data | `split_data_all` |
| subset | `subset_all` |
| preprocessing | `preprocessing_all` |
| batch_analysis | `batch_analysis_all` |
| sample_representation | `sample_representation_all` |
| integration | `integration_all` |
| clustering | `clustering_all` |
| celltype_prediction | `celltype_prediction_all` |
| label_harmonization | `label_harmonization_all` |
| reference_mapping | `reference_mapping_all` |
| label_transfer | `label_transfer_all` |
| majority_voting | `majority_voting_all` |
| metrics | `metrics_all` |
| marker_genes | `marker_genes_all` |
| collect | `collect_all` |
| uncollect | `uncollect_all` |
| exploration | `exploration_all` |

You can pass several targets in one call ([see documentation](https://scatlastb.readthedocs.io/en/latest/getting_started/call_pipeline.html)), and you can target a specific output file path instead of a `_all` rule for a narrower re-run.

### Config structure

Each workflow's configfiles typically set:
- `output_dir` / `images` — where pipeline outputs / plots land (usually `data/pipeline/<atlas>/...`, `data/images/<atlas>/...`)
- `defaults:` — module parameters shared across all `DATASETS` entries in that workflow (e.g. integration methods, clustering resolutions, QC thresholds)
- `DATASETS:` — one entry per named workflow instance. Each entry's `input:` block chains pipeline modules together, e.g.:

  ```yaml
  DATASETS:
    my_dataset:
      input:
        relabel: <path to an upstream .zarr>
        preprocessing: relabel   # preprocessing consumes relabel's output
        integration: preprocessing
  ```

  The dataset name (`my_dataset`) becomes the `dataset~` wildcard in output paths, and a module's `_all` target aggregates every `DATASETS` entry that references it — not just one.
- `MARKER_GENES:` — gene panels consumed by the `marker_genes` module (e.g. `configs/HLCA/gene_sets.yaml`, `configs/HICA_gene_sets.yaml`).

## Workflows

| Directory | Atlas / analysis |
| --- | --- |
| [`load_data/`](load_data/README.md) | Download & harmonize input datasets from CELLxGENE |
| [`HLCA/`](HLCA/README.md) | HLCA: [`QC/`](HLCA/QC/README.md) (Fig. 2) and [`batch_analysis/`](HLCA/batch_analysis/README.md) (Fig. 4) |
| [`HRCA/`](HRCA/README.md) | HRCA integration, per-lineage benchmarking and marker genes |
| [`HARP/`](HARP/README.md) | HARP HVG-selection benchmark, per-lineage and global (port of `harp_figures/figure2/C`) |

Note, that the `feature_selection` workflows are deprecated and should be ignored. Feature-selection benchmarking is now part of the HARP workflow above.