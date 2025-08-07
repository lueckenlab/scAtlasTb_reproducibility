#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml  \
    configs/hlca/defaults.yaml  \
    configs/hlca/gene_sets.yaml  \
    configs/hlca/load_data.yaml \
    configs/hlca/qc.yaml \
    configs/hlca/integration.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
