import random
import pickle

import numpy as np
import tensornetwork as tn
from math import sin, cos, e

from qiskit.circuit import ParameterExpression
from tqdm import tqdm

from QCPcircuit import QCPcircuit, Gate
from MPS.parseQCP import parseQCP
from helpers.angle_preparation import evaluate_angle
from typing import (Optional, Text)


class MPS_Simulator:
    """
    Self implemented MPS simulator.
    :param circ: circuit to simulate
    :param fidelity: 100 - fidelity = max_truncation_err allowed for SVD (100 fidelity means no error)
    :param 𝓧: maximal number of singular values to keep after SVD
    :param show_progress_bar: boolean to enable or disable progress bar
    :param circ_name: name of the output
    """

    shrink_after_measure = True

    def __init__(self, 
                 circ: QCPcircuit, 
                 fidelity: Optional[float] = None,
                 𝓧: Optional[int] = None,
                 show_progress_bar: Optional[bool] = False,
                 circ_name: Optional[Text] = "./trash",
                 post_selection: Optional[bool] = True):
        self.𝓧 = 𝓧
        self.threshold = None if not fidelity or fidelity == 100 else (100 - fidelity)/100
        self.circ = circ
        if circ is None: raise Exception("circ is None")
        self.circ_name = circ_name
        self.network = self.create_MPS()
        self.indices = list(range(len(self.network)))
        self.show_progress_bar = show_progress_bar
        self.measured_gates = set()
        self.unmeasured_gates = set()
        self.param_angles = set()
        self.real_𝓧s = []
        self.post_selection = post_selection


    def create_MPS(self):
        rank = self.circ.numQubits

        # edge case 1
        if rank < 2:
            mps = [tn.Node(np.array([[1], [0]], dtype=complex))]
            return mps

        mps = [tn.Node(np.array([[1], [0]], dtype=complex))] + \
            [tn.Node(np.array([[[1]], [[0]]], dtype=complex)) for _ in range(rank - 2)] + \
            [tn.Node(np.array([[1], [0]], dtype=complex))]

        for i in range(1, self.circ.numQubits-2):
            mps[i][2] ^ mps[i+1][1]

        if self.circ.numQubits < 3:
            mps[0][1] ^ mps[1][1]
        else:
            mps[0][1] ^ mps[1][1]
            mps[-1][1] ^ mps[-2][2]

        return mps

    def iterate_circ(self):
        if self.circ is None: raise Exception("circ is None")
        
        pbar = tqdm(self.circ.gates, ncols=100) if self.show_progress_bar else self.circ.gates
        skip = 0
        for i, g in enumerate(pbar):
            if self.post_selection and g.name == "measure":
                # TODO: add a check if circ ends in measurements.
                # TODO: Problem that you can have measure 0, cx 1 2, measure 1, measure 2
                # if not all(x.name == "measure" for x in pbar.iterable[i:]):
                #     raise NotImplementedError(
                #         "Postselection is set, but the circuit does not end in measure Gates.\n"
                #         "This is unexpected. Every circuit here should end with a measurement gate."
                #     )
                self.measured_gates.add(self.indices.index(g.target))
                if i+1 == len(pbar):
                    self.unmeasured_gates = set(range(self.circ.numQubits)).difference(self.measured_gates)
                    if self.show_progress_bar:
                        pbar.close()
                    break
                else:
                    continue

            """ Optimisation: if angles add to 0, skip them """
            if skip > 0:
                skip -= 1
                continue
            param = g.param
            if g.name in ["rx","ry","rz"]:
                name = g.name
                angle = g.param
                next = i + 1                
                while next < len(self.circ.gates) \
                    and self.circ.gates[next].name == name \
                    and self.circ.gates[next].target == g.target:
                    angle += self.circ.gates[next].param
                    next += 1
                    skip += 1
                param = angle
                if angle == 0:
                    continue
            """"""
            
            gate = Gate(g.name)
            gate.param = param

            if isinstance(param, ParameterExpression):
                self.param_angles.add(str(param))

            gate.control = self.indices.index(g.control) if g.control is not None else None
            gate.target = self.indices.index(g.target)

            if self.show_progress_bar:
                pbar.set_description(gate.name)
            getattr(self, gate.name)(gate)




    """
    ----------      RESULTS     -----------
    """

    def get_state_vector(self):
        if self.post_selection:
            return self.get_state_vector_post_selection()
        else:
            return self.get_state_vector_normal()

    def get_state_vector_normal(self):
        """
        Runs contract_mps and returns the state vector of the MPS.
        The order is corrected according to self.indices.
        """
        node = self.contract_mps()
        vec = np.reshape(node.tensor, newshape=(2**self.circ.numQubits))
        vec2 = np.copy(vec)
        indices = self.indices

        for i, _ in enumerate(vec):
            ii = 0
            for q in range(self.circ.numQubits):
                old = (i >> q) & 1
                q2 = indices.index(q)
                ii = ii | (old << q2)

            vec2[i] = vec[ii]

        return vec2

    def get_state_vector_post_selection(self):
        """
        Runs contract_mps_postselection and returns the tensor (should be scalar for binary classification).
        """
        node = self.contract_mps_postselection()
        return np.reshape(node.tensor, newshape=(2**len(self.unmeasured_gates)))

    def contract_mps(self) -> tn.Node:
        """
        Contracts all connected edges of the MPS.
        Returns a Node having as many edges as the MPS has.
        The edge order is not correct and needs to be corrected!
        The original MPS is kept in self.network.
        """
        mps = list(tn.copy(self.network)[0].values())

        # edge case 1
        if len(mps) < 2:
            return mps[0]

        """
        # also works
        mps.reverse()
        m = mps
        e = m.pop(0)
        for n in m:
        for n in m:
            e = e @ n
        result = e
        """

        mps.reverse()
        de = []
        for m in mps:
            de.append(m.get_all_dangling().pop())
        result = tn.contractors.auto(mps, output_edge_order=de)

        return result

    def contract_mps_postselection(self) -> tn.Node:
        """
        Contracts the MPS with the assumption that all measured nodes measured 0.
        Returns the contracted mps: one node with with len(unmeasured_gates) edges.
        The node should already have the correct edge_order.
        The original MPS is kept in self.network.
        """
        mps = list(tn.copy(self.network)[0].values())
        zero_nodes = []

        for mgi in self.measured_gates:
            node = tn.Node(np.array([1, 0], dtype=complex))
            node.edges[0] ^ mps[mgi].get_all_dangling()[0]
            zero_nodes.append(node)

        
        indices = reversed([i for i in self.indices if i in self.unmeasured_gates])
        de = []
        for i in indices:
            de.append(mps[i].get_all_dangling().pop())
        assert len(self.unmeasured_gates) == len(de), \
            "RESULT POSTSELECTION NOT WORKING. Number of dangling edges unequal to number of unmeasured gates."

        result = tn.contractors.auto(mps+zero_nodes, output_edge_order=de)

        return result


    def measure_states(self, states: list[str]) -> dict[str, float]:
        """
        Measure the probability of a given state.
        :param states: The states of the qubits. e.g. ["0001", "0010", "0011", "0100"]
        :return: A dictionary containing the probability of each state in the given states.
                e.g. {"0001": 0.1, "0010":0.2, ...}
        """
        output = dict()
        for state_string in states:
            state = list([int(i) for i in state_string])
            state = list(reversed(state))
            state = [state[self.indices.index(i)] for i, _ in enumerate(state)]

            mps = list(tn.copy(self.network)[0].values())
            vectorNodes = []
            for id, node in enumerate(mps):
                vector = [1,0] if state[id] == 0 else [0,1]
                vectorNode = tn.Node(np.array(vector, dtype=complex))

                vectorNode.edges[0] ^ node.get_all_dangling()[0]
                vectorNodes.append(vectorNode)

            result = tn.contractors.auto(mps+vectorNodes, ignore_edge_order=True)
            output[state_string] = abs(result.tensor.item())**2
        return output



    
    """
    ----------      GATES     -----------
    """
    def apply_gate(self, gate, target):
        gate_edge = gate[1]
        node = self.network[target]
        dangling = node.get_all_dangling()[0]
        new_edge = gate_edge ^ dangling
        self.network[target] = tn.contract(new_edge)

    def x(self, gate):
        node = tn.Node(np.array([[0, 1], [1, 0]], dtype=complex))
        self.apply_gate(node, gate.target)

    def y(self, gate):
        node = tn.Node(np.matrix([[0,-1j], [1j,0]], dtype=complex))
        self.apply_gate(node, gate.target)
    def z(self, gate):
        node = tn.Node(np.matrix([[1,0], [0,-1]], dtype=complex))
        self.apply_gate(node, gate.target)
    def h(self, gate):
        node = tn.Node(np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2))
        self.apply_gate(node, gate.target)

    def rx(self, gate):
        θ = evaluate_angle(gate.param)
        u = np.array([
            [cos(θ/2),-1j*sin(θ/2)],
            [-1j*sin(θ/2),cos(θ/2)]
        ], dtype=complex)
        node = tn.Node(u)
        self.apply_gate(node, gate.target)

    def ry(self, gate):
        θ = evaluate_angle(gate.param)
        u = np.array([
            [cos(θ/2),-sin(θ/2)],
            [sin(θ/2),cos(θ/2)]
        ], dtype=complex)
        node = tn.Node(u)
        self.apply_gate(node, gate.target)

    def rz(self, gate):
        θ = evaluate_angle(gate.param)
        u = np.array([
            [e ** (-1j * (θ/2)),0],
            [0,e ** (1j * (θ/2))]
        ], dtype=complex)
        node = tn.Node(u)
        self.apply_gate(node, gate.target)

    def swap(self, gate):
        u = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ], dtype=complex)
        uu = tn.Node(np.reshape(u, newshape=(2, 2, 2, 2)))

        ctl = gate.control
        tgt = gate.target

        flip = ctl > tgt
        if flip:
            uu.reorder_edges([uu[1],uu[0],uu[3],uu[2]])
            tgt, ctl = ctl, tgt

        self.multi_qubit_gate(ctl, tgt, uu)

    def cx(self, gate):
        u = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        uu = tn.Node(np.reshape(u, newshape=(2, 2, 2, 2)))
        self.controlled(gate, uu)

    def crx(self, gate):
        θ = evaluate_angle(gate.param)
        u = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, cos(θ / 2), -1j * sin(θ / 2)],
            [0, 0, -1j * sin(θ / 2), cos(θ / 2)]
        ], dtype=complex)
        uu = tn.Node(np.reshape(u, newshape=(2, 2, 2, 2)))
        self.controlled(gate, uu)

    def cy(self, gate):
        u = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, -1j],
            [0, 0, 1j, 0]
        ], dtype=complex)
        uu = tn.Node(np.reshape(u, newshape=(2, 2, 2, 2)))
        self.controlled(gate, uu)

    def cry(self, gate):
        θ = evaluate_angle(gate.param)
        u = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, cos(θ / 2), -sin(θ / 2)],
            [0, 0, sin(θ / 2), cos(θ / 2)]
        ], dtype=complex)
        uu = tn.Node(np.reshape(u, newshape=(2, 2, 2, 2)))
        self.controlled(gate, uu)


    def cz(self, gate):
        u = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, -1]
        ], dtype=complex)
        uu = tn.Node(np.reshape(u, newshape=(2, 2, 2, 2)))
        self.controlled(gate, uu)

    def crz(self, gate):
        θ = evaluate_angle(gate.param)
        u = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, e ** (-1j * (θ / 2)), 0],
            [0, 0, 0, e ** (1j * (θ / 2))]
        ], dtype=complex)
        uu = tn.Node(np.reshape(u, newshape=(2, 2, 2, 2)))
        self.controlled(gate, uu)


    def controlled(self, gate, uu):
        ctl = gate.control
        tgt = gate.target

        flip = ctl > tgt
        if flip:
            uu.reorder_edges([uu[1],uu[0],uu[3],uu[2]])
            tgt, ctl = ctl, tgt
        self.multi_qubit_gate(ctl, tgt, uu)

    def multi_qubit_gate(self, ctl, tgt, uu, index_optim = True):
        def get_swap():
            swap = np.array([
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
            ], dtype=complex)
            s = tn.Node(np.reshape(swap, newshape=(2, 2, 2, 2)))
            return s

        goto = tgt - 1
        start = ctl
        for i in range(start, goto):
            self.multi_qubit_gate_low(i, i+1, get_swap())
            if index_optim:
                self.indices[i], self.indices[i + 1] = self.indices[i + 1], self.indices[i]
                if self.post_selection and (intersect := self.measured_gates.intersection({i, i + 1})):
                    if len(intersect) == 2:
                        pass
                    elif i in self.measured_gates:
                        self.measured_gates.remove(i)
                        self.measured_gates.add(i+1)
                    elif i+1 in self.measured_gates:
                        self.measured_gates.remove(i+1)
                        self.measured_gates.add(i)

        assert goto+1 == tgt
        self.multi_qubit_gate_low(goto, goto+1, uu)

        if not index_optim:
            for i in range(goto-1,start-1,-1):
                self.multi_qubit_gate_low(i, i+1, get_swap())

    def multi_qubit_gate_low(self, ctl, tgt, uu):
        if abs(ctl - tgt) != 1:
            raise Exception("cx != 1")

        node1 = self.network[ctl]
        node2 = self.network[tgt]

        node1.get_all_dangling()[0] ^ uu.edges[2]
        node2.get_all_dangling()[0] ^ uu.edges[3]

        new_node = node1 @ node2 @ uu
        """
        also works:
        tmp1 = node1 @ node2
        temp_edge = tn.flatten_edges_between(uu, tmp1)
        new_node = tn.contract(temp_edge)
        """
        """
        # also works
        oeo = []        
        oeo += filter(lambda e: not set(e.get_nodes()) & {uu, node2}, node1.edges)
        oeo += [uu.edges[0], uu.edges[1]]
        oeo += filter(lambda e: not set(e.get_nodes()) & {uu, node1}, node2.edges)
        new_node = tn.contractors.auto([node1, node2, uu], output_edge_order=oeo)
        """

        dangling = list(new_node.get_all_dangling())
        def gand(n): return [e for e in n.edges if not e.is_dangling()]
        non_dangling = list(gand(new_node))

        if len(self.network) == 2:
            l = [dangling[0]]
            r = [dangling[1]]
        elif min(ctl, tgt) == 0:
            l = [dangling[0]]
            r = [dangling[1], non_dangling[0]]
        elif max(ctl, tgt) == len(self.network) - 1:
            l = [dangling[0], non_dangling[0]]
            r = [dangling[1]]
        else:
            l = [dangling[0], non_dangling[0]]
            r = [dangling[1], non_dangling[1]]

        try:
            u, vh, trun_vals = tn.split_node(new_node, left_edges=l, right_edges=r,
                                             max_truncation_err=self.threshold,
                                             max_singular_values=self.𝓧)
                                             
            # self.real_𝓧s.append(max(u.tensor.shape)+len(trun_vals))
            self.real_𝓧s.append(max(u.tensor.shape))

        except np.linalg.LinAlgError as LinAlgError:
            print("Following tensor did not converge:")
            print(new_node.tensor)
            print("Min: ", new_node.tensor.min())
            print("Max: ", new_node.tensor.max())
            print("NaN at indices: ", np.argwhere(np.isnan(new_node.tensor)))
            
            # new_node.tensor.tofile("LINALG_ERROR.txt")
            raise LinAlgError

        self.network[ctl] = u
        self.network[tgt] = vh


    def measure(self, gate):
        """
        Applies the measurement gate.
        """
        mps = list(tn.copy(self.network)[0].values())
        mps_2 = list(tn.copy(self.network)[0].values())
        measure_node = tn.Node(np.array([[1, 0], [0, 0]], dtype=complex))
        for i in range(len(mps)):
            m, m1 = mps[i], mps_2[i]
            m1.set_tensor(np.conj(m1.tensor))
            if i == gate.target:
                m.get_all_dangling()[0] ^ measure_node.edges[0]
                m1.get_all_dangling()[0] ^ measure_node.edges[1]
            else:
                m.get_all_dangling()[0] ^ m1.get_all_dangling()[0]

        prob_0_tgt = abs(tn.contractors.auto(mps + mps_2 + [measure_node], ignore_edge_order=True).tensor.item())
        # measured = random.choices([0,1], [prob_0_tgt, 1-prob_0_tgt])[0]
        measured = 0
        update_value = np.sqrt(prob_0_tgt) if measured == 0 else np.sqrt(1-prob_0_tgt)
        if measured == 0:
            update_matrix = np.array([[1/update_value,0], [0,0]], dtype=complex)
        else:
            update_matrix = np.array([[0, 0], [0, 1/update_value]], dtype=complex)

        update_node = tn.Node(update_matrix)
        update_node.edges[0] ^ self.network[gate.target].get_all_dangling()[0]

        new_node = update_node @ self.network[gate.target]
        self.network[gate.target] = new_node

        if not self.shrink_after_measure:
            return

        # shrink tensors
        for x in [i for i, n in enumerate(self.network) if n != new_node]:
            eye = tn.Node(np.reshape(np.eye(4, dtype=complex), newshape=(2, 2, 2, 2)))
            ctl = x
            tgt = gate.target
            flip = ctl > tgt
            if flip:
                tgt, ctl = ctl, tgt
            self.multi_qubit_gate(ctl, tgt, eye, index_optim = False)


    def renormalize(self):
        # TODO: NOT WORKING !
        mps = list(tn.copy(self.network)[0].values())
        mps_2 = list(tn.copy(self.network)[0].values())
        for i in range(len(mps)):
            m, m1 = mps[i], mps_2[i]
            m1.set_tensor(np.conj(m1.tensor))
            m.get_all_dangling()[0] ^ m1.get_all_dangling()[0]
        update_value = abs(tn.contractors.auto(mps + mps_2, ignore_edge_order=True).tensor.item())
        for node in self.network:
            node.set_tensor(node.tensor / update_value)

if __name__ == "__main__":

    import sys

    print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)

    def test_total_prob(p, fidelity=100, 𝓧=None):
        c = parseQCP(p + ".qcp")
        simulator = MPS_Simulator(c, fidelity, 𝓧)
        simulator.iterate_circ()

        mps = list(tn.copy(simulator.network)[0].values())
        mps_2 = list(tn.copy(simulator.network)[0].values())
        for i in range(len(mps)):
            m, m1 = mps[i], mps_2[i]
            m1.set_tensor(np.conj(m1.tensor))
            m.get_all_dangling()[0] ^ m1.get_all_dangling()[0]
        aaa = tn.contractors.auto(mps+mps_2, ignore_edge_order=True)
        print("Total probability: ", abs(aaa.tensor.item()))

    def test_result(p, fidelity=100, 𝓧=None):
        c = parseQCP(p + ".qcp")
        simulator = MPS_Simulator(c, fidelity, 𝓧)
        simulator.iterate_circ()
        result = simulator.contract_mps()
        r = simulator.get_state_vector(result)
        from helpers import v2s
        print(v2s(r))

    test_total_prob("./challenge/qf21_n15", 𝓧=3)