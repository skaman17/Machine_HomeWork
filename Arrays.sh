#!/bin/bash

# Declare an array of fruits 

fruits=("Apple" "Banana" "Orange" "Grapes" "Strawberry")

# Loop through the array and print each fruit on a separate line

for fruit in "${fruits[@]}"; do
    echo "$fruit"
done

