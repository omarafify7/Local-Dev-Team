# Step 1: Initialize an empty list to store Fibonacci numbers
fibonacci_numbers = []

# Step 2: Set the first two Fibonacci numbers
a, b = 0, 1

# Step 3: Append these two numbers to the list
fibonacci_numbers.append(a)
fibonacci_numbers.append(b)

# Step 4: Use a loop to calculate the next 8 Fibonacci numbers
for _ in range(8):
    # Calculate the next number by summing the last two numbers in the list
    try:
        next_number = fibonacci_numbers[-1] + fibonacci_numbers[-2]
    except IndexError as e:
        print(f"Error calculating next Fibonacci number: {e}")
        break
    # Append this new number to the list
    fibonacci_numbers.append(next_number)

# Step 5: Convert the list of Fibonacci numbers to a comma-separated string
try:
    fibonacci_sequence = ', '.join(map(str, fibonacci_numbers))
except Exception as e:
    print(f"Error converting list to string: {e}")
    fibonacci_sequence = ""

# Step 6: Print the resulting string
print(fibonacci_sequence)
