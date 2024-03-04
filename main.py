import argparse
import os
import pickle
from tqdm import tqdm

from MPS.simulator import MPS_Simulator

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str,
                        help='Path of the 🥒-file containing the circuits. ',
                        choices=[os.path.join("createdCircuits", f) for f in os.listdir("createdCircuits")] + os.listdir("createdCircuits"),
                        default=os.listdir("createdCircuits")[0])
    parser.add_argument('--threshold', type=float, default=0,
                        help='The maximal truncation error for the simulation.')
    parser.add_argument('--chi', type=float, default=None,
                        help='The 𝓧 value of the Simulation. Number of singual vaulues to keep.')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        if os.path.exists(alternative := os.path.join("createdCircuits", args.path)):
            args.path = alternative
        else:
            raise FileNotFoundError(f"There is no file called {args.path}")

    with open(args.path, "rb") as f:
        circuits = pickle.load(f)

    for meta, QCP_circ, qiskit_circ in tqdm(circuits[:1],
                                            total=len(circuits),
                                            desc="Simulating circuits",
                                            ncols=150):
        # filename = os.path.join("createdImages", f"qiskit_circ_{time.strftime('%Y%m%d-%H%M%S')}.png") \
        #     if len(circuits) > 1 else "output.png"
        # qiskit_circ.draw("mpl", filename=filename)

        mps = MPS_Simulator(circ=QCP_circ, threshold=args.threshold, 𝓧=args.chi, show_progress_bar=True, circ_name="./trash")
        mps.iterate_circ()
        print(mps.get_result())
