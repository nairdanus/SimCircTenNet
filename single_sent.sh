#!/bin/bash

# Set the directory path
directory="./Data"

# Check if the directory exists
if [ ! -d "$directory" ]; then
  echo "Directory not found: $directory"
  exit 1
fi

cd "$directory"

read -p "Enter sentence: " choice

echo "$choice" > "single_sentence.txt"

cd ..

./create_circuits.sh "single_sentence" -i -s
echo "Printing images..."
sleep 2
xdg-open "string.png"
sleep 2

./simulate.sh createdCircuits/single_sentence.pkl
./postprocess.sh createdSimulations/single_sentence
