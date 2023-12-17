#!/bin/bash


# Check if the correct number of arguments is provided

if [ "$#" -ne 2 ]; then 
    echo "Usage: $0 <source_file> <destination_directory>"
    exit 1
fi

# Assign the arguments to variables 

source_file="$1"
destination_directory="$2"

# Check if the source file is exist

if [ ! -f "$source_file" ]; then
    echo "Error: Source file '$source_file' doesn't exists."
    exit 1
fi

# Check if the destination directory exists

if [ ! -d "$destination_directory" ]; then 
    echo "Error: Destination directory '$destination_directory' doesn't exists"
    exit 1
fi


# Copy the file to the destination directory

cp "$source_file" "$destination_directory"


# Check if the file we copied existing in destination directory

copied_file="$destination_directory/$(basename "$source_file")"
if [ -f "$copied_file" ]; then
    echo "File '$source_file' successfully copied to '$destination_directory'."
else
    echo "Error: File '$source_file' could not be copied to '$destination_directory'."
fi


