#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml  \
    configs/load_data/config.yaml  \
  --snakefile $pipeline/workflow/Snakefile \
    $@
