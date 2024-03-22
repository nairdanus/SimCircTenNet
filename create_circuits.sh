#!/bin/bash

# Set the directory path
directory="./Data"
# Check if the directory exists
if [ ! -d "$directory" ]; then
  echo "Directory not found: $directory"
  exit 1
fi

cd "$directory"
datasets=(*)
echo "please enter a dataset (choose from the following)"
for ((i=0; i<${#datasets[@]}; i++)); do
  echo "$((i+1)) ${datasets[i]}"
done


read -p "Enter dataset (number): " choice

# Validate the input
if [[ ! "$choice" =~ ^[0-9]+$ || "$choice" -lt 1 || "$choice" -gt ${#datasets[@]} ]]; then
  echo "Invalid choice. Please enter a valid number."
  exit 1
fi

# Get the selected file
selected_file="${datasets[$((choice-1))]}"

cd ..


read -p "Enter the syntax model (pregroup, bagofwords, sequential): " chosen_syntax

read -p "Enter the Ansatz (iqp, sim14, sim15, StrongEnt): " chosen_ansatz

read -p "How many layers? " chosen_layers

read -p "How many qubits for sentences? " chosen_sents

read -p "How many qubits for nouns? " chosen_nouns

read -p "How many qubits for prepositional phrases? " chosen_prep

source ./venv/bin/activate
command="python create_circuits.py --syntax $chosen_syntax --ansatz $chosen_ansatz --layers $chosen_layers --q_n $chosen_nouns --q_s $chosen_sents --dataset $selected_file"

for arg in "$@"; do
    if [[ "$arg" == "-i" ]]; then
        command+=" --draw True" 
        break
    fi
done

eval $command
deactivate