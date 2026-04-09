# Simulation Results Summary

## Configuration
- **Topology**: Irregular Mesh XY, 64 nodes (8×8), `64_nodes-connectivity_matrix_0-links_removed_0.txt`
- **Traffic**: TRANSPOSE synthetic
- **Sim cycles**: 100,000
- **VCs per vnet**: 4
- **spin_freq**: 1024 (epoch / cooldown length)
- **spin_mult**: 1

## Variants
| Variant | Binary | Key param |
|---------|--------|-----------|
| Baseline | `gem5_baseline.opt` | Fixed epoch drain every 1024 cycles |
| Regional (old) | `gem5_regional.opt` | VC occupancy threshold = 50% per quadrant |
| Dynamic | `gem5_dynamic.opt` | Stall-triggered: drain if any flit waits > 100 cycles, cooldown = 1024 cycles |

| Regional (new) | `gem5_regional_new.opt` | Stall-triggered per-quadrant: drain if any flit waits > 100 cycles, cooldown = 100 cycles |

---

## Average Flit Latency (cycles)

### Old variants (spin_freq=1024, inj 0.02–0.60)

| Inj Rate | Baseline | Regional (old) | Dynamic | Regional vs Baseline |
|----------|----------|----------------|---------|----------------------|
| 0.02 | 15.63 | 15.58 | 15.63 | -0.36% |
| 0.04 | 15.72 | 15.67 | 15.72 | -0.36% |
| 0.06 | 15.82 | 15.77 | 15.82 | -0.35% |
| 0.08 | 15.93 | 15.87 | 15.93 | -0.35% |
| 0.10 | 16.06 | 16.00 | 16.06 | -0.35% |
| 0.12 | 16.22 | 16.17 | 16.22 | -0.34% |
| 0.14 | 16.42 | 16.36 | 16.42 | -0.38% |
| 0.16 | 16.66 | 16.60 | 16.66 | -0.37% |
| 0.18 | 16.97 | 16.90 | 16.96 | -0.40% |
| 0.20 | 17.35 | 17.28 | 17.35 | -0.41% |
| 0.22 | 17.89 | 17.81 | 17.89 | -0.48% |
| 0.24 | 18.83 | 18.72 | 18.83 | -0.60% |
| 0.26 | 22.04 | 21.73 | 22.05 | -1.41% |
| **0.28** | **368.30** | **358.31** | **369.14** | **-2.71%** |
| 0.30 | 555.86 | 543.50 | 548.52 | -2.22% |
| 0.32 | 706.87 | 700.77 | 702.42 | -0.86% |
| 0.34 | 883.56 | 872.14 | 883.68 | -1.29% |
| 0.36 | 1122.82 | 1121.48 | 1135.86 | -0.12% |
| 0.38 | 1232.25 | 1229.22 | 1232.87 | -0.25% |
| 0.40 | 1363.28 | 1354.88 | 1362.04 | -0.62% |
| 0.42 | 1483.67 | 1481.19 | 1483.56 | -0.17% |
| 0.44 | 1586.83 | 1579.30 | 1584.25 | -0.47% |
| 0.46 | 1704.73 | 1693.13 | 1714.08 | -0.68% |
| 0.48 | 1867.22 | 1861.77 | 1886.62 | -0.29% |
| 0.50 | 1953.02 | 1945.50 | 1951.02 | -0.38% |
| 0.52 | 2023.37 | 2017.79 | 2022.04 | -0.28% |
| 0.54 | 2085.63 | 2078.86 | 2086.30 | -0.32% |
| 0.56 | 2093.49 | 2089.48 | 2092.37 | -0.19% |
| 0.58 | 2111.12 | 2105.49 | 2108.47 | -0.27% |
| 0.60 | 2133.34 | 2125.53 | 2136.89 | -0.37% |

**Saturation point**: all three variants saturate at **inj = 0.28**

---

### Regional (new) — stall-triggered (stall_threshold=100, cooldown=100, inj 0.05–0.50)

| Inj Rate | Avg Flit Latency | Total Drains |
|----------|-----------------|--------------|
| 0.05 | 15.71 | 0 |
| 0.10 | 16.00 | 0 |
| 0.15 | 16.48 | 0 |
| 0.20 | 17.28 | 0 |
| 0.25 | 19.64 | 102 |
| **0.30** | **694.25** | **5793** |
| 0.35 | 1296.26 | 6798 |
| 0.40 | 1669.27 | 8484 |
| 0.45 | 2066.57 | 8727 |
| 0.50 | 2248.37 | 8850 |

**Saturation point**: between inj = 0.25 and 0.30 (similar to baseline)

**Key observation**: 0 drains at inj ≤ 0.20 — no flit ever stalls > 100 cycles at light load,
so the network runs completely drain-free. The baseline always performs 291 drains regardless.

## Total Drains (`total_DRAIN_spins`)
- Baseline: **291** drains per simulation (fixed, every 1024 cycles over 100k cycles)
- Dynamic: **291** drains (stall-triggered but cooldown = 1024, same rate)
- Regional (old): stat not available in that binary

## Key Observations
1. **Regional drain consistently lowers latency** by ~0.3–1.4% before saturation
2. **Dynamic drain ≈ baseline** — stall-triggered with 1024-cycle cooldown fires at same rate as fixed epoch
3. All three **saturate at the same injection rate** (0.28) — regional drain does not extend throughput
4. Biggest regional improvement is around saturation point (inj=0.26–0.28)
