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

from create_circuits import create_circuits, load_circuits

from ML.classificators import Trainer


def train(dataset: str,
          syntax: str,
          ansatz: str,
          layers: int,
          n_single_q: int,
          q_s: int, 
          q_n: int, 
          q_np: int,
          q_pp: int, 
          q_c: int,
          q_punc: int,
          𝓧: int,
          fidelity: float,
          method: Literal["COBYLA", "SPSA"],
          cost: Literal["CROSS", "MSE"],
          maxiter: int,
          learning_rate: float, # ONLY WITH SPSA
          perturbation: float,  # ONLY WITH SPSA
          ):

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
                                    q_punc=q_punc,
                                    n_single_q=n_single_q,)
    
    trainer = Trainer(circs=load_circuits(circuits_path),
                      method=method,
                      cost=cost,
                      maxiter=maxiter,
                      learning_rate=learning_rate,
                      perturbation=perturbation,
                      𝓧=𝓧,
                      fidelity=fidelity)

    trainer.train()


    if os.path.exists(param_path): os.remove(param_path)
    os.rename("angles.yaml", param_path)
    secure_copy_path = param_path.replace(".yaml", "_" + str(time()) + ".yaml")
    shutil.copyfile(param_path, secure_copy_path)

    return secure_copy_path
