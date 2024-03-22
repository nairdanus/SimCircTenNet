#!/bin/bash

# Set the directory path
directory="./Data"

file="single_sentence.txt"
pkl_file="single_sentence.pkl"


# Check if the directory exists
if [ ! -d "$directory" ]; then
  echo "Directory not found: $directory"
  exit 1
fi

cd "$directory"

read -p "Enter sentence: " choice

echo "$choice" > "$file"

cd ..

read -p "Enter the syntax model (pregroup, bagofwords, sequential): " chosen_syntax

read -p "Enter the Ansatz (iqp, sim14, sim15, StrongEnt): " chosen_ansatz

read -p "How many layers? " chosen_layers

read -p "How many qubits for sentences? " chosen_sents

read -p "How many qubits for nouns? " chosen_nouns

read -p "How many qubits for prepositional phrases? " chosen_prep

rm "string.png"
rm "circ.png"

source ./venv/bin/activate
python create_circuits.py --syntax "$chosen_syntax" --ansatz "$chosen_ansatz" --layers "$chosen_layers" --q_n "$chosen_nouns" --q_s "$chosen_sents" --dataset "$file" --filename "$pkl_file" --draw True

echo "Printing images..."
sleep 2
xdg-open "string.png"
sleep 2
if [ -d "createdSimulations/single_sentence" ]; then
  rm -rf createdSimulations/single_sentence
fi
./simulate.sh createdCircuits/single_sentence.pkl
./postprocess.sh createdSimulations/single_sentence
