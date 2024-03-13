import cmath
from QCPcircuit import Gate, QCPcircuit

def parseQCP(path):
    with open(path, "r") as fp:
        circ = QCPcircuit()

        opt = {}
        for line in fp.read().splitlines():
            # ignore comments
            if line.startswith('//'): continue

            # first line that is no comment has to be num of used qbits
            if (circ.numQubits is None):
                circ.numQubits = int(line)
                continue

            gate_comp = line.split()
            gate = Gate(gate_comp[0])

            # gates with parameters
            if (line.startswith('r')):
                if opt.get(gate_comp[1]) is None:
                    opt[gate_comp[1]] = float(eval(gate_comp[1].replace("pi", str(cmath.pi))))
                gate.param = opt[gate_comp[1]]
                gate.target = int(gate_comp[2])
                circ.gates.append(gate)
                continue

            # controlled rotation gates
            if (line.startswith('cr')):
                if opt.get(gate_comp[1]) is None:
                    opt[gate_comp[1]] = float(eval(gate_comp[1].replace("pi", str(cmath.pi))))
                gate.param = opt[gate_comp[1]]
                gate.control = int(gate_comp[2])
                gate.target = int(gate_comp[3])
                circ.gates.append(gate)
                continue

            # controlled gates
            if (line.startswith('c')):
                gate.control = int(gate_comp[1])
                gate.target = int(gate_comp[2])
                circ.gates.append(gate)
                continue

            if (line.startswith('swap')):
                gate.control = int(gate_comp[1])
                gate.target = int(gate_comp[2])
                circ.gates.append(gate)
                continue

            # single qbit gates without parameters
            gate.target = int(gate_comp[1])
            circ.gates.append(gate)
    return circ
