#!/bin/bash

# Ask to provide a sentence

echo -n "Please type a sentence to reverse: "
read sentence

# Reverse the sentence word by word 

reversed_sentence=$(echo "$sentence" | awk '{ for(i=NF;i>0;i--) printf "%s ",$i}')

# Print the reversed sentence 
echo "Reversed sentence is: $reversed_sentence."

