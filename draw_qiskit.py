import argparse
import os
import pickle
import time

from tqdm import tqdm

from create_circuits import load_circuits

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str,
                        help='Path of the 🥒-file containing the circuits. ',
                        choices=[os.path.join("createdCircuits", f) for f in os.listdir("createdCircuits")] + os.listdir("createdCircuits"),
                        required=True)
    parser.add_argument("--max_images", type=int,
                        help="Maximum number of images to generate. For generating all images type 0.",
                        default=10)
    args = parser.parse_args()

    if not os.path.exists("createdImages/"): os.mkdir("createdImages/")

    if not os.path.exists(args.path):
        if os.path.exists(alternative := os.path.join("createdCircuits", args.path)):
            args.path = alternative
        else:
            raise FileNotFoundError(f"There is no file called {args.path}")

    circuits = load_circuits(args.path)

    if args.max_images == 0:
        args.max_images = len(circuits)
    args.max_images = min(args.max_images, len(circuits))

    for meta, QCP_circ, qiskit_circ in circuits:
        filename = os.path.join("createdImages", f"qiskit_circ_{time.strftime('%Y%m%d-%H%M%S')}.png") \
            if len(circuits) > 1 else "circ.png"
        qiskit_circ.draw("mpl", filename=filename)
