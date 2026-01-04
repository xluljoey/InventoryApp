import customtkinter as ctk
from tkinter import messagebox
from core.products import get_product_names, restock_product

class AddStockWindow(ctk.CTkToplevel):
    def __init__(self, parent, refresh_callback, pre_selected_id=None):
        super().__init__(parent)
        self.title("Restock Inventory")
        self.geometry("500x550")
        self.configure(fg_color="#f1f5f9")
        self.refresh_callback = refresh_callback
        
        # --- LINUX STABILITY ---
        self.lift()
        self.after(100, self.focus_force)
        self.grab_set() 
        
        # Main Card
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        card.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(card, text="Restock Product", 
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#0f172a").pack(pady=20)

        # Data Lookup
        self.product_map = {}
        products = get_product_names()
        names = [p[1] for p in products]
        for p in products: 
            self.product_map[p[1]] = p[0]

        # Product Dropdown
        ctk.CTkLabel(card, text="SELECT PRODUCT", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748b").pack(anchor="w", padx=55)
        self.product_var = ctk.StringVar(value=names[0] if names else "No Products")
        self.dropdown = ctk.CTkOptionMenu(card, variable=self.product_var, values=names, 
                                         width=350, height=45, fg_color="#f8fafc", 
                                         text_color="#1e293b", button_color="#cbd5e1")
        self.dropdown.pack(pady=10)

        # Pre-selection logic if clicked from dashboard
        if pre_selected_id:
            for name, id in self.product_map.items():
                if id == pre_selected_id:
                    self.product_var.set(name)
                    break

        # Quantity Input
        ctk.CTkLabel(card, text="ADDITIONAL BAGS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748b").pack(anchor="w", padx=55, pady=(10,0))
        self.qty_entry = ctk.CTkEntry(card, placeholder_text="e.g. 50", width=350, height=45)
        self.qty_entry.pack(pady=10)

        # Submit Button
        self.btn = ctk.CTkButton(card, text="UPDATE STOCK LEVEL", 
                                 fg_color="#10b981", hover_color="#059669",
                                 height=50, width=350, 
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 command=self.submit)
        self.btn.pack(pady=40)

    def submit(self):
        try:
            selected_name = self.product_var.get()
            p_id = self.product_map.get(selected_name)
            qty_text = self.qty_entry.get()

            if not qty_text:
                messagebox.showwarning("Input Missing", "Please enter the number of bags.", parent=self)
                return

            qty = float(qty_text)
            
            if restock_product(p_id, qty):
                messagebox.showinfo("Success", f"Added {qty} bags to {selected_name}", parent=self)
                self.refresh_callback() # Refresh Dashboard
                self.destroy()
            else:
                messagebox.showerror("Error", "Could not update database.", parent=self)
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for quantity.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)