from decimal import Decimal, getcontext
from math import factorial

def chudnovsky_pi(digits):
    """
    Compute π using the Chudnovsky algorithm to the specified number of digits.
    :param digits: Number of decimal digits of π to compute.
    :return: Computed value of π.
    """
    # Set precision for decimal calculations
    getcontext().prec = digits + 2  # Extra digits for internal precision

    # Constants in the Chudnovsky algorithm
    C = 426880 * Decimal(10005).sqrt()
    M, L, X, K = 1, 13591409, 1, 6
    S = L  # Initial value of the series sum

    for i in range(1, digits):
        M = (M * (12 * i - 11) * (12 * i - 5) * (12 * i - 1)) // (i ** 3)
        L += 545140134
        X *= -262537412640768000  # (-640320)^3
        S += Decimal(M * L) / X

    π = C / S
    return +π  # Unary + applies the precision context

# Example Usage
if __name__ == "__main__":
    digits = int(input("Enter the number of decimal digits of π to compute: "))
    pi_value = chudnovsky_pi(digits)
    # print(f"Calculated value of π to {digits} digits:\n{pi_value}")

    with open('pi_value.txt','w') as f:
        f.write(str(pi_value))

print('These are the',digits,'digits of pi:\n',pi_value )



