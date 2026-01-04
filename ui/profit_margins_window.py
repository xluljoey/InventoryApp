import customtkinter as ctk
from tkinter import ttk, messagebox
from db.database import get_db_connection
from core.sales import get_sales_history
from datetime import datetime, timedelta

class ProfitMarginsWindow(ctk.CTkToplevel):
    """Window showing profit margins analysis"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Profit Margins Analysis")
        self.geometry("1200x800")
        self.configure(fg_color="#f1f5f9")
        
        # Linux/Fedora display fixes
        self.lift()
        self.attributes("-topmost", True)
        self.after(50, lambda: self.attributes("-topmost", False))
        self.update_idletasks()
        self.grab_set()
        
        # Header
        header = ctk.CTkFrame(self, fg_color="#1e293b", height=80, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="💰 Profit Margins Analysis", 
                     font=("Arial", 22, "bold"), 
                     text_color="white").pack(pady=25)
        
        # Main content with tabs
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Filter frame
        filter_frame = ctk.CTkFrame(content, fg_color="white", corner_radius=15)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        filter_inner = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_inner.pack(pady=15, padx=20)
        
        ctk.CTkLabel(filter_inner, text="Time Period:", 
                     font=("Arial", 12, "bold"), 
                     text_color="#0f172a").pack(side="left", padx=(0, 10))
        
        self.period_var = ctk.StringVar(value="All Time")
        period_options = ["Today", "This Week", "This Month", "This Year", "All Time"]
        period_menu = ctk.CTkOptionMenu(filter_inner, variable=self.period_var, 
                                       values=period_options, width=150,
                                       command=self.update_display)
        period_menu.pack(side="left", padx=10)
        
        # Summary cards
        summary_frame = ctk.CTkFrame(content, fg_color="transparent")
        summary_frame.pack(fill="x", pady=(0, 10))
        
        self.total_revenue_card = ctk.CTkFrame(summary_frame, fg_color="white", corner_radius=15, height=100)
        self.total_revenue_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.total_revenue_card.pack_propagate(False)
        
        self.total_cost_card = ctk.CTkFrame(summary_frame, fg_color="white", corner_radius=15, height=100)
        self.total_cost_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.total_cost_card.pack_propagate(False)
        
        self.total_profit_card = ctk.CTkFrame(summary_frame, fg_color="white", corner_radius=15, height=100)
        self.total_profit_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.total_profit_card.pack_propagate(False)
        
        self.margin_card = ctk.CTkFrame(summary_frame, fg_color="white", corner_radius=15, height=100)
        self.margin_card.pack(side="left", fill="both", expand=True, padx=(0, 0))
        self.margin_card.pack_propagate(False)
        
        # Table frame
        table_frame = ctk.CTkFrame(content, fg_color="white", corner_radius=15)
        table_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(table_frame, text="Product Profit Analysis", 
                     font=("Arial", 16, "bold"), 
                     text_color="#0f172a").pack(pady=(15, 10), padx=20, anchor="w")
        
        # Treeview
        tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                        fieldbackground="white", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#10b981')])
        
        self.tree = ttk.Treeview(tree_container, 
                                columns=("product", "revenue", "cost", "profit", "margin", "qty_sold"), 
                                show="headings", height=15)
        
        self.tree.heading("product", text="Product")
        self.tree.heading("revenue", text="Revenue (GHS)")
        self.tree.heading("cost", text="Cost (GHS)")
        self.tree.heading("profit", text="Profit (GHS)")
        self.tree.heading("margin", text="Margin %")
        self.tree.heading("qty_sold", text="Qty Sold")
        
        self.tree.column("product", width=250, anchor="w")
        self.tree.column("revenue", width=150, anchor="center")
        self.tree.column("cost", width=150, anchor="center")
        self.tree.column("profit", width=150, anchor="center")
        self.tree.column("margin", width=120, anchor="center")
        self.tree.column("qty_sold", width=120, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Load initial data
        self.update_display()
    
    def get_date_filter(self):
        """Get date filter based on selected period"""
        today = datetime.now().date()
        period = self.period_var.get()
        
        if period == "Today":
            return today.strftime("%Y-%m-%d")
        elif period == "This Week":
            week_start = today - timedelta(days=today.weekday())
            return week_start.strftime("%Y-%m-%d")
        elif period == "This Month":
            return today.replace(day=1).strftime("%Y-%m-%d")
        elif period == "This Year":
            return today.replace(month=1, day=1).strftime("%Y-%m-%d")
        else:  # All Time
            return None
    
    def update_display(self, *args):
        """Update the display with profit margin data"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get sales data
        conn = get_db_connection()
        cursor = conn.cursor()
        
        date_filter = self.get_date_filter()
        
        if date_filter:
            cursor.execute("""
                SELECT s.product_id, p.name, p.price, p.cost_price, 
                       SUM(s.quantity) as total_qty, SUM(s.total_price) as total_revenue
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE date(s.date) >= ?
                GROUP BY s.product_id, p.name, p.price, p.cost_price
                ORDER BY total_revenue DESC
            """, (date_filter,))
        else:
            cursor.execute("""
                SELECT s.product_id, p.name, p.price, p.cost_price, 
                       SUM(s.quantity) as total_qty, SUM(s.total_price) as total_revenue
                FROM sales s
                JOIN products p ON s.product_id = p.id
                GROUP BY s.product_id, p.name, p.price, p.cost_price
                ORDER BY total_revenue DESC
            """)
        
        sales_data = cursor.fetchall()
        conn.close()
        
        # Calculate totals
        total_revenue = 0
        total_cost = 0
        total_profit = 0
        
        # Process each product
        for row in sales_data:
            product_id, product_name, selling_price, cost_price, qty_sold, revenue = row
            
            # Handle None cost_price
            if cost_price is None:
                cost_price = 0
                cost = 0
                profit = revenue
                margin_pct = 100.0 if revenue > 0 else 0.0
            else:
                cost = qty_sold * cost_price
                profit = revenue - cost
                margin_pct = (profit / revenue * 100) if revenue > 0 else 0.0
            
            total_revenue += revenue
            total_cost += cost
            total_profit += profit
            
            # Color code margin
            margin_color = "#10b981" if margin_pct >= 20 else "#f59e0b" if margin_pct >= 10 else "#ef4444"
            
            # Insert into tree
            self.tree.insert("", "end", values=(
                product_name,
                f"{revenue:.2f}",
                f"{cost:.2f}" if cost_price else "N/A",
                f"{profit:.2f}",
                f"{margin_pct:.1f}%",
                f"{qty_sold:.1f}"
            ), tags=(margin_color,))
        
        # Update summary cards
        self.update_summary_cards(total_revenue, total_cost, total_profit)
        
        # Configure tag colors
        self.tree.tag_configure("#10b981", foreground="#10b981")
        self.tree.tag_configure("#f59e0b", foreground="#f59e0b")
        self.tree.tag_configure("#ef4444", foreground="#ef4444")
    
    def update_summary_cards(self, revenue, cost, profit):
        """Update summary cards with totals"""
        # Clear existing labels
        for widget in self.total_revenue_card.winfo_children():
            widget.destroy()
        for widget in self.total_cost_card.winfo_children():
            widget.destroy()
        for widget in self.total_profit_card.winfo_children():
            widget.destroy()
        for widget in self.margin_card.winfo_children():
            widget.destroy()
        
        # Revenue card
        ctk.CTkLabel(self.total_revenue_card, text="Total Revenue", 
                     font=("Arial", 11, "bold"), 
                     text_color="#64748b").pack(pady=(15, 5))
        ctk.CTkLabel(self.total_revenue_card, text=f"GHS {revenue:.2f}", 
                     font=("Arial", 20, "bold"), 
                     text_color="#10b981").pack()
        
        # Cost card
        ctk.CTkLabel(self.total_cost_card, text="Total Cost", 
                     font=("Arial", 11, "bold"), 
                     text_color="#64748b").pack(pady=(15, 5))
        ctk.CTkLabel(self.total_cost_card, text=f"GHS {cost:.2f}", 
                     font=("Arial", 20, "bold"), 
                     text_color="#ef4444").pack()
        
        # Profit card
        profit_color = "#10b981" if profit >= 0 else "#ef4444"
        ctk.CTkLabel(self.total_profit_card, text="Total Profit", 
                     font=("Arial", 11, "bold"), 
                     text_color="#64748b").pack(pady=(15, 5))
        ctk.CTkLabel(self.total_profit_card, text=f"GHS {profit:.2f}", 
                     font=("Arial", 20, "bold"), 
                     text_color=profit_color).pack()
        
        # Margin card
        margin_pct = (profit / revenue * 100) if revenue > 0 else 0.0
        margin_color = "#10b981" if margin_pct >= 20 else "#f59e0b" if margin_pct >= 10 else "#ef4444"
        ctk.CTkLabel(self.margin_card, text="Profit Margin", 
                     font=("Arial", 11, "bold"), 
                     text_color="#64748b").pack(pady=(15, 5))
        ctk.CTkLabel(self.margin_card, text=f"{margin_pct:.1f}%", 
                     font=("Arial", 20, "bold"), 
                     text_color=margin_color).pack()

