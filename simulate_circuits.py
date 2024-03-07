import argparse
import os
import pickle
import time
from datetime import timedelta

from tqdm import tqdm

from MPS.simulator import MPS_Simulator

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('simulator', choices=['mps'], default="mps", help="What simulator to use.")
    parser.add_argument('--file', type=str,
                        help='Path of the 🥒-file containing the circuits. ',
                        choices=[os.path.join("createdCircuits", f) for f in os.listdir("createdCircuits")] + os.listdir("createdCircuits"),
                        default=os.listdir("createdCircuits")[0])
    parser.add_argument('--threshold', type=float, default=0,
                        help='The maximal truncation error for the simulation. (Type 0 to deactivate)')
    parser.add_argument('--chi', type=float, default=None,
                        help='The 𝓧 value of the Simulation. Number of singular values to keep. (Type 0 to deactivate)')
    args = parser.parse_args()

    if os.path.exists(path := os.path.join("createdCircuits", os.path.basename(args.file))):
        args.path = path
        args.file_name = os.path.basename(args.path).split(".")[0]
    else:
        raise FileNotFoundError(f"There is no file called {args.path}")

    with open(args.path, "rb") as f:
        circuits = pickle.load(f)

    job_meta = time.strftime(
            f"""
%m.%d.-%H:%M - Starting job {os.path.basename(args.path)}
    Threshold: {args.threshold}
    Chi:{args.chi}
______________________________________________________________
"""
    )
    start_time = time.perf_counter()

    for meta, QCP_circ, qiskit_circ in tqdm(circuits,
                                            total=len(circuits),
                                            desc="Simulating circuits",
                                            ncols=150):
        mps = MPS_Simulator(circ=QCP_circ, threshold=args.threshold, 𝓧=args.chi, show_progress_bar=False, circ_name="./trash")
        mps.iterate_circ()

        o_filename = args.file_name + time.strftime('%Y%m%d-%H%M%S.pkl')
        with open(os.path.join("createdOutputs", o_filename), "wb") as f:
            pickle.dump(mps.get_result(), f)
        job_meta += time.strftime(f"%m.%d.-%H:%M - Simulated circuit {meta}\n")

    job_meta += "______________________________________________________________\n"
    job_meta += time.strftime(f"%m.%d.-%H:%M - Completed job {os.path.basename(args.path)}\n")
    elapsed_time = time.perf_counter() - start_time
    job_meta += f"Total elapsed Time: {timedelta(seconds=elapsed_time)}\n"
    job_meta += f"Average time per circuit: {timedelta(seconds=elapsed_time/len(circuits))}\n"

    if not os.path.exists(new_dir := os.path.join("createdOutputs", "Meta")): os.mkdir(new_dir)
    with open(os.path.join("createdOutputs", "Meta", args.file_name + time.strftime('%Y%m%d-%H%M%S.txt')), "w") as f:
        f.write(job_meta)

