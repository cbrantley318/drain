import os
import re
import sys

def parse_tail_latency(stats_file):
    """Extract p95, p99, max, and mean latency from a stats.txt file."""
    with open(stats_file, 'r') as f:
        content = f.read()

    # Extract mean
    mean_match = re.search(r'flit_latency_histogram::mean\s+([\d.]+)', content)
    max_match  = re.search(r'max_flit_latency\s+(\d+)', content)
    size_match = re.search(r'flit_latency_histogram::bucket_size\s+(\d+)', content)
    hist_match = re.search(r'flit_latency_histogram \|(.+)', content)

    if not all([mean_match, max_match, size_match, hist_match]):
        return None

    mean       = float(mean_match.group(1))
    max_lat    = int(max_match.group(1))
    bucket_size = int(size_match.group(1))

    # Parse histogram buckets: each entry is "count  pct%  cum_pct%"
    buckets = re.findall(r'(\d+)\s+[\d.]+%\s+([\d.]+)%', hist_match.group(1))

    p95 = p99 = None
    for i, (count, cum_pct) in enumerate(buckets):
        cum = float(cum_pct)
        lat = (i + 1) * bucket_size  # upper bound of bucket
        if p95 is None and cum >= 95.0:
            p95 = lat
        if p99 is None and cum >= 99.0:
            p99 = lat
            break

    return {'mean': mean, 'p95': p95, 'p99': p99, 'max': max_lat}


def scan_results(results_dir):
    print("{:<12} {:<12} {:<8} {:<8} {:<8} {:<8}".format(
        'benchmark', 'inj_rate', 'mean', 'p95', 'p99', 'max'))
    print('-' * 60)

    for root, dirs, files in os.walk(results_dir):
        if 'stats.txt' in files:
            stats_file = os.path.join(root, 'stats.txt')
            result = parse_tail_latency(stats_file)
            if result is None:
                continue

            # Extract benchmark and injection rate from path
            parts = root.split('/')
            bench = next((p for p in parts if p in ['BIT_ROTATION', 'SHUFFLE', 'TRANSPOSE']), '?')
            inj   = next((p for p in parts if p.startswith('inj-')), '?').replace('inj-', '')

            print("{:<12} {:<12} {:<8.2f} {:<8} {:<8} {:<8}".format(
                bench, inj,
                result['mean'],
                result['p95'] if result['p95'] else '?',
                result['p99'] if result['p99'] else '?',
                result['max']))


if __name__ == '__main__':
    results_dir = sys.argv[1] if len(sys.argv) > 1 else './results'
    scan_results(results_dir)
