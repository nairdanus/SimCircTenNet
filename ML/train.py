import numpy as np
from collections import defaultdict
from tqdm import tqdm
import cmath
import os
import sys
import shutil
import yaml
from time import time

from create_circuits import create_circuits, load_circuits

from ML.classificators import SingleSentClassificator
from ML.classificators import CompleteClassificator


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
          fidelity,
          MAX_SPSA_ITER = 100,
          method = "complete"):

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
    
    classificator_params = {
        "learning_rate": 0.0015,
        "perturbation": 0.06,
        "maxiter": MAX_SPSA_ITER,
        "X": 𝓧,
        "fidelity": fidelity
    }
    if method == "single":
        for (meta, circ, _) in load_circuits(circuits_path):
            print(meta)
            sys.stdout.flush()
            classificator = SingleSentClassificator(circ=circ,
                                                    meta=meta,
                                                    **classificator_params)
            classificator.apply_spsa()
    else:
        classificator = CompleteClassificator(circs=load_circuits(circuits_path), **classificator_params)
        classificator.apply_spsa()

    if os.path.exists(param_path): os.remove(param_path)
    os.rename("angles.yaml", param_path)
    shutil.copyfile(param_path, param_path.replace(".yaml", "_" + str(time()) + ".yaml"))

    return param_path
