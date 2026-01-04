import customtkinter as ctk
from tkinter import ttk, messagebox
from core.sales import get_sales_history
from core.products import get_all_products
from db.database import get_db_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from collections import defaultdict

class AnalyticsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Product Analytics")
        self.geometry("1300x750")
        self.configure(fg_color="#f1f5f9")
        self.withdraw()
        
        # Header
        header = ctk.CTkFrame(self, fg_color="white", corner_radius=15, height=80)
        header.pack(fill="x", padx=40, pady=20)
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="📊 Product Sales Analytics", font=("Arial", 18, "bold"), text_color="#10b981").pack(pady=15)
        
        # Product Selection Frame
        selector_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        selector_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(selector_frame, text="Select Product:", font=("Arial", 12, "bold")).pack(side="left", padx=15, pady=15)
        
        self.product_var = ctk.StringVar()
        self.product_dropdown = ctk.CTkComboBox(
            selector_frame,
            variable=self.product_var,
            values=[p[1] for p in get_all_products()],
            width=200,
            height=35,
            command=self.update_graphs
        )
        self.product_dropdown.pack(side="left", padx=(0, 15), pady=15)
        
        # Set first product as default
        products = get_all_products()
        if products:
            self.product_dropdown.set(products[0][1])
        
        # Graph Canvas
        self.canvas_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        self.deiconify()
        self.update_graphs()
        self.after(100, self.grab_set)
    
    def get_product_sales_data(self, product_name):
        """Get last 30 days sales data for a product"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sales_by_date = defaultdict(lambda: {"quantity": 0, "revenue": 0})
        
        # Join with products table to match by name
        cursor.execute("""
            SELECT date(s.date) as sale_date, SUM(s.quantity), SUM(s.total_price)
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE p.name = ? AND date(s.date) >= date('now', '-30 days', 'localtime')
            GROUP BY date(s.date)
            ORDER BY date(s.date) ASC
        """, (product_name,))
        
        for row in cursor.fetchall():
            date, qty, revenue = row
            sales_by_date[date] = {"quantity": qty or 0, "revenue": revenue or 0}
        
        conn.close()
        
        # Fill missing dates with zero
        all_dates = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
            all_dates.append(date)
        
        return all_dates, sales_by_date
    
    def update_graphs(self, value=None):
        """Update product graphs (accepts optional value from dropdown)"""
        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        product_name = self.product_var.get()
        if not product_name:
            return
        
        try:
            dates, sales_data = self.get_product_sales_data(product_name)
            quantities = [sales_data[d]["quantity"] for d in dates]
            revenues = [sales_data[d]["revenue"] for d in dates]
            
            # Check if there's any data
            total_qty = sum(quantities)
            total_revenue = sum(revenues)
            
            if total_qty == 0:
                # Show "No data" message
                no_data_frame = ctk.CTkFrame(self.canvas_frame, fg_color="white", corner_radius=15)
                no_data_frame.pack(fill="both", expand=True)
                
                msg_label = ctk.CTkLabel(no_data_frame, text=f"📊 No sales data yet for '{product_name}'",
                                        font=("Arial", 16, "bold"), text_color="#64748b")
                msg_label.pack(pady=80)
                
                sub_label = ctk.CTkLabel(no_data_frame, text="Sales will appear here once this product is sold",
                                        font=("Arial", 12), text_color="#94a3b8")
                sub_label.pack()
                return
            
            # Create figure with 2 subplots
            fig = Figure(figsize=(12, 5), dpi=100)
            fig.patch.set_facecolor("#f1f5f9")
            
            # Quantity Plot
            ax1 = fig.add_subplot(121)
            ax1.plot(range(len(dates)), quantities, marker='o', color='#10b981', linewidth=2, markersize=5)
            ax1.fill_between(range(len(dates)), quantities, alpha=0.3, color='#10b981')
            ax1.set_title(f'{product_name} - Quantity Sold (Last 30 Days)', fontsize=12, fontweight='bold', color='#10b981')
            ax1.set_xlabel('Date', fontsize=10)
            ax1.set_ylabel('Quantity (bags)', fontsize=10)
            ax1.set_xticks(range(0, len(dates), 5))
            ax1.set_xticklabels([dates[i] for i in range(0, len(dates), 5)], rotation=45, ha='right', fontsize=8)
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_facecolor('white')
            
            # Revenue Plot
            ax2 = fig.add_subplot(122)
            ax2.bar(range(len(dates)), revenues, color='#059669', alpha=0.7, width=0.6)
            ax2.set_title(f'{product_name} - Revenue (Last 30 Days)', fontsize=12, fontweight='bold', color='#10b981')
            ax2.set_xlabel('Date', fontsize=10)
            ax2.set_ylabel('Revenue (GHS)', fontsize=10)
            ax2.set_xticks(range(0, len(dates), 5))
            ax2.set_xticklabels([dates[i] for i in range(0, len(dates), 5)], rotation=45, ha='right', fontsize=8)
            ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
            ax2.set_facecolor('white')
            
            fig.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Summary Stats
            avg_qty = total_qty / len([q for q in quantities if q > 0]) if any(quantities) else 0
            
            stats_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
            stats_frame.pack(fill="x", padx=40, pady=(0, 20))
            
            stats_text = f"Total Quantity (30 days): {total_qty:.0f} bags | Total Revenue: GHS {total_revenue:.2f} | Avg Sale: {avg_qty:.1f} bags"
            ctk.CTkLabel(stats_frame, text=stats_text, font=("Arial", 11), text_color="#10b981").pack(pady=12)
        
        except Exception as e:
            # Show error message
            error_frame = ctk.CTkFrame(self.canvas_frame, fg_color="white", corner_radius=15)
            error_frame.pack(fill="both", expand=True)
            
            error_label = ctk.CTkLabel(error_frame, text="⚠️ Error Loading Analytics",
                                      font=("Arial", 14, "bold"), text_color="#ef4444")
            error_label.pack(pady=40)
            
            details_label = ctk.CTkLabel(error_frame, text=str(e),
                                        font=("Arial", 10), text_color="#64748b")
            details_label.pack(pady=10)
