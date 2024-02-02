# Define the list 

fruits = ["banana", "strawberry", "apple", "peach"]

# Element to check

check_el = input("What is your fruit: ")

# Check if element is in a list

if check_el in fruits:
    print(f"Hey, '{check_el}' is in the list!")
else:
    print(f"I'm sorry, '{check_el}' is not in the list!")
