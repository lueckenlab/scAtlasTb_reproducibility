import pandas as pd
from matplotlib import pyplot as plt


def clean_slot_names(adata, replace_str='', replace_with=''):
    for name, slot in adata.__dict__.items():
        if isinstance(slot, dict):
            slot = {k.replace(replace_str, replace_with): v for k, v in slot.items()}
            setattr(adata, name, slot)
        elif isinstance(slot, pd.DataFrame):
            slot.columns = [x.replace(replace_str, replace_with) for x in slot.columns]
            # setattr(adata, name, slot)
        if name == '_uns':
            for key, value in adata.uns.items():
                if key.startswith('marker_genes'):
                    adata.uns[key]['params']['groupby'] = key.replace(
                        'marker_genes_group=',
                        '',
                    ).replace(
                        replace_str,
                        replace_with
                    )


def plot_diff_per_clusters(
    adata,
    cluster_key,
    diff_key,
    x_label=None,
    width=6,
    height_factor=0.2,
    figsize=None,
    agg="mean",
    quantile=None,
    cluster_thresh=10,
    save=None,
):
    if x_label is None:
        x_label = diff_key

    # ensure categorical for consistent color mapping
    if not pd.api.types.is_categorical_dtype(adata.obs[cluster_key]):
        adata.obs[cluster_key] = adata.obs[cluster_key].astype("category")

    # filter clusters by size
    value_counts = adata.obs[cluster_key].value_counts()
    value_counts = value_counts[value_counts > cluster_thresh]
    clusters = value_counts.index

    df = adata.obs[adata.obs[cluster_key].isin(clusters)]
    gb = df.groupby(cluster_key, observed=True)[diff_key]

    if quantile is not None:
        diff_per_cluster = gb.quantile(quantile)
    else:
        diff_per_cluster = gb.agg(agg)

    diff_per_cluster = diff_per_cluster.sort_values()

    # ---- color mapping from AnnData ----
    colors = None
    color_key = f"{cluster_key}_colors"
    if color_key in adata.uns:
        cat_to_color = dict(
            zip(adata.obs[cluster_key].cat.categories, adata.uns[color_key])
        )
        colors = [cat_to_color.get(k, "#333333") for k in diff_per_cluster.index]

    # ---- plot ----
    if figsize is None:
        figsize = (width, len(diff_per_cluster) * height_factor)

    fig, ax = plt.subplots(figsize=figsize)

    diff_per_cluster.plot.barh(ax=ax, color=colors)

    for i, (k, v) in enumerate(diff_per_cluster.items()):
        ax.text(v, i, f"n={value_counts[k]}", va="center")

    ax.grid(False)
    ax.set_xlabel(x_label)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    if save:
        plt.savefig(save, bbox_inches='tight', dpi=300)

    plt.show()

    return diff_per_cluster.sort_values(ascending=False)
