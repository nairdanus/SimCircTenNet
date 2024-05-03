import numpy as np
from collections import defaultdict
from tqdm import tqdm
import cmath
import os
import sys
import shutil
import yaml
from time import time
from typing import Literal

from simulate_circuits import simulate_single_circuit
from postprocess_circuits import postprocess_single_circuit

from QCPcircuit import QCPcircuit
from helpers. angle_preparation import get_angles, update_angles

from qiskit_algorithms.optimizers import SPSA
from scipy.optimize import minimize

from concurrent.futures import ThreadPoolExecutor



class Trainer:

    def __init__(self,
                 circs: list,
                 method: Literal["COBYLA", "SPSA"],
                 cost: Literal["CROSS", "MSE"],
                 maxiter: int,
                 learning_rate: float, # ONLY WITH SPSA
                 perturbation: float,  # ONLY WITH SPSA
                 𝓧=None, 
                 fidelity=100,
                 out_file="train.txt"):
        self.out_file = out_file
        
        self.cost = cost
        self.method = method
        if method == "SPSA":
            self.spsa = SPSA(maxiter=maxiter, 
                             learning_rate=learning_rate, perturbation=perturbation, 
                             second_order=False)

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

        self.max_iter = maxiter
        self.cur_iter = 0
        
        self.cur_time = time()

    def train(self):
        print("Minimizing")
        sys.stdout.flush()

        if self.method == "SPSA":
            result = self.spsa.minimize(fun=self.loss_function, x0=self.angle_list)
        elif self.method == "COBYLA":
            result = minimize(self.loss_function, self.angle_list, 
                              method='COBYLA', options={"maxiter": self.max_iter})
        else:
            print("WHAT IS THE TRAINING METHOD???")
            exit(1)

        return result
    
    def loss_function(self, angles):
        self.write_angles(angles)
        self.run_simulation()
        self.get_simulation_result()

        K = [i for i in range(len(self.probs)) if i not in self.error_indices]
        N = len(K)

        if self.cost == "CROSS":
            loss = -(1/N) * sum(
                int(self.golds[i]) * np.log(self.probs[i].get("1", 0)) + (1-int(self.golds[i])) * np.log(1-self.probs[i].get("1", 0))
                for i in K
            )
        elif self.cost == "MSE":
            loss = (1/N) * sum(
                (self.probs[i].get("1", 0) - int(self.golds[i]))**2 
                for i in K
            )
        else:
            print("WHAT IS THE COST FUNCTION???")
            exit(1)

        self.cur_iter += 1
        elapsed_time = time() - self.cur_time
        self.cur_time = time()
        out = f"iter {self.cur_iter}: {loss}\n\tTime passed: {elapsed_time}\n"
        with open(self.out_file, mode="a") as f:
            f.write(out)
        print(out)
        sys.stdout.flush()
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