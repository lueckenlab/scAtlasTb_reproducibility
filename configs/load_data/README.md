# Data loading

Downloads the source datasets listed in [`datasets.tsv`](datasets.tsv) (mostly from CELLxGENE) and harmonizes their metadata against [`schema_mapping_tier1.tsv`](schema_mapping_tier1.tsv), merging per organ.

## Usage

From the repository root:

```bash
bash configs/load_data/run.sh load_data_all -n     # dry run
bash configs/load_data/run.sh load_data_all -c 10  # execute
```

Unlike the other workflows, this config has no `DATASETS:` block — instead `load_data_all` builds one merged output per `organ` value found in `datasets.tsv`, using `PREPARE_DATA`-style logic from the `load_data` snakemake module rather than the generic `input:` chaining described in the [top-level README](../README.md).

## Configfiles loaded

| File | Purpose |
| --- | --- |
| `.profiles/czbiohub/cluster_config.yaml` | SLURM cluster resources |
| `configs/global.yaml` | OS / GPU / conda channel settings shared by all workflows |
| `configs/load_data/config.yaml` | Points to `dataset_meta` and `schema_file` below, sets `output_dir`/`images` |

## Inputs

- [`datasets.tsv`](datasets.tsv) — one row per source dataset: study, organ, CELLxGENE collection/dataset IDs, annotation columns to keep, etc. Adding a row here adds a dataset to `load_data_all`.
- [`schema_mapping_tier1.tsv`](schema_mapping_tier1.tsv) — maps each dataset's native metadata columns onto the shared tier-1 schema used downstream (e.g. `donor_id`, `organism_ontology_term_id`).

## Output

`data/pipeline/load_data/...zarr`, merged per organ (see `output_dir` in `configs/load_data/config.yaml`).
