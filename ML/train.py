import numpy as np
from collections import defaultdict
from tqdm import tqdm
import cmath
import os
import shutil
import yaml

from qiskit_algorithms.optimizers import SPSA

from QCPcircuit import QCPcircuit
from helpers. angle_preparation import get_angles, update_angles

from create_circuits import create_circuits, load_circuits
from simulate_circuits import simulate_single_circuit
from postprocess_circuits import postprocess_single_circuit




class Classificator:

    def __init__(self, circ: QCPcircuit, meta: tuple, learning_rate: float, perturbation: float, 𝓧=None, fidelity=100):
        self.learning_rate = learning_rate
        self.fidelity = fidelity
        self.𝓧 = 𝓧

        self.circ = circ
        self.simulator = None
        self.run_simulation()
        self.angles = get_angles(self.simulator.param_angles)
        self.angle_list = list(self.angles.values())

        self.prob = None
        
        self.meta = meta
        self.gold = meta[1]

        self.spsa = SPSA(maxiter=100, learning_rate=learning_rate, perturbation=perturbation, second_order=False)

    def apply_spsa(self):
        result = self.spsa.minimize(self.loss_function, x0=self.angle_list)
        new_angle_list = []
        for a in result.x:
            a = a % (2*cmath.pi)
            new_angle_list.append(a)
        self.write_angles(new_angle_list)
        return result
    
    def loss_function(self, angles):
        # Cross-entropy loss
        self.write_angles(angles)
        self.run_simulation()
        self.get_simulation_result()
        return -np.log(self.prob[self.gold])

    def run_simulation(self):
        self.simulator = simulate_single_circuit(self.circ, self.fidelity, self.𝓧)

    def get_simulation_result(self):
        self.prob = postprocess_single_circuit(self.simulator)
    
    def write_angles(self, new_angle_list):
        new_angles = defaultdict(float)
        for i, key in enumerate(self.angles.keys()):
            new_angles[key] = new_angle_list[i]
        update_angles(new_angles)


def train(dataset,
          syntax,
          ansatz,
          layers,
          q_s, 
          q_n, 
          q_np,
          q_pp, 
          q_c,
          q_punc,
          𝓧,
          fidelity):

    if not os.path.exists("createdParams"): os.mkdir("createdParams")
    param_path = os.path.join("createdParams", f"{dataset}_{syntax}-{ansatz}_{layers}_{q_s}_{q_n}_{q_pp}–{𝓧}_{fidelity}.yaml")
    
    if os.path.exists(param_path):
        if os.path.exists("angles.yaml"): os.remove("angles.yaml")
        shutil.copyfile(param_path, "angles.yaml")
    else:
        with open("angles.yaml", 'w') as yaml_file:
            yaml.dump(dict(), yaml_file)

    circuits_path = create_circuits(dataset=dataset,
                                    syntax=syntax,
                                    ansatz=ansatz,
                                    layers=layers,
                                    q_s=q_s,
                                    q_n=q_n,
                                    q_np=q_np,
                                    q_pp=q_pp,
                                    q_c= q_c,
                                    q_punc=q_punc)
    
    for (meta, circ, _) in load_circuits(circuits_path):
        print(meta)
        classificator = Classificator(circ=circ,
                                      meta=meta,
                                      learning_rate=0.05,
                                      perturbation=0.06,
                                      𝓧=𝓧,
                                      fidelity=fidelity)
        classificator.apply_spsa()

    if os.path.exists(param_path): os.remove(param_path)
    os.rename("angles.yaml", param_path)

    return param_path
