from matplotlib import pyplot as plt


def clean_prefixes(adata, prefix):
    adata.obs.columns = adata.obs.columns.str.replace(prefix, '')
    
    adata.obsm = {
        key.replace(prefix, ''): adata.obsm[key]
        for key in adata.obsm.keys()
    }
    
    adata.obsp = {
        key.replace(prefix, ''): adata.obsp[key]
        for key in adata.obsp.keys()
    }
    
    adata.uns = {
        key.replace(prefix, ''): adata.uns[key]
        for key in adata.uns.keys()
    }


def plot_diff_per_clusters(
    adata,
    cluster_key,
    diff_key,
    x_label=None,
    width=6,
    height_factor=0.2,
    figsize=None,
    agg='mean',
    cluster_thresh=10,
):
    if x_label is None:
        x_label = diff_key
    
    value_counts = adata.obs[cluster_key].astype(str).value_counts()
    value_counts = value_counts[value_counts > cluster_thresh]
    clusters = value_counts.index
    df = adata.obs.query(f'`{cluster_key}`.isin(@clusters)')
    diff_per_cluster = df.groupby(
        cluster_key,
        observed=True
    )[diff_key].agg(agg)
    diff_per_cluster = diff_per_cluster.sort_values()

    # plot
    if figsize is None:
        figsize = (width, len(diff_per_cluster) * height_factor)
    fig, ax = plt.subplots(figsize=figsize)
    
    diff_per_cluster.plot.barh(ax=ax)
    
    for i, (k, v) in enumerate(diff_per_cluster.items()):
        ax.text(v, i, f'{value_counts[k]}', va='center')
    
    ax.grid(False)
    ax.set_xlabel(x_label)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.show()
    
    return diff_per_cluster


def back_to_back_barplot(
    df,
    group_col,
    left_col,
    right_col,
    figsize=(7, 8),
    title='',
    round_decimals=2,
    left_color='steelblue',
    right_color='tomato',
    scale=False,
    xlim_left=None,
    xlim_right=None,
):
    from matplotlib.ticker import FuncFormatter

    df = df.groupby(group_col, observed=True)[[left_col, right_col]].mean().sort_values(by=right_col)
    left_max, right_max = df[left_col].max(), df[right_col].max()

    plot_left  = -df[left_col]  / (left_max  if scale else 1)
    plot_right =  df[right_col] / (right_max if scale else 1)

    fig, ax = plt.subplots(figsize=figsize)
    ax.barh(df.index, plot_left,  color=left_color)
    ax.barh(df.index, plot_right, color=right_color)

    lim = lambda val, mx: -(val / mx if scale else val) if val else None
    xmin = lim(xlim_left, left_max)
    xmax = (xlim_right / right_max if scale else xlim_right) if xlim_right else None
    ax.set_xlim(
        xmin if xmin is not None else ax.get_xlim()[0],
        xmax if xmax is not None else ax.get_xlim()[1],
    )

    scale_fmt = lambda x, _: f'{abs(x) * (left_max if x < 0 else right_max):.{round_decimals}g}'
    plain_fmt  = lambda x, _: f'{abs(x):.{round_decimals}g}'
    ax.xaxis.set_major_formatter(FuncFormatter(scale_fmt if scale else plain_fmt))

    ax.axvline(0, color='black', linewidth=0.8)
    fig.canvas.draw()
    for tick in ax.xaxis.get_major_ticks():
        c = left_color if tick.get_loc() < 0 else right_color if tick.get_loc() > 0 else 'black'
        tick.label1.set_color(c)
        tick.tick1line.set_color(c)

    ax.annotate(left_col,  xy=(0.25, -0.05), xycoords='axes fraction', ha='center', va='top', color=left_color)
    ax.annotate(right_col, xy=(0.75, -0.05), xycoords='axes fraction', ha='center', va='top', color=right_color)
    ax.set_ylabel(group_col, labelpad=15)
    ax.set_title(title)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    ax.margins(y=0)
    plt.tight_layout()
    plt.show()


### Similarity matrix
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.cluster.hierarchy import linkage
from sklearn.metrics import pairwise_distances


def _make_conf_matrix(df, group_col, value_col, groups, values):
    """Build a boolean contingency matrix reindexed to given groups/values."""
    return (
        pd.crosstab(df[group_col], df[value_col])
        .reindex(index=groups, columns=values, fill_value=0)
        .astype(bool)
    )


def _compute_similarity(conf1, conf2, metric):
    """Compute similarity matrix between two contingency matrices."""
    if metric == 'overlap':
        intersection = conf1.values.astype(int) @ conf2.values.astype(int).T
        row_sums = conf1.values.sum(axis=1)[:, None]
        return np.where(row_sums != 0, intersection / row_sums, 0)
    return 1 - pairwise_distances(conf1.values, conf2.values, metric=metric)


def _get_groups_and_values(df1, df2, group_col, value_col, keep_missing=False):
    """Return group sets, sorted groups, and union of values for two DataFrames."""
    g1, g2 = set(df1[group_col].unique()), set(df2[group_col].unique())
    groups = sorted(g1 | g2 if keep_missing else g1 & g2)
    values = sorted(set(df1[value_col].unique()) | set(df2[value_col].unique()))
    return g1, g2, groups, values


def calculate_pairwise_similarity(
    df1, df2, group_col, value_col,
    metric='jaccard', keep_missing=False,
):
    """
    Computes an (n x m) similarity matrix between all groups in df1 vs df2.

    Returns a DataFrame where sim_df.iloc[i, j] is the similarity between
    group i from df1 and group j from df2.
    """
    g1, g2, groups, values = _get_groups_and_values(df1, df2, group_col, value_col, keep_missing)

    rows = sorted(g1) if keep_missing else groups
    cols = sorted(g2) if keep_missing else groups

    conf1 = _make_conf_matrix(df1, group_col, value_col, rows, values)
    conf2 = _make_conf_matrix(df2, group_col, value_col, cols, values)

    return pd.DataFrame(
        _compute_similarity(conf1, conf2, metric),
        index=conf1.index,
        columns=conf2.index,
    )


def calculate_matched_similarity(
    df1, df2, group_col, value_col, metric='jaccard'
):
    """
    Computes similarity only for matching groups (present in both df1 and df2).

    Returns a Series indexed by group name.
    """
    _, _, groups, values = _get_groups_and_values(df1, df2, group_col, value_col)
    conf1 = _make_conf_matrix(df1, group_col, value_col, groups, values)
    conf2 = _make_conf_matrix(df2, group_col, value_col, groups, values)
    return pd.Series(
        np.diag(
            _compute_similarity(conf1, conf2, metric)
        ),
        index=groups,
        name=metric
    )


def plot_similarity_heatmap(
    sim_df,
    title='Group Similarity',
    xlabel='Dataset 2',
    ylabel='Dataset 1',
    na_color='white',
    lower_only=True,
    ordering='row',
    cbar_name='Similarity Index',
    title_fontsize=16,
    filter_0=True,
    **kwargs
):
    """Plots a clustered heatmap from a similarity dataframe."""
    import inspect

    default_kwargs = dict(
        vmin=0,
        vmax=sim_df.max().max(),
        cmap='viridis',
        xticklabels=True,
        yticklabels=True,
        row_cluster=True,
        dendrogram_ratio=0.05,
        cbar_pos=(-0.05, 0.4, .03, .45),
    )
    plot_params = {**default_kwargs, **kwargs}
    
    if filter_0:
        # remove any empty rows or columns
        sim_df = sim_df.loc[sim_df.any(axis=1), sim_df.any(axis=0)]
        
    if min(sim_df.shape) == 0:
        print('Empty similarity matrix')
        return
    
    is_square = sim_df.shape[0] == sim_df.shape[1]
    is_symmetric = is_square and (sim_df - sim_df.T).abs().max().max() < 1e-10
    lower_only = lower_only and is_symmetric

    if plot_params.get('row_cluster') and is_square:
        target = sim_df.fillna(0) if ordering == 'row' else sim_df.T.fillna(0)
        z = linkage(target, method='average', optimal_ordering=True)
        plot_params |= dict(row_linkage=z, col_linkage=z)

    h_allowed = inspect.signature(sns.heatmap).parameters.keys()
    h_kwargs = {k: v for k, v in plot_params.items() if k in h_allowed}

    cmap = plot_params.get('cmap')
    if isinstance(cmap, str):
        cmap = sns.color_palette(cmap, as_cmap=True).copy()
        cmap.set_bad(na_color)
        plot_params['cmap'] = cmap

    with sns.axes_style("white"):
        g = sns.clustermap(sim_df, **plot_params)

        if lower_only:
            if g.dendrogram_row is not None:
                idx = g.dendrogram_row.reordered_ind
            else:
                # If no clustering was done, use the natural index order
                idx = np.arange(len(sim_df))
            n = len(idx)
            mask = np.triu(np.ones((n, n), dtype=bool), k=1)
            g.ax_heatmap.clear()
            sns.heatmap(
                sim_df.iloc[idx, idx],
                mask=mask,
                ax=g.ax_heatmap,
                cbar=False,
                **h_kwargs
            )
            g.ax_col_dendrogram.set_visible(False)
            g.fig.suptitle(title, fontsize=title_fontsize)
        else:
            g.fig.suptitle(title, y=1.05, fontsize=title_fontsize)

        g.ax_heatmap.tick_params(
            axis='both', labelsize=12, length=4, width=1,
            bottom=True, right=True,
        )
        g.ax_heatmap.set_xlabel(xlabel, fontsize=12, labelpad=15)
        g.ax_heatmap.set_ylabel(ylabel, fontsize=12, labelpad=15)

        g.ax_cbar.yaxis.set_label_position('left')
        g.ax_cbar.tick_params(labelsize=10)
        g.ax_cbar.set_ylabel(cbar_name, rotation=90, labelpad=15, fontsize=16)

    return g


def run_similarity_analysis(
    df1,
    df2,
    group_col,
    value_col,
    df1_label='df1',
    df2_label='df2',
    metric='jaccard',
    keep_missing=False,
    self_compare=False,
    return_mtx=False,
    transpose=True,
    save_dir=None,
    **kwargs
):
    """Main entry point to calculate and plot similarities."""
    # 1. Calculate
    sim_df = calculate_pairwise_similarity(
        df1, df2, group_col, value_col, metric=metric, 
        keep_missing=keep_missing
    )
    
    if transpose:
        sim_df = sim_df.T
    
    if not kwargs.get('cbar_name') and isinstance(metric, str):
        kwargs['cbar_name'] = metric
    
    # 2. Plot
    g = plot_similarity_heatmap(
        sim_df,
        xlabel=df1_label, 
        ylabel=df2_label,
        **kwargs
    )
    if save_dir:
        g.savefig(f'{save_dir}/{df1_label}-vs-{df2_label}.svg')
    
    if self_compare:
        if g.dendrogram_row is not None:
            ordered_labels = sim_df.index[g.dendrogram_row.reordered_ind]
        else:
            ordered_labels = sim_df.index
        kwargs |= {'row_cluster': False, 'col_cluster': False}
        title = kwargs.pop('title', None)
        title_prefix = title if title else f"Self-Overlap"
        
        # Recursive-like call for self comparison if needed
        for df, label in [(df1, df1_label), (df2, df2_label)]:
            self_sim = calculate_pairwise_similarity(df, df, group_col, value_col, metric=metric)
            # force same ordering as first plot
            self_sim = self_sim.reindex(index=ordered_labels, columns=ordered_labels)
            
            g = plot_similarity_heatmap(
                self_sim, 
                xlabel=label, ylabel=label,
                title=f"Self-Overlap ({label})", 
                **kwargs
            )
            
            if save_dir:
                g.savefig(f'{save_dir}/{label}-vs-{label}.svg')

    if return_mtx:
        return sim_df


### DEPRECATED
def jaccard_matrix(
    df1,
    df2,
    group_col,
    value_col,
    df1_label='df1',
    df2_label='df2',
    ordering='row',
    self_compare=False,
    keep_missing=False,
    plot_title='Cell type marker gene overlap',
    na_color='lightgray',
    **kwargs
):
    """
    Computes Jaccard similarity between groups in two DataFrames 
    and plots a clustered heatmap.
    """
    import pandas as pd
    import numpy as np
    import seaborn as sns
    from scipy.cluster.hierarchy import linkage
    from sklearn.metrics import pairwise_distances
    
    def make_conf_matrix(df):
        return (
            pd.crosstab(df[group_col], df[value_col])
                .reindex(index=groups, columns=values, fill_value=0)
                .astype(bool)
        )

    g1, g2 = set(df1[group_col].unique()), set(df2[group_col].unique())
    groups = sorted(g1 | g2 if keep_missing else g1 & g2)
    values = set(df1[value_col].unique()) | set(df2[value_col].unique())
    
    confusion_g1 = make_conf_matrix(df1)
    confusion_g2 = make_conf_matrix(df2)
    
    # jaccard similarity
    sim_df = pd.DataFrame(
        1 - pairwise_distances(
            confusion_g1.values,
            confusion_g2.values,
            metric='jaccard',
        ),
        index=groups,
        columns=groups,
    )
    
    # build plot
    kwargs = dict(
        vmin=0,
        vmax=sim_df.max().max(),
        cmap='viridis',
        xticklabels=True, 
        yticklabels=True,
        dendrogram_ratio=0.05,
        cbar_pos=(-0.05, 0.4, .03, .45),
    ) | kwargs
    
    target = sim_df if ordering == 'row' else sim_df.T
    z = linkage(target, method='average', optimal_ordering=True)
    kwargs |= dict(
        row_linkage=z,
        col_linkage=z,
        row_cluster=True,
        col_cluster=True,
    )
    
    # set missing cell type similarities to NA
    sim_df.loc[list(set(groups) - set(df1[group_col].unique())), :] = np.nan
    sim_df.loc[:, list(set(groups) - set(df2[group_col].unique()))] = np.nan
    
    cmap = kwargs.get('cmap')
    if isinstance(cmap, str):
        cmap = sns.color_palette(cmap, as_cmap=True)
        cmap.set_bad(na_color)
        kwargs['cmap'] = cmap
    
    with sns.axes_style("white"):
        g = sns.clustermap(sim_df, **kwargs)
        
        # axes labels
        g.ax_heatmap.set_xlabel(df2_label, fontsize=16, labelpad=15)
        g.ax_heatmap.set_ylabel(df1_label, fontsize=16, labelpad=15)
        
        # axes ticks
        g.ax_heatmap.tick_params(axis='both', labelsize=14)
        
        # legend
        g.ax_cbar.yaxis.set_label_position('left')
        g.ax_cbar.set_ylabel('Jaccard Similarity', rotation=90, labelpad=15, fontsize=26)
    
        # title
        g.fig.suptitle(plot_title, y=1.05, fontsize=30)
    
    if self_compare:
        return_dfs = {f'{df1_label} vs {df2_label}': sim_df}
        for df, label in [(df1, df1_label), (df2, df2_label)]:
            _sim_df = jaccard_matrix(
                df1=df, df2=df,
                group_col=group_col,
                value_col=value_col,
                df1_label=label,
                df2_label=label,
                ordering=ordering,
                keep_missing=keep_missing,
                plot_title=f'{plot_title} ({label})',
                na_color=na_color,
                **kwargs
            )
            return_dfs['df1_label'] = _sim_df
        return return_dfs
    
    return sim_df