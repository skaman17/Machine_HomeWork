#!/bin/bash

# Check if a filename is provided as a command line argument

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

filename="$1"

# Check if the file exists

if [ ! -f "$filename" ]; then
    echo "Error: File '$filename' doesn't exists."
    exit 1
fi

# Attemp to read the file and print it's contents

if content=$(cat "$filename" 2>/dev/null); then
    echo "File contents of '$filename':"
    echo "$content"

else 
    echo "Error: Unable to read the contents of '$filename'."
    exit 1
fi

    
