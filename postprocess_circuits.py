import os
import pickle
from helpers. braket import v2s
import argparse
from collections import defaultdict

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
    result = defaultdict()
    k_0, k_1 = remove_equal_parts(list(d.keys())[0], list(d.keys())[1])
    result[k_0] = d[list(d.keys())[0]]
    result[k_1] = d[list(d.keys())[1]]
    return dict(result)

def parse_ket(ket):
    ket_elements = ket.split(" + ")
    result = defaultdict(float)
    for ket_element in ket_elements:
        p, bits = ket_element.split("|")
        bits = bits.replace("⟩", "")
        p = abs(complex(p)) ** 2
        result[bits] = p

    return remove_equal_bits(dict(result))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str,
                        help='Path of the directory containing the simulated circuits.',
                        choices=[os.path.join("createdSimulations", f) for f in
                                 os.listdir("createdSimulations")] + os.listdir("createdSimulations"),
                        default=os.listdir("createdCircuits")[0])
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

        result_vec = simulator.get_state_vector()
        result = parse_ket(v2s(result_vec, ignore_small_values=True))
        best_result = max(result.items(), key=lambda x: x[1])

        print()
        print(meta)
        print("{0}: {1}, {2}".format(*best_result,
                                meta[1] == best_result[0]))
        print(result)
        print()


