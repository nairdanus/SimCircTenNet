import os
import pickle
import argparse
from collections import defaultdict
import numpy as np

from MPS import MPS_Simulator
from helpers. braket import v2d

def remove_equal_parts(str1, str2):
    result_str1 = ""
    result_str2 = ""
    for char1, char2 in zip(str1, str2):
        if char1 != char2:
            result_str1 += char1
            result_str2 += char2
    return result_str1, result_str2

def remove_equal_bits(d):
    if len(d) != 2: return d
    res = defaultdict()
    k_0, k_1 = remove_equal_parts(list(d.keys())[0], list(d.keys())[1])
    res[k_0] = d[list(d.keys())[0]]
    res[k_1] = d[list(d.keys())[1]]
    return dict(res)


def postprocess_single_circuit(simulator):
    
    result_vec = simulator.get_state_vector()

    if len(result_vec) != 2:
        result = remove_equal_bits(v2d(result_vec, ignore_small_values=True))
    else:
        result = v2d(result_vec, ignore_small_values=False)

    assert len(result) == 2, "Postprocess has three labels!!!"

    return result



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str,
                        help='Path of the directory containing the simulated circuits.',
                        choices=[os.path.join("createdSimulations", f) for f in
                                 os.listdir("createdSimulations")] + os.listdir("createdSimulations"),
                        default=os.listdir("createdSimulations")[0])
    args = parser.parse_args()

    if not os.path.exists(args.dir):
        if os.path.exists(path := os.path.join("createdSimulations", args.dir)):
            args.dir = path
        else:
            raise FileNotFoundError(f"There is no directory called {args.dir}")

    for file in os.listdir(args.dir):
        if file.endswith("Meta.txt"): continue
        file = os.path.join(args.dir, file)
        with open(file, "rb") as f:
            simulator, meta = pickle.load(f)

        if isinstance(simulator, MPS_Simulator):
            result_vec = simulator.get_state_vector()
            if len(result_vec) != 2:
                result = remove_equal_bits(v2d(result_vec, ignore_small_values=True))
            else:
                result = v2d(result_vec, ignore_small_values=False)

            best_result = max(result.items(), key=lambda x: x[1])

            print()
            print(meta)
            print("{0}: {1}, {2}".format(*best_result,
                                    meta[1] == best_result[0]))
            print("X max: ", max(simulator.real_𝓧s))
            print("X avg: ", sum(simulator.real_𝓧s)/len(simulator.real_𝓧s))
            print(result)
            print()

        elif isinstance(simulator, dict):
            print(meta)
            print(simulator)

        else:
            raise NotImplementedError(f"Unrecognized simulator of type {type(simulator)}!")


