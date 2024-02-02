#Function for addition

def add(x, y):
    return x + y

#Function for subtraction

def subtract(x, y):
    return x - y

#Function for divide

def divide(x, y):
    if y == 0:
        return"Can't divide with 0"
    return x / y

#Function for multiply

def multiply(x, y):
    return x * y

#User guidlines
while True:
    print("Options:")
    print("Enter 'add' for addition")
    print("Enter 'subtract' for subtraction")
    print("Enter 'divide' for division")
    print("Enter 'multiply' for multiplication")
    print("Enter 'quit' to stop the program")

    user_input = input(": ")

    if user_input == "quit":
        break
    elif user_input in ["add", "subtract", "multiply", "divide"]:
        number1 = float(input("Enter your number: "))
        number2 = float(input("Enter your second number: "))
        
        if user_input == "add":
            print("Result: ", add(number1, number2))
        elif user_input == "subtract":
            print("Result: ", subtract(number1, number2))
        elif user_input == "divide":
            print("Result: ", divide(number1, number2))
        elif user_input == "multiply":
            print("Result: ", multiply(number1, number2))

    else:
        print("Wrong variables, please try again.")
