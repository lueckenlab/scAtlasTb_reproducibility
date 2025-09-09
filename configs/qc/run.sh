#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml  \
    configs/qc/global.yaml  \
    configs/qc/hlca.yaml  \
  --snakefile $pipeline/workflow/Snakefile \
    $@
