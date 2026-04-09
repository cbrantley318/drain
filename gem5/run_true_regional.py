import os
import subprocess
import multiprocessing

binary          = 'build/Garnet_standalone/gem5_true_regional.opt'
conf_file       = '64_nodes-connectivity_matrix_0-links_removed_0.txt'
out_dir         = './results_cmp_true_regional'
stall_threshold = 100

num_cores = 64
num_rows  = 8
cycles    = 100000
vc_       = 4
spin_freq = 100   # cooldown after each drain (cycles)

inj_rates = [round(0.05 * i, 2) for i in range(1, 11)]  # 0.05 to 0.50

os.system('rm -rf {0} && mkdir -p {0}'.format(out_dir))


def run_one(inj):
    odir = '{}/TRANSPOSE/freq-{}/vc-{}/inj-{:.2f}'.format(
        out_dir, spin_freq, vc_, inj)
    os.makedirs(odir)

    os.system(
        '{bin} -d {odir} configs/example/garnet_synth_traffic.py '
        '--topology=irregularMesh_XY --num-cpus={nc} --num-dirs={nc} '
        '--mesh-rows={nr} --network=garnet2.0 --router-latency=1 '
        '--sim-cycles={cyc} --spin=1 --conf-file={cf} '
        '--spin-file=spin_configs/SR_{cf} '
        '--spin-freq={freq} --spin-mult=1 '
        '--uTurn-crossbar=1 --inj-vnet=0 --vcs-per-vnet={vc} '
        '--injectionrate={inj:.2f} --synthetic=transpose '
        '--routing-algorithm=0 '
        '--regional-drain --num-quadrants=4 --stall-threshold={st} '
        '--regional-spin-file=spin_configs/SR_16_nodes-connectivity_matrix_0-links_removed_0.txt '
        '2>/dev/null'.format(
            bin=binary, odir=odir, nc=num_cores, nr=num_rows,
            cyc=cycles, cf=conf_file, freq=spin_freq,
            vc=vc_, inj=inj, st=stall_threshold))

    try:
        out = subprocess.check_output(
            "grep -ri average_flit_latency {} | "
            "sed 's/.*average_flit_latency[[:space:]]*//'".format(odir),
            shell=True)
        lat = float(out.strip())
    except Exception:
        lat = -1.0

    try:
        out2 = subprocess.check_output(
            "grep -ri q_drain_count {} | head -1".format(odir),
            shell=True)
        drains = out2.strip().decode()
    except Exception:
        drains = "n/a"

    print('inj={:.2f}  lat={:.2f}  drains={}'.format(inj, lat, drains))
    return (inj, lat)


num_workers = max(1, multiprocessing.cpu_count() - 1)
pool = multiprocessing.Pool(num_workers)
pool.map(run_one, inj_rates)
pool.close()
pool.join()
