import argparse
import os
import pickle

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-path', type=str, help='Path of the 🥒-file containing the circuits. ',
                        choices=[os.path.join("createdCircuits", f) for f in os.listdir("createdCircuits")],
                        default=[os.path.join("createdCircuits", f) for f in os.listdir("createdCircuits")][0])

    args = parser.parse_args()

    with open(args.path, "rb") as f:
        circuits = pickle.load(f)

    print(len(circuits))
    for meta, QCP_circ, qiskit_circ in circuits[:1]:
        print(meta)
        print(QCP_circ)
        qiskit_circ.draw("mpl", filename="test_circ.png")
