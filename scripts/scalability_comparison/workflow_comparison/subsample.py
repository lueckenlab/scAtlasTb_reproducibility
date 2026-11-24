"""
Create the shared inputs for both arms of the workflow comparison.

Moves raw counts (raw/X) into X, drops everything the workflow doesn't need and
writes one .h5ad per subsample size. This step is not timed.

Usage (scanpy env):
    python subsample.py <input.h5ad> <out_dir> 50000 100000 250000 full
"""
import sys
from pathlib import Path

import anndata as ad
import numpy as np

KEEP_OBS = ['dataset', 'ann_finest_level', 'study', 'donor_id', 'sample']
SEED = 0

input_file, out_dir, *sizes = sys.argv[1:]
out_dir = Path(out_dir)
out_dir.mkdir(parents=True, exist_ok=True)

print(f'Read {input_file}...', flush=True)
adata = ad.read_h5ad(input_file)
adata = ad.AnnData(
    X=adata.raw.X,
    obs=adata.obs[KEEP_OBS].copy(),
    var=adata.raw.var[[]].copy(),
)
assert np.issubdtype(adata.X.dtype, np.number)
assert (adata.X[:1000].data % 1 == 0).all(), 'X does not look like raw counts'

# one permutation, so smaller subsamples are nested in larger ones
order = np.random.default_rng(SEED).permutation(adata.n_obs)
for size in sizes:
    if size == 'full':
        subset = adata
    else:
        n = int(size)
        assert n <= adata.n_obs, f'{n} > {adata.n_obs} cells'
        idx = np.sort(order[:n])
        subset = adata[idx].copy()
    # drop categories that disappear through subsampling
    subset.obs = subset.obs.apply(
        lambda s: s.cat.remove_unused_categories() if s.dtype == 'category' else s
    )
    out_file = out_dir / f'HLCA_{size}.h5ad'
    print(f'Write {subset.n_obs} cells to {out_file}...', flush=True)
    subset.write_h5ad(out_file)
