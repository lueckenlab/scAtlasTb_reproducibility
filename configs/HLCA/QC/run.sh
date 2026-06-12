#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml \
    configs/HLCA/gene_sets.yaml \
    configs/HLCA/defaults.yaml \
    configs/HLCA/QC/defaults.yaml \
    configs/HLCA/QC/core.yaml \
    configs/HLCA/QC/extended.yaml \
    configs/HLCA/QC/followup_qc.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
