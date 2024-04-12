import os
from collections import defaultdict 
import yaml
import matplotlib.pyplot as plt
from tqdm import tqdm
import time

from simulate_circuits import simulate_single_circuit
from DisCoCat import DisCoCat
from helpers import qiskitCirc2qcp

def get_chis(sentence: str, n_layers=3, draw=False) -> str:
    """
    Takes a sentence and then simulates different circuits for that sentence.
    These circuits are then simulated with different circuit widths.
    The results are written in createdChis/sentence.yaml. This path is returned.
    """
    with open("Data/chi_test.txt", "w") as f: f.write(sentence)
    if not os.path.exists("createdChis"): os.mkdir("createdChis")
    output = defaultdict(dict)
    output["meta"] = {
        "sentence": sentence,
        "numLayers": n_layers,
    }

    valid_chars = '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    out_file_name = os.path.join("createdChis", ''.join(c for c in sentence[:255].strip().replace(" ", "_") if c in valid_chars) + ".yaml")
    
    test_set = list(range(1, 16))

    if os.path.exists(out_file_name):
        confirmation = input(f"Do you want to overwrite {sentence}? [yes/no]")
        match confirmation:
            case "yes" | "y":
                print(f"Overwriting {sentence}...")
            case _:
                exit(1)

    for param in tqdm(test_set):

        start = time.time()

        d = DisCoCat(syntax_model="pre",
                    dataset_name="chi_test",
                    ansatz="iqp",
                    n_layers=n_layers,
                    disable_tqdm=True,
                    q_s=1,
                    q_n=param, 
                    q_np=param,
                    q_pp=param, 
                    q_c=param,
                    q_punc=param,
                    )
        if draw and param < 10:
            draw_path = out_file_name.replace(".yaml", "")
            if not os.path.exists(draw_path): os.mkdir(draw_path)
            if param == test_set[0]: 
                d.string_diagrams[0].draw(path=os.path.join(draw_path, "string.png"))
            d.circuits[0][1].draw("mpl", filename=os.path.join(draw_path, f"{param}_circ.png"))

        circ = qiskitCirc2qcp(d.circuits[0][1])

        simulator = simulate_single_circuit(circ)

        output[param] = {
            "numQubits": circ.numQubits,
            "chi": {
                "all": simulator.real_𝓧s,
                "avg": sum(simulator.real_𝓧s) / len(simulator.real_𝓧s) if simulator.real_𝓧s else 0,
                "max": max(simulator.real_𝓧s) if simulator.real_𝓧s else 0
                },
            "numAngles": len(simulator.param_angles),
            "duration": time.time() - start,
        }
        with open(out_file_name, "w") as f:
            yaml.dump(dict(output), f)

    os.remove("Data/chi_test.txt")

    return out_file_name


def analyse_chis(file_name):
    with open(file_name, 'r') as file:
        data = yaml.safe_load(file)

    # Extract x and y data
    x1 = []
    x2 = []
    chi_max = []
    chi_avg = []
    sentence = data["meta"]["sentence"]

    for key, value in data.items():
        if key == "meta": continue
        x1.append(int(key))
        x2.append(value['numQubits'])
        chi_max.append(value['chi']['max'])
        chi_avg.append(value['chi']['avg'])
    
    # Plot
    fig, ax1 = plt.subplots()

    # Plot Chi Max and Chi Avg on primary y-axis
    ax1.plot(x2, chi_max, label='Chi Max')
    ax1.plot(x2, chi_avg, label='Chi Avg')
    ax1.set_xlabel('Circuit Width')
    ax1.set_ylabel('Chi Value')
    ax1.set_title(sentence + f"\n{data['meta']['numLayers']} Layers")
    ax1.legend()

    # Create a secondary x-axis with custom labels below the primary x-axis
    ax2 = ax1.twiny()
    ax2.set_xticks(x2)
    ax2.set_xticklabels(x1)
    ax2.set_xlabel('Atomic Types')

    plt.show()