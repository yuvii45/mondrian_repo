# run_all.py

import subprocess
import os

BASE = os.path.dirname(os.path.abspath(__file__))
solver_path = os.path.join(BASE, "solver.py")

for n in range(3, 11):
    outfile = os.path.join(BASE, f"output_{n}.txt")
    print(f"\n=== Running n={n} ===")

    with open(outfile, "w") as f:
        # Start solver and stream the output
        process = subprocess.Popen(
            ["python", solver_path, str(n)],
            cwd=BASE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Read output line-by-line as the solver prints it
        for line in process.stdout:
            print(line, end="")   # show live
            f.write(line)         # save to file

        process.wait()

    print(f"=== Finished n={n}, saved to {outfile} ===\n")
