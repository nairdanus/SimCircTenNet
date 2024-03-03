from qiskit import QuantumCircuit, transpile

from QCPcircuit import QCPcircuit, Gate

def qiskitCirc2qcp(circ: QuantumCircuit):

    qcp = QCPcircuit()

    qcp.numQubits = circ.num_qubits

    for instruction in circ.data:
        gate = Gate(instruction.operation.name)

        if param := instruction.operation.params:
            assert len(param) < 2
            gate.param = param[0]

        if instruction.operation.name != "measure":
            if len(qubits := tuple(i.index for i in instruction.qubits)) == 1:
                gate.control = None
                gate.target = qubits[0]
            else:
                gate.control, gate.target = qubits

        else:
            gate.target, _ = instruction.qubits[0].index, instruction.clbits[0].index  # TODO: measurement to another index on classical register

        qcp.gates.append(gate)

    return qcp


if __name__ == '__main__':
    import pickle

    with open("../10_animals_plants.pkl", "rb") as f:
        data = pickle.load(f)
    circ = list(data.values())[0]

    qiskitCirc2qcp(circ)
