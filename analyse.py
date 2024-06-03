import os
import sys

from helpers import get_chis, analyse_chis, analyse_layers

def analyse_all(subdir=""):
    for f in os.listdir(os.path.join("createdChis", subdir)):
        if not f.endswith(".yaml"): continue
        f = os.path.join("createdChis", subdir, f)
        analyse_chis(f)


if __name__ == "__main__":
    args = sys.argv

    usage_message = f"Usage: \n{args[0]} run [-layer int] [sentence...] | eval [dir...] | eval_layers file"

    if len(args) < 2: print(usage_message); exit(1)

    match args[1]:

        case "run":
            if '-layer' in args:
                layer_index = args.index('-layer')
                if layer_index + 1 < len(args):
                    layer_value = args[layer_index + 1]
                    try:
                        n_layers = int(layer_value)
                        args = args[:layer_index-1] + args[layer_index+1:]
                    except ValueError: print(usage_message); exit(1)
                else:
                    print(usage_message); exit(1)
            else:
                n_layers = 3

            if len(args) == 2:
                sents = [
                    "Alice loves Bob.",
                    "A quantum computer is a computer that takes advantage of quantum mechanical phenomena.",
                    "All animals are equal, but some animals are more equal than others.",
                ]
            else:
                sents = args[2:]
            for s in sents:
                get_chis(s, draw=True, n_layers=n_layers)

        case "eval":
            if len(args) == 2:
                analyse_all()
            else:
                for subdir in args[2:]:
                    analyse_all(subdir)

        case "eval_layers":
            if len(args) == 2:
                print(usage_message)
                exit(1)
            else:
                analyse_layers(file_name=args[2])

        case _:
            print(usage_message)
            exit(1)
