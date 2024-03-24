import os
import pickle
from helpers. braket import v2s
import argparse
from collections import defaultdict

from MPS import MPS_Simulator

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

def renormalize_dict(d):
    return {key: value / sum(d.values()) for key, value in d.items()}

def parse_ket(ket):
    invalid_sum = False
    if ket.endswith(' (<INVALID_SUM>)'):
        invalid_sum = True
        ket = ket.replace(' (<INVALID_SUM>)', '')

    ket_elements = ket.split(" + ")
    res = defaultdict(float)
    for ket_element in ket_elements:
        p, bits = ket_element.split("|")
        bits = bits.replace("⟩", "")
        p = abs(complex(p)) ** 2
        res[bits] = p

    return renormalize_dict(dict(res)) if invalid_sum else dict(res)



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

        if type(simulator) == MPS_Simulator:
            result_vec = simulator.get_state_vector()
            if len(result_vec) != 2:
                result = remove_equal_bits(parse_ket(v2s(result_vec, ignore_small_values=True)))
            else:
                result = parse_ket(v2s(result_vec, ignore_small_values=False))

            best_result = max(result.items(), key=lambda x: x[1])

            print()
            print(meta)
            print("{0}: {1}, {2}".format(*best_result,
                                    meta[1] == best_result[0]))
            print()

        elif type(simulator) == dict:
            print(meta)
            print(simulator)

        else:
            raise NotImplementedError(f"Unrecognized simulator of type {type(simulator)}!")


