import argparse
import os
import time

from ML import train, evaluate


DATASET = "100_animals_plants.csv"
TESTSET = "10_animals_plants.csv"
SYNTAX = "seq"

ANSATZ = "iqp"
LAYERS = 5
Q_S = 1
Q_N = 3
Q_PP = 3

𝓧 = None
FIDELITY = 100

EPOCHS = 10

kwargs = {
      "syntax": SYNTAX,
      "ansatz": ANSATZ,
      "layers": LAYERS,
      "q_s": Q_S,
      "q_n": Q_N,
      "q_pp": Q_PP,
      "X": 𝓧,
      "fidelity": FIDELITY,
}

out_file = f"TRAIN_{time.time()}.txt"

if __name__=="__main__":
      with open(out_file, 'w') as f:
            f.write(time.strftime(
        f"""
%m.%d.-%H:%M - Starting training:
      DATASET = {DATASET}
      TESTSET = {TESTSET}
      SYNTAX = {SYNTAX}

      ANSATZ = {ANSATZ}
      LAYERS = {LAYERS}
      Q_S = {Q_S}
      Q_N = {Q_N}
      Q_PP = {Q_PP}

      𝓧 = {𝓧}
      FIDELITY = {FIDELITY}

      EPOCHS = {EPOCHS}

______________________________________________________________

"""
    ))

      for e in range(EPOCHS):
            param_path = train(dataset=DATASET, **kwargs)
            print("Evaluating...")
            acc = evaluate(dataset=TESTSET, param_path="createdParams/BACKUP copy.yaml", **kwargs)
            print(f"Accuracy: {acc}")
            with open(out_file, 'a') as f:
                  f.write(f"Accuracy at epoch {e}: {acc}\n")

with open(out_file, 'a') as f:
      f.write(time.strftime(f"\n FINISHED at %m.%d.-%H:%M"))
