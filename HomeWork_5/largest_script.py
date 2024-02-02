# Define the name of a file
file_name = str(input("Name of a file: "))

try: 
    # Open file for check
    with open(file_name, "r") as file: 
        # Chech the numbers from the file and convert them into integers
         numbers = [int(line.strip()) for line in file.readlines()]

    if not numbers:
        print("File is empty.")
    else:
        # Look up for the largest number in the file:
        largest_number = max(numbers)
        print("The largest number is: ", largest_number)

except FileNotFoundError:
    print(f"The file '{file_name}'is not found.")
except ValueError:
    print("Error. The file contains non-integer values")
except Exception as e:
    print(f"An error occured: {str(e)}")
