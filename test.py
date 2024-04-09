import os
import sys
import random
import contextlib
import numpy as np
from tqdm import tqdm

from MPS import test_simulator, MPS_Simulator
from DisCoCat import DisCoCat
from helpers import qiskitCirc2qcp, v2d


def test_post_selection(sentence: str):

    def dict_almost_equal(d1, d2):
        if set(d1) != set(d2): return False
        for k in d1:
            if not np.isclose(d1[k], d2[k]): return False
        return True

    with open("Data/post_sel_test.txt", "w") as f: f.write(sentence)
    all_tests_passed = True

    for l in random.sample(range(10), 3):

        d = DisCoCat(syntax_model="pre",
                    dataset_name="post_sel_test",
                    ansatz="iqp",
                    n_layers=l,
                    disable_tqdm=True,
                    q_s=1, 
                    q_n=random.randint(1, 7), 
                    q_pp=random.randint(1, 7), 
                    q_c=random.randint(1, 7),
                    q_punc=random.randint(1, 7),
                    q_np=random.randint(1, 7))
        circ = qiskitCirc2qcp(d.circuits[0][1])

        simulators = [
            MPS_Simulator(circ=circ, post_selection=True),
            MPS_Simulator(circ=circ, post_selection=False)
            ]
        for s in simulators: s.iterate_circ()
        results = [v2d(s.get_state_vector()) for s in simulators]

        if dict_almost_equal(results[0], results[1]): continue
        
        all_tests_passed = False
        print(f"PROBLEM!!!\nWITH POST SELECTION: {results[0]}\nWITHOUT POST SELECTION: {results[1]}\n")

    os.remove("Data/post_sel_test.txt")
    if all_tests_passed: print("Post selection seems to work fine!")



if __name__ == "__main__":

    print("\nTesting simulator:")
    test_simulator()
    print("\nTesting Post Selection:")
    test_post_selection("Alice loves Bob.")
