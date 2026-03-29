#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml \
    configs/HLCA/gene_sets.yaml \
    configs/HLCA/QC/global.yaml \
    configs/HLCA/QC/core.yaml \
    configs/HLCA/QC/extended.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
