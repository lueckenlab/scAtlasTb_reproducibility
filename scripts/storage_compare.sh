#!/usr/bin/env bash
# storage_compare — compare actual vs symlink-expanded disk usage by subfolder
# Usage: storage_compare [directory] [depth] [output.tsv]

set -euo pipefail

DIR=${1:-.}
DEPTH=${2:-1}
TSV_OUT=${3:-storage_compare_$(date +%Y%m%d_%H%M%S).tsv}

# ── helpers ──────────────────────────────────────────────────────────────────

die() { echo "error: $*" >&2; exit 1; }
hr()  { printf '%.0s─' $(seq 1 72); echo; }

bytes_to_human() {
  local b=$1
  if   (( b >= 1073741824 )); then printf "%.1fG" "$(echo "scale=1; $b/1073741824" | bc)"
  elif (( b >= 1048576 ));    then printf "%.1fM" "$(echo "scale=1; $b/1048576"    | bc)"
  elif (( b >= 1024 ));       then printf "%.1fK" "$(echo "scale=1; $b/1024"       | bc)"
  else                             printf "%dB"   "$b"
  fi
}

# ── validation ───────────────────────────────────────────────────────────────

[[ -d "$DIR" ]] || die "'$DIR' is not a directory"
command -v bc &>/dev/null || die "bc is required"

# ── single-pass data collection ──────────────────────────────────────────────
# find -printf "%s %P" reads sizes from inodes directly — no du subprocess per file.
# Two passes of find: one following symlinks (expanded), one not (actual).
# awk aggregates both into associative arrays keyed by subfolder.

collect() {
  local follow=$1  # "-follow" or ""
  find "$DIR" $follow -type f -printf "%s\t%P\n" 2>/dev/null
}

parse() {
  awk -v depth="$DEPTH" -v dir="$DIR" '
    {
      size = $1
      path = substr($0, index($0, $2))
      n = split(path, parts, "/")
      if (n >= depth) {
        key = parts[1]
        for (i = 2; i <= depth; i++) key = key "/" parts[i]
      } else {
        key = path
      }
      sizes[key] += size
    }
    END { for (k in sizes) print dir "/" k "\t" sizes[k] }
  '
}

# collect both passes, sort and join on subfolder name
join_data() {
  join -t $'\t' -a1 -a2 -e 0 -o 1.1,1.2,2.2 \
    <(collect ""        | parse | sort) \
    <(collect "-follow" | parse | sort)
}

# ── single pass: collect data, tee to tsv, render stdout ─────────────────────

echo "folder	actual_bytes	expanded_bytes	ratio" > "$TSV_OUT"

echo
echo "  storage_compare  │  $DIR  (depth $DEPTH)"
hr
printf "  %-42s  %8s  %10s  %6s\n" "folder" "actual" "expanded" "ratio"
hr

total_actual=0
total_expanded=0

while IFS=$'\t' read -r subdir actual expanded; do
  total_actual=$(( total_actual + actual ))
  total_expanded=$(( total_expanded + expanded ))
  ratio=$(echo "scale=2; if ($actual > 0) $expanded / $actual else 0" | bc)

  # write raw bytes to tsv
  printf "%s\t%s\t%s\t%s\n" "$subdir" "$actual" "$expanded" "$ratio" >> "$TSV_OUT"

  # pretty-print to stdout
  printf "  %-42s  %8s  %10s  %5sx\n" \
    "$subdir" \
    "$(bytes_to_human "$actual")" \
    "$(bytes_to_human "$expanded")" \
    "$ratio"

done < <(join_data | sort)

total_ratio=$(echo "scale=2; if ($total_actual > 0) $total_expanded / $total_actual else 0" | bc)

# tsv total row
printf "TOTAL\t%s\t%s\t%s\n" "$total_actual" "$total_expanded" "$total_ratio" >> "$TSV_OUT"

# stdout total row
hr
printf "  %-42s  %8s  %10s  %5sx\n" \
  "TOTAL" \
  "$(bytes_to_human "$total_actual")" \
  "$(bytes_to_human "$total_expanded")" \
  "$total_ratio"
hr
echo
echo "  TSV saved to: $TSV_OUT"
echo