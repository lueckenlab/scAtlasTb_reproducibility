#!/usr/bin/env bash
set -e -x

pipeline="$(realpath ../scAtlasTb)"

snakemake \
  --profile .profiles/czbiohub \
  --configfile \
    configs/comp_resources.yaml  \
    configs/load_data/datasets.yaml  \
  --snakefile $pipeline/workflow/Snakefile \
    $@
