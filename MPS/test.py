import numpy as np
import tensornetwork as tn
from parseQCP import *
from simulator import *
import os
from helpers import *
import sys

if __name__ == "__main__":    

    paths = sys.argv[1:]
    assert all([os.path.isfile(x) and x.endswith(".qcp") for x in paths])
    
    dir = "./test_circs"

    def compare(a, b):
        #return np.array_equal(r, expected)
        return len(a) == len(b) and np.isclose(a, b).all()
    
    def iterator():
        if len(paths) > 0:
            for path in paths:
                name = os.path.relpath(path, dir)
                yield path, name
            pass
        else:
            for root, _, files in os.walk(dir):
                for f in [f for f in sorted(files) if f.endswith(".qcp")]:
                    path = os.path.join(root, f)
                    name = os.path.relpath(path, dir)
                    yield path, name
                
    fail = False
    for path, name in iterator():   
        with open(path, "r") as fp:        
            lines = fp.readlines()
            last = lines[-1]
            pfx = "//!T:"
            if not last.startswith(pfx): continue
            t = last[len(pfx):]         
            vvv = eval(t)
            ok_vals = None
            if isinstance(vvv, tuple):
                ok_vals = list(vvv)
            else:
                ok_vals = [vvv]
            ok_vals = [o if not isinstance(o, str) else s2v(o) for o in ok_vals]
            #if isinstance(vvv, str): vvv = s2v(vvv)

            expected = list([np.array(o, dtype=complex) for o in ok_vals])
            ###
            #xif name != 'cnot/test9.qcp': continue######
            print("running test:", name)##
            c = parseQCP(path)
            #print(c)
            simulator = MPS_Simulator(c)
            simulator.iterate_circ()


            #0100100011
            #m = simulator.measure_states(["0100100011"[::-1]])
            #m = simulator.measure_states(["0100100011"])
            #m = simulator.measure_states(["0100100011"])
            #m = simulator.measure_states(["001"])
            #print("measured state:", m)

            result = simulator.get_result()
            r = simulator.get_state_vector(result)
            #r = np.reshape(result.tensor, newshape=(2**simulator.circ.numQubits))
            
            test_ok = any([compare(r, e) for e in expected])
            if test_ok:
                print("  PASS")
                print("      :", v2s(r))       
            else:
                print("  FAIL")
                print("    RESULT:", r)
                print("          :", ",".join(str(r).split(" "))       )
                print("          :", v2s(r))                       
                #print(result.tensor)
                print("    EXPECT:", expected[0])
                print("          :", v2s(expected[0]))     
                for e in expected[1:]:
                    print("        OR:", e)
                    print("          :", v2s(e))
                fail = True
    if fail:
        print("some tests failed")
        exit(1)
    else:
        print("all tests passed")
