import random
import os

from qiskit.circuit import ParameterExpression
import cmath

import yaml

ANGLE_FILE = os.environ.get("ANGLE_FILE")
if not ANGLE_FILE: ANGLE_FILE = "angles.yaml"

if not os.path.exists(ANGLE_FILE):
    if "createdParams" in ANGLE_FILE and not os.path.exists("createdParams/"):
        os.mkdir("createdParams/")
    with open(ANGLE_FILE, 'w') as yaml_file:
        yaml.dump(dict(), yaml_file)

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
        with open(ANGLE_FILE, 'r') as yaml_file:
            angles = yaml.safe_load(yaml_file)
        if not str(θ) in angles.keys():
            angles[str(θ)] = float(2*cmath.pi*random.random())

        with open(ANGLE_FILE, 'w') as yaml_file:
            yaml.dump(angles, yaml_file)

        return angles[str(θ)]

    raise NotImplementedError(f"Unsupported type {type(θ)} for an angle θ!")

def get_angles(angle_names: set[str]):
    with open(ANGLE_FILE, 'r') as yaml_file:
        angles = yaml.safe_load(yaml_file)

    return {n: angles[n] for n in angle_names}


def update_angles(updated_angles: dict[str, float]):
    with open(ANGLE_FILE, 'r') as yaml_file:
        angles = yaml.safe_load(yaml_file)

    for k, v in updated_angles.items():
        angles[k] = float(v)

    with open(ANGLE_FILE, 'w') as yaml_file:
        yaml.dump(angles, yaml_file)
