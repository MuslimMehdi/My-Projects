import random
import time
import string

def brute_hello(target, delay=0.05):
    alphabet = list(string.ascii_lowercase + " ")
    result = ""
    i = 0

    while result != target:
        letter = random.choice(alphabet)
        guess = result + letter
        print(guess, end="\r", flush=True)
        time.sleep(delay)
        if letter == target[i]:
            result += letter
            i += 1
            alphabet = list(string.ascii_lowercase + " ")
    print("\nDone:", result)

if __name__ == "__main__":
    i= input ("Enter what u want to type:\n")
    brute_hello(i.lower())