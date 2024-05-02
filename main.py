import argparse
import os
import time

from ML import train, evaluate

DATASET = "grammar_aware.csv"
TESTSET = "test_grammar_aware.csv"
SYNTAX = "pre"

ANSATZ = "iqp"
LAYERS = 7
Q_S = 1
Q_N = 1
Q_NP = 1
Q_PP = 1
Q_C = 1
Q_PUNC = 1

𝓧 = None
FIDELITY = 100

EPOCHS = 50
MAX_SPSA_ITER = 50

kwargs = {
      "syntax": SYNTAX,
      "ansatz": ANSATZ,
      "layers": LAYERS,
      "q_s": Q_S,
      "q_n": Q_N,
      "q_np": Q_NP,
      "q_pp": Q_PP,
      "q_c": Q_C,
      "q_punc": Q_PUNC,
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
      Q_S = {Q_S}
      Q_N = {Q_N}
      Q_NP = {Q_NP}
      Q_PP = {Q_PP}
      Q_C = {Q_C}
      Q_PUNC = {Q_PUNC}

      𝓧 = {𝓧}
      FIDELITY = {FIDELITY}

      EPOCHS = {EPOCHS}
      MAX_SPSA_ITER = {MAX_SPSA_ITER}

______________________________________________________________

"""
    ))

      for e in range(EPOCHS):
            param_path = train(dataset=DATASET, MAX_SPSA_ITER=MAX_SPSA_ITER, **kwargs)
            print("Evaluating...")
            acc = evaluate(dataset=DATASET, param_path=param_path, **kwargs)
            print(f"Accuracy: {acc}")
            with open(out_file, 'a') as f:
                  f.write(f"Accuracy at epoch {e}: {acc}\n")

with open(out_file, 'a') as f:
      f.write(time.strftime(f"\n FINISHED at %m.%d.-%H:%M")) 
