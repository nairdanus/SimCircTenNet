#!/bin/bash
if [ -z "$1" ]; then
  # Set the directory path
  directory="./createdCircuits"
  # Check if the directory exists
  if [ ! -d "$directory" ]; then
    echo "Directory not found: $directory"
    exit 1
  fi

  cd "$directory"
  circs=(*)
  echo "Please enter which circuits to simulate (choose from the following)"
  for ((i=0; i<${#circs[@]}; i++)); do
    echo "$((i+1)))  ${circs[i]}"
  done
  read -p "Enter a pickle file (number): " choice
  # Validate the input
  if [[ ! "$choice" =~ ^[0-9]+$ || "$choice" -lt 1 || "$choice" -gt ${#circs[@]} ]]; then
    echo "Invalid choice. Please enter a valid number."
    exit 1
  fi
  # Get the selected file
  selected_file="${circs[$((choice-1))]}"
  cd ..

else
  selected_file="$1"
fi


PS3="Enter the Simulator number: "
options=("Personal_MPS" "Qiskit_MPS")
select chosen_ansatz in "${options[@]}"; do
    case $chosen_ansatz in
        "Personal_MPS")
            echo "You chose my personal MPS"
            break
            ;;
        "Qiskit_MPS")
            echo "You chose Qiskit's AerSimulator MPS"
            break
            ;;
        *)
            echo "Invalid option. Please select a number from 1 to 4."
            ;;
    esac
done

read -p "Enter fidelity: " fidelity

read -p "Enter 𝓧: " chi

source venv/bin/activate
command="python simulate_circuits.py $chosen_simulator --file $selected_file"
if [ -n "$fidelity" ]; then
    command+=" --fidelity $fidelity"
fi

if [ -n "$chi" ]; then
    command+=" --chi $chi"
fi
eval $command
deactivate