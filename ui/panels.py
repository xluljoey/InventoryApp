"""
Panel classes that can be embedded in tabs instead of opening separate windows
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from core.sales import get_today_revenue, get_sales_history
from core.products import get_all_products, get_all_customers, add_customer, add_product
from core.products import get_product_names, admin_add_product, admin_update_price, admin_overwrite_stock, admin_delete_product
from core.products import get_low_stock_products, get_expiring_products, get_expired_products
from db.database import get_db_connection
from datetime import datetime
from ui.analytics_window import AnalyticsWindow
from ui.customer_history_window import CustomerHistoryWindow
from ui.add_product_window import AddProductWindow
from ui.add_stock_window import AddStockWindow
from ui.receipt_generator import generate_receipt

class DailySalesPanel(ctk.CTkFrame):
    """Daily Sales panel for embedding in tabs"""
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        # Revenue Card
        revenue_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15, height=100)
        revenue_card.pack(fill="x", padx=20, pady=(20, 20))
        revenue_card.pack_propagate(False)
        
        ctk.CTkLabel(revenue_card, text="TODAY'S REVENUE", 
                     font=("Arial", 12, "bold"), text_color="#64748b").pack(pady=(15, 0))
        
        self.revenue_lbl = ctk.CTkLabel(revenue_card, text="GHS 0.00", 
                                        font=("Arial", 42, "bold"), text_color="#10b981")
        self.revenue_lbl.pack(pady=(5, 15))
        
        # Sales Records
        records_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        records_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(records_card, text="SALES RECORDS", 
                     font=("Arial", 12, "bold"), 
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
            try:
                sale_date = datetime.fromisoformat(s[5].split('.')[0]).date()
            except:
                sale_date = None
            
            if sale_date == today:
                values = (
                    s[0],  # ID
                    s[1],  # Product
                    s[2] if s[2] else "Cash",  # Customer
                    f"{s[3]:.1f}",  # Qty
                    f"{s[4]:.2f}",  # Total
                    "Full"  # Paid
                )
                self.tree.insert("", "end", values=values)
    
    def refresh(self):
        """Refresh the panel data"""
        self.load_data()

class AnalyticsPanel(ctk.CTkFrame):
    """Analytics panel - merged with Reports (kept for backwards compatibility)"""
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, fg_color="transparent")
        # Redirect to Reports panel
        self.parent_window = parent.winfo_toplevel()
        self.refresh_callback = refresh_callback
        self.setup_ui()
    
    def setup_ui(self):
        # This panel is now part of Reports & Analytics tab
        # Show message directing to Reports & Analytics
        info_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        info_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(info_card, text="📊 Reports & Analytics", 
                     font=("Arial", 24, "bold"), text_color="#10b981").pack(pady=40)
        
        ctk.CTkLabel(info_card, text="Analytics has been merged with Reports.", 
                     font=("Arial", 14), text_color="#64748b").pack(pady=10)
        
        ctk.CTkLabel(info_card, text="Click on the 'Reports & Analytics' tab above.", 
                     font=("Arial", 12), text_color="#94a3b8").pack(pady=5)
    
    def open_analytics(self):
        """Open full analytics window"""
        from ui.analytics_window import AnalyticsWindow
        AnalyticsWindow(self.parent_window)

class CustomersPanel(ctk.CTkFrame):
    """Customers panel for embedding in tabs"""
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        # Registration Card
        form_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        form_card.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(form_card, text="REGISTER NEW CUSTOMER", 
                     font=("Arial", 12, "bold"), 
                     text_color="#64748b").pack(pady=(15, 5))
        
        inner_form = ctk.CTkFrame(form_card, fg_color="transparent")
        inner_form.pack(pady=20, padx=20)
        
        self.name_entry = ctk.CTkEntry(inner_form, placeholder_text="Full Name", width=250, height=40)
        self.name_entry.grid(row=0, column=0, padx=10)
        
        self.phone_entry = ctk.CTkEntry(inner_form, placeholder_text="Phone Number", width=200, height=40)
        self.phone_entry.grid(row=0, column=1, padx=10)
        
        self.btn_add = ctk.CTkButton(inner_form, text="Add Customer", height=40,
                                    fg_color="#10b981", hover_color="#059669",
                                    font=("Arial", 12, "bold"),
                                    command=self.save_customer)
        self.btn_add.grid(row=0, column=2, padx=10)
        
        # Table Card
        table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        table_card.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(table_card, text="CUSTOMER LIST", 
                 font=("Arial", 12, "bold"), 
                 text_color="#64748b").grid(row=0, column=0, sticky="w", pady=(15, 10), padx=20)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                        fieldbackground="white", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#10b981')])
        
        tree_container = ctk.CTkFrame(table_card, fg_color="transparent")
        tree_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_container, columns=("id", "name", "phone", "balance"), 
                    show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="CUSTOMER NAME")
        self.tree.heading("phone", text="PHONE")
        self.tree.heading("balance", text="DEBT (GHS)")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("phone", width=150, anchor="center")
        self.tree.column("balance", width=120, anchor="center")

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Action Buttons (kept below the table so they remain visible)
        action_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        ctk.CTkButton(action_frame, text="✏️ Edit", 
                 command=self.edit_customer,
                 fg_color="#3b82f6", hover_color="#2563eb",
                 height=40, width=150,
                 font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="📊 View History", 
                     command=self.view_history,
                     fg_color="#10b981", hover_color="#059669",
                     height=40, width=200,
                     font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="💰 Clear Debt", 
                     command=self.clear_debt,
                     fg_color="#f59e0b", hover_color="#d97706",
                     height=40, width=150,
                     font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="🗑️ Delete", 
                     command=self.delete_customer,
                     fg_color="#ef4444", hover_color="#dc2626",
                     height=40, width=150,
                     font=("Arial", 11, "bold")).pack(side="left", padx=5)
    
    def save_customer(self):
        """Save new customer"""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Customer name is required", parent=self)
            return
        
        try:
            add_customer(name, phone)
            messagebox.showinfo("Success", f"Customer '{name}' added!", parent=self)
            self.name_entry.delete(0, "end")
            self.phone_entry.delete(0, "end")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)
    
    def load_data(self):
        """Load customer data"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        customers = get_all_customers()
        for c in customers:
            self.tree.insert("", "end", values=(c[0], c[1], c[2] or "", f"{c[3]:.2f}"))
    
    def edit_customer(self):
        """Edit selected customer"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer to edit", parent=self)
            return
        
        item = self.tree.item(selection[0])
        customer_id = item['values'][0]
        current_name = item['values'][1]
        current_phone = item['values'][2]
        
        # Create a simple edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Customer")
        dialog.geometry("400x320")
        dialog.after(10, lambda: dialog.focus_force())
        dialog.after(100, lambda: dialog.lift())
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Main container with background
        main_frame = ctk.CTkFrame(dialog, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(main_frame, text="Edit Customer Details", font=("Arial", 16, "bold"), text_color="#1e293b").pack(pady=(20, 15))
        
        name_entry = ctk.CTkEntry(main_frame, placeholder_text="Full Name", width=300, height=40)
        name_entry.pack(pady=10)
        name_entry.insert(0, current_name)
        
        phone_entry = ctk.CTkEntry(main_frame, placeholder_text="Phone Number", width=300, height=40)
        phone_entry.pack(pady=10)
        phone_entry.insert(0, str(current_phone))
        
        def save_changes():
            new_name = name_entry.get().strip()
            new_phone = phone_entry.get().strip()
            
            if not new_name:
                messagebox.showerror("Error", "Name cannot be empty", parent=dialog)
                return
            
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE customers SET name = ?, phone = ? WHERE id = ?", 
                             (new_name, new_phone, customer_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Customer updated successfully", parent=dialog)
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update customer: {e}", parent=dialog)
        
        ctk.CTkButton(dialog, text="Save Changes", command=save_changes,
                     fg_color="#10b981", hover_color="#059669", height=40, width=200).pack(pady=20)

    def view_history(self):
        """View customer purchase history"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer to view history", parent=self)
            return
        
        item = self.tree.item(selection[0])
        customer_id = item['values'][0]
        customer_name = item['values'][1]
        
        parent_window = self.winfo_toplevel()
        CustomerHistoryWindow(parent_window, customer_id, customer_name)
    
    def clear_debt(self):
        """Clear customer debt"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer", parent=self)
            return
        
        item = self.tree.item(selection[0])
        customer_id = item['values'][0]
        customer_name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Clear debt for {customer_name}?", parent=self):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE customers SET balance = 0 WHERE id = ?", (customer_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Debt cleared!", parent=self)
            self.load_data()
    
    def delete_customer(self):
        """Delete customer with admin authentication"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer to delete", parent=self)
            return
        
        item = self.tree.item(selection[0])
        customer_id = item['values'][0]
        customer_name = item['values'][1]
        
        # Verify admin password
        from tkinter.simpledialog import askstring
        from db.database import verify_admin_password
        
        pw = askstring("Admin Authentication", f"Enter Admin Password to delete '{customer_name}':", show="*")
        if pw is None:
            return
            
        if not verify_admin_password(pw):
            messagebox.showerror("Access Denied", "Incorrect password. Admin privileges required to delete customers.", parent=self)
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you absolutely sure you want to delete '{customer_name}'?\nThis will remove all their records permanently.", parent=self):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Customer deleted!", parent=self)
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete customer: {e}", parent=self)
    
    def refresh(self):
        """Refresh the panel data"""
        self.load_data()

class ReportsPanel(ctk.CTkFrame):
    """Reports & Analytics panel for embedding in tabs"""
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.refresh_callback = refresh_callback
        self.setup_ui()
    
    def setup_ui(self):
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(card, text="📊 Reports & Analytics", 
                     font=("Arial", 24, "bold"), text_color="#10b981").pack(pady=40)
        
        ctk.CTkLabel(card, text="Generate comprehensive business reports and analyze sales data", 
                     font=("Arial", 14), text_color="#64748b").pack(pady=10)
        
        # Report buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        ctk.CTkButton(btn_frame, text="📄 Generate Sales Report", 
                     command=self.generate_sales_report,
                     fg_color="#10b981", hover_color="#059669",
                     height=50, width=300,
                     font=("Arial", 14, "bold")).pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="📈 View Product Analytics", 
                     command=self.open_analytics,
                     fg_color="#3b82f6", hover_color="#2563eb",
                     height=50, width=300,
                     font=("Arial", 14, "bold")).pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="💰 Profit Margins", 
                     command=self.open_profit_margins,
                     fg_color="#8b5cf6", hover_color="#7c3aed",
                     height=50, width=300,
                     font=("Arial", 14, "bold")).pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="🔄 Reset All Analytics", 
                     command=self.reset_analytics,
                     fg_color="#f59e0b", hover_color="#d97706",
                     height=50, width=300,
                     font=("Arial", 14, "bold")).pack(pady=10)
    
    def generate_sales_report(self):
        """Generate sales report"""
        from ui.reports_window import ReportsWindow
        parent_window = self.winfo_toplevel()
        ReportsWindow(parent_window)
    
    def open_analytics(self):
        """Open analytics window"""
        from ui.analytics_window import AnalyticsWindow
        parent_window = self.winfo_toplevel()
        AnalyticsWindow(parent_window)
    
    def open_profit_margins(self):
        """Open profit margins window"""
        from ui.profit_margins_window import ProfitMarginsWindow
        parent_window = self.winfo_toplevel()
        ProfitMarginsWindow(parent_window)
    
    def reset_analytics(self):
        """Reset all analytics data with admin password verification"""
        # Request admin password
        from tkinter.simpledialog import askstring
        from db.database import verify_admin_password
        
        pw = askstring("Reset Analytics", "Enter Admin Password:", show="*")
        if pw is None:  # User clicked cancel
            return
        
        if not verify_admin_password(pw):
            messagebox.showerror("Access Denied", "Wrong password. Only admins can reset analytics.", parent=self)
            return
        
        # Confirm reset
        if not messagebox.askyesno("Confirm Reset", "Reset all analytics data?\nThis will clear all sales history.", parent=self):
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Delete all sales records
            cursor.execute("DELETE FROM sales")
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "All analytics data has been reset!", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset analytics: {e}", parent=self)

class ManageStockPanel(ctk.CTkFrame):
    """Manage Stock panel for embedding in tabs"""
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        # Tabs for different stock operations
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
    
    def setup_manage_tab(self):
        """Setup the Manage Existing Products tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_manage, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card, text="MANAGE EXISTING PRODUCTS", 
                     font=("Arial", 12, "bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=10)
        
        self.products = get_product_names()
        self.p_map = {p[1]: p[0] for p in self.products}
        product_names = list(self.p_map.keys()) if self.p_map else ["No Products"]
        
        ctk.CTkLabel(inner, text="Select Product:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        self.drop = ctk.CTkOptionMenu(inner, values=product_names, width=450, height=40, fg_color="#f8fafc", text_color="#1e293b")
        self.drop.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Update Price (GHS):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.up = ctk.CTkEntry(inner, placeholder_text="New price per bag", width=450, height=40)
        self.up.pack(pady=5)
        ctk.CTkButton(inner, text="Update Price", command=self.do_p, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=450).pack(pady=10)
        
        ctk.CTkLabel(inner, text="Correct Stock (Bags):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.us = ctk.CTkEntry(inner, placeholder_text="Number of bags to set", width=450, height=40)
        self.us.pack(pady=5)
        ctk.CTkButton(inner, text="Update Stock Level", command=self.do_s, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=450).pack(pady=10)
        
        ctk.CTkLabel(inner, text="Cost Price per Bag (GHS):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.ucost = ctk.CTkEntry(inner, placeholder_text="Cost price for profit calculation", width=450, height=40)
        self.ucost.pack(pady=5)
        ctk.CTkButton(inner, text="Update Cost Price", command=self.do_cost, 
                     fg_color="#8b5cf6", hover_color="#7c3aed", height=40, width=450).pack(pady=10)
        
        ctk.CTkButton(inner, text="DELETE THIS PRODUCT", command=self.do_d, 
                     fg_color="#ef4444", hover_color="#dc2626", height=40, width=450).pack(pady=(20, 15))
    
    def setup_add_tab(self):
        """Setup the Add New Product tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_add, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card, text="ADD NEW PRODUCT", 
                     font=("Arial", 12, "bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(inner, text="Product Name:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        self.en = ctk.CTkEntry(inner, placeholder_text="e.g. Rice, Maize, Soya", width=450, height=40)
        self.en.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Category:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.ec = ctk.CTkEntry(inner, placeholder_text="e.g. Feed, Grain", width=450, height=40)
        self.ec.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Selling Price per Bag (GHS):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.ep = ctk.CTkEntry(inner, placeholder_text="e.g. 100.00", width=450, height=40)
        self.ep.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Cost Price per Bag (GHS) - Optional:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.ecost = ctk.CTkEntry(inner, placeholder_text="e.g. 70.00 (for profit calculation)", width=450, height=40)
        self.ecost.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Weight per Bag (kg):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.ew = ctk.CTkEntry(inner, placeholder_text="e.g. 50", width=450, height=40)
        self.ew.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Initial Stock (kg):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.es = ctk.CTkEntry(inner, placeholder_text="e.g. 1000", width=450, height=40)
        self.es.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Low Stock Alert Threshold (Bags):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.ethreshold = ctk.CTkEntry(inner, placeholder_text="e.g. 5 (default)", width=450, height=40)
        self.ethreshold.insert(0, "5")
        self.ethreshold.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Batch Number (Optional):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.ebatch = ctk.CTkEntry(inner, placeholder_text="e.g. BATCH-2024-001", width=450, height=40)
        self.ebatch.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Expiry Date (Optional, YYYY-MM-DD):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.eexpiry = ctk.CTkEntry(inner, placeholder_text="e.g. 2024-12-31", width=450, height=40)
        self.eexpiry.pack(pady=5)
        
        ctk.CTkButton(inner, text="Add Product", command=self.do_a, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=450).pack(pady=(20, 15))
    
    def setup_arrivals_tab(self):
        """Setup the New Arrivals tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_arrivals, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card, text="NEW ARRIVALS / STOCK IN", 
                     font=("Arial", 12, "bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=10)
        
        self.products_arr = get_product_names()
        self.p_map_arr = {p[1]: p[0] for p in self.products_arr}
        product_names_arr = list(self.p_map_arr.keys()) if self.p_map_arr else ["No Products"]
        
        ctk.CTkLabel(inner, text="Select Product:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        self.drop_arr = ctk.CTkOptionMenu(inner, values=product_names_arr, width=450, height=40, fg_color="#f8fafc", text_color="#1e293b")
        self.drop_arr.pack(pady=5)
        
        ctk.CTkLabel(inner, text="Quantity to Add (kg):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(15, 5))
        self.qty_arr = ctk.CTkEntry(inner, placeholder_text="e.g. 500", width=450, height=40)
        self.qty_arr.pack(pady=5)
        
        ctk.CTkButton(inner, text="Add Stock", command=self.do_arr, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=450).pack(pady=(20, 15))
    
    def do_p(self):
        """Update price"""
        try:
            pname = self.drop.get()
            if pname == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            pid = self.p_map[pname]
            new_price = float(self.up.get())
            if admin_update_price(pid, new_price):
                messagebox.showinfo("Success", f"Price updated for {pname}!", parent=self)
                self.up.delete(0, "end")
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("Error", "Failed to update price", parent=self)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)
    
    def do_s(self):
        """Update stock"""
        try:
            pname = self.drop.get()
            if pname == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            pid = self.p_map[pname]
            bags = float(self.us.get())
            if admin_overwrite_stock(pid, bags):
                messagebox.showinfo("Success", f"Stock updated for {pname}!", parent=self)
                self.us.delete(0, "end")
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("Error", "Failed to update stock", parent=self)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)
    
    def do_cost(self):
        """Update cost price"""
        try:
            pname = self.drop.get()
            if pname == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            pid = self.p_map[pname]
            cost_text = self.ucost.get().strip()
            if not cost_text:
                messagebox.showerror("Error", "Please enter a cost price", parent=self)
                return
            cost_price = float(cost_text)
            if cost_price < 0:
                messagebox.showerror("Error", "Cost price cannot be negative", parent=self)
                return
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET cost_price = ? WHERE id = ?", (cost_price, pid))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Cost price updated for {pname}!", parent=self)
            self.ucost.delete(0, "end")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid cost price", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)
    
    def do_d(self):
        """Delete product"""
        pname = self.drop.get()
        if pname == "No Products":
            messagebox.showerror("Error", "No products available", parent=self)
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete '{pname}'?\nThis cannot be undone!", parent=self):
            pid = self.p_map[pname]
            if admin_delete_product(pid):
                messagebox.showinfo("Success", f"{pname} deleted!", parent=self)
                self.load_data()
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("Error", "Failed to delete product", parent=self)
    
    def do_a(self):
        """Add product"""
        try:
            name = self.en.get().strip()
            category = self.ec.get().strip()
            price = float(self.ep.get())
            weight = float(self.ew.get())
            stock = float(self.es.get())
            
            # Get optional fields
            threshold_text = self.ethreshold.get().strip()
            low_threshold = float(threshold_text) if threshold_text else 5.0
            
            batch_number = self.ebatch.get().strip() or None
            expiry_text = self.eexpiry.get().strip()
            expiry_date = expiry_text if expiry_text else None
            
            # Get cost price (optional)
            cost_text = self.ecost.get().strip()
            cost_price = float(cost_text) if cost_text else None
            
            # Validate expiry date format if provided
            if expiry_date:
                try:
                    from datetime import datetime
                    datetime.strptime(expiry_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Expiry date must be in YYYY-MM-DD format", parent=self)
                    return
            
            # Convert initial stock (kg) to number of bags
            if weight <= 0:
                messagebox.showerror("Error", "Weight per bag must be greater than 0", parent=self)
                return

            bags = stock / weight

            # Use add_product to preserve category/unit data
            add_product(name, category, 'bag', weight, price, bags, low_threshold, batch_number, expiry_date, cost_price)
            messagebox.showinfo("Success", f"{name} added!", parent=self)
            self.en.delete(0, "end")
            self.ec.delete(0, "end")
            self.ep.delete(0, "end")
            self.ecost.delete(0, "end")
            self.ew.delete(0, "end")
            self.es.delete(0, "end")
            self.ethreshold.delete(0, "end")
            self.ethreshold.insert(0, "5")
            self.ebatch.delete(0, "end")
            self.eexpiry.delete(0, "end")
            self.load_data()
            if self.refresh_callback:
                self.refresh_callback()
        except ValueError:
            messagebox.showerror("Error", "Please check all inputs", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)
    
    def do_arr(self):
        """Add stock arrival"""
        try:
            pname = self.drop_arr.get()
            if pname == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            parent_window = self.winfo_toplevel()
            AddStockWindow(parent_window, self.refresh_callback, self.p_map_arr[pname])
            self.qty_arr.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)
    
    def load_data(self):
        """Reload product data"""
        self.products = get_product_names()
        self.p_map = {p[1]: p[0] for p in self.products}
        product_names = list(self.p_map.keys()) if self.p_map else ["No Products"]
        if hasattr(self, 'drop'):
            self.drop.configure(values=product_names)
            if product_names and product_names[0] != "No Products":
                self.drop.set(product_names[0])
        
        self.products_arr = get_product_names()
        self.p_map_arr = {p[1]: p[0] for p in self.products_arr}
        product_names_arr = list(self.p_map_arr.keys()) if self.p_map_arr else ["No Products"]
        if hasattr(self, 'drop_arr'):
            self.drop_arr.configure(values=product_names_arr)
            if product_names_arr and product_names_arr[0] != "No Products":
                self.drop_arr.set(product_names_arr[0])
    
    def refresh(self):
        """Refresh the panel data"""
        self.load_data()


class AlertsPanel(ctk.CTkFrame):
    """Alerts panel showing low stock, expired, and near expiry products"""
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the alerts panel UI"""
        # Header
        header = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header, text="⚠️ Alerts & Notifications", 
                     font=("Arial", 18, "bold"), 
                     text_color="#0f172a").pack(pady=15, padx=20, anchor="w")
        
        # Main scrollable content
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Low Stock Section
        self.low_stock_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        self.low_stock_frame.pack(fill="x", pady=10)
        
        # Expired Products Section
        self.expired_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        self.expired_frame.pack(fill="x", pady=10)
        
        # Near Expiry Section
        self.expiring_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        self.expiring_frame.pack(fill="x", pady=10)
    
    def load_data(self):
        """Load and display all alerts"""
        # Clear existing content
        for widget in self.low_stock_frame.winfo_children():
            widget.destroy()
        for widget in self.expired_frame.winfo_children():
            widget.destroy()
        for widget in self.expiring_frame.winfo_children():
            widget.destroy()
        
        # Load Low Stock Products
        self.load_low_stock()
        
        # Load Expired Products
        self.load_expired()
        
        # Load Near Expiry Products
        self.load_expiring()
    
    def load_low_stock(self):
        """Load low stock products"""
        low_stock = get_low_stock_products()
        
        # Header
        header = ctk.CTkFrame(self.low_stock_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(header, text="📉 Low Stock Products", 
                     font=("Arial", 14, "bold"), 
                     text_color="#ef4444").pack(side="left")
        
        ctk.CTkLabel(header, text=f"{len(low_stock)} item(s)", 
                     font=("Arial", 12), 
                     text_color="#64748b").pack(side="right")
        
        if not low_stock:
            ctk.CTkLabel(self.low_stock_frame, text="✅ No low stock items", 
                        font=("Arial", 12), text_color="#10b981").pack(pady=15, padx=20)
            return
        
        # Table
        table_frame = ctk.CTkFrame(self.low_stock_frame, fg_color="transparent")
        table_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                       fieldbackground="white", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#fef3c7')])
        
        tree = ttk.Treeview(table_frame, columns=("name", "stock", "threshold"), show="headings", height=min(len(low_stock), 8))
        tree.heading("name", text="Product Name")
        tree.heading("stock", text="Current Stock (Bags)")
        tree.heading("threshold", text="Threshold")
        
        tree.column("name", width=300, anchor="w")
        tree.column("stock", width=150, anchor="center")
        tree.column("threshold", width=150, anchor="center")
        
        for p in low_stock:
            if len(p) >= 10:
                bags = p[6] / p[4] if p[4] > 0 else 0
                threshold = p[7] if p[7] is not None else 5.0
            else:
                bags = p[6] / p[4] if p[4] > 0 else 0
                threshold = 5.0
            
            tree.insert("", "end", values=(p[1], f"{bags:.1f}", f"{threshold:.1f}"))
        
        tree.pack(fill="x")
    
    def load_expired(self):
        """Load expired products"""
        expired = get_expired_products()
        
        # Header
        header = ctk.CTkFrame(self.expired_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(header, text="❌ Expired Products", 
                     font=("Arial", 14, "bold"), 
                     text_color="#dc2626").pack(side="left")
        
        ctk.CTkLabel(header, text=f"{len(expired)} item(s)", 
                     font=("Arial", 12), 
                     text_color="#64748b").pack(side="right")
        
        if not expired:
            ctk.CTkLabel(self.expired_frame, text="✅ No expired products", 
                        font=("Arial", 12), text_color="#10b981").pack(pady=15, padx=20)
            return
        
        # Table
        table_frame = ctk.CTkFrame(self.expired_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                       fieldbackground="white", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#fee2e2')])
        
        tree = ttk.Treeview(table_frame, columns=("name", "batch", "expiry", "stock"), show="headings", height=min(len(expired), 25))
        tree.heading("name", text="Product Name")
        tree.heading("batch", text="Batch Number")
        tree.heading("expiry", text="Expiry Date")
        tree.heading("stock", text="Stock (Bags)")
        
        tree.column("name", width=250, anchor="w")
        tree.column("batch", width=150, anchor="center")
        tree.column("expiry", width=150, anchor="center")
        tree.column("stock", width=120, anchor="center")
        
        for p in expired:
            bags = p[4] / p[5] if p[5] > 0 else 0
            batch = p[6] if len(p) > 6 and p[6] else "N/A"
            expiry = p[3] if p[3] else "N/A"
            
            tree.insert("", "end", values=(p[1], batch, expiry, f"{bags:.1f}"))
        
        # Add scrollbar for expired products
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
    
    def load_expiring(self):
        """Load near expiry products"""
        expiring = get_expiring_products(30)
        
        # Header
        header = ctk.CTkFrame(self.expiring_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(header, text="⏰ Near Expiry (Within 30 Days)", 
                     font=("Arial", 14, "bold"), 
                     text_color="#f59e0b").pack(side="left")
        
        ctk.CTkLabel(header, text=f"{len(expiring)} item(s)", 
                     font=("Arial", 12), 
                     text_color="#64748b").pack(side="right")
        
        if not expiring:
            ctk.CTkLabel(self.expiring_frame, text="✅ No products expiring soon", 
                        font=("Arial", 12), text_color="#10b981").pack(pady=15, padx=20)
            return
        
        # Table
        table_frame = ctk.CTkFrame(self.expiring_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                       fieldbackground="white", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#fef3c7')])
        
        tree = ttk.Treeview(table_frame, columns=("name", "batch", "expiry", "days", "stock"), show="headings", height=min(len(expiring), 25))
        tree.heading("name", text="Product Name")
        tree.heading("batch", text="Batch Number")
        tree.heading("expiry", text="Expiry Date")
        tree.heading("days", text="Days Left")
        tree.heading("stock", text="Stock (Bags)")
        
        tree.column("name", width=200, anchor="w")
        tree.column("batch", width=150, anchor="center")
        tree.column("expiry", width=120, anchor="center")
        tree.column("days", width=100, anchor="center")
        tree.column("stock", width=120, anchor="center")
        
        from datetime import datetime
        today = datetime.now().date()
        
        for p in expiring:
            bags = p[4] / p[5] if p[5] > 0 else 0
            batch = p[6] if len(p) > 6 and p[6] else "N/A"
            expiry = p[3] if p[3] else "N/A"
            
            # Calculate days until expiry
            days_left = "N/A"
            if expiry and expiry != "N/A":
                try:
                    exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
                    days = (exp_date - today).days
                    days_left = str(days) if days >= 0 else "0"
                except:
                    pass
            
            tree.insert("", "end", values=(p[1], batch, expiry, days_left, f"{bags:.1f}"))
        
        # Add scrollbar for near expiry products
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
    
    def refresh(self):
        """Refresh the panel data"""
        self.load_data()