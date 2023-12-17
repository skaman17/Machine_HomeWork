#!/bin/bash

# Check if a filename is provided as a command line argument

if [ "$#" -ne 1 ]; then 
    echo "Usage: $0 <filename>"
    exit 1 
fi

filename="$1"

# Check if the file exists

if [ ! -f "$filename" ]; then
    echo "Error: file '$filename' doesn't exist."
    exit 1
fi

# Use the wc command to count the number of lines in the file

line_count=$(wc -l < "$filename")

# Print the number of lines

echo "Number of lines in '$filename': $line_count."
