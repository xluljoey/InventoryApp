import customtkinter as ctk
from tkinter import ttk
from db.database import get_db_connection
from datetime import datetime

class CustomerHistoryWindow(ctk.CTkToplevel):
    """Window showing customer history: sales, credit, and payment history"""
    def __init__(self, parent, customer_id, customer_name):
        super().__init__(parent)
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.title(f"Customer History - {customer_name}")
        self.geometry("1200x800")
        self.configure(fg_color="#f1f5f9")
        
        # Linux/Fedora display fixes
        self.lift()
        self.attributes("-topmost", True)
        self.after(50, lambda: self.attributes("-topmost", False))
        self.update_idletasks()
        self.grab_set()
        
        # Force window to render
        self.update()
        
        # Header
        header = ctk.CTkFrame(self, fg_color="#1e293b", height=80, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text=f"📋 Customer History: {customer_name}", 
                     font=("Arial", 22, "bold"), 
                     text_color="white").pack(pady=25)
        
        # Main content with tabs
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(content, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, 10))
        
        self.tabs = {}
        self.current_tab = None
        
        # Create tabs
        self.create_tab_button(tab_frame, "💰 Sales History", "sales")
        self.create_tab_button(tab_frame, "💳 Credit History", "credit")
        self.create_tab_button(tab_frame, "💵 Payment History", "payments")
        
        # Content area
        self.content_area = ctk.CTkFrame(content, fg_color="white", corner_radius=15)
        self.content_area.pack(fill="both", expand=True)
        
        # Show sales tab by default
        self.show_tab("sales")
    
    def create_tab_button(self, parent, text, tab_key):
        """Create a tab button"""
        btn = ctk.CTkButton(parent, text=text, 
                           command=lambda: self.show_tab(tab_key),
                           fg_color="#475569", hover_color="#334155",
                           height=40, width=200,
                           font=("Arial", 12, "bold"))
        btn.pack(side="left", padx=5)
        self.tabs[tab_key] = btn
    
    def show_tab(self, tab_key):
        """Show a specific tab"""
        # Update button colors
        for key, btn in self.tabs.items():
            if key == tab_key:
                btn.configure(fg_color="#10b981", hover_color="#059669")
            else:
                btn.configure(fg_color="#475569", hover_color="#334155")
        
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        self.current_tab = tab_key
        
        # Load appropriate content
        if tab_key == "sales":
            self.load_sales_history()
        elif tab_key == "credit":
            self.load_credit_history()
        elif tab_key == "payments":
            self.load_payment_history()
    
    def load_sales_history(self):
        """Load and display sales history"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all sales for this customer
        cursor.execute("""
            SELECT s.id, p.name, s.quantity, s.total_price, s.amount_paid, s.date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.customer_id = ?
            ORDER BY s.date DESC
        """, (self.customer_id,))
        
        sales = cursor.fetchall()
        conn.close()
        
        # Header
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="Sales History", 
                     font=("Arial", 18, "bold"), 
                     text_color="#0f172a").pack(side="left")
        
        total_label = ctk.CTkLabel(header_frame, 
                                   text=f"Total Sales: {len(sales)} transactions", 
                                   font=("Arial", 12), 
                                   text_color="#64748b")
        total_label.pack(side="right")
        
        # Table
        table_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Treeview styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                       fieldbackground="white", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#10b981')])
        
        tree = ttk.Treeview(table_frame, columns=("date", "product", "quantity", "total", "paid", "debt"), 
                           show="headings", height=15)
        
        tree.heading("date", text="Date")
        tree.heading("product", text="Product")
        tree.heading("quantity", text="Quantity")
        tree.heading("total", text="Total Price")
        tree.heading("paid", text="Amount Paid")
        tree.heading("debt", text="Debt Added")
        
        tree.column("date", width=180, anchor="center")
        tree.column("product", width=200, anchor="w")
        tree.column("quantity", width=100, anchor="center")
        tree.column("total", width=120, anchor="center")
        tree.column("paid", width=120, anchor="center")
        tree.column("debt", width=120, anchor="center")
        
        tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate data
        total_sales = 0
        total_paid = 0
        total_debt = 0
        
        for sale in sales:
            sale_id, product_name, quantity, total_price, amount_paid, date_str = sale
            debt = total_price - amount_paid if total_price > amount_paid else 0
            
            # Format date - handle multiple formats for Windows/Linux compatibility
            formatted_date = date_str
            if date_str:
                try:
                    # Try ISO format first
                    if '.' in date_str:
                        date_str = date_str.split('.')[0]
                    # Try common SQLite formats
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                            break
                        except:
                            continue
                except:
                    formatted_date = str(date_str) if date_str else "N/A"
            
            tree.insert("", "end", values=(
                formatted_date,
                product_name,
                f"{quantity:.1f}",
                f"GHS {total_price:.2f}",
                f"GHS {amount_paid:.2f}",
                f"GHS {debt:.2f}" if debt > 0 else "₵ 0.00"
            ))
            
            total_sales += total_price
            total_paid += amount_paid
            total_debt += debt
        
        # Summary
        summary_frame = ctk.CTkFrame(self.content_area, fg_color="#f8fafc", corner_radius=10)
        summary_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        summary_inner = ctk.CTkFrame(summary_frame, fg_color="transparent")
        summary_inner.pack(pady=15, padx=20)
        
        ctk.CTkLabel(summary_inner, text="Summary:", 
                     font=("Arial", 14, "bold"), 
                     text_color="#0f172a").pack(anchor="w", pady=(0, 10))
        
        stats_frame = ctk.CTkFrame(summary_inner, fg_color="transparent")
        stats_frame.pack(fill="x")
        
        ctk.CTkLabel(stats_frame, text=f"Total Sales: GHS {total_sales:.2f}", 
                     font=("Arial", 12), text_color="#0f172a").pack(side="left", padx=20)
        ctk.CTkLabel(stats_frame, text=f"Total Paid: GHS {total_paid:.2f}", 
                     font=("Arial", 12), text_color="#10b981").pack(side="left", padx=20)
        ctk.CTkLabel(stats_frame, text=f"Total Debt: GHS {total_debt:.2f}", 
                     font=("Arial", 12), text_color="#ef4444").pack(side="left", padx=20)
    
    def load_credit_history(self):
        """Load and display credit history (debt accumulation from sales)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get sales where debt was created (amount_paid < total_price)
        cursor.execute("""
            SELECT s.id, p.name, s.quantity, s.total_price, s.amount_paid, 
                   (s.total_price - s.amount_paid) as debt, s.date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.customer_id = ? AND s.amount_paid < s.total_price
            ORDER BY s.date DESC
        """, (self.customer_id,))
        
        credits = cursor.fetchall()
        conn.close()
        
        # Header
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="Credit History", 
                     font=("Arial", 18, "bold"), 
                     text_color="#0f172a").pack(side="left")
        
        total_label = ctk.CTkLabel(header_frame, 
                                   text=f"Total Credit Entries: {len(credits)}", 
                                   font=("Arial", 12), 
                                   text_color="#64748b")
        total_label.pack(side="right")
        
        # Table
        table_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Treeview styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                       fieldbackground="white", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#f59e0b')])
        
        tree = ttk.Treeview(table_frame, columns=("date", "product", "quantity", "total", "paid", "debt"), 
                           show="headings", height=15)
        
        tree.heading("date", text="Date")
        tree.heading("product", text="Product")
        tree.heading("quantity", text="Quantity")
        tree.heading("total", text="Total Price")
        tree.heading("paid", text="Amount Paid")
        tree.heading("debt", text="Debt Amount")
        
        tree.column("date", width=180, anchor="center")
        tree.column("product", width=200, anchor="w")
        tree.column("quantity", width=100, anchor="center")
        tree.column("total", width=120, anchor="center")
        tree.column("paid", width=120, anchor="center")
        tree.column("debt", width=120, anchor="center")
        
        tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate data
        total_debt = 0
        
        for credit in credits:
            sale_id, product_name, quantity, total_price, amount_paid, debt, date_str = credit
            
            # Format date - handle multiple formats for Windows/Linux compatibility
            formatted_date = date_str
            if date_str:
                try:
                    # Try ISO format first
                    if '.' in date_str:
                        date_str = date_str.split('.')[0]
                    # Try common SQLite formats
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                            break
                        except:
                            continue
                except:
                    formatted_date = str(date_str) if date_str else "N/A"
            
            tree.insert("", "end", values=(
                formatted_date,
                product_name,
                f"{quantity:.1f}",
                f"GHS {total_price:.2f}",
                f"GHS {amount_paid:.2f}",
                f"GHS {debt:.2f}"
            ))
            
            total_debt += debt
        
        # Summary
        summary_frame = ctk.CTkFrame(self.content_area, fg_color="#fef3c7", corner_radius=10)
        summary_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        summary_inner = ctk.CTkFrame(summary_frame, fg_color="transparent")
        summary_inner.pack(pady=15, padx=20)
        
        ctk.CTkLabel(summary_inner, text=f"Total Credit Accumulated: GHS {total_debt:.2f}", 
                     font=("Arial", 14, "bold"), 
                     text_color="#92400e").pack()
    
    def load_payment_history(self):
        """Load and display payment history"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get payment history
        cursor.execute("""
            SELECT id, amount, previous_balance, new_balance, date
            FROM payment_history
            WHERE customer_id = ?
            ORDER BY date DESC
        """, (self.customer_id,))
        
        payments = cursor.fetchall()
        conn.close()
        
        # Header
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="Payment History", 
                     font=("Arial", 18, "bold"), 
                     text_color="#0f172a").pack(side="left")
        
        total_label = ctk.CTkLabel(header_frame, 
                                   text=f"Total Payments: {len(payments)}", 
                                   font=("Arial", 12), 
                                   text_color="#64748b")
        total_label.pack(side="right")
        
        # Table
        table_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Treeview styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                       fieldbackground="white", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#10b981')])
        
        tree = ttk.Treeview(table_frame, columns=("date", "amount", "previous", "new", "reduction"), 
                           show="headings", height=15)
        
        tree.heading("date", text="Date")
        tree.heading("amount", text="Payment Amount")
        tree.heading("previous", text="Previous Balance")
        tree.heading("new", text="New Balance")
        tree.heading("reduction", text="Reduction")
        
        tree.column("date", width=180, anchor="center")
        tree.column("amount", width=150, anchor="center")
        tree.column("previous", width=150, anchor="center")
        tree.column("new", width=150, anchor="center")
        tree.column("reduction", width=150, anchor="center")
        
        tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate data
        total_paid = 0
        
        for payment in payments:
            pay_id, amount, previous_balance, new_balance, date_str = payment
            reduction = previous_balance - new_balance
            
            # Format date - handle multiple formats for Windows/Linux compatibility
            formatted_date = date_str
            if date_str:
                try:
                    # Try ISO format first
                    if '.' in date_str:
                        date_str = date_str.split('.')[0]
                    # Try common SQLite formats
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                            break
                        except:
                            continue
                except:
                    formatted_date = str(date_str) if date_str else "N/A"
            
            tree.insert("", "end", values=(
                formatted_date,
                f"GHS {amount:.2f}",
                f"GHS {previous_balance:.2f}",
                f"GHS {new_balance:.2f}",
                f"GHS {reduction:.2f}"
            ))
            
            total_paid += amount
        
        # Summary
        summary_frame = ctk.CTkFrame(self.content_area, fg_color="#dcfce7", corner_radius=10)
        summary_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        summary_inner = ctk.CTkFrame(summary_frame, fg_color="transparent")
        summary_inner.pack(pady=15, padx=20)
        
        ctk.CTkLabel(summary_inner, text=f"Total Payments Made: GHS {total_paid:.2f}", 
                     font=("Arial", 14, "bold"), 
                     text_color="#166534").pack()
        
        if not payments:
            no_data = ctk.CTkLabel(self.content_area, 
                                  text="No payment history found.\nPayments will appear here when recorded.", 
                                  font=("Arial", 14), 
                                  text_color="#64748b",
                                  justify="center")
            no_data.pack(expand=True)

