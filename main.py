import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Database Setup
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT,
    amount REAL,
    category TEXT,
    date TEXT
)
""")
conn.commit()

# Functions
def add_expense():
    desc = desc_entry.get()
    amount = amount_entry.get()
    category = category_entry.get()
    date = date_entry.get()

    if not desc or not amount or not category or not date:
        messagebox.showerror("Error", "All fields are required!")
        return
    
    try:
        amount = float(amount)
        cursor.execute("INSERT INTO expenses (description, amount, category, date) VALUES (?, ?, ?, ?)",
                       (desc, amount, category, date))
        conn.commit()
        desc_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        load_expenses()
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")

def load_expenses():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM expenses")
    for expense in cursor.fetchall():
        tree.insert("", "end", values=expense)

def delete_expense():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No expense selected")
        return

    for item in selected_item:
        expense_id = tree.item(item, "values")[0]
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        tree.delete(item)

def show_statistics():
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()

    if not data:
        messagebox.showerror("Error", "No data available")
        return

    df = pd.DataFrame(data, columns=["Category", "Total"])
    df.plot(kind="bar", x="Category", y="Total", legend=False, color="skyblue")
    plt.title("Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Total Spent")
    plt.xticks(rotation=45)
    plt.show()

# GUI Setup
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("600x500")

# Layout Configuration (Fix for entry fields not appearing)
root.columnconfigure(1, weight=1)

# Labels and Entries
tk.Label(root, text="Description:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
desc_entry = tk.Entry(root, width=40)
desc_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

tk.Label(root, text="Amount:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
amount_entry = tk.Entry(root, width=40)
amount_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

tk.Label(root, text="Category:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
category_entry = tk.Entry(root, width=40)
category_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

tk.Label(root, text="Date (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
date_entry = tk.Entry(root, width=40)
date_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

# Buttons
tk.Button(root, text="Add Expense", command=add_expense, bg="green", fg="white").grid(row=4, column=0, columnspan=2, pady=10)
tk.Button(root, text="Show Statistics", command=show_statistics, bg="blue", fg="white").grid(row=5, column=0, columnspan=2, pady=5)
tk.Button(root, text="Delete Expense", command=delete_expense, bg="red", fg="white").grid(row=7, column=0, columnspan=2, pady=10)
# Table (Treeview)
columns = ("ID", "Description", "Amount", "Category", "Date")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=100)
tree.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")

# Scrollbar for Treeview
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=6, column=2, sticky="ns")



# Load Expenses
load_expenses()

# Run App
root.mainloop()
