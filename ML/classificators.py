import numpy as np
from collections import defaultdict
from tqdm import tqdm
import cmath
import os
import sys
import shutil
import yaml
from time import time

from simulate_circuits import simulate_single_circuit
from postprocess_circuits import postprocess_single_circuit

from QCPcircuit import QCPcircuit
from helpers. angle_preparation import get_angles, update_angles

from qiskit_algorithms.optimizers import SPSA
from scipy.optimize import minimize

LOSS = "CROSS"
# LOSS = "MSE"


class CompleteClassificator:

    def __init__(self, circs: list, 
                 learning_rate: float, perturbation: float, maxiter: int, 
                 𝓧=None, fidelity=100):
        self.learning_rate = learning_rate
        self.fidelity = fidelity
        self.𝓧 = 𝓧

        self.metas, self.circs, _ = list(list(t) for t in zip(*circs))
        self.golds = [meta[1] for meta in self.metas]
        
        self.simulators = None
        self.run_simulation()
        
        self.angles = set()
        for simulator in self.simulators: self.angles.update(simulator.param_angles)
        self.angle_dict = get_angles(self.angles)
        self.angle_list = list(self.angle_dict.values())

        self.probs = None
        self.get_simulation_result()

        self.error_indices = set()
        for i, prob in enumerate(self.probs):
            if len(prob) != 2:
                print(f"RESULT NOT BINARY AT SENT {self.metas[i]}. Probably not reduced to s. \n   -> ANGLES WERE NOT UPDATED.")
                self.error_indices.add(i)

        self.spsa = SPSA(maxiter=maxiter, learning_rate=learning_rate, perturbation=perturbation, second_order=False)
        self.spsa_iter = 0

    def apply_spsa(self):
        print("Minimizing")
        sys.stdout.flush()
        result = minimize(self.loss_function, self.angle_list, method='COBYLA', options={"maxiter": 1000})
        new_angle_list = []
        for a in result.x:
            a = a % (2*cmath.pi)
            new_angle_list.append(a)
        self.write_angles(new_angle_list)
        return result
    
    def loss_function(self, angles):
        self.spsa_iter += 1
        print(f"iter {self.spsa_iter}")
        sys.stdout.flush()
        self.write_angles(angles)
        self.run_simulation()
        self.get_simulation_result()
        
        if LOSS == "CROSS":
            loss = (1/len(self.probs)) * sum(
                -np.log(self.probs[i].get("1", 0)) for i in range(len(self.probs)) if i not in self.error_indices
            )
        elif LOSS == "MSE":        
            loss = (1/len(self.probs)) * sum(
                (self.probs[i].get("1", 0) - int(self.golds[i]))**2 
                for i in range(len(self.probs)) if i not in self.error_indices 
            )
        else:
            print("WHAT IS THE COST FUNCTION???")
            exit(1)
        print(loss)
        return loss

    def run_simulation(self):
        self.simulators = [
            simulate_single_circuit(circ, self.fidelity, self.𝓧) for circ in self.circs
            ]

    def get_simulation_result(self):
        self.probs = [
            postprocess_single_circuit(simulator) for simulator in self.simulators
            ]
    
    def write_angles(self, new_angle_list):
        new_angles = defaultdict(float)
        for i, key in enumerate(self.angle_dict.keys()):
            new_angles[key] = new_angle_list[i]
        update_angles(new_angles)




class SingleSentClassificator:

    def __init__(self, circ: QCPcircuit, meta: tuple, 
                 learning_rate: float, perturbation: float, maxiter: int, 
                 𝓧=None, fidelity=100):
        self.learning_rate = learning_rate
        self.fidelity = fidelity
        self.𝓧 = 𝓧

        self.circ = circ
        self.simulator = None
        self.run_simulation()
        self.angles = get_angles(self.simulator.param_angles)
        self.angle_list = list(self.angles.values())

        self.prob = None
        self.get_simulation_result()
        self.error = False
        if len(self.prob) != 2:
            print(f"RESULT NOT BINARY AT SENT {meta}. Probably not reduced to s. \n   -> ANGLES WERE NOT UPDATED.")
            self.error = True
            return

        self.meta = meta
        self.gold = meta[1]

        self.spsa = SPSA(maxiter=maxiter, learning_rate=learning_rate, perturbation=perturbation, second_order=False)

    def apply_spsa(self):
        if self.error: return
        result = self.spsa.minimize(self.loss_function, x0=self.angle_list)
        new_angle_list = []
        for a in result.x:
            a = a % (2*cmath.pi)
            new_angle_list.append(a)
        self.write_angles(new_angle_list)
        return result
    
    def loss_function(self, angles):
        self.write_angles(angles)
        self.run_simulation()
        self.get_simulation_result()
        
        # Cross-entropy loss
        # return -np.log(self.prob.get(self.gold, 0))
        
        # Some other loss
        return (self.prob.get(self.gold, 0) - int(self.gold))**2


    def run_simulation(self):
        self.simulator = simulate_single_circuit(self.circ, self.fidelity, self.𝓧)

    def get_simulation_result(self):
        self.prob = postprocess_single_circuit(self.simulator)
    
    def write_angles(self, new_angle_list):
        new_angles = defaultdict(float)
        for i, key in enumerate(self.angles.keys()):
            new_angles[key] = new_angle_list[i]
        update_angles(new_angles)


