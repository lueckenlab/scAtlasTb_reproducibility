#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml  \
    configs/HICA_gene_sets.yaml  \
    configs/feature_selection/HICA/defaults.yaml  \
    configs/feature_selection/HICA/workflow.yaml \
    configs/feature_selection/HICA/DC_integration.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
