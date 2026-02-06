# n!=(n-0)*(n-1)*(n-2)
n = int(input("Enter a number\n:"))
total = n
for i in range(1, n - 1):
    f = n - i
    total *= f
print(total)
