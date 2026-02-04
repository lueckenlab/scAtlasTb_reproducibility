#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    .profiles/czbiohub/cluster_config.yaml \
    configs/global.yaml \
    configs/HLCA_gene_sets.yaml \
    configs/qc/global.yaml \
    configs/qc/workflow.yaml \
    configs/qc/followup_qc.yaml \
    configs/qc/extended.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
