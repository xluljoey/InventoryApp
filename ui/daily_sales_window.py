import customtkinter as ctk
from tkinter import ttk
from core.sales import get_today_revenue, get_sales_history
from db.database import get_db_connection
from datetime import datetime

class DailySalesWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Daily Sales Report")
        self.geometry("1100x800")
        self.configure(fg_color="#f1f5f9")
        self.withdraw()
        
        # Header
        ctk.CTkLabel(self, text="Daily Sales Report", 
                     font=ctk.CTkFont(size=28, weight="bold"), 
                     text_color="#0f172a").pack(pady=(30, 20))
        
        # Revenue Card
        revenue_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15, height=100)
        revenue_card.pack(fill="x", padx=40, pady=(0, 30))
        revenue_card.pack_propagate(False)
        
        ctk.CTkLabel(revenue_card, text="TODAY'S REVENUE", 
                     font=("Arial", 12, "bold"), text_color="#64748b").pack(pady=(15, 0))
        
        self.revenue_lbl = ctk.CTkLabel(revenue_card, text="GHS 0.00", 
                                        font=("Arial", 42, "bold"), text_color="#10b981")
        self.revenue_lbl.pack(pady=(5, 15))
        
        # Sales Records
        records_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        records_card.pack(fill="both", expand=True, padx=40, pady=(0, 30))
        
        ctk.CTkLabel(records_card, text="SALES RECORDS", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        # Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                        fieldbackground="white", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#10b981')])
        
        tree_frame = ctk.CTkFrame(records_card, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Product", "Customer", "Qty", "Total", "Paid"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Product", text="Product")
        self.tree.heading("Customer", text="Customer")
        self.tree.heading("Qty", text="Qty (Bags)")
        self.tree.heading("Total", text="Total (GHS)")
        self.tree.heading("Paid", text="Paid (GHS)")
        
        for col in ("ID", "Product", "Customer", "Qty", "Total", "Paid"):
            self.tree.column(col, width=120, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        
        self.deiconify()
        self.load_data()
        self.after(100, self.grab_set)
    
    def load_data(self):
        """Load today's sales data"""
        # Update revenue
        revenue = get_today_revenue()
        self.revenue_lbl.configure(text=f"GHS {revenue:.2f}")
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load sales history
        all_sales = get_sales_history()
        today = datetime.now().date()
        
        for s in all_sales:
            # Extract date from timestamp
            try:
                sale_date = datetime.fromisoformat(s[5].split('.')[0]).date()
            except:
                sale_date = None
            
            # Only show today's sales
            if sale_date == today:
                values = (
                    s[0],  # ID
                    s[1],  # Product
                    s[2] if s[2] else "Cash",  # Customer
                    f"{s[3]:.1f}",  # Qty
                    f"{s[4]:.2f}",  # Total
                    "Full"  # Paid (would need another column in sales table for tracking)
                )
                self.tree.insert("", "end", values=values)
