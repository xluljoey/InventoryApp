import customtkinter as ctk
from tkinter import messagebox, ttk
from core.products import get_product_names, admin_add_product, admin_update_price, admin_overwrite_stock, admin_delete_product
from db.database import get_db_connection
from datetime import datetime

class AdminWindow(ctk.CTkToplevel):
    def __init__(self, parent, refresh_callback):
        super().__init__(parent)
        self.title("Inventory Manager")
        self.geometry("700x750")
        self.configure(fg_color="#f1f5f9")
        self.refresh_callback = refresh_callback
        
        # Header
        ctk.CTkLabel(self, text="Inventory Manager", 
                     font=ctk.CTkFont(size=28, weight="bold"), 
                     text_color="#0f172a").pack(pady=(30, 20))
        
        # Tabs
        self.tabs = ctk.CTkTabview(self, segmented_button_selected_color="#10b981")
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tab 1: Manage Existing
        self.tab_manage = self.tabs.add("Manage Stock")
        self.setup_manage_tab()
        
        # Tab 2: Add New Product
        self.tab_add = self.tabs.add("Add Product")
        self.setup_add_tab()
        
        # Tab 3: New Arrivals
        self.tab_arrivals = self.tabs.add("New Arrivals")
        self.setup_arrivals_tab()
        
        self.grab_set()
    
    def setup_manage_tab(self):
        """Setup the Manage Existing Products tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_manage, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main Card
        card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card, text="MANAGE EXISTING PRODUCTS", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=10)
        
        # Product dropdown
        self.products = get_product_names()
        self.p_map = {p[1]: p[0] for p in self.products}
        product_names = list(self.p_map.keys()) if self.p_map else ["No Products"]
        
        ctk.CTkLabel(inner, text="Select Product:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        self.drop = ctk.CTkOptionMenu(inner, values=product_names, width=450, height=40, fg_color="#f8fafc", text_color="#1e293b")
        self.drop.pack(pady=5)
        
        # Update Price Section
        ctk.CTkLabel(inner, text="Update Price (GHS):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.up = ctk.CTkEntry(inner, placeholder_text="New price per bag", width=450, height=40)
        self.up.pack(pady=5)
        ctk.CTkButton(inner, text="Update Price", command=self.do_p, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=450).pack(pady=10)
        
        # Overwrite Stock Section
        ctk.CTkLabel(inner, text="Correct Stock (Bags):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.us = ctk.CTkEntry(inner, placeholder_text="Number of bags to set", width=450, height=40)
        self.us.pack(pady=5)
        ctk.CTkButton(inner, text="Update Stock Level", command=self.do_s, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=450).pack(pady=10)
        
        # Delete Product Section
        ctk.CTkButton(inner, text="DELETE THIS PRODUCT", command=self.do_d, 
                     fg_color="#ef4444", hover_color="#dc2626", height=40, width=450).pack(pady=(20, 15))
    
    def setup_add_tab(self):
        """Setup the Add New Product tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_add, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main Card
        card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card, text="ADD NEW PRODUCT", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(inner, text="Product Name:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        self.en = ctk.CTkEntry(inner, placeholder_text="e.g. Rice, Maize, Soya", width=450, height=40)
        self.en.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Price per Bag (GHS):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(10, 5))
        self.ep = ctk.CTkEntry(inner, placeholder_text="e.g. 150", width=450, height=40)
        self.ep.pack(pady=5)
        
        ctk.CTkLabel(inner, text="KG per Bag:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(10, 5))
        self.ew = ctk.CTkEntry(inner, placeholder_text="e.g. 50", width=450, height=40)
        self.ew.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Initial Stock (Bags):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(10, 5))
        self.es = ctk.CTkEntry(inner, placeholder_text="e.g. 100", width=450, height=40)
        self.es.pack(pady=5)
        
        ctk.CTkButton(inner, text="CREATE PRODUCT", command=self.do_add, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=450).pack(pady=(15, 20))
    
    def setup_arrivals_tab(self):
        """Setup the New Arrivals tab for recording stock additions"""
        scroll = ctk.CTkScrollableFrame(self.tab_arrivals, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main Card
        card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card, text="RECORD NEW ARRIVALS", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=10)
        
        # Product dropdown
        self.products_arr = get_product_names()
        self.p_map_arr = {p[1]: p[0] for p in self.products_arr}
        product_names_arr = list(self.p_map_arr.keys()) if self.p_map_arr else ["No Products"]
        
        ctk.CTkLabel(inner, text="Select Product:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        self.drop_arr = ctk.CTkOptionMenu(inner, values=product_names_arr, width=500, height=40, fg_color="#f8fafc", text_color="#1e293b")
        self.drop_arr.pack(pady=5)
        
        # Current stock display
        ctk.CTkLabel(inner, text="Current Stock:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.current_stock_lbl = ctk.CTkLabel(inner, text="-- Bags", text_color="#10b981", font=("Arial", 11, "bold"))
        self.current_stock_lbl.pack(anchor="w", pady=5)
        
        self.drop_arr.configure(command=lambda x: self.update_stock_display())
        
        # Add stock
        ctk.CTkLabel(inner, text="Quantity to Add (Bags):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.add_qty = ctk.CTkEntry(inner, placeholder_text="Number of bags arriving", width=500, height=40)
        self.add_qty.pack(pady=5)
        
        ctk.CTkButton(inner, text="RECORD ARRIVAL", command=self.do_arrival, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=500).pack(pady=(15, 20))
        
        # Stock History
        history_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        history_card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(history_card, text="ARRIVAL HISTORY", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        # Treeview for history
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                        fieldbackground="white", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#10b981')])
        
        tree_frame = ctk.CTkFrame(history_card, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.history_tree = ttk.Treeview(tree_frame, columns=("Date", "Product", "Before", "Added", "After"), show="headings", height=8)
        self.history_tree.heading("Date", text="Date/Time")
        self.history_tree.heading("Product", text="Product")
        self.history_tree.heading("Before", text="Before (Bags)")
        self.history_tree.heading("Added", text="Added")
        self.history_tree.heading("After", text="After (Bags)")
        
        for col in ("Date", "Product", "Before", "Added", "After"):
            self.history_tree.column(col, width=100, anchor="center")
        
        self.history_tree.pack(fill="both", expand=True)
        self.load_arrival_history()
    
    def update_stock_display(self):
        """Update the current stock display when product is selected"""
        try:
            selected = self.drop_arr.get()
            if selected == "No Products":
                self.current_stock_lbl.configure(text="-- Bags")
                return
            
            p_id = self.p_map_arr[selected]
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT current_stock, weight_per_unit FROM products WHERE id = ?", (p_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                bags = result[0] / result[1] if result[1] > 0 else 0
                self.current_stock_lbl.configure(text=f"{bags:.1f} Bags")
        except:
            pass
    
    def load_arrival_history(self):
        """Load and display arrival history"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.date, p.name, r.old_qty, r.added_qty, r.new_qty
            FROM restock_history r
            JOIN products p ON r.product_id = p.id
            ORDER BY r.date DESC LIMIT 20
        """)
        rows = cursor.fetchall()
        conn.close()
        
        for r in rows:
            date_str = r[0].split('.')[0] if isinstance(r[0], str) else str(r[0])
            self.history_tree.insert("", "end", values=(date_str, r[1], f"{r[2]:.0f}", f"{r[3]:.0f}", f"{r[4]:.0f}"))
    
    def do_arrival(self):
        """Record a new stock arrival"""
        try:
            selected = self.drop_arr.get()
            if selected == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            
            qty = float(self.add_qty.get())
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0", parent=self)
                return
            
            p_id = self.p_map_arr[selected]
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get current stock and weight
            cursor.execute("SELECT current_stock, weight_per_unit FROM products WHERE id = ?", (p_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Product not found", parent=self)
                conn.close()
                return
            
            old_stock_kg = result[0]
            weight = result[1]
            old_bags = old_stock_kg / weight if weight > 0 else 0
            new_stock_kg = old_stock_kg + (qty * weight)
            
            # Update stock
            cursor.execute("UPDATE products SET current_stock = ? WHERE id = ?", (new_stock_kg, p_id))
            
            # Log the arrival
            cursor.execute("""
                INSERT INTO restock_history (product_id, old_qty, added_qty, new_qty, date)
                VALUES (?, ?, ?, ?, ?)
            """, (p_id, old_bags, qty, old_bags + qty, datetime.now()))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Added {qty} bags to {selected}", parent=self)
            self.add_qty.delete(0, "end")
            self.update_stock_display()
            self.load_arrival_history()
            self.refresh_callback()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)

    def do_add(self):
        try:
            name = self.en.get().strip()
            price = float(self.ep.get())
            weight = float(self.ew.get())
            bags = float(self.es.get())
            
            if not name:
                messagebox.showerror("Error", "Product name cannot be empty", parent=self)
                return
            
            admin_add_product(name, price, weight, bags)
            messagebox.showinfo("Success", f"Product '{name}' created!", parent=self)
            self.en.delete(0, "end")
            self.ep.delete(0, "end")
            self.ew.delete(0, "end")
            self.es.delete(0, "end")
            self.refresh_callback()
        except ValueError:
            messagebox.showerror("Error", "Check all numeric inputs", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)

    def do_p(self):
        try:
            selected = self.drop.get()
            if selected == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            
            price = float(self.up.get())
            admin_update_price(self.p_map[selected], price)
            messagebox.showinfo("Success", f"Price updated to GHS {price:.2f}", parent=self)
            self.up.delete(0, "end")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)

    def do_s(self):
        try:
            selected = self.drop.get()
            if selected == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            
            bags = float(self.us.get())
            admin_overwrite_stock(self.p_map[selected], bags)
            messagebox.showinfo("Success", f"Stock set to {bags} bags", parent=self)
            self.us.delete(0, "end")
            self.refresh_callback()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)

    def do_d(self):
        try:
            selected = self.drop.get()
            if selected == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            
            if messagebox.askyesno("Confirm", f"Delete '{selected}' permanently?", parent=self):
                admin_delete_product(self.p_map[selected])
                messagebox.showinfo("Success", f"Product '{selected}' deleted", parent=self)
                self.refresh_callback()
                self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)