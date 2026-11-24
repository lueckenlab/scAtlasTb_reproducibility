from tqdm import tqdm, dask
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, vstack, issparse
import dask.array as da
import anndata as ad
import scanpy as sc
import sparse
from matplotlib import pyplot as plt


def get_adjacency(
    X,
    weighted: bool,
    k: int = 1,
    _lambda: float = 1,
    tol: float = 1e-5,
    use_dask: bool = False,
    chunk_size: int = 50_000,
):
    """
    Retrieve adjacency matrix from distances or connectivities.
    
    :param weighted: whether to preserve weighting of adjacency or return unweighted adjacency
        Default: weighted=False - 1 when edge present, 0 when edge not present
    :param k: power of matrix multiplication. Computationally expensive and densifies the matrix.
        Default: 1, no multiplication performed.
    """
    assert issparse(X) or isinstance(X, da.Array), 'matrix must be scipy sparse matrix or dask array'

    if use_dask and not isinstance(X, da.Array):
        X = da.from_array(X, chunks=(-1, chunk_size)).map_blocks(sparse.COO)

    for _ in range(1, k):
        X = X.dot(X.T)

    if _lambda != 1:
        from decimal import Decimal  # for exact values
        X *= np.float32(Decimal(_lambda) ** k)

    if issparse(X):
        X.data[X.data < tol] = 0
        X.eliminate_zeros()

    if not weighted:
        X = (X > 0).astype('float32')
    return X


def graph_similarity(
    adata: ad.AnnData,
    obsp_keys: list,
    operator='intersection',
    use_dask=True,
    chunk_size=50_000,
    power_k=1,
    _lambda=1,
    weighted=False,
    log_scale=False,
    max_scale=False,
    scale='min',
):
    """
    kNN-based graph similarity
    
    :params obsp_keys: list of 
    :param operator: operator='intersection' -> kNN overlap, operator='union' -> number of edge occurrence for all embeddings
    """
    # set tqdm for non-dask computations
    obsp_keys = tqdm(obsp_keys) if not use_dask else obsp_keys
    
    x_diff = None
    
    for key in obsp_keys:
        
        x = get_adjacency(
            adata.obsp[key],
            weighted=weighted,
            k=power_k,
            _lambda=_lambda,
            use_dask=use_dask,
        )
        
        if x_diff is None:
            # assuming that obsp_keys references weighted adjacency matrix
            x_diff = x.copy()
            min_degrees = x_diff.sum(axis=0)
            union = x_diff.copy()
            continue
        
        
        # calculate global minimum degree
        min_degrees = np.minimum(min_degrees, x.sum(axis=0))

        # calculate union of edges
        union = da.maximum(union, x) if use_dask else union.maximum(x)
        
        if operator == 'intersection':
            x_diff = get_adjacency(
                x_diff,
                weighted=weighted,
                k=power_k,
                _lambda=_lambda,
                use_dask=use_dask,
            )
            # element-wise multiplication (logical AND) -> intersection of same edges
            x_diff = da.multiply(x_diff, x) if use_dask else x_diff.multiply(x)
        
        # if operator == 'difference':
        #     # element-wise multiplication -> intersection of same edges
        #     x_diff = 1 - da.multiply(x_diff, x) if use_dask else 1 - x_diff.multiply(x)
        
        
        elif operator == 'sum':
            # element-wise sum -> number of graphs that edge exists
            x_diff += x
        
        elif operator == 'xor':
            # element-wise != -> highlight differences between edges
            x_diff = (x_diff != x).astype('float32')  # logical XOR
        
        elif operator == 'product':
            # matrix multiplication
            x_diff = x_diff.dot(x)
            
            if not use_dask:
                x_diff.data[x_diff.data < 1e-5] = 0
                x_diff.eliminate_zeros()
        
        else:
            raise ValueError(f'unknown operator "{operator}"')
    
    # sum up intersecting edges per node
    x_diff = x_diff.sum(axis=0)
    
    if isinstance(x_diff, da.Array):
        with dask.TqdmCallback(desc=f"compute graph {operator}"):
            x_diff = x_diff.compute().todense()
    else:
        x_diff = x_diff.A1
    
    # determine scaling factors
    scaling_factor = 1
    if scale == 'min':
        scaling_factor = min_degrees + 1
    elif scale in ['max', 'union']:
        scaling_factor = union.sum(axis=0) + 1
    
    if isinstance(scaling_factor, da.Array):
        with dask.TqdmCallback(desc=f"compute {scale} scaling factor"):
            scaling_factor = scaling_factor.compute().todense()
    elif isinstance(scaling_factor, np.matrix):
        scaling_factor = scaling_factor.A1
    
    # scale values
    x_diff /= scaling_factor
    
    if log_scale:
        x_diff = np.log1p(x_diff)

    if max_scale:
        x_diff /= x_diff.max()
    
    return x_diff


### Distance-based graph similarity

import tracemalloc
import time
import itertools
from collections import defaultdict
from scipy.spatial import distance
from scipy.sparse import triu, tril, csr_matrix, coo_matrix
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
from concurrent.futures import ThreadPoolExecutor, as_completed

import multiprocessing
multiprocessing.set_start_method('spawn', force=True)


def symmetrize_mask(x, verbose=False):
    row_mask, col_mask = [], []
    triangles = triu(x > 0), tril(x > 0).T
    diff_mask = triangles[0] != triangles[1]

    for i, tri in enumerate(triangles):
        indices = diff_mask.multiply(tri).nonzero()
        row_mask.append(indices[i])
        col_mask.append(indices[(i + 1) % 2])
    
    row_mask = np.concatenate(row_mask)
    col_mask = np.concatenate(col_mask)
    
    if verbose:
        print(f'{len(row_mask)} entries to be symmetrized')
    
    return row_mask, col_mask


def is_symmetric(x):
    # Check if the matrix is equal to its transpose
    # return (x != x.transpose()).nnz == 0
    # return triu(x).nnz == tril(x).nnz
    return (x.sum(0) % 2 == 0).all()
    # return (x != x.T).nnz == 0


def symmetrize_if_needed(x):
    if is_symmetric(x):
        return x
    return x.maximum(x.T)


def _compute_distances(rows, cols, obsm, n_jobs=-1, batch_size=100_000, **kwargs):
    
    def _compute_row_distance(obsm, row, first, last):
        indices = np.arange(first, last)
        dist = distance.cdist(
            obsm[[row], :],
            obsm[cols[first:last], :],
            **kwargs
        )
        return indices, dist


    def _compute_batch(obsm, batch_rows, batch_firsts, batch_lasts):
        return [
            _compute_row_distance(obsm, *args)
            for args in zip(batch_rows, batch_firsts, batch_lasts)
        ]

    unique_rows, first_occurrence, counts = np.unique(
        rows,
        return_index=True,
        return_counts=True
    )
    last_occurrence = first_occurrence + counts
    n_rows = len(unique_rows)
    
    if n_jobs == 1:
        results = [
            _compute_row_distance(obsm, *args)
            for args in tqdm(
                zip(unique_rows, first_occurrence, last_occurrence),
                desc="Computing distances",
                mininterval=1,
                total=n_rows,
            )
        ]

    else:
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'obsm.npy')
            np.save(filename, obsm)
            obsm_mmap = np.load(filename, mmap_mode='r')
            
            batched_args = (
                (
                    unique_rows[i:i + batch_size],
                    first_occurrence[i:i + batch_size],
                    last_occurrence[i:i + batch_size],
                )
                for i in range(0, n_rows, batch_size)
            )
            results = Parallel(n_jobs=n_jobs, backend='loky')(
                delayed(_compute_batch)(obsm_mmap, *args)
                for args in tqdm(
                    batched_args,
                    desc="Computing distances",
                    total=int(n_rows / batch_size)
                )
            )
            # Flatten the list of lists
            results = (item for sublist in results for item in sublist)
    
    distances = np.zeros(rows.shape[0])
    for indices, dist in results:
        distances[indices] = dist
    
    # # check if distances added to correct location
    # distances_correct = np.zeros(n_distances)
    # for i in tqdm(range(n_distances), desc='Compute missing distances', mininterval=1):
    #     dist = distance.cdist(obsm[[rows[i]], :], obsm[[cols[i]], :])[0][0]
    #     distances_correct[i] = dist
    # print(np.all(distances == distances_correct))
    
    return distances


def compute_missing_distances(
    adata,
    obsp_key_1,
    obsm_key,
    obsp_key_2,
    inplace=True,
    return_matrix=True,
    n_jobs=-1,
    batch_size=100_000,
    **kwargs,
):
    """
    Compute missing distances. Due to scanpy's heuristic, only distances for k-nearest neighbors are kept.
    In order to compare distances across embeddings, the corresponding distances of edges from one embedding
    must be present or recomputed for the other embedding.
    
    :param obsp_key_1: slot for pair-wise distances from embedding 1
    :param obsm_key: slot for embedding 1 used for missing distance computation
    :param obsp_key_2: slot slot for pair-wise distances from embedding 2
    """
    x1 = adata.obsp[obsp_key_1]
    x2 = adata.obsp[obsp_key_2]
    obsm = adata.obsm[obsm_key]
    
    if isinstance(x1, da.Array):
        x1 = x1.compute()
    if isinstance(x2, da.Array):
        x2 = x2.compute()
    
    # fill in missing values to make distance matrix symmetric
    for _ in tqdm(range(1), desc='Symmetrize matrix'):
        x1 = symmetrize_if_needed(x1)
        x2 = symmetrize_if_needed(x2)
    
    # get neighbors that are not computed in the other graph
    print('Determine missing distances...')
    x1_adj, x2_adj = triu(x1 > 0), triu(x2 > 0)
    # XOR and x1 values > 0
    rows, cols = (x1_adj != x2_adj).multiply(x2_adj).nonzero()
    del x1_adj, x2_adj
    
    n_distances = len(rows)
    print(f'{n_distances} edges to recompute')
    
    if n_distances > 0:
        # compute distances
        new_distances = _compute_distances(
            rows, cols, obsm, n_jobs=n_jobs, batch_size=batch_size, **kwargs,
        )
        
        # add distances to distance matrix in place
        new_distances = coo_matrix(
            (new_distances, (rows, cols)),
            shape=x1.shape,
            dtype='float32',
        )
        x1 = (x1.tocoo() + new_distances + new_distances.T).tocsr()
        
    if inplace:
        print('Set distances inplace...')
        adata.obsp[obsp_key_1] = x1

    if return_matrix:
        return x1


def plot_ranked_distances(adata, x1, x2):
    """
    Diagnostic plot for distance computation
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    metrics = ['avg_distance_1', 'avg_distance_2']
    for x, metric in zip([x1, x2], metrics):
        ax1.plot(
            adata.obs[f'{metric}:{x1}-vs-{x2}'].sort_values().values,
            label=x
        )
    ax1.set_xlabel('rank')
    ax1.set_ylabel('avg distance')
    ax1.set_title('Ranked average distance per node')
    ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    metrics = ['avg_difference', 'avg_distance_diff']
    for metric in metrics:
        ax2.plot(adata.obs[f'{metric}:{x1}-vs-{x2}'].sort_values().values, label=metric)
    ax2.set_xlabel('rank')
    ax2.set_ylabel('score')
    ax2.set_title('Ranked graph differences')
    ax2.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    fig.subplots_adjust(wspace=1)
    plt.show()


def plot_distances_scatter(adata, x1, x2, **kwargs):
    """
    Diagnostic plot for distance computation
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.scatter(
        adata.obs[f'avg_distance_1:{x1}-vs-{x2}'],
        adata.obs[f'avg_distance_2:{x1}-vs-{x2}'],
        **kwargs,
    )
    ax1.set_xlabel(x1)
    ax1.set_ylabel(x2)
    ax1.set_title('Average distance per node')
    
    metrics = ['avg_difference', 'avg_distance_diff']
    for metric in metrics:
        ax2.scatter(
            adata.obs[f'{metric}:{x1}-vs-{x2}'],
            adata.obs[f'{metric}:{x2}-vs-{x1}'],
            label=metric,
            **kwargs,
        )
    ax2.set_xlabel(metrics[0])
    ax2.set_ylabel(metrics[1])
    ax2.set_title('Graph differences')
    ax2.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    fig.subplots_adjust(wspace=0.5)
    plt.show()


def sparse_spearman(matrix1, matrix2, max_workers=None, n_jobs=-1):
    
    def _sparse_spearman(row1, row2):
        
        def pad_zeros(x, shape):
            x_pad = np.zeros(shape, dtype=x.dtype)
            x_pad[-x.shape[0]:] = x
            return x_pad
        
        n, n2 = row1.shape[0], row2.shape[0]
        
        # Avoid division by zero for constant rows
        if n <= 1 or n2 <= 1 or np.all(row1 == row1[0]) or np.all(row2 == row2[0]):
            return np.nan
        
        # check if rows have same length, otherwise pad with zeros
        if n > n2:
            row2 = pad_zeros(row2, n)
        elif n < n2:
            row1 = pad_zeros(row1, n2)
        
        # Rank the data
        rank1 = np.argsort(np.argsort(row1)) + 1
        rank2 = np.argsort(np.argsort(row2)) + 1

        # Calculate Spearman correlation
        return 1 - (6 * np.sum((rank1 - rank2) ** 2)) / (n * (n**2 - 1))
    
    def get_row_data(x, i):
        return x.data[x.indptr[i]:x.indptr[i+1]]

    
    assert matrix1.shape == matrix2.shape, f'shape mismatch: {matrix1.shape}, {matrix2.shape}'
    
    n_rows = matrix1.shape[0]
    row_data = [
        (get_row_data(matrix1, i), get_row_data(matrix2, i))
        for i in range(n_rows)
    ]

    with parallel_backend('loky'):
        results = Parallel(n_jobs=n_jobs)(
            delayed(_sparse_spearman)(row1, row2)
            for row1, row2 in tqdm(row_data, desc="Spearman correlation", mininterval=1, total=n_rows)
        )

    return np.array(results)


def get_knn(x, k):
    from numba import njit
    
    @njit
    def filter_row_knn(data, indices, indptr, k):
        new_data = []
        new_indices = []
        new_indptr = [0]

        for i in range(len(indptr) - 1):
            start = indptr[i]
            end = indptr[i + 1]

            row_data = data[start:end]
            row_indices = indices[start:end]

            if len(row_data) <= k:
                mask = np.ones(len(row_data), dtype=np.bool_)
            else:
                # get k-largest threshold
                threshold = np.partition(row_data, -k)[-k]
                mask = row_data >= threshold

            new_data.extend(row_data[mask])
            new_indices.extend(row_indices[mask])
            new_indptr.append(len(new_data))

        return np.array(new_data), np.array(new_indices), np.array(new_indptr)

    if isinstance(x, da.Array):
        x = x.compute()
    x = csr_matrix(x)  # ensure CSR format

    data, indices, indptr = filter_row_knn(x.data, x.indices, x.indptr, k)
    return csr_matrix((data, indices, indptr), shape=x.shape)

#     if isinstance(x, da.Array):
#         x = x.compute()
#     x = csr_matrix(x)  # ensure CSR format for fast row access
#     new_data = []
#     new_indices = []
#     indptr = [0]

#     # Iterate over each row
#     for i in tqdm(range(x.shape[0]), desc=f'Select {k} nearest neighbors', mininterval=1):
#         # Get the non-zero values and columns for the current row
#         start, end = x.indptr[i], x.indptr[i + 1]
#         row_data = x.data[start:end]
#         row_indices = x.indices[start:end]

#         # set values that are smaller than k to 0
#         if len(row_data) < k:
#             mask = np.ones_like(row_data, dtype=bool)
#         else:
#             kth_smallest = np.partition(row_data, k - 1)[k - 1]
#             mask = row_data >= kth_smallest

#         new_data.extend(row_data[mask])
#         new_indices.extend(row_indices[mask])
#         indptr.append(len(new_data))

#     return csr_matrix((new_data, new_indices, indptr), shape=x.shape)


def compare_distances(
    adata,
    obsp_key_1,
    obsm_key_1,
    obsp_key_2,
    obsm_key_2,
    scale_distances=True,
    quantile=0.9,
    k_max=50,
    log_scale_diffs=False,
    **kwargs,
):
    """
    Compare distances of same edges but from different representations.
    """
    
    if isinstance(adata.obsp[obsp_key_1], da.Array):
        adata.obsp[obsp_key_1] = adata.obsp[obsp_key_1].compute()
    
    if isinstance(adata.obsp[obsp_key_2], da.Array):
        adata.obsp[obsp_key_2] = adata.obsp[obsp_key_2].compute()
    
    x2 = compute_missing_distances(
        adata,
        obsp_key_1=obsp_key_2,
        obsm_key=obsm_key_2,
        obsp_key_2=obsp_key_1,
        inplace=False,
        return_matrix=True,
        **kwargs,
    ).copy()
    
    print('Get kNN...')
    x1 = get_knn(adata.obsp[obsp_key_1], k=k_max)
    nnz_mask = x1 > 0
    x2 = x2.multiply(nnz_mask)
    x2.eliminate_zeros()
    
    print('Calculate degress...')
    degrees = nnz_mask.sum(axis=0)
    degrees[degrees == 0] = 1
    # print('zero degrees', (degrees == 0).sum())
    # print('zero degrees', ((x1 > 0).sum(axis=0) == 0).sum())
    # print('zero degrees', (x1.sum(axis=0) == 0).sum())

        
    if scale_distances:
        # x1.data = 1 / np.log10(x1.data + 1)
        # x2.data = 1 / np.log10(x2.data + 1)
        print(f'scale distances by {quantile} quantile...')
        x1.data /= np.quantile(adata.obsp[obsp_key_1].data, q=quantile)
        x2.data /= np.quantile(adata.obsp[obsp_key_2].data, q=quantile)

    print('Calculate differences...')
    diff_mtx = x1 - x2
    diff_mtx.data = np.abs(diff_mtx.data)
    avg_diff = (diff_mtx.sum(axis=0) / degrees).A1
    avg_dist_diff = np.abs((x1.sum(axis=0) - x2.sum(axis=0)) / degrees).A1

    # if scale:
    #     print(f'scale by {quantile} quantile...')
    #     avg_diff /= np.quantile(avg_diff, q=quantile)
    #     avg_dist_diff /= np.quantile(avg_dist_diff, q=quantile)
    
    if log_scale_diffs:
        print('log scale...')
        avg_diff = np.log10(avg_diff + 1)
        avg_dist_diff = np.log10(avg_dist_diff + 1)
        
    return pd.DataFrame(
        {
            # mean only for neighborhoods of interest
            'average_distance_1': (x1.sum(axis=0) / degrees).A1,
            'average_distance_2': (x2.sum(axis=0) / degrees).A1,
            'average_difference': avg_diff,
            'average_distance_diff': avg_dist_diff,
            'spearman_correlation': avg_dist_diff,  # quick workaround
            # 'spearman_correlation': sparse_spearman(x1, x2),
        },
        index=adata.obs_names
    )
