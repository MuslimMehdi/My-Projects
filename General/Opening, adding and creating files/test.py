#This piece of code firstly takes an input from the user then writes them to a file named members (If it doesn't exist then it would create it)

time=str(input("Kindly enter your name :\n"))\

with open ('members.txt', "w") as file:
    file.write(name)
    file.write(role)
with open('members.txt', "r") as file:
    print(file.read())

# COULD HAVE USE THIS CODE BELOW
# name = str(input("Kindly enter your name :\n"))
# role = str(input("Kindly enter your role  :\n"))
#
# # Open file in read+write mode
# with open('members.txt', "r+") as file:
#     file.write(name + "\n")
#     file.write(role + "\n")
#     print(file.read())
