import os
import sys

from helpers import get_chis, analyse_chis

def analyse_all(subdir=""):
    for f in os.listdir(os.path.join("createdChis", subdir)):
        if not f.endswith(".yaml"): continue
        f = os.path.join("createdChis", subdir, f)
        analyse_chis(f)


if __name__ == "__main__":

    usage_message = f"Usage: \n{sys.argv[0]} run [sentence...] | eval [dir...]"

    if len(sys.argv) < 2: print(usage_message); exit(1)

    match sys.argv[1]:

        case "run":
            if len(sys.argv) == 2:
                sents = [
                    "Alice loves Bob.",
                    "A quantum computer is a computer that takes advantage of quantum mechanical phenomena.",
                    "All animals are equal, but some animals are more equal than others.",
                ]
            else:
                sents = sys.argv[2:]
            for s in sents:
                get_chis(s, draw=True)

        case "eval":
            if len(sys.argv) == 2:
                analyse_all()
            else:
                for subdir in sys.argv[2:]:
                    analyse_all(subdir)

        case _:
            print(usage_message)
            exit(1)
