#!/bin/bash

# Check if -s (for Single sentence) and -i (for save Images) is given
found_s=false
found_i=false
for arg in "$@"; do
    if [ "$arg" = "-s" ]; then
        found_s=true
    fi
    if [ "$arg" = "-i" ]; then
        found_i=true
    fi
done

if [ -z "$1" ]; then
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
    echo "$((i+1)))  ${datasets[i]}"
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
else
  selected_file="$1"
fi

PS3="Enter the syntax model number: "
options=("pregroup" "bag-of-words" "sequential")
select chosen_syntax in "${options[@]}"; do
    case $chosen_syntax in
        "pregroup")
            echo "You chose pregroup"
            break
            ;;
        "bag-of-words")
            echo "You chose bag-of-words"
            break
            ;;
        "sequential")
            echo "You chose sequential"
            break
            ;;
        *)
            echo "Invalid option. Please select a number from 1 to 3."
            ;;
    esac
done

PS3="Enter the Ansatz number: "
options=("iqp" "sim14" "sim15" "StrongEnt")
select chosen_ansatz in "${options[@]}"; do
    case $chosen_ansatz in
        "iqp")
            echo "You chose iqp"
            break
            ;;
        "sim14")
            echo "You chose sim14"
            break
            ;;
        "sim15")
            echo "You chose sim15"
            break
            ;;
        "StrongEnt")
            echo "You chose StrongEnt"
            break
            ;;
        *)
            echo "Invalid option. Please select a number from 1 to 4."
            ;;
    esac
done

read -p "How many layers? " chosen_layers

read -p "How many qubits for sentences? " chosen_sents

read -p "How many qubits for nouns? " chosen_nouns

read -p "How many qubits for prepositional phrases? " chosen_prep

command="python create_circuits.py --syntax $chosen_syntax --ansatz $chosen_ansatz --layers $chosen_layers --q_n $chosen_nouns --q_s $chosen_sents --dataset $selected_file"

if [ "$found_s" = true ]; then
  command+=" --filename single_sentence.pkl"
fi
if [ "$found_i" = true ]; then
  command+=" --draw True"
fi

source ./venv/bin/activate
eval $command
deactivate