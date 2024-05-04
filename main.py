import argparse
import os
import time
from typing import Literal

os.environ["OUT_FILE"] = f"createdTrainings/TRAIN_{time.time()}.txt"
os.environ["ANGLE_FILE"] = f"createdParams/angles_{time.time()}.yaml"

from ML import train, evaluate



#### HYPERPARAMS ####

DATASET = "grammar_aware.csv"
TESTSET = "test_grammar_aware.csv"
SYNTAX: Literal["PRE", "BOW", "SEQ"] = "PRE"

ANSATZ: Literal["IQP", "SIM14", "SIM15", "STRONGENT"] = "IQP"
LAYERS = 7
SINGLE_LAYERS = 1  # ONLY IF ANY Q_X ARE 1
Q_S = 1
Q_N = 2
Q_NP = 2
Q_PP = 2
Q_C = 2
Q_PUNC = 2

𝓧 = None
FIDELITY = 100

METHOD: Literal["COBYLA", "SPSA"] = "SPSA"
COST: Literal["CROSS", "MSE"] = "CROSS"
MAXITER: int = 1000
LEARNING_RATE: float = 0.15 # ONLY WITH SPSA
PERTURBATION: float = 0.06 # ONLY WITH SPSA


############################




kwargs = {
      "dataset": DATASET,
      "syntax": SYNTAX,
      "ansatz": ANSATZ,
      "layers": LAYERS,
      "n_single_q": SINGLE_LAYERS,
      "q_s": Q_S,
      "q_n": Q_N,
      "q_np": Q_NP,
      "q_pp": Q_PP,
      "q_c": Q_C,
      "q_punc": Q_PUNC,
      "X": 𝓧,
      "fidelity": FIDELITY,
      "method": METHOD,
      "cost": COST,
      "maxiter": MAXITER,
      "learning_rate": LEARNING_RATE,
      "perturbation": PERTURBATION,
}


if __name__=="__main__":

      print("TRAIN FILE: ", os.environ.get("OUT_FILE"))
      print("PID:", os.getpid())
      
      if not os.path.exists("createdTrainings/"): os.mkdir("createdTrainings/")
      with open(os.environ.get("OUT_FILE"), 'w') as f:
            f.write(time.strftime(
        f"""
%m.%d.-%H:%M - Starting training with PID {os.getpid()}:
      DATASET = {DATASET}
      # TESTSET = {TESTSET}
      SYNTAX = {SYNTAX}

      ANSATZ = {ANSATZ}
      LAYERS = {LAYERS}
      SINGLE_LAYERS = {SINGLE_LAYERS}
      Q_S = {Q_S}
      Q_N = {Q_N}
      Q_NP = {Q_NP}
      Q_PP = {Q_PP}
      Q_C = {Q_C}
      Q_PUNC = {Q_PUNC}

      𝓧 = {𝓧}
      FIDELITY = {FIDELITY}

      METHOD = {METHOD}
      COST = {COST}
      MAXITER = {MAXITER}
      LEARNING_RATE = {LEARNING_RATE} # ONLY WITH SPSA
      PERTURBATION = {PERTURBATION} # ONLY WITH SPSA


______________________________________________________________

"""
    ))
      result = train(**kwargs)

      with open(os.environ.get("OUT_FILE"), 'a') as f:
            f.write(time.strftime(f"\n\n\nFINISHED at %m.%d.-%H:%M"))
            f.write(f"\nANGLES AT: {os.environ.get('ANGLE_FILE')}\n\n\n")
            f.write(result)