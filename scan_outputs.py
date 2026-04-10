import os
import subprocess
import matplotlib
matplotlib.use('Agg')  # must be before importing pyplot
import matplotlib.pyplot as plt

root = "."
search_term = "average_packet_latency"
# search_term = "max_flit_latency"
# search_term = "min_flit_latency"

target_dirs = ["vc-2", "vc-4"]
files = []

print "started scanning"


for dirpath, dirnames, filenames in os.walk(root):
    if os.path.basename(dirpath) in target_dirs:
        dirnames[:] = []
        print(dirpath)

        cmd = r"grep -nri {0} . | sed 's/\.\/inj-\([0-9.]*\)\/stats\.txt:[0-9]*:system\.ruby\.network\.average_packet_latency\s*\([0-9.]*\)\s*$/\1,\2/'".format(search_term)
        result = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=dirpath,
            shell=True
        )
        stdout, stderr = result.communicate()

        if stdout:
            # sort by injection rate
            lines = [l.strip() for l in stdout.strip().split("\n") if l.strip()]
            lines.sort(key=lambda x: float(x.split(",")[0]))

            filename = dirpath.lstrip("./").replace("/", "_") + ".txt"
            files.append(filename)
            print("making file: ", filename)
            with open(filename, "w") as f:
                f.write("\n".join(lines) + "\n")

for filepath in files:
    with open(filepath, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    x = []
    y = []
    for line in lines:
        parts = line.split(",")
        x.append(float(parts[0]))
        y.append(float(parts[1]))

    plt.plot(x, y, marker='o')
    plt.xlabel("Injection Rate")
    plt.ylabel("Average Packet Latency")
    plt.title(filepath.replace(".txt", ""))
    plt.grid(True)
    plt.ylim(0, 15000)
    plt.xlim(0, 1)

    pngname = os.path.splitext(filepath)[0] + ".png"
    plt.savefig(pngname)
    plt.clf()
    print("saved plot: ", pngname)