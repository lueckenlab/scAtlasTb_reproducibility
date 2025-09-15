#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml  \
    configs/feature_selection/global.yaml  \
    configs/feature_selection/gene_sets.yaml  \
    configs/feature_selection/luca.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
