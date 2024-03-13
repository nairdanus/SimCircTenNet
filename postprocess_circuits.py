import pickle
from helpers. braket import v2s
import argparse

if __name__ == "__main__":
    with open("createdSimulations/single_sentence/c-20240314-003311.pkl", "rb") as f:
        result_vec = pickle.load(f)
    print(v2s(result_vec))

