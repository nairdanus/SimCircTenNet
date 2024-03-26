import argparse
import os
from tqdm import tqdm

from DisCoCat import DisCoCat
from MPS import MPS_Simulator
from helpers import v2d
from helpers.circuit_preparation import qiskitCirc2qcp
from ML import Classificator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The complete training pipeline.')
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
    parser.add_argument('--fidelity', type=float, default=None,
                        help='The maximal truncation error for the simulation. (Type 0 to deactivate)')
    parser.add_argument('--chi', type=int, default=None,
                        help='The 𝓧 value of the Simulation. Number of singular values to keep. (Type 0 to deactivate)')
    parser.add_argument('--learn_rate', type=float, default=0.01,
                        help='The learning rate.')

    args = parser.parse_args()

    args.dataset = args.dataset.split(".")[0]

    if not os.path.isdir("createdCircuits"): os.mkdir("createdCircuits")

    d = DisCoCat(syntax_model=args.syntax,
                 dataset_name=args.dataset,
                 ansatz=args.ansatz,
                 n_layers=args.layers,
                 q_s=args.q_s,
                 q_n=args.q_n,
                 q_pp=args.q_pp)

    circs = []
    for meta, circ in tqdm(d.circuits,
                           total=len(d.circuits),
                           desc="Translating Qiskit to QCP",
                           ncols=150):
        circs.append((meta, qiskitCirc2qcp(circ), circ))

    for meta, QCP_circ, qiskit_circ in tqdm(circs,
                                            total=len(circs),
                                            desc="Simulating circuits",
                                            ncols=150):
        simulator = MPS_Simulator(circ=QCP_circ, fidelity=args.fidelity, 𝓧=args.chi, show_progress_bar=False,
                        circ_name="./trash")
        simulator.iterate_circ()
        result_vec = simulator.get_state_vector()
        result = v2d(result_vec, ignore_small_values=False)

        Classificator(prob=result,
                      meta=meta,
                      angle_names=simulator.param_angles,
                      learning_rate=args.learn_rate)

        # TODO



