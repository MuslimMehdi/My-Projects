#Thanks to ChatGPT I was able to debug my code with ease but in my future projects I wouldnt use it and rely on my own expertise
import os


print("_"*109+"\nWelcome to MoA notes a versatile one spot solution to all your note taking and project management requirement\n"+"_"*109)


if __name__=="__main__":
    while True :
        file=input("1. Do u want to create a new file \n2. Access an already existing file\n3. Do u want to delete a file\n4.To exit the program\nEnter numbers for their respective options (i.e: 1 for option 1) : ")


        if int(file) == 1: # to create new file
            filename = input("Enter the file name : ")+".txt"
            print("Note : After Modifing the data press enter and type save to save it")
        with open(filename, "x+") as f: # Creates a new file and opens it in read and write mode. It raises an objection if the file already exists
            while True:
                line = input()
                if line.strip().upper() == "SAVE":
                    break
                f.write(line + "\n")

                print(f"All data saved to {filename}")

        elif int(file) == 2:# to Access already existing file. I wroteif first then ChatGPT told me its elif(brain not braining under stress)
        filename=input("Enter the file name : ")+".txt"
        print("Note : After Modifing the data press enter and type save to save it")
            with open(filename, "r+") as f: # I was stuck for an hour at this due to not adding "as f" and another 15 mins more as i was writing "file.read" instead of "f.read" as I called the function f (Stop relying on ChatGPT)
                print(f.read())  # Reads data
                while True:
                    wline = input()
                    if wline.strip().upper() == "SAVE":
                        break
                    f.write(wline + "\n")

                    print(f"All data saved to {filename}")

        elif int(file) == 3:
            filename = input("Enter the file name : ")+".txt"
            if os.path.exists(filename):
                os.remove(filename)
                print(f"File '{filename}' deleted successfully.")
            else:
                print("Error: File does not exist.")

        elif int(file) == 4:
            print('_'*72+"\nThank u for visiting. Take care and have a good day. Hope to see u again\n"+'_'*72)
            break

        else:
            print("Please choose either 1,2 or 3")




