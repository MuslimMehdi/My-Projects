import random
import time

def brute_numbers(target, delay=0.05):
    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    result = ""
    i = 0

    while result != target:
        digit = random.choice(digits)
        guess = result + digit
        print(guess, end="\r", flush=True)
        time.sleep(delay)
        if digit == target[i]:
            result += digit
            i += 1
    print("\nDone:", result)

if __name__ == "__main__":
    i = input("Enter a number to simulate typing:\n")
    if not i.isdigit():
        print("Only numeric input is allowed!")
    else:
        brute_numbers(i)
