import os
import subprocess
from multiprocessing import Pool

binary = 'build/Garnet_standalone/gem5.opt'
# os.system("scons -j15 {}".format(binary))

bench_caps = ["BIT_ROTATION", "TORNADO", "TRANSPOSE", "UNIFORM_RANDOM"]
bench = ["bit_rotation", "tornado", "transpose", "uniform_random"]
file = ['64_nodes-connectivity_matrix_0-links_removed_0.txt', '256_nodes-connectivity_matrix_0-links_removed_0.txt']

routing_algorithm = ["ADAPT_RAND_", "UP_DN_", "Escape_VC_UP_DN_"]

# num_cores = [64, 256]
# num_rows = [8, 16]
num_cores = [64]
num_rows = [8]

start_injection_rate = 0.02     #DEFAULT = 0.02 (KEEP IT MULTIPLE OF 0.02)
max_injection_rate = 0.4       #DEFAULT = 1.0
inj_rate_delta = 0.06           #MAKE SURE THIS IS MULTIPLE OF 0.02 OR AT LEAST 0.01, OTHERWISE FILENAMES WILL SUCK

# start_injection_rate = 0.52


os.system('rm -rf ./results/')
os.system('mkdir -p results')
num_processes = 20              #this is the number of cores you want gem5 to run on

out_dir = './results'
cycles = 100000
vc_ = 2
stall_thresh_ = 0
rout_ = 0
spin_freq = 0

def run_sim(args):
    c, b, injection_rate = args
    if (stall_thresh_ == 0):
        cmd = ("{0:s} -d {1:s}/{2:d}/{4:s}/{3:s}/freq-{7:d}/vc-{5:d}/inj-{6:1.2f} "
            "configs/example/garnet_synth_traffic.py "
            "--topology=irregularMesh_XY --num-cpus={2:d} --num-dirs={2:d} "
            "--mesh-rows={8:d} --network=garnet2.0 --router-latency=1 "
            "--sim-cycles={9:d} --spin=1 --conf-file={10:s} "
            "--spin-file=spin_configs/SR_{10:s} --spin-freq={7:d} --spin-mult=1 "
            "--uTurn-crossbar=1 --inj-vnet=0 --vcs-per-vnet={5:d} "
            "--injectionrate={6:1.2f} --synthetic={11:s} "
            '--regional-drain --num-quadrants=4 --stall-threshold={12:d} '
            "--routing-algorithm={13:d} 2>>/tmp/gem5_errors.log").format(
                binary, out_dir, num_cores[c], bench_caps[b],
                routing_algorithm[rout_], vc_, injection_rate,
                spin_freq, num_rows[c], cycles, file[c], bench[b], stall_thresh_, rout_)
    else:
        cmd = ("{0:s} -d {1:s}/{2:d}/{4:s}/{3:s}/thresh-{12:d}/vc-{5:d}/inj-{6:1.2f} "
            "configs/example/garnet_synth_traffic.py "
            "--topology=irregularMesh_XY --num-cpus={2:d} --num-dirs={2:d} "
            "--mesh-rows={8:d} --network=garnet2.0 --router-latency=1 "
            "--sim-cycles={9:d} --spin=1 --conf-file={10:s} "
            "--spin-file=spin_configs/SR_{10:s} --spin-freq={7:d} --spin-mult=1 "
            "--uTurn-crossbar=1 --inj-vnet=0 --vcs-per-vnet={5:d} "
            "--injectionrate={6:1.2f} --synthetic={11:s} "
            '--regional-drain --num-quadrants=4 --stall-threshold={12:d} '
            '--regional-spin-file=spin_configs/SR_16_nodes-connectivity_matrix_0-links_removed_0.txt '
            "--routing-algorithm={13:d} 2>>/tmp/gem5_errors.log").format(
                binary, out_dir, num_cores[c], bench_caps[b],
                routing_algorithm[rout_], vc_, injection_rate,
                spin_freq, num_rows[c], cycles, file[c], bench[b], stall_thresh_, rout_)

    os.system(cmd)

# Build all jobs upfront
jobs = []
for c in range(len(num_cores)):
    for b in range(len(bench)):
        injection_rate = start_injection_rate
        while injection_rate <= max_injection_rate:
            jobs.append((c, b, round(injection_rate, 2)))
            injection_rate += inj_rate_delta

print("Running {} simulations across 20 cores...".format(len(jobs)))

pool = Pool(processes=num_processes)
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
                # pkt_lat = float(packet_latency)
                print("injection_rate={1:1.2f} \t Packet Latency: {0:f}".format(pkt_lat, injection_rate))
                injection_rate += inj_rate_delta
                injection_rate = round(injection_rate, 2)
            else:
                pkt_lat = 1000
