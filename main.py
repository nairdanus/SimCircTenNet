import argparse
import os

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

out_file = f"{DATASET}_{SYNTAX}.txt"

if __name__=="__main__":
      with open(out_file, 'wa') as f:
            f.write(f"Starting training:\n")

      for e in range(EPOCHS):
            param_path = train(dataset=DATASET,**kwargs)
            acc = evaluate(dataset=TESTSET, param_path=param_path, **kwargs)
            
            with open(out_file, 'a') as f:
                  f.write(f"Accuracy at epoch {e}: {acc}\n")
