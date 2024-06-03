# SimCircTenNet
Simulating Circuits in Quantum Natural Language Processing using Tensor Networks

## Setup
```bash
    python -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt
```

## Test Single Sentence
To test the output for a single sentence run the following and see result images ("circ.png", "string.png"). The simulation output will be printed out.
```bash
    bash ./single_sent.sh
```


## Training
Set the hyperparameters for training in main.py and then run:
```bash
    source ./venv/bin/activate
    python main.py
```


## Complexity Analysis
Run the analyse.py script and specify the hyperparameters in chi.py
