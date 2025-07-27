#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../sc-atlasing-toolbox)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    configs/comp_resources.yaml  \
    configs/hlca/defaults.yaml  \
    configs/hlca/gene_sets.yaml  \
    configs/hlca/load_data.yaml \
    configs/hlca/qc.yaml \
    configs/hlca/integration.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
