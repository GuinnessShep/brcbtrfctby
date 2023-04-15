#!/bin/bash

# Find and install Python requirements files
find_requirements() {
    for entry in "$1"/*; do
        if [[ -d "$entry" ]]; then
            find_requirements "$entry"
        elif [[ -f "$entry" ]] && [[ "${entry##*/}" == "requirements.txt" ]]; then
            echo "Installing requirements from $entry"
            pip install -r "$entry"
        fi
    done
}

echo "Searching for and installing requirements.txt files in subdirectories..."
find_requirements "$(pwd)"

echo "All requirements installed."
