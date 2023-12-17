#!/bin/bash 

# Generate random numbers from 1 to 100
secret_number=$((RANDOM % 100 + 1))
max_attempts=5
attempts=0

echo "Hi, welcome to "Guess the Number Game!", let's play! "

while [ $attempts -lt $max_attempts ]; do 
    # Get user's number
    read -p "Type your number between 1 and 100: " guess
    
    # Check if the guess is correct
    if [ $guess -eq $secret_number ]; then
        echo "Congradulations! You have guessed the right number!"
        exit 0
    elif [ $guess -lt $secret_number ]; then 
        echo "Too low number, please try again."
    else 
        echo "Too high number, please try again."
    fi

    # Increment the attempts
    ((attempts++))

done

#If there are no correct answers
echo "Sorry you have run out of your attempts. Please try again later. the correct number is: $secret_number. "
exit 0

