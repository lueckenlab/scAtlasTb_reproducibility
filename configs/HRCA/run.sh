#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    configs/global.yaml  \
    configs/HRCA/defaults.yaml  \
    configs/HRCA/marker_genes.yaml  \
    configs/HRCA/integration.yaml \
  --snakefile $pipeline/workflow/Snakefile \
    $@
