import argparse
import os
import pickle
from collections import defaultdict
from tqdm import tqdm

from DisCoCat import DisCoCat
from helpers.circuit_preparation import qiskitCirc2qcp


def create_circuits(dataset,
                    syntax, 
                    ansatz,
                    layers,
                    q_s,
                    q_n,
                    q_pp,
                    draw=False,
                    filename=None):

    dataset = dataset.split(".")[0]

    if not os.path.isdir("createdCircuits"): os.mkdir("createdCircuits")

    d = DisCoCat(syntax_model=syntax, 
                 dataset_name=dataset,
                 ansatz=ansatz,
                 n_layers=layers,
                 q_s=q_s,
                 q_n=q_n,
                 q_pp=q_pp)

    if draw is True:
        d.string_diagrams[0].draw(path="string.png")
        d.circuits[0][1].draw("mpl", filename="circ.png")
        d.circuit_diagrams[0].draw(path="circ_dia.png")

    result = []
    for meta, circ in tqdm(d.circuits,
                           total=len(d.circuits),
                           desc="Translating Qiskit to QCP",
                           ncols=150):
        result.append((meta, qiskitCirc2qcp(circ), circ))

    if not filename:
        filename = f"{dataset}-{ansatz}-{syntax}_{layers}_{q_s}_{q_n}_{q_n}.pkl"

    with open(os.path.join("createdCircuits", filename), "wb") as f:
        print("Saving to", os.path.join("createdCircuits", args.filename))
        pickle.dump(result, file=f)

    return filename



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates all circuits of a dataset. Saves a 🥒-file in the format '
                                                 'tuple((sentence, label), QCP-Circuit, qiskit-circuit))')
    parser.add_argument('--syntax', type=str, help="What syntax model should be used. Pregroup, bag-of-words or sequential.", default="pregroup", 
                        choices=["pregroup", "pre", "bobcat",
                                 "bow", "bagofwords", "bag-of-words",
                                 "seq", "sequential"])
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
    parser.add_argument('--q_pp', type=int, help='How many Qubits for prepositional phrases.', default=1, required=False)
    parser.add_argument('--filename', type=str, help='What filename to save the 🥒-file')
    parser.add_argument('--draw', type=bool,
                        help='Draws example string diagram and quantum circuit. Saves to string.png and circ.png',
                        default=False)
    args = parser.parse_args()
    result =  create_circuits(dataset=args.dataset,
                              syntax=args.syntax,
                              ansatz=args.ansatz,
                              layers=args.layers,
                              q_s=args.q_s,
                              q_n=args.q_n,
                              q_pp=args.q_pp,
                              draw=args.draw,
                              filename=args.filename)

    print(f"Created cicuits. Written to:\n{result}")
