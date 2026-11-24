"""
Plot the run time comparison between the brute-force and scAtlasTb arms.

Reads, under <base_dir>/<arm>/<size>/rep<r>/:
    measure_total.tsv   whole run (all arms)
    measure_steps.tsv   per stage (brute force)
    snakemake.log       per job start/finish times (scAtlasTb)

Usage:
    python plot_runtime.py <base_dir> <out_dir>
"""
import re
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ARMS = ['brute_force', 'scAtlasTb_j1', 'scAtlasTb_jN']
ARM_LABELS = {
    'brute_force': 'brute force',
    'scAtlasTb_j1': 'scAtlasTb, 1 job at a time',
    'scAtlasTb_jN': 'scAtlasTb, parallel jobs',
}
ARM_COLORS = {'brute_force': '#2a78d6', 'scAtlasTb_j1': '#eb6834', 'scAtlasTb_jN': '#1baf7a'}
STAGES = ['preprocessing', 'integration', 'metrics']
STAGE_COLORS = {'preprocessing': '#86b6ef', 'integration': '#2a78d6', 'metrics': '#104281'}
INK, INK_MUTED, GRID = '#1a1a19', '#6b6a64', '#e6e5e0'

plt.rcParams.update({
    'font.size': 9,
    'axes.edgecolor': INK_MUTED,
    'axes.labelcolor': INK,
    'axes.titlesize': 10,
    'axes.titleweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'axes.axisbelow': True,
    'grid.color': GRID,
    'xtick.color': INK_MUTED,
    'ytick.color': INK_MUTED,
    'legend.frameon': False,
})


def arm_key(arm_dir):
    """scAtlasTb_j<N> with N > 1 -> scAtlasTb_jN"""
    return 'scAtlasTb_jN' if re.fullmatch(r'scAtlasTb_j([2-9]|\d\d+)', arm_dir) else arm_dir


def size_key(size):
    return np.inf if size == 'full' else int(size)


def read_runs(base_dir):
    runs = []
    for path in base_dir.glob('*/*/rep*/measure_total.tsv'):
        df = pd.read_csv(path, sep='\t').tail(1)  # last run if a directory was measured twice
        df['arm'] = arm_key(path.parts[-4])
        df['size'] = path.parts[-3]
        df['rep'] = path.parts[-2]
        df['run_dir'] = path.parent
        runs.append(df)
    df = pd.concat(runs, ignore_index=True)
    df['size'] = df['size'].astype(str)
    return df


def parse_snakemake_log(log_file):
    """Duration and stage of every job from the Snakemake log"""
    ts_pattern = re.compile(r'^\[(\w{3} \w{3} +\d+ [\d:]+ \d{4})\]$')
    jobs, finished = {}, {}
    lines = Path(log_file).read_text().splitlines()
    for i, line in enumerate(lines):
        match = ts_pattern.match(line)
        if not match or i + 1 >= len(lines):
            continue
        time = datetime.strptime(match.group(1), '%a %b %d %H:%M:%S %Y')
        nxt = lines[i + 1]
        if m := re.match(r'^Finished job (\d+)\.', nxt):
            finished[m.group(1)] = time
            continue
        # job header: "rule <name>:" ... "jobid: <id>" or "Job <id>: <message>"
        block = lines[i + 1:i + 15]
        if m := re.match(r'^Job (\d+):', nxt):
            jobid = m.group(1)
        else:
            ids = [re.search(r'jobid: (\d+)', b) for b in block]
            ids = [x.group(1) for x in ids if x]
            if not ids:
                continue
            jobid = ids[0]
        outputs = [b for b in block if b.strip().startswith('output:')]
        # module directory right under the scAtlasTb output_dir ("<out>/pipeline/<module>/...")
        stage = re.findall(r'/pipeline/(\w+)/', outputs[0])[-1] if outputs else None
        method = re.search(r'method=(\w+)', '\n'.join(block))
        jobs[jobid] = {'start': time, 'stage': stage, 'method': method.group(1) if method else None}
    rows = []
    for jobid, job in jobs.items():
        if jobid in finished and job['stage'] in STAGES:
            rows.append(job | {'seconds': (finished[jobid] - job['start']).total_seconds()})
    return pd.DataFrame(rows)


def read_stages(runs):
    """Time per stage (summed over jobs/steps) for every run"""
    rows = []
    for run in runs.itertuples():
        if run.arm == 'brute_force':
            steps = pd.read_csv(run.run_dir / 'measure_steps.tsv', sep='\t')
            steps['stage'] = steps['step'].str.split(':').str[0].map(
                {'preprocess': 'preprocessing', 'integrate': 'integration', 'metrics': 'metrics'})
            steps['method'] = np.where(steps['stage'] == 'integration', steps['step'].str.split(':').str[1], None)
            steps = steps.rename(columns={'wall_s': 'seconds'})
        else:
            log = run.run_dir / 'snakemake.log'
            if not log.exists():
                continue
            steps = parse_snakemake_log(log)
        steps = steps[['stage', 'method', 'seconds']].assign(arm=run.arm, size=run.size, rep=run.rep)
        rows.append(steps)
    return pd.concat(rows, ignore_index=True)


def grouped_bars(ax, df, value, ylabel, scale=1.0, group='size'):
    """One group per size (or other column), one bar per arm (mean over replicates), replicates as dots"""
    sizes = sorted(df[group].unique(), key=size_key if group == 'size' else str)
    arms = [a for a in ARMS if a in df['arm'].unique()]
    width = 0.8 / len(arms)
    for j, arm in enumerate(arms):
        for i, size in enumerate(sizes):
            vals = df.loc[(df['arm'] == arm) & (df[group] == size), value] / scale
            if vals.empty:
                continue
            x = i + (j - (len(arms) - 1) / 2) * width
            ax.bar(x, vals.mean(), width * 0.92, color=ARM_COLORS[arm],
                   label=ARM_LABELS[arm] if i == 0 else None)
            ax.scatter(np.full(len(vals), x), vals, s=12, color=INK, zorder=3, linewidths=0)
    if group == 'size':
        ax.set_xticks(range(len(sizes)), [f'{int(s):,}' if s != 'full' else 'full' for s in sizes])
        ax.set_xlabel('cells')
    else:
        ax.set_xticks(range(len(sizes)), sizes)
    ax.set_ylabel(ylabel)
    ax.grid(axis='x', visible=False)


def plot_totals(runs, out_dir):
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.4))
    grouped_bars(axes[0], runs, 'wall_s', 'wall time (min)', scale=60)
    axes[0].set_title('Wall time')
    runs = runs.assign(cpu_s=runs['cpu_user_s'] + runs['cpu_sys_s'])
    grouped_bars(axes[1], runs, 'cpu_s', 'CPU time (min)', scale=60)
    axes[1].set_title('CPU time')
    grouped_bars(axes[2], runs, 'peak_rss_mb', 'peak memory (GB)', scale=1024)
    axes[2].set_title('Peak memory (summed RSS)')
    grouped_bars(axes[3], runs, 'disk_actual_mb', 'disk (GB)', scale=1024)
    axes[3].set_title('Disk used by outputs')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=len(labels), bbox_to_anchor=(0.5, 1.04))
    fig.tight_layout()
    fig.savefig(out_dir / 'runtime_totals.png', dpi=200, bbox_inches='tight')
    fig.savefig(out_dir / 'runtime_totals.pdf', bbox_inches='tight')
    plt.close(fig)


def plot_stages(stages, runs, out_dir):
    """Stacked time per stage per arm, one panel per size; marker = wall time of the whole run"""
    sizes = sorted(stages['size'].unique(), key=size_key)
    fig, axes = plt.subplots(1, len(sizes), figsize=(3.6 * len(sizes) + 1, 3.6), squeeze=False)
    per_rep = stages.groupby(['arm', 'size', 'rep', 'stage'])['seconds'].sum().reset_index()
    mean = per_rep.groupby(['arm', 'size', 'stage'])['seconds'].mean().unstack('stage').reindex(columns=STAGES)
    wall = runs.groupby(['arm', 'size'])['wall_s'].mean()
    for ax, size in zip(axes[0], sizes):
        arms = [a for a in ARMS if (a, size) in mean.index]
        bottom = np.zeros(len(arms))
        for stage in STAGES:
            vals = np.array([mean.loc[(a, size), stage] for a in arms]) / 60
            vals = np.nan_to_num(vals)
            ax.bar(range(len(arms)), vals, 0.6, bottom=bottom, color=STAGE_COLORS[stage],
                   edgecolor='white', linewidth=1, label=stage)
            bottom += vals
        ax.scatter(range(len(arms)), [wall.get((a, size), np.nan) / 60 for a in arms],
                   marker='_', s=400, color=INK, linewidths=2, zorder=3, label='wall time of whole run')
        ax.set_xticks(range(len(arms)), [ARM_LABELS[a].replace(', ', ',\n') for a in arms])
        ax.set_title(f'{int(size):,} cells' if size != 'full' else 'full HLCA')
        ax.set_ylabel('summed step/job time (min)')
        ax.grid(axis='x', visible=False)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=len(labels), bbox_to_anchor=(0.5, 1.06))
    fig.tight_layout()
    fig.savefig(out_dir / 'runtime_stages.png', dpi=200, bbox_inches='tight')
    fig.savefig(out_dir / 'runtime_stages.pdf', bbox_inches='tight')
    plt.close(fig)


def plot_methods(stages, out_dir):
    """Integration time per method, incl. postprocessing, neighbors and UMAP of all its output types
    (brute force: the whole integrate step; scAtlasTb: summed time of all integration jobs of that method)"""
    df = stages[(stages['stage'] == 'integration') & stages['method'].notna()]
    df = df.groupby(['arm', 'size', 'rep', 'method'])['seconds'].sum().reset_index()
    sizes = sorted(df['size'].unique(), key=size_key)
    fig, axes = plt.subplots(1, len(sizes), figsize=(4.2 * len(sizes) + 1, 3.4), squeeze=False)
    for ax, size in zip(axes[0], sizes):
        grouped_bars(ax, df[df['size'] == size], 'seconds', 'run time (min)', scale=60, group='method')
        ax.set_title(f'Integration per method, {int(size):,} cells' if size != 'full' else 'Integration per method, full HLCA')
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=len(labels), bbox_to_anchor=(0.5, 1.06))
    fig.tight_layout()
    fig.savefig(out_dir / 'runtime_methods.png', dpi=200, bbox_inches='tight')
    fig.savefig(out_dir / 'runtime_methods.pdf', bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    base_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    runs = read_runs(base_dir)
    runs.drop(columns='run_dir').to_csv(out_dir / 'runtime_totals.tsv', sep='\t', index=False)
    stages = read_stages(runs)
    stages.to_csv(out_dir / 'runtime_steps.tsv', sep='\t', index=False)
    plot_totals(runs, out_dir)
    plot_stages(stages, runs, out_dir)
    plot_methods(stages, out_dir)
    print(f'Wrote plots to {out_dir}')
