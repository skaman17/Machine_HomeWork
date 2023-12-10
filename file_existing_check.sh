#!/bin/bash

# Ask the user for the filename 

echo -n "Enter filename to check: "
read file_name

# Che if the file is existing in current directory

if [ -e "$file_name" ]; then
    echo "File '$file_name' exists in the current directory."
else
    echo "File '$file_name' doesn't exists in current directory."
fi
