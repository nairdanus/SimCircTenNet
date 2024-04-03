from collections import defaultdict

import numpy as np
import math
import functools as ft

def v2s(v, ignore_small_values=False):
    if len(v) == 0: return "<INVALID_VEC_LEN>"
    n = math.log2(len(v))
    if n != int(n) or n < 1: return "<INVALID_VEC_LEN>"
    n = int(n)

    sum = ft.reduce(lambda agg,nxt: agg + abs(nxt)**2, v, 0)
    valid_sum = np.isclose([1], sum).all()

    assert n < 100
    def i():
        for i in range(len(v)):
            if ignore_small_values and np.isclose(v[i], 0, atol=1.e-3): continue
            q = '|' + format(i, '0'+str(n)+'b')[-n:] + '⟩'
            if v[i] == 0: continue
            a = v[i] if v[i].imag else v[i].real
            yield str(a)+q

    return " + ".join(i()) + (" (<INVALID_SUM>)" if not valid_sum else "")

def s2v(s:str):
    import functools as ft
    s = s.strip()
    s = s.replace(">","⟩")

    bs = " (<INVALID_SUM>)"
    if s.endswith(bs):
        #print("warning:"+bs) ignore
        s = s[0:len(s)-len(bs)]

    sums = s.split(" + ")
    for i, s in enumerate(sums):
        [amp, ket] = s.split("|")
        assert ket[len(ket)-1] == "⟩"
        sums[i] = amp, ket[0:len(ket)-1]
    bitlen = len(sums[0][1])
    assert all(len(ket) == bitlen for amp, ket in sums)
    for i, (amp, ket) in enumerate(sums):
        amp = amp if len(amp) > 0 else 1
        sums[i] = complex(amp), int(ket, 2)
    #print(sums)
    sum = ft.reduce(lambda agg,s: agg + abs(s[0])**2, sums, 0)
    valid_sum = np.isclose([1], sum).all()
    if not valid_sum:
        #print("warning2:"+bs) ignore
        pass

    res = np.zeros(2**bitlen,dtype=complex)
    for _, (amp, ket) in enumerate(sums):
        res[ket] = amp
    return res

def s2d(s:str):
    def renormalize_dict(d):
        return {key: value / sum(d.values()) for key, value in d.items()}

    invalid_sum = False
    ket = s
    if s.endswith(' (<INVALID_SUM>)'):
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

def v2d(v, ignore_small_values=False):
    return s2d(v2s(v, ignore_small_values))



if __name__ == "__main__":
    #a = [0.70710678+0.j, 0.        +0.j, 0.70710678+0.j, 0.        +0.j]
    #a = [0.4+0.3j,0.4,0.3j,0,0,0,0,0]
    #a = [1,0,0,0,0,0,0,0]
    a = [0,0,0,1]
    #a = [1.0,0.1]
    #a = [1,0,0,0,0]
    #a= [0,1]
    #a = [1,-2,3j,-4j,5+6j,-7-8j,0,0]

    s = v2s(np.array(a, dtype=complex))
    v = s2v(s)

    print(a)
    print(s)
    print(v)

    print("ok:", np.isclose(a,v).all())

    print(s2v("0.70710678|0> + 0.70710678|1>"))

    assert v2s([1,0,0,0,0,0,0,0]) == "1|000⟩"
    assert v2s([0,1,0,0,0,0,0,0]) == "1|001⟩"
    assert v2s([1,0,0,0]) == "1|00⟩"
    assert v2s([0,1,0,0]) == "1|01⟩"
    assert v2s([1,0]) == "1|0⟩"
    assert v2s([0,1]) == "1|1⟩"
    assert v2s([1]+[0] * (2 ** 10-1)) == "1|0000000000⟩"