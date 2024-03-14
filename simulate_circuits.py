import argparse
import os
import pickle
import time
from datetime import timedelta

from tqdm import tqdm

from MPS.simulator import MPS_Simulator

META_FILE = ""


def write_meta(input: str):
    global META_FILE
    if not META_FILE: META_FILE = os.path.join(args.out_dir, time.strftime('%Y%m%d-%H%M%S_Meta.txt'))
    with open(META_FILE, "a") as f:
        f.write(input)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('simulator', choices=['mps'], default="mps", help="What simulator to use.")
    parser.add_argument('--file', type=str,
                        help='Path of the 🥒-file containing the circuits. ',
                        choices=[os.path.join("createdCircuits", f) for f in
                                 os.listdir("createdCircuits")] + os.listdir("createdCircuits"),
                        default=os.listdir("createdCircuits")[0])
    parser.add_argument('--fidelity', type=float, default=None,
                        help='The maximal truncation error for the simulation. (Type 0 to deactivate)')
    parser.add_argument('--chi', type=int, default=None,
                        help='The 𝓧 value of the Simulation. Number of singular values to keep. (Type 0 to deactivate)')
    args = parser.parse_args()

    if os.path.exists(path := os.path.join("createdCircuits", os.path.basename(args.file))):
        args.path = path
        args.file_name = os.path.basename(args.path).split(".")[0]
    else:
        raise FileNotFoundError(f"There is no file called {args.path}")

    if not os.path.isdir("createdSimulations"): os.mkdir("createdSimulations")
    args.out_dir = os.path.join("createdSimulations", args.file_name)
    if not os.path.isdir(args.out_dir): os.mkdir(args.out_dir)

    with open(args.path, "rb") as f:
        circuits = pickle.load(f)

    write_meta(time.strftime(
        f"""
%m.%d.-%H:%M - Starting job {os.path.basename(args.path)}
    Fidelity: {args.fidelity}
    Chi: {args.chi}
______________________________________________________________
"""
    ), )
    start_time = time.perf_counter()

    for meta, QCP_circ, qiskit_circ in tqdm(circuits,
                                            total=len(circuits),
                                            desc="Simulating circuits",
                                            ncols=150):
        mps = MPS_Simulator(circ=QCP_circ, fidelity=args.fidelity, 𝓧=args.chi, show_progress_bar=False,
                            circ_name="./trash")
        mps.iterate_circ()

        with open(os.path.join(args.out_dir, time.strftime('c-%Y%m%d-%H%M%S.pkl')), "wb") as f:
            pickle.dump((mps, meta), f)
        write_meta(time.strftime(f"%m.%d.-%H:%M - Simulated circuit {meta}\n"))

    end_meta = "______________________________________________________________\n"
    end_meta += time.strftime(f"%m.%d.-%H:%M - Completed job {os.path.basename(args.path)}\n")
    elapsed_time = time.perf_counter() - start_time
    end_meta += f"Total elapsed Time: {timedelta(seconds=elapsed_time)}\n"
    end_meta += f"Average time per circuit: {timedelta(seconds=elapsed_time / len(circuits))}\n"
    write_meta(end_meta)
