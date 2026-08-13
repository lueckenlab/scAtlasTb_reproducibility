#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml  \
    configs/HARP/gene_sets/gene_sets.yaml \
    configs/HARP/defaults.yaml \
    configs/HARP/prepare_data.yaml \
    configs/HARP/feature_selection.yaml \
    configs/HARP/config.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
