import argparse
import os
import pickle
from collections import defaultdict
from tqdm import tqdm

from DisCoCat import DisCoCat
from helpers.circuit_preparation import qiskitCirc2qcp

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates all circuits of a dataset. Saves a 🥒-file in the format '
                                                 'tuple((sentence, label), QCP-Circuit, qiskit-circuit))')
    parser.add_argument('--dataset', type=str, help='Wich dataset to use for creating the circuits.',
                        default="10_animals_plants",
                        choices=[f.split(".")[0] for f in os.listdir("Data")] + os.listdir("Data"),
                        required=False)
    parser.add_argument('--ansatz', type=str, help='What Ansatz to use for the ciruits.',
                        default="iqp", choices=["iqp", "sim14", "sim15", "StrongEnt", "se"], required=False)
    parser.add_argument('--layers', type=int, help='How many layers to use for the Ansatz.',
                        default=1, required=False)
    parser.add_argument('--q_s', type=int, help='How many Qubits for sentences.', default=1, required=False)
    parser.add_argument('--q_n', type=int, help='How many Qubits for nouns.', default=1, required=False)
    parser.add_argument('--q_p', type=int, help='How many Qubits for prepositional phrases.', default=1, required=False)
    parser.add_argument('--filename', type=str, help='What filename to save the 🥒-file')
    args = parser.parse_args()

    args.dataset = args.dataset.split(".")[0]

    d = DisCoCat(dataset_name=args.dataset,
                 ansatz=args.ansatz,
                 n_layers=args.layers,
                 q_s=args.q_s,
                 q_n=args.q_n,
                 q_p=args.q_p)

    result = []
    for meta, circ in tqdm(d.circuits,
                           total=len(d.circuits),
                           desc="Translating Qiskit to QCP",
                           ncols=150):
        result.append((meta, qiskitCirc2qcp(circ), circ))

    if not args.filename:
        args.filename = f"{args.dataset}-{args.ansatz}_{args.layers}_{args.q_s}_{args.q_n}_{args.q_n}.pkl"

    with open(os.path.join("createdCircuits", args.filename), "wb") as f:
        print("Saving to", os.path.join("createdCircuits", args.filename))
        pickle.dump(result, file=f)
