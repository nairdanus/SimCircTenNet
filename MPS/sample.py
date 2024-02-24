import numpy as np
import tensornetwork as tn
from parseQCP import *
from simulator import *
import os
from helpers import *
import sys

if __name__ == "__main__":    
    if len(sys.argv) < 3:
        print("Usage:", sys.argv[0], "count circ1.qcp ... circN.qcp", file=sys.stderr)
        exit(1)

    n = int(sys.argv[1])
    paths = sys.argv[2:]
    assert all([os.path.isfile(x) and x.endswith(".qcp") for x in paths])
    
    def iterator():
        for path in paths:
            name = os.path.relpath(path, os.path.curdir)
            yield path, name
                
    for path, name in iterator():   
        with open(path, "r") as fp:        
            print("sampling:", name)
            c = parseQCP(path)
            samples = {}
            for i in range(n):
                simulator = MPS_Simulator(c)
                simulator.shrink_after_measure = False
                simulator.iterate_circ()
                result = simulator.get_result()
                v = simulator.get_state_vector(result)
                v = np.round(v, decimals=5)
                s = v2s(v)
                samples[s] = (0 if not samples.get(s) else samples[s]) + 1
                
            print("N".rjust(8) + "%".rjust(6) + "  state")
            for k,v in samples.items():
                print(str(v).rjust(8) + (str(round(v/n*100, 1))).rjust(6) + "  " + k) 


