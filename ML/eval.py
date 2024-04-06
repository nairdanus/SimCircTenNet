import os
import shutil
import yaml

from create_circuits import create_circuits, load_circuits
from simulate_circuits import simulate_single_circuit
from postprocess_circuits import postprocess_single_circuit



class Evaluator:

    def __init__(self, circuits_path, 𝓧=None, fidelity=100):
        self.correct = 0
        self.n_circs = 0

        for (meta, circ, _) in load_circuits(circuits_path):
            simulator = simulate_single_circuit(circ, fidelity, 𝓧)
            result = postprocess_single_circuit(simulator)
            gold_label = meta[1]
            self.correct += result[gold_label]
            self.n_circs += 1


    def accuracy(self):
        return round(self.correct / self.n_circs, 3)



def evaluate(param_path, 
             dataset,
             syntax,
             ansatz,
             layers,
             q_s,
             q_n,
             q_pp,
             𝓧,
             fidelity):

    circuits_path = create_circuits(dataset=dataset,
                                    syntax=syntax,
                                    ansatz=ansatz,
                                    layers=layers,
                                    q_s=q_s,
                                    q_n=q_n,
                                    q_pp=q_pp)
    if os.path.exists("angles.yaml"): os.remove("angles.yaml")
    shutil.copyfile(param_path, "angles.yaml")
    
    evaluator = Evaluator(circuits_path=circuits_path, 
                          𝓧=𝓧, 
                          fidelity=fidelity)

    acc = evaluator.accuracy()

    with open("angles.yaml", 'w') as yaml_file:
        yaml.dump(dict(), yaml_file)

    return acc
