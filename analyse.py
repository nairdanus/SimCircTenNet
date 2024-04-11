import os

from helpers import get_chis, analyse_chis

def analyse_all():
    for f in os.listdir("createdChis"):
        if not f.endswith(".yaml"): continue
        f = os.path.join("createdChis", f)
        analyse_chis(f)


if __name__ == "__main__":
    get_chis("Alice loves Bob.", draw=True)
    get_chis("A quantum computer is a computer that takes advantage of quantum mechanical phenomena.", draw=True)
    get_chis("All animals are equal, but some animals are more equal than others.", draw=True)
    # analyse_all()