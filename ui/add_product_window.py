import tkinter as tk
from tkinter import messagebox
from core.products import add_product

class AddProductWindow:
    def __init__(self, parent, refresh_callback):
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Register New Product")
        self.window.geometry("350x450")

        # Form Fields
        tk.Label(self.window, text="Product Name").pack(pady=5)
        self.name_entry = tk.Entry(self.window)
        self.name_entry.pack()

        tk.Label(self.window, text="Category (e.g. Feed, Grain)").pack(pady=5)
        self.cat_entry = tk.Entry(self.window)
        self.cat_entry.pack()

        tk.Label(self.window, text="Bag Weight (kg)").pack(pady=5)
        self.weight_entry = tk.Entry(self.window)
        self.weight_entry.insert(0, "50") # Default to 50kg
        self.weight_entry.pack()

        tk.Label(self.window, text="Selling Price (GHS)").pack(pady=5)
        self.price_entry = tk.Entry(self.window)
        self.price_entry.pack()

        tk.Label(self.window, text="Initial Stock (Bags)").pack(pady=5)
        self.stock_entry = tk.Entry(self.window)
        self.stock_entry.insert(0, "0")
        self.stock_entry.pack()

        tk.Button(
            self.window, 
            text="SAVE PRODUCT", 
            command=self.save, 
            bg="#9C27B0", # Purple color for new items
            fg="white", 
            font=("Arial", 10, "bold")
        ).pack(pady=30)

    def save(self):
        try:
            name = self.name_entry.get()
            cat = self.cat_entry.get()
            weight = float(self.weight_entry.get())
            price = float(self.price_entry.get())
            stock = float(self.stock_entry.get())

            if name:
                # Add to DB via core/products.py
                add_product(name, cat, "kg", weight, price, stock)
                messagebox.showinfo("Success", f"{name} added to inventory!")
                self.window.destroy()
                self.refresh_callback() # Refresh the main dashboard
            else:
                messagebox.showerror("Error", "Product Name is required!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for weight, price, and stock.")