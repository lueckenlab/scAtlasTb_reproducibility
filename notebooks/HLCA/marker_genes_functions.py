import scanpy as sc
from tqdm import tqdm


def read_yaml_file(file, keys=['MARKER_GENES']):
    import yaml

    if not keys:
        keys = []

    with open(file, 'r') as file:
        _dict = yaml.safe_load(file)

    for key in keys:
        _dict = _dict[key]

    return _dict


def filter_marker_genes(marker_gene_file, adata):
    all_gene_sets = read_yaml_file(marker_gene_file, keys=['MARKER_GENES'])

    for marker_key, marker_dict in all_gene_sets.items():
        all_gene_sets[marker_key] = {
            ct: [g for g in g_list if g in adata.var_names.values]
            for ct, g_list in marker_dict.items()
            if len(g_list) > 0
        }

    all_genes = set()
    for marker_key in all_gene_sets:
        all_genes = all_genes.union(*all_gene_sets[marker_key].values())

    print(f'{len(all_genes)} unique marker genes')

    return all_gene_sets, all_genes


def extract_de_genes(adata, n_genes=20):
    de_genes = set()

    for key in tqdm(adata.uns.keys()):
        if not key.startswith('marker_genes'):
            continue

        rank_genes_df = sc.get.rank_genes_groups_df(
            adata,
            key=key,
            group=None,
        )
        genes = (
            rank_genes_df.groupby('group')
            .head(n_genes)['names']
            .unique()
            .tolist()
        )
        de_genes.update(genes)

    return de_genes


def update_marker_gene_keys(adata, prefix='leiden'):
    for key in tqdm(adata.uns.keys()):
        if key.startswith('marker_genes') and prefix in key:
            adata.uns[key]['params']['groupby'] = key.split('=')[1]


def get_marker_genes(adata, key='rank_genes_groups', n_genes=100, **kwargs):
    kwargs = dict(group=None) | kwargs

    df = sc.get.rank_genes_groups_df(
        adata,
        key=key,
        **kwargs,
    ).assign(
        l2fc_abs=lambda x: x['logfoldchanges'].abs(),
    ).rename(
        columns={'names': 'gene'},
    )

    if 'group' in df.columns:
        df = df.sort_values(
            by=['group', 'logfoldchanges', 'pvals'],
            ascending=[True, False, True],
        ).groupby('group').head(n_genes)

    return df
