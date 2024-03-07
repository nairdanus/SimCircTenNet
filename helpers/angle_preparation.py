import random

from qiskit.circuit import ParameterExpression
import cmath

def evaluate_angle(θ):
    """
    Evaluates the angle θ. Specifically for ParameterExpression containing
    variable for parameter to learn.
    :param θ: anything
    :return: float
    """
    if isinstance(θ, float):
        return θ

    if isinstance(θ, ParameterExpression):
        str(θ)  # TODO: lookup for training data
        return float(cmath.pi*random.random())

    raise NotImplementedError(f"Unsupported type {type(θ)} for an angle θ!")
