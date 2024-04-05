import numpy as np
from collections import defaultdict
from tqdm import tqdm
import cmath
import os
import yaml

from QCPcircuit import QCPcircuit
from helpers. angle_preparation import get_angles, update_angles

from create_circuits import create_circuits, load_circuits
from simulate_circuits import simulate_single_circuit
from postprocess_circuits import postprocess_single_circuit




class Classificator:

    def __init__(self, circ: QCPcircuit, meta: tuple, learning_rate: float, 𝓧=None, fidelity=100):
        self.learning_rate = learning_rate
        self.fidelity = fidelity
        self.𝓧 = 𝓧

        self.circ = circ
        self.simulator = None
        self.run_simulation()
        self.angles = get_angles(self.simulator.param_angles)
        self.perturbed_angles = {n: a for n, a in self.angles.items()}

        self.prob = None
        self.get_simulation_result()

        self.meta = meta
        self.gold = meta[1]

        self.correct = self.prob[self.gold] > 0.5


    def run_simulation(self):
        self.simulator = simulate_single_circuit(self.circ, self.fidelity, self.𝓧)

    def get_simulation_result(self):
        self.prob = postprocess_single_circuit(self.simulator)

    def loss_function(self):
        # Cross-entropy loss
        return -np.log(self.prob[self.gold])

    def perturb(self, angle):
        update_angles({ angle: (self.angles[angle] + 0.001) % (2*cmath.pi) })  # Small perturbation

    def reset(self):
        update_angles(self.angles)

    def apply_gradient_descent(self):
        gradients = defaultdict(float)
        for angle in tqdm(self.angles, total=len(self.angles), desc="Angles: "):
            original_loss = self.loss_function()
            self.perturb(angle)

            # Calculate the gradient using finite differences
            self.run_simulation()
            self.get_simulation_result()
            perturbed_loss = self.loss_function()
            
            gradients[angle] = (perturbed_loss - original_loss) / 0.001
            self.reset()

        # Update rotation angles using gradients and learning rate
        update_angles({
            angle: (self.angles[angle] - self.learning_rate * gradients[angle]) % (2*cmath.pi) for angle in gradients
        })


def train(dataset,
          syntax,
          ansatz,
          layers,
          q_s,
          q_n,
          q_pp,
          𝓧,
          fidelity):
          
    with open("angles.yaml", 'w') as yaml_file:
        yaml.dump(dict(), yaml_file)
    circuits_path = create_circuits(dataset=dataset,
                                    syntax=syntax,
                                    ansatz=ansatz,
                                    layers=layers,
                                    q_s=q_s,
                                    q_n=q_n,
                                    q_pp=q_pp)
    
    for (meta, circ, _) in load_circuits(circuits_path):
        classificator = Classificator(circ=circ,
                                      meta=meta,
                                      learning_rate=0.01,
                                      𝓧=𝓧,
                                      fidelity=fidelity)
        print(classificator.meta, classificator.correct)
        classificator.apply_gradient_descent()

    if not os.path.exists("createdparams"): os.mkdir("createdParams")
    param_path = os.path.join("createdParams", f"{dataset}_{syntax}-{ansatz}_{layers}_{q_s}_{q_n}_{q_pp}–{𝓧}_{fidelity}.yaml")
    os.rename("angles.yaml", param_path)

    return param_path
