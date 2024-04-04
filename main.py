import argparse
import os

from ML.train import train

DATASET = "10_animals_plants.csv"
SYNTAX = "seq"

ANSATZ = "iqp"
LAYERS = 5
Q_S = 1
Q_N = 3
Q_PP = 3

𝓧 = None
FIDELITY = 100



if __name__=="__main__":

      train(dataset=DATASET,
            syntax=SYNTAX,
            ansatz=ANSATZ,
            layers=LAYERS,
            q_s=Q_S,
            q_n=Q_N,
            q_pp=Q_PP,
            𝓧=𝓧,
            fidelity=FIDELITY
            )