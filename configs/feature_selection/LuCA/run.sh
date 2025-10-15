#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml  \
    configs/HLCA_gene_sets.yaml  \
    configs/feature_selection/LuCA/workflow.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
