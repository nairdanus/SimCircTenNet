class Gate:
    def __init__(self, name):
        self.name = name
        self.param = None
        self.target = None
        self.control = None

    def __repr__(self):
        return self.name

    def __str__(self):
        str = self.name
        if (self.param is not None): str += f"({self.param})"
        if (self.control is not None): str += f" {self.control}"
        if (self.target is not None): str += f" {self.target}"
        return str


class QCPcircuit:
    def __init__(self) -> None:
        self.numQubits = None
        self.gates = []

    def __str__(self):
        str = f"{self.numQubits}\n"
        str += "\n".join([i.__str__() for i in self.gates])
        return str