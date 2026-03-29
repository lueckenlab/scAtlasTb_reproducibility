#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml \
    configs/HLCA/gene_sets.yaml \
    configs/HLCA/global.yaml \
    configs/HLCA/core.yaml \
    configs/HLCA/extended.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
