import os
import re
import matplotlib.pyplot as plt

BENCH     = "TRANSPOSE"
spin_freq = 1024
vc_       = 4
PERCENTILES = [95, 99]

VARIANTS = {
    "baseline": "./results_cmp_baseline",
    "regional": "./results_cmp_regional",
    "dynamic":  "./results_cmp_dynamic",
}


def parse_histogram(stats_file):
    """Return (bucket_size, list of counts) from flit_latency_histogram."""
    bucket_size = None
    counts = []
    with open(stats_file) as f:
        for line in f:
            if 'flit_latency_histogram::bucket_size' in line:
                bucket_size = int(line.split()[-1])
            elif line.startswith('system.ruby.network.flit_latency_histogram |'):
                # Each bucket: "count  pct%  cum%" separated by |
                parts = line.split('|')[1:]  # skip stat name
                for p in parts:
                    p = p.strip()
                    if not p:
                        continue
                    tokens = p.split()
                    if tokens:
                        counts.append(int(tokens[0]))
    return bucket_size, counts


def percentile_from_hist(bucket_size, counts, pct):
    """Return the latency value at the given percentile."""
    total = sum(counts)
    if total == 0:
        return float('nan')
    target = total * pct / 100.0
    cumulative = 0
    for i, c in enumerate(counts):
        cumulative += c
        if cumulative >= target:
            return (i + 1) * bucket_size  # upper edge of bucket
    return len(counts) * bucket_size


def read_tail_latency(out_dir, pct):
    inj_list, lat_list = [], []
    inj = 0.02
    while True:
        d = "{}/{}/freq-{}/vc-{}/inj-{:1.2f}".format(
            out_dir, BENCH, spin_freq, vc_, inj)
        stats_file = os.path.join(d, "stats.txt")
        if not os.path.exists(stats_file):
            break
        try:
            bucket_size, counts = parse_histogram(stats_file)
            if bucket_size is None or not counts:
                raise ValueError("no histogram")
            lat = percentile_from_hist(bucket_size, counts, pct)
            if lat >= 2000:
                break
            inj_list.append(inj)
            lat_list.append(lat)
        except Exception:
            pass
        inj = round(inj + 0.02, 2)
    return inj_list, lat_list


fig, axes = plt.subplots(1, len(PERCENTILES), figsize=(12, 4), sharey=False)

for ax, pct in zip(axes, PERCENTILES):
    for label, out_dir in VARIANTS.items():
        inj, lat = read_tail_latency(out_dir, pct)
        if inj:
            ax.plot(inj, lat, marker='o', markersize=3, label=label)
    ax.set_title("P{} Flit Latency — {}".format(pct, BENCH))
    ax.set_xlabel("Injection Rate")
    ax.set_ylabel("Latency (cycles)")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("tail_latency.png", dpi=150)
plt.show()
print("Saved tail_latency.png")
