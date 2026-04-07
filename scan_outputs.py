import os
import subprocess

root = "."
search_term = "average_packet_latency"
target_dir = "vc-4"

for dirpath, dirnames, filenames in os.walk(root):
    if os.path.basename(dirpath) == target_dir:
        dirnames[:] = []  # prevent os.walk from going deeper
        result = subprocess.Popen(
            ["grep", "-nri", search_term, "."],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=dirpath
        )
        stdout, stderr = result.communicate()
        if stdout:
            filename = dirpath.lstrip("./").replace("/", "_") + ".txt"
            with open(filename, "w") as f:
                f.write(stdout)