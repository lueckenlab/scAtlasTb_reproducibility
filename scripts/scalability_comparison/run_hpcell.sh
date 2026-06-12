singularity exec \
  --no-home \
  --bind $(realpath ./data):/data \
  --bind $(realpath ./scripts/scalability_comparison):/scripts \
  hpcell.sif Rscript scripts/hpcell.R