"""
Brute-force arm of the workflow comparison: the same preprocessing -> integration ->
metrics workflow as scAtlasTb.yaml, written the way a typical analysis script would be.

- every stage reads the full .h5ad into memory (no Dask, no backed/partial reads)
- every stage writes a full .h5ad copy, including all count layers (no linking),
  one per method and output type, with neighbors and UMAP (as scAtlasTb's integration output)
- same functions and parameters as the scAtlasTb modules

Each stage runs as its own process so that it can use the same pre-existing conda
environment scAtlasTb uses for that step (see run_brute_force.sh).

Usage:
    python brute_force.py preprocess <input.h5ad> <preprocessed.h5ad>
    python brute_force.py integrate <method> <preprocessed.h5ad> <output_prefix>
        -> <output_prefix>_<output_type>.h5ad for each output type of the method
    python brute_force.py metrics <integrated.h5ad> <metrics.tsv>
"""
import argparse

import numpy as np
import pandas as pd
import scanpy as sc

BATCH = 'dataset'
LABEL = 'ann_finest_level'
N_HVG = 2000
N_PCS = 50
TARGET_SUM = 10_000
SEED = 0
CLUSTER_RESOLUTIONS = np.round(np.arange(0.2, 2.01, 0.2), 1)  # same grid as scAtlasTb


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def preprocess(input_file, output_file):
    log(f'Read {input_file}...')
    adata = sc.read_h5ad(input_file)
    adata.layers['counts'] = adata.X.copy()

    log('Normalize...')
    sc.pp.normalize_total(adata, target_sum=TARGET_SUM)
    sc.pp.log1p(adata)
    adata.layers['normcounts'] = adata.X.copy()

    log('Filter genes...')
    sc.pp.filter_genes(adata, min_cells=1)

    log('Highly variable genes...')
    sc.pp.highly_variable_genes(adata, n_top_genes=N_HVG)

    log('PCA...')
    sc.pp.pca(adata, n_comps=N_PCS, mask_var='highly_variable', svd_solver='covariance_eigh')

    log('Neighbors...')
    sc.pp.neighbors(adata, use_rep='X_pca')

    log(f'Write {output_file}...')
    adata.write_h5ad(output_file)


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------
# Each method returns its outputs by type, as in scAtlasTb:
#   'full'  -> corrected feature matrix (cells x HVGs)
#   'embed' -> low-dimensional embedding
#   'knn'   -> True if the method's kNN graph is stored in adata (in .obsp/.uns['neighbors'])

def pca(adata):
    sc.pp.pca(adata, n_comps=N_PCS, svd_solver='covariance_eigh')
    return adata.obsm['X_pca']


def run_unintegrated(adata):
    embedding = pca(adata)
    sc.pp.neighbors(adata, use_rep='X_pca')
    return {'full': adata.X, 'embed': embedding, 'knn': True}


def run_combat(adata):
    sc.pp.combat(adata, key=BATCH)
    return {'full': adata.X}


def run_harmonypy(adata):
    pca(adata)
    sc.external.pp.harmony_integrate(adata, key=BATCH, basis='X_pca', random_state=SEED)
    return {'embed': adata.obsm['X_pca_harmony']}


def run_scvi(adata, model_dir):
    import os
    import scvi

    scvi.settings.seed = SEED
    scvi.settings.num_threads = int(os.environ.get('OMP_NUM_THREADS', 1))
    adata = sc.AnnData(adata.layers['counts'], obs=adata.obs[[BATCH]].copy())  # scVI models raw counts
    scvi.model.SCVI.setup_anndata(adata, batch_key=BATCH)
    model = scvi.model.SCVI(adata)
    model.train(check_val_every_n_epoch=1)  # as in scAtlasTb (for loss curves)
    model.save(model_dir, overwrite=True)
    return {'embed': model.get_latent_representation()}


def run_bbknn(adata):
    pca(adata)
    sc.external.pp.bbknn(adata, batch_key=BATCH, use_rep='X_pca')
    return {'knn': True}


METHODS = {
    'unintegrated': run_unintegrated,
    'combat': run_combat,
    'harmonypy': run_harmonypy,
    'scvi': run_scvi,
    'bbknn': run_bbknn,
}


def integrate(method, input_file, output_prefix):
    """Writes one full .h5ad per output type: <output_prefix>_<output_type>.h5ad"""
    log(f'Read {input_file}...')
    adata = sc.read_h5ad(input_file)
    adata.X = adata.layers['normcounts']

    log(f'Run {method} on {N_HVG} HVGs...')
    adata_hvg = adata[:, adata.var['highly_variable']].copy()
    if method == 'scvi':
        outputs = run_scvi(adata_hvg, model_dir=f'{output_prefix}_model')
    else:
        outputs = METHODS[method](adata_hvg)

    for output_type, result in outputs.items():
        log(f'Postprocess output type "{output_type}"...')
        out = adata.copy()  # the usual "save everything" pattern: full object per result
        out.uns['integration'] = {'method': method, 'output_type': output_type}

        if output_type == 'knn':
            out.obsp['connectivities'] = adata_hvg.obsp['connectivities']
            out.obsp['distances'] = adata_hvg.obsp['distances']
            out.uns['neighbors'] = adata_hvg.uns['neighbors']
        else:
            if output_type == 'full':
                out.obsm['X_corrected'] = result
                corrected = sc.AnnData(result, obs=adata_hvg.obs[[]])
                result = pca(corrected)
            out.obsm['X_emb'] = result
            sc.pp.neighbors(out, use_rep='X_emb')

        log('UMAP...')
        sc.tl.umap(out)

        output_file = f'{output_prefix}_{output_type}.h5ad'
        log(f'Write {output_file}...')
        out.write_h5ad(output_file)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def metrics(integrated_file, output_file):
    import scib

    log(f'Read {integrated_file}...')
    adata = sc.read_h5ad(integrated_file)
    method = adata.uns['integration']['method']
    output_type = adata.uns['integration']['output_type']

    # label-based metrics only use labelled cells (as in scAtlasTb)
    adata = adata[adata.obs[LABEL].notna()].copy()

    log('Optimal Leiden clustering...')
    scib.me.cluster_optimal_resolution(
        adata,
        label_key=LABEL,
        cluster_key='cluster',
        resolutions=CLUSTER_RESOLUTIONS,
    )

    scores = {
        'nmi': lambda: scib.me.nmi(adata, 'cluster', LABEL),
        'ari': lambda: scib.me.ari(adata, 'cluster', LABEL),
        'graph_connectivity': lambda: scib.me.graph_connectivity(adata, LABEL),
        'isolated_label_f1': lambda: scib.me.isolated_labels_f1(adata, LABEL, BATCH, embed=None),
        'ilisi': lambda: scib.me.ilisi_graph(adata, BATCH, type_='knn', subsample=50, scale=True),
        'clisi': lambda: scib.me.clisi_graph(adata, LABEL, type_='knn', subsample=50, scale=True),
    }
    # embedding-based metrics are not defined for kNN graph outputs (as in scAtlasTb)
    if output_type != 'knn':
        scores |= {
            'asw_label': lambda: scib.me.silhouette(adata, LABEL, embed='X_emb'),
            'asw_batch': lambda: scib.me.silhouette_batch(adata, BATCH, LABEL, embed='X_emb'),
            'isolated_label_asw': lambda: scib.me.isolated_labels_asw(adata, LABEL, BATCH, embed='X_emb'),
        }

    rows = []
    for metric, compute in scores.items():
        log(f'Compute {metric}...')
        rows.append({'method': method, 'output_type': output_type, 'metric': metric, 'score': compute()})

    log(f'Write {output_file}...')
    pd.DataFrame(rows).to_csv(output_file, sep='\t', index=False)


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    stages = parser.add_subparsers(dest='stage', required=True)

    p = stages.add_parser('preprocess')
    p.add_argument('input_file')
    p.add_argument('output_file')

    p = stages.add_parser('integrate')
    p.add_argument('method', choices=METHODS)
    p.add_argument('input_file')
    p.add_argument('output_prefix')

    p = stages.add_parser('metrics')
    p.add_argument('integrated_file')
    p.add_argument('output_file')

    args = vars(parser.parse_args())
    stage = args.pop('stage')
    {'preprocess': preprocess, 'integrate': integrate, 'metrics': metrics}[stage](**args)
