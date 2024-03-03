from lambeq import AtomicType, BobcatParser, TensorAnsatz
from lambeq.backend.tensor import Dim
from lambeq import PytorchModel
from helpers.data_preparation import get_data

def get_tensor_diagram(sent='This is an example sentence.'):
    parser = BobcatParser()
    pregroup_diagram = parser.sentence2diagram(sent)

    ansatz = TensorAnsatz({AtomicType.NOUN: Dim(2), AtomicType.SENTENCE: Dim(4)})
    tensor_diagram = ansatz(pregroup_diagram)

    tensor_diagram.draw()

    return tensor_diagram


tensor_diagrams = [get_tensor_diagram(x) for x in get_data("50_simple_gpt_sents")[:10]]

model = PytorchModel.from_diagrams(tensor_diagrams)

