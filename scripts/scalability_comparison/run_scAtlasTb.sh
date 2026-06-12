#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    scripts/scalability_comparison/scAtlasTb.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
