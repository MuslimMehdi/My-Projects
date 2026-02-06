#This project was made by Admin (Muslim Mehdi) when he was practicing OOP (Object-Oriented Programming) in Python
class Account:
    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print(f"Deposited: {amount:,}\nNew Balance: {self.balance:,}")
        else:
            print("Invalid deposit amount. Amount must be positive.")

    def withdraw(self, amount):
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            print(f"Withdrawn: {amount:,}. New Balance: {self.balance:,}")
        else:
            print("Invalid withdrawal amount or insufficient balance.")

    def get_balance(self):
        return self.balance


class Savings_Account(Account):
    def __init__(self, balance=0):
        super().__init__(balance)
        self.profit_rate = 0.1026  # 10.26% profit on savings

    def calculate_profit(self):
        return self.balance * self.profit_rate

    def get_balance_with_profit(self):
        return self.balance + self.calculate_profit()


# Function to get user input for deposit or withdrawal
def get_transaction_amount():
    while True:
        try:
            amount = int(input("Enter the amount: "))
            if amount > 0:
                return amount
            else:
                print("Amount must be positive. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


# Main program
if __name__ == "__main__":
    # Initialize accounts
    current_account = Account()
    savings_account = Savings_Account()

    while True:
        # Main menu
        print("1. Make a Transaction (Deposit/Withdraw)")
        print("2. Check Current Account Balance")
        print("3. Check Savings Account Balance")
        print("4. Exit")
        choice = input("Enter your choice (1-4)\n: ")

        if choice == "1":
            # Transaction menu
            print("\n--- Transaction Menu ---")
            print("1. Deposit")
            print("2. Withdraw")
            transaction_choice = input("Enter your choice (1-2)\n: ")

            if transaction_choice == "1":
                amount = get_transaction_amount()
                current_account.deposit(amount)
            elif transaction_choice == "2":
                amount = get_transaction_amount()
                current_account.withdraw(amount)
            else:
                print("Invalid choice. Please try again.")

        elif choice == "2":
            # Check Current Account Balance
            print(f"\nCurrent Account Balance: {current_account.get_balance():,}")

        elif choice == "3":
            # Check Savings Account Balance
            print(f"\nSavings Account Balance: {savings_account.get_balance():,}")
            print(f"Savings Account Balance with Profit: {savings_account.get_balance_with_profit():,}")

        elif choice == "4":
            # Exit the program
            print("Thank you for using the Bank Account System. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")