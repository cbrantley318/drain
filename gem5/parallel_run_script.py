import os
import subprocess
from multiprocessing import Pool

binary = 'build/Garnet_standalone/gem5.opt'
os.system("scons -j15 {}".format(binary))

bench_caps = ["BIT_ROTATION", "SHUFFLE", "TRANSPOSE"]
bench = ["bit_rotation", "shuffle", "transpose"]
file = ['64_nodes-connectivity_matrix_0-links_removed_0.txt', '256_nodes-connectivity_matrix_0-links_removed_0.txt']

routing_algorithm = ["ADAPT_RAND_", "UP_DN_", "Escape_VC_UP_DN_"]

num_cores = [64, 256]
num_rows = [8, 16]

os.system('rm -rf ./results')
os.system('mkdir results')

out_dir = './results'
cycles = 100000
vc_ = 4
rout_ = 0
spin_freq = 1024

def run_sim(args):
    c, b, injection_rate = args
    cmd = ("{0:s} -d {1:s}/{2:d}/{4:s}/{3:s}/freq-{7:d}/vc-{5:d}/inj-{6:1.2f} "
           "configs/example/garnet_synth_traffic.py "
           "--topology=irregularMesh_XY --num-cpus={2:d} --num-dirs={2:d} "
           "--mesh-rows={8:d} --network=garnet2.0 --router-latency=1 "
           "--sim-cycles={9:d} --spin=1 --conf-file={10:s} "
           "--spin-file=spin_configs/SR_{10:s} --spin-freq={7:d} --spin-mult=1 "
           "--uTurn-crossbar=1 --inj-vnet=0 --vcs-per-vnet={5:d} "
           "--injectionrate={6:1.2f} --synthetic={11:s} "
           "--routing-algorithm={12:d} 2>/dev/null").format(
               binary, out_dir, num_cores[c], bench_caps[b],
               routing_algorithm[rout_], vc_, injection_rate,
               spin_freq, num_rows[c], cycles, file[c], bench[b], rout_)
    os.system(cmd)

# Build all jobs upfront
jobs = []
for c in range(len(num_cores)):
    for b in range(len(bench)):
        injection_rate = 0.02
        while injection_rate <= 1.0:
            jobs.append((c, b, round(injection_rate, 2)))
            injection_rate += 0.02

print("Running {} simulations across 20 cores...".format(len(jobs)))

pool = Pool(processes=20)
pool.map(run_sim, jobs)
pool.close()
pool.join()

print("All simulations done. Extracting results...")

# Extract results
for c in range(len(num_cores)):
    for b in range(len(bench)):
        print("cores: {} benchmark: {} vc-{}".format(num_cores[c], bench_caps[b], vc_))
        pkt_lat = 0
        injection_rate = 0.02
        while pkt_lat < 200.00:
            output_dir = ("{0:s}/{1:d}/{3:s}/{2:s}/freq-{6:d}/vc-{4:d}/inj-{5:1.2f}".format(
                out_dir, num_cores[c], bench_caps[b], routing_algorithm[rout_],
                vc_, injection_rate, spin_freq))

            if os.path.exists(output_dir):
                packet_latency = subprocess.check_output(
                    "grep -nri average_flit_latency {0:s} | sed 's/.*system.ruby.network.average_flit_latency\s*//'".format(output_dir),
                    shell=True)
                pkt_lat = float(packet_latency)
                print("injection_rate={1:1.2f} \t Packet Latency: {0:f}".format(pkt_lat, injection_rate))
                injection_rate += 0.02
            else:
                pkt_lat = 1000
