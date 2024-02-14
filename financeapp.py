import sqlite3
from datetime import datetime

# Initialize Application

#This initializes the database and saves it to a file called finance_tracker.db
def setup_database():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        category_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES Users(id),
        FOREIGN KEY (category_id) REFERENCES Categories(id)
    )''')
    #make the table if it doesnt exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS Categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )''')
    conn.commit()
    conn.close()

setup_database()

# At the beginning initialize current_user_id
current_user_id = None

def login_user():
    global current_user_id  # Declare as global to modify the global variable
    username = input("Username: ")
    password = input("Password: ")
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        print("Login successful.")
        current_user_id = user[0]  # Update the global variable upon successful login
        return True
    else:
        print("Invalid username or password.")
        return False


def main_menu():
    while True:
        print("Welcome to Personal Finance Tracker")
        print("1: Register / Login")
        print("2: Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            register_login()
        elif choice == '2':
            print("Exiting application.")
            break

def register_login():
    while True:
        print("\nRegister / Login")
        print("1: Register")
        print("2: Login")
        print("3: Return to Main Menu")
        choice = input("Choose an option: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            if login_user():
                dashboard()
                # After returning from the dashboard, we should break to avoid an infinite loop
                break
        elif choice == '3':
            break

def register_user():
    username = input("Enter new username: ")
    password = input("Enter new password: ")
    # In a real application, you should hash the password before storing it
    try:
        conn = sqlite3.connect('finance_tracker.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("Registration successful. Please log in.")
    except sqlite3.IntegrityError:
        print("Username already exists. Please choose a different username.")
    finally:
        conn.close()

def login_user():
    username = input("Username: ")
    password = input("Password: ")
    # Password should be checked against a hash in a real application but this is a place holder
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        print("Login successful.")
        # Setting a global variable for user_id to maintain state; consider a more secure method in production
        global current_user_id
        current_user_id = user[0]
        return True
    else:
        print("Invalid username or password.")
        return False


def record_transaction():
    while True:
        print("\nRecord Income/Expense")
        print("1: Record Income")
        print("2: Record Expense")
        print("3: Return to Dashboard")
        choice = input("Choose an option: ")

        if choice == '1':
            record_income()
        elif choice == '2':
            record_expense()
        elif choice == '3':
            break

def record_income():
    amount = float(input("Enter amount: "))
    source = input("Enter source: ")
    # using the current date; in a real application, allow the user to specify the date
    date = datetime.now().strftime('%Y-%m-%d')
    # Category is optional for income; you could implement category selection or creation here
    category_id = None  # Placeholder; implement category selection or set to None

    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Transactions (user_id, type, amount, description, date, category_id)
                      VALUES (?, 'income', ?, ?, ?, ?)''', (current_user_id, amount, source, date, category_id))
    conn.commit()
    conn.close()
    print("Income recorded successfully.")

def record_expense():
    amount = float(input("Enter amount: "))
    description = input("Enter description: ")
    date = datetime.now().strftime('%Y-%m-%d')
    # Implement category selection for expenses, as it's mandatory
    category_id = select_category()  # Placeholder for a category selection function

    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Transactions (user_id, type, amount, description, date, category_id)
                      VALUES (?, 'expense', ?, ?, ?, ?)''', (current_user_id, amount, description, date, category_id))
    conn.commit()
    conn.close()
    print("Expense recorded successfully.")

def view_transactions():
    print("\nViewing Transactions")
    # initially display all transactions; enhancements can include pagination and filtering
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT date, type, amount, description FROM Transactions WHERE user_id = ? ORDER BY date DESC''', (current_user_id,))
    transactions = cursor.fetchall()

    if transactions:
        print("Date\t\tType\tAmount\tDescription")
        for transaction in transactions:
            date, t_type, amount, description = transaction
            print(f"{date}\t{t_type}\t{amount}\t{description}")
    else:
        print("No transactions found.")

    # Placeholder for additional functionality such as filtering by date range or category
    input("Press any key to return to the Dashboard...")

view_transactions()

def manage_categories():
    while True:
        print("\nManage Categories")
        print("1: Add Category")
        print("2: Edit Category")
        print("3: Delete Category")
        print("4: Return to Dashboard")
        choice = input("Choose an option: ")

        if choice == '1':
            add_category()
        elif choice == '2':
            edit_category()
        elif choice == '3':
            delete_category()
        elif choice == '4':
            break

def add_category():
    category_name = input("Enter new category name: ")
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Categories (name) VALUES (?)", (category_name,))
        conn.commit()
        print("Category added successfully.")
    except sqlite3.IntegrityError:
        print("Category already exists.")
    finally:
        conn.close()

def edit_category():
    categories = list_categories()
    if not categories:
        return

    category_id = input("Enter the ID of the category you want to edit: ")
    new_name = input("Enter new category name: ")
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Categories SET name = ? WHERE id = ?", (new_name, category_id))
    conn.commit()
    conn.close()
    print("Category updated successfully.")

def delete_category():
    categories = list_categories()
    if not categories:
        return

    category_id = input("Enter the ID of the category you want to delete: ")
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()
    print("Category deleted successfully.")

def list_categories():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Categories")
    categories = cursor.fetchall()
    if not categories:
        print("No categories found.")
        return None

    print("Categories:")
    for id, name in categories:
        print(f"{id}: {name}")
    return categories

def select_category():
    categories = list_categories()
    if not categories:
        print("No categories available. Please add a category first.")
        return None

    while True:
        category_id = input("Enter the ID of the category you want to select: ")
        # Validate the selected category ID
        if any(category[0] == int(category_id) for category in categories):
            return category_id
        else:
            print("Invalid category ID. Please select a valid ID from the list.")


def generate_report():
    while True:
        print("\nGenerate Report")
        print("1: Summary Report")
        print("2: Detailed Report by Category")
        print("3: Return to Dashboard")
        choice = input("Choose an option: ")

        if choice == '1':
            generate_summary_report()
        elif choice == '2':
            generate_detailed_report()
        elif choice == '3':
            break

def generate_summary_report():
    print("\nSummary Report")
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()

    # Fetch total income
    cursor.execute('''SELECT SUM(amount) FROM Transactions
                      WHERE type = 'income' AND user_id = ?''', (current_user_id,))
    total_income = cursor.fetchone()[0] or 0

    # Fetch total expenses
    cursor.execute('''SELECT SUM(amount) FROM Transactions
                      WHERE type = 'expense' AND user_id = ?''', (current_user_id,))
    total_expense = cursor.fetchone()[0] or 0

    net_flow = total_income - total_expense

    print(f"Total Income: {total_income}")
    print(f"Total Expense: {total_expense}")
    print(f"Net Flow: {net_flow}")

    input("Press any key to return to the Dashboard...")

def generate_detailed_report():
    print("\nDetailed Report by Category")
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()

    # Fetch and group transactions by category with totals
    cursor.execute('''SELECT Categories.name, SUM(Transactions.amount), Transactions.type
                      FROM Transactions
                      JOIN Categories ON Transactions.category_id = Categories.id
                      WHERE Transactions.user_id = ?
                      GROUP BY Transactions.category_id, Transactions.type''', (current_user_id,))
    
    transactions = cursor.fetchall()

    if transactions:
        print("Category\tType\tTotal")
        for category, amount, t_type in transactions:
            print(f"{category}\t{t_type}\t{amount}")
    else:
        print("No transactions to report.")

    input("Press any key to return to the Dashboard...")


def dashboard():
    while True:
        print("\nDashboard")
        print("1: Record Income/Expense")
        print("2: View Transactions")
        print("3: Manage Categories")
        print("4: Generate Report")
        print("5: Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            record_transaction()
        elif choice == '2':
            view_transactions()
        elif choice == '3':
            manage_categories()
        elif choice == '4':
            generate_report()
        elif choice == '5':
            # Logout breaking the loop 
            print("Logging out...")
            break


# Main function to start the application
def main():
    main_menu()

if __name__ == "__main__":
    main()
