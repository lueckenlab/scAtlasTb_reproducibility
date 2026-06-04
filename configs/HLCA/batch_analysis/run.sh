#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml  \
    configs/HLCA/gene_sets.yaml \
    configs/HLCA/defaults.yaml  \
    configs/HLCA/batch_analysis/defaults.yaml  \
    configs/HLCA/batch_analysis/workflow.yaml  \
    configs/HLCA/batch_analysis/followup.yaml  \
  --snakefile $pipeline/workflow/Snakefile \
    $@
