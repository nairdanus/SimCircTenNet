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


read -p "Enter the Ansatz (iqp, sim14, sim15, StrongEnt): " chosen_ansatz

read -p "How many layers? " chosen_layers

read -p "How many qubits for sentences? " chosen_sents

read -p "How many qubits for nouns? " chosen_nouns

read -p "How many qubits for prepositional phrases? " chosen_prep

source ./venv/bin/activate
python create_circuits.py --ansatz "$chosen_ansatz" --layers "$chosen_layers" --q_n "$chosen_nouns" --q_s "$chosen_sents" --dataset "$file" --filename "$pkl_file"
sleep 5
python draw_qiskit.py --path "$pkl_file"
echo "Printing image..."
sleep 2
open "output.png"

deactivate