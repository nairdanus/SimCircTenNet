#!/bin/bash

# Set the directory path
directory="./createdSimulations"
# Check if the directory exists
if [ ! -d "$directory" ]; then
  echo "Directory not found: $directory"
  exit 1
fi

cd "$directory"
circs=(*)
echo "Please enter which simulations to process (choose from the following)"
for ((i=0; i<${#circs[@]}; i++)); do
  echo "$((i+1)) ${circs[i]}"
done
read -p "Enter a directory (number): " choice
# Validate the input
if [[ ! "$choice" =~ ^[0-9]+$ || "$choice" -lt 1 || "$choice" -gt ${#circs[@]} ]]; then
  echo "Invalid choice. Please enter a valid number."
  exit 1
fi
# Get the selected directory
selected_dir="${circs[$((choice-1))]}"
cd ..


source venv/bin/activate
command="python postprocess_circuits.py --dir $selected_dir"
eval $command
deactivate