snakemake --configfile scripts/scalability_comparison/scib-pipeline.yaml \
    --snakefile ../scib-pipeline/Snakefile \
    --use-conda \
    $@