from lambeq import BobcatParser, spiders_reader, cups_reader
from lambeq import AtomicType, IQPAnsatz, Sim14Ansatz, Sim15Ansatz, StronglyEntanglingAnsatz
from pytket.extensions.qiskit import tk_to_qiskit

from tqdm.auto import tqdm

from helpers import data_preparation



class DisCoCat():
    """
    Based on the chosen syntax model and ansatz, this class creates qiskit circuits for a dataset.
    The output is saved in self.circuits as list(tuple(data, qiskit_circuit)).
    
    """
    def __init__(self, 
                 syntax_model: str, 
                 dataset_name: str, 
                 ansatz: str, 
                 n_layers: int, 
                 q_s: int, 
                 q_n: int, 
                 q_np: int,
                 q_pp: int,
                 q_c: int,
                 q_punc: int,
                 n_single_q: int = 12,
                 disable_tqdm = False):
        """

        :param syntax_model: Choose the syntax model that should be used
                            Options: Pregroup Grammar ('pregroup'), Bag-of-words ('bow') or Word-Sequence ('seq')
        :param dataset_name: The name of the dataset e.g. 100_animals_plants
        :param ansatz: Choose the ansatz that should be used
                        Options: iqp, sim14, sim15, strongent
        :param n_layers: Number of layers
        :param q_s: Number of qubits for sentence type
        :param q_n: Number of qubits for noun type
        :param q_pp: Number of qubits for prepositional phrase type
        """
        self.data = data_preparation.get_data(dataset_name)

        self.disable_tqdm = disable_tqdm

        match syntax_model.lower():
            case "pre" | "pregroup" | "bobcat":
                self.parser = BobcatParser(verbose='text')
            case "bow" | "bagofwords" | "bag-of-words":
                self.parser = spiders_reader
            case "seq" | "sequential":
                self.parser = cups_reader
            case other:
                raise ValueError(f"{other} is not a valid syntax model! Try pregroup, bow or seq.")

        ob_map = {
            AtomicType.SENTENCE: q_s,
            AtomicType.NOUN: q_n,
            AtomicType.NOUN_PHRASE: q_np,
            AtomicType.PREPOSITIONAL_PHRASE: q_pp,
            AtomicType.CONJUNCTION: q_c,
            AtomicType.PUNCTUATION: q_punc,
        }
        match ansatz.lower():
            case "iqp":
                self.ansatz = IQPAnsatz(ob_map, n_layers=n_layers, n_single_qubit_params=n_single_q)
            case "sim14":
                self.ansatz = Sim14Ansatz(ob_map, n_layers=n_layers, n_single_qubit_params=n_single_q)
            case "sim15":
                self.ansatz = Sim15Ansatz(ob_map, n_layers=n_layers, n_single_qubit_params=n_single_q)
            case "strongent" | "se":
                self.ansatz = StronglyEntanglingAnsatz(ob_map, n_layers=n_layers, n_single_qubit_params=n_single_q)
            case other:
                raise ValueError(f"{other} is not a valid Ansatz! Try iqp, sim14, sim15 or strongent.")

        self.string_diagrams = self.get_string_diagrams()
        self.circuit_diagrams = self.get_circuit_diagrams()
        self.qiskit_circuits = [tk_to_qiskit(circ.to_tk()) for circ in tqdm(self.circuit_diagrams,
                                                                            total=len(self.circuit_diagrams),
                                                                            desc="Translating diagrams to Qiskit",
                                                                            ncols=150,
                                                                            disable=self.disable_tqdm)]

        self.circuits = list(zip(self.data, self.qiskit_circuits))

    def get_string_diagrams(self):
        data_iter = tqdm(self.data,
                         total=len(self.data),
                         desc="Parsing sentences",
                         ncols=150,
                         disable=self.disable_tqdm)
        if all(isinstance(s, str) for s in self.data):
            return [self.parser.sentence2diagram(sent) for sent in data_iter]
        if all(isinstance(s, tuple) and len(s) == 2 for s in self.data):
            return [self.parser.sentence2diagram(sent) for sent, _ in data_iter]

        raise NotImplementedError("The data is heterogeneous or this type of data is not implemented!")

    def get_circuit_diagrams(self):
        return [self.ansatz(sent) for sent in tqdm(self.string_diagrams,
                                                   total=len(self.string_diagrams),
                                                   desc="Generating circuits",
                                                   ncols=150,
                                                   disable=self.disable_tqdm)]



if __name__ == "__main__":
    disCoCat = DisCoCat(dataset_name="10_animals_plants", ansatz="iqp", n_layers=1, q_s=1, q_n=1, q_p=1)

    disCoCat.qiskit_circuits[0].draw(output='mpl', filename='disCoCat.png')
