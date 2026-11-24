"""
Run a command and record its resource usage, including all child processes.

Samples the process tree every --interval seconds (psutil) and appends one summary
row to --summary. Peak RSS is the peak of the summed RSS over the whole tree, i.e. the
memory the node needs (for parallel Snakemake jobs this adds up concurrent jobs).
CPU time comes from getrusage(RUSAGE_CHILDREN) (all reaped descendants). I/O bytes are
summed over every process seen, using its last sample (very short-lived processes may be missed).
Optionally records the on-disk size of --disk-dir after the command finishes.

Usage:
    python measure.py --summary runs.tsv --label arm=brute_force size=50000 rep=1 step=preprocess \
        [--disk-dir DIR] [--timeseries ts.tsv] -- <command ...>
"""
import argparse
import csv
import os
import resource
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil

MB = 1024 ** 2


def tree(proc):
    try:
        return [proc] + proc.children(recursive=True)
    except psutil.NoSuchProcess:
        return []


def disk_usage(directory):
    """Bytes on disk without following symlinks (actual) and following them (expanded)."""
    actual, expanded = 0, 0
    seen = set()
    for root, dirs, files in os.walk(directory, followlinks=True):
        for name in files:
            path = os.path.join(root, name)
            try:
                st = os.stat(path)
            except FileNotFoundError:
                continue
            expanded += st.st_size
            real = os.path.realpath(path)
            if real.startswith(os.path.realpath(directory)) and (st.st_dev, st.st_ino) not in seen:
                seen.add((st.st_dev, st.st_ino))
                actual += st.st_size
    return actual, expanded


parser = argparse.ArgumentParser()
parser.add_argument('--summary', required=True)
parser.add_argument('--label', nargs='*', default=[], help='key=value pairs added to the row')
parser.add_argument('--disk-dir', default=None)
parser.add_argument('--timeseries', default=None)
parser.add_argument('--interval', type=float, default=1.0)
parser.add_argument('command', nargs=argparse.REMAINDER)
args = parser.parse_args()

command = args.command[1:] if args.command[:1] == ['--'] else args.command
assert command, 'no command given'
labels = dict(kv.split('=', 1) for kv in args.label)

start = time.time()
start_iso = datetime.now().isoformat(timespec='seconds')
popen = subprocess.Popen(command)
root = psutil.Process(popen.pid)

last = {}  # (pid, create_time) -> (read_bytes, write_bytes) at last sample
peak_rss = 0
ts_rows = []

while popen.poll() is None:
    rss = 0
    for p in tree(root):
        try:
            with p.oneshot():
                rss += p.memory_info().rss
                io = p.io_counters()
                last[(p.pid, p.create_time())] = (io.read_bytes, io.write_bytes)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    peak_rss = max(peak_rss, rss)
    if args.timeseries:
        ts_rows.append((round(time.time() - start, 1), round(rss / MB, 1)))
    time.sleep(args.interval)

exit_code = popen.returncode
wall = time.time() - start
usage = resource.getrusage(resource.RUSAGE_CHILDREN)
read_bytes, write_bytes = (sum(v[i] for v in last.values()) for i in range(2))

row = labels | {
    'host': socket.gethostname(),
    'start': start_iso,
    'exit_code': exit_code,
    'wall_s': round(wall, 1),
    'cpu_user_s': round(usage.ru_utime, 1),
    'cpu_sys_s': round(usage.ru_stime, 1),
    'peak_rss_mb': round(peak_rss / MB, 1),
    'read_mb': round(read_bytes / MB, 1),
    'write_mb': round(write_bytes / MB, 1),
}
if args.disk_dir and Path(args.disk_dir).exists():
    actual, expanded = disk_usage(args.disk_dir)
    row |= {'disk_actual_mb': round(actual / MB, 1), 'disk_expanded_mb': round(expanded / MB, 1)}

summary = Path(args.summary)
summary.parent.mkdir(parents=True, exist_ok=True)
write_header = not summary.exists()
with open(summary, 'a', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(row.keys()), delimiter='\t', extrasaction='ignore')
    if write_header:
        writer.writeheader()
    writer.writerow(row)

if args.timeseries:
    with open(args.timeseries, 'w') as f:
        f.write('t_s\trss_mb\n')
        f.writelines(f'{t}\t{r}\n' for t, r in ts_rows)

print(f'[measure] {labels} wall={row["wall_s"]}s peak_rss={row["peak_rss_mb"]}MB exit={exit_code}', file=sys.stderr)
sys.exit(exit_code)
