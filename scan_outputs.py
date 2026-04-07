import os
import subprocess

root = "."
search_term = "average_packet_latency"
target_dir = "vc-4"

files = []

for dirpath, dirnames, filenames in os.walk(root):
    if os.path.basename(dirpath) == target_dir:
        dirnames[:] = []  # prevent os.walk from going deeper
        print(dirpath)

        #filters to injection rate and avg packet latency as a CSV 
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
            filename = dirpath.lstrip("./").replace("/", "_") + ".txt"
            files.append(filename)
            print("making file: ", filename)
            with open(filename, "w") as f:
                f.write(stdout)

for file in files:
    #add script to plot the png here