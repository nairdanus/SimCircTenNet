import argparse
import pickle

from MPS import simulator

if __name__ == "__main__":
    with open("createdSimulations/single_sentence/c-20240314-000817.pkl", "rb") as f:
        mps = pickle.load(f)

    mps
    a = 0

