import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from core.products import add_customer, get_all_customers
from db.database import get_db_connection

class CustomerWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Customer Management")
        self.geometry("1100x850")  # Large enough to show all buttons without resizing
        self.minsize(1000, 750)  # Prevent window from being too small
        self.configure(fg_color="#f1f5f9")
        self.minsize(1000, 750)  # Set minimum size to prevent too small windows
        
        # Performance optimizations for Linux
        try:
            # Disable window decorations that can cause lag
            self.update_idletasks()
        except:
            pass

        # Linux focus fixes (optimized)
        self.lift()
        self.attributes("-topmost", True)
        # Reduce delay for faster window appearance
        self.after(50, lambda: self.attributes("-topmost", False))
        self.grab_set()

        # Header
        ctk.CTkLabel(self, text="Customer Management", 
                     font=ctk.CTkFont(size=28, weight="bold"), 
                     text_color="#0f172a").pack(pady=(30, 20))

        # Registration Card
        form_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        form_card.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(form_card, text="REGISTER NEW CUSTOMER", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 5))

        inner_form = ctk.CTkFrame(form_card, fg_color="transparent")
        inner_form.pack(pady=20, padx=20)

        self.name_entry = ctk.CTkEntry(inner_form, placeholder_text="Full Name", width=250, height=40)
        self.name_entry.grid(row=0, column=0, padx=10)

        self.phone_entry = ctk.CTkEntry(inner_form, placeholder_text="Phone Number", width=200, height=40)
        self.phone_entry.grid(row=0, column=1, padx=10)

        self.btn_add = ctk.CTkButton(inner_form, text="Add Customer", height=40,
                                    fg_color="#10b981", hover_color="#059669",
                                    font=ctk.CTkFont(weight="bold"),
                                    command=self.save_customer)
        self.btn_add.grid(row=0, column=2, padx=10)

        # Table Card - Use grid for better control
        table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        table_card.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Header
        ctk.CTkLabel(table_card, text="CUSTOMER LIST", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        # Consistent Treeview Styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#1e293b", 
                        fieldbackground="white", rowheight=35, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#f8fafc")
        style.map("Treeview", background=[('selected', '#10b981')])

        # Use grid for table_card to manage layout better
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(1, weight=1)
        
        # Tree and scrollbar container - Fixed to leave room for buttons
        tree_container = ctk.CTkFrame(table_card, fg_color="transparent")
        tree_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(tree_container, columns=("id", "name", "phone", "balance"), 
                                show="headings", height=10)  # Reduced to ensure buttons visible
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="CUSTOMER NAME")
        self.tree.heading("phone", text="PHONE")
        self.tree.heading("balance", text="DEBT (GHS)")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("phone", width=150, anchor="center")
        self.tree.column("balance", width=120, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Action Buttons
        action_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        ctk.CTkButton(action_frame, text="✏️ Edit Customer", 
                     command=self.edit_customer,
                     fg_color="#3b82f6", hover_color="#2563eb",
                     height=40, width=140, font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="💰 Pay Debt", 
                     command=self.pay_debt,
                     fg_color="#10b981", hover_color="#059669",
                     height=40, width=140, font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="✏️ Adjust Debt", 
                     command=self.adjust_debt,
                     fg_color="#f59e0b", hover_color="#d97706",
                     height=40, width=140, font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text="🗑️ Delete Customer", 
                     command=self.delete_customer,
                     fg_color="#ef4444", hover_color="#dc2626",
                     height=40, width=160, font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        self.after(200, self.load_customers)

    def save_customer(self):
        name = self.name_entry.get().strip()
        if name:
            add_customer(name, self.phone_entry.get().strip())
            messagebox.showinfo("Success", f"Customer {name} added!", parent=self)
            self.name_entry.delete(0, "end")
            self.phone_entry.delete(0, "end")
            self.load_customers()
        else:
            messagebox.showerror("Error", "Name is required!", parent=self)

    def load_customers(self):
        # Batch update for better performance
        items_to_delete = list(self.tree.get_children())
        if items_to_delete:
            for item in items_to_delete:
                self.tree.delete(item)
        
        # Get all customers at once
        customers = get_all_customers()
        # Batch insert for better performance
        for c in customers:
            # Format balance column
            display_vals = list(c)
            if len(display_vals) > 3: 
                display_vals[3] = f"₵ {display_vals[3]:.2f}"
            self.tree.insert("", "end", values=display_vals)
        
        # Update display once at the end
        self.update_idletasks()
    
    def get_selected_customer(self):
        """Get the selected customer from tree"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer first!", parent=self)
            return None
        
        item = self.tree.item(selection[0])
        values = item['values']
        return {
            'id': values[0],
            'name': values[1],
            'phone': values[2],
            'balance': float(values[3].replace('₵ ', '').replace(',', ''))
        }
    
    def edit_customer(self):
        """Edit customer name and phone"""
        customer = self.get_selected_customer()
        if not customer:
            return
        
        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Customer")
        dialog.geometry("450x350")
        dialog.configure(fg_color="#f1f5f9")
        dialog.transient(self)
        
        # Linux/Fedora display fixes - updated order for better rendering
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(100, lambda: self._setup_edit_dialog_content(dialog, customer))
        dialog.grab_set()
        dialog.after(50, lambda: dialog.attributes("-topmost", False))
    
    def _setup_edit_dialog_content(self, dialog, customer):
        """Helper method to set up the edit dialog content after a delay to ensure proper rendering"""
        ctk.CTkLabel(dialog, text=f"Edit Customer: {customer['name']}", 
                    font=("Arial", 18, "bold"), 
                    text_color="#0f172a").pack(pady=(20, 20))
        
        content = ctk.CTkFrame(dialog, fg_color="white", corner_radius=15)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(content, text="Customer Name:", 
                    text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(20, 5))
        
        name_entry = ctk.CTkEntry(content, width=400, height=40)
        name_entry.insert(0, customer['name'])
        name_entry.pack(padx=20, pady=(0, 10))
        
        ctk.CTkLabel(content, text="Phone Number:", 
                    text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(10, 5))
        
        phone_entry = ctk.CTkEntry(content, width=400, height=40)
        phone_entry.insert(0, customer['phone'])
        phone_entry.pack(padx=20, pady=(0, 20))
        
        def save_changes():
            new_name = name_entry.get().strip()
            new_phone = phone_entry.get().strip()
            
            if not new_name:
                messagebox.showerror("Error", "Name cannot be empty!", parent=dialog)
                return
            
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE customers SET name = ?, phone = ? WHERE id = ?", 
                             (new_name, new_phone, customer['id']))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Customer updated successfully!", parent=dialog)
                dialog.destroy()
                self.load_customers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {e}", parent=dialog)
        
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        ctk.CTkButton(btn_frame, text="Save Changes", command=save_changes,
                     fg_color="#10b981", hover_color="#059669",
                     width=150, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy,
                     fg_color="#64748b", hover_color="#475569",
                     width=100, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        # Final update to ensure all elements are rendered properly
        dialog.update_idletasks()
        dialog.focus_set()  # Ensure dialog gets focus after all elements are added
    
    def pay_debt(self):
        """Record a debt payment"""
        customer = self.get_selected_customer()
        if not customer:
            return
        
        if customer['balance'] <= 0:
            messagebox.showinfo("No Debt", f"{customer['name']} has no outstanding debt.", parent=self)
            return
        
        # Create payment dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Pay Debt")
        dialog.geometry("450x400")
        dialog.configure(fg_color="#f1f5f9")
        dialog.transient(self)
        
        # Linux/Fedora display fixes - updated order for better rendering
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(100, lambda: self._setup_pay_debt_dialog_content(dialog, customer))
        dialog.grab_set()
        dialog.after(50, lambda: dialog.attributes("-topmost", False))
    
    def _setup_pay_debt_dialog_content(self, dialog, customer):
        """Helper method to set up the pay debt dialog content after a delay to ensure proper rendering"""
        # Header label
        header_label = ctk.CTkLabel(dialog, text=f"Pay Debt: {customer['name']}", 
                    font=("Arial", 18, "bold"), 
                    text_color="#0f172a")
        header_label.pack(pady=(20, 10))
        
        content = ctk.CTkFrame(dialog, fg_color="white", corner_radius=15)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Show current debt
        debt_frame = ctk.CTkFrame(content, fg_color="#fee2e2", corner_radius=10)
        debt_frame.pack(fill="x", padx=20, pady=(20, 20))
        
        ctk.CTkLabel(debt_frame, text="Current Debt:", 
                    font=("Arial", 12), text_color="#991b1b").pack(pady=(10, 0))
        ctk.CTkLabel(debt_frame, text=f"GHS {customer['balance']:.2f}", 
                    font=("Arial", 24, "bold"), text_color="#dc2626").pack(pady=(0, 10))
        
        ctk.CTkLabel(content, text="Payment Amount (GHS):", 
                    text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(20, 5))
        
        payment_entry = ctk.CTkEntry(content, width=400, height=40, 
                                     placeholder_text=f"Enter amount (max: {customer['balance']:.2f})")
        payment_entry.pack(padx=20, pady=(0, 20))
        
        def process_payment():
            try:
                payment = float(payment_entry.get().strip())
                
                if payment <= 0:
                    messagebox.showerror("Error", "Payment must be greater than 0!", parent=dialog)
                    return
                
                if payment > customer['balance']:
                    messagebox.showerror("Error", f"Payment cannot exceed debt (GHS {customer['balance']:.2f})!", parent=dialog)
                    return
                
                # Update customer balance and record payment history
                conn = get_db_connection()
                cursor = conn.cursor()
                previous_balance = customer['balance']
                new_balance = previous_balance - payment
                
                # Update balance
                cursor.execute("UPDATE customers SET balance = ? WHERE id = ?", 
                             (new_balance, customer['id']))
                
                # Record payment in history
                cursor.execute("""
                    INSERT INTO payment_history (customer_id, amount, previous_balance, new_balance)
                    VALUES (?, ?, ?, ?)
                """, (customer['id'], payment, previous_balance, new_balance))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", 
                                  f"Payment recorded: GHS {payment:.2f}\nNew balance: GHS {new_balance:.2f}", 
                                  parent=dialog)
                dialog.destroy()
                self.load_customers()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process payment: {e}", parent=dialog)
        
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        ctk.CTkButton(btn_frame, text="Process Payment", command=process_payment,
                     fg_color="#10b981", hover_color="#059669",
                     width=180, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy,
                     fg_color="#64748b", hover_color="#475569",
                     width=100, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        # Final update to ensure all elements are rendered properly
        dialog.update_idletasks()
        dialog.focus_set()  # Ensure dialog gets focus after all elements are added
    
    def adjust_debt(self):
        """Manually adjust customer debt (for corrections)"""
        customer = self.get_selected_customer()
        if not customer:
            return
        
        # Create adjustment dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Adjust Debt")
        dialog.geometry("450x400")
        dialog.configure(fg_color="#f1f5f9")
        dialog.transient(self)
        
        # Linux/Fedora display fixes - updated order for better rendering
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(100, lambda: self._setup_adjust_debt_dialog_content(dialog, customer))
        dialog.grab_set()
        dialog.after(50, lambda: dialog.attributes("-topmost", False))
    
    def _setup_adjust_debt_dialog_content(self, dialog, customer):
        """Helper method to set up the adjust debt dialog content after a delay to ensure proper rendering"""
        # Header label
        header_label = ctk.CTkLabel(dialog, text=f"Adjust Debt: {customer['name']}", 
                    font=("Arial", 18, "bold"), 
                    text_color="#0f172a")
        header_label.pack(pady=(20, 10))
        
        content = ctk.CTkFrame(dialog, fg_color="white", corner_radius=15)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Show current debt
        debt_frame = ctk.CTkFrame(content, fg_color="#fef3c7", corner_radius=10)
        debt_frame.pack(fill="x", padx=20, pady=(20, 20))
        
        ctk.CTkLabel(debt_frame, text="Current Debt:", 
                    font=("Arial", 12), text_color="#92400e").pack(pady=(10, 0))
        ctk.CTkLabel(debt_frame, text=f"GHS {customer['balance']:.2f}", 
                    font=("Arial", 24, "bold"), text_color="#d97706").pack(pady=(0, 10))
        
        ctk.CTkLabel(content, text="New Debt Amount (GHS):", 
                    text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(20, 5))
        
        debt_entry = ctk.CTkEntry(content, width=400, height=40, 
                                  placeholder_text="Enter new debt amount")
        debt_entry.insert(0, str(customer['balance']))
        debt_entry.pack(padx=20, pady=(0, 10))
        
        # Warning
        warning_frame = ctk.CTkFrame(content, fg_color="#fee2e2", corner_radius=10)
        warning_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkLabel(warning_frame, 
                    text="⚠️ Use this carefully! This directly sets the debt amount.\nUse 'Pay Debt' for recording payments.", 
                    font=("Arial", 10), text_color="#991b1b", justify="center").pack(pady=10)
        
        def apply_adjustment():
            try:
                new_debt = float(debt_entry.get().strip())
                
                if new_debt < 0:
                    messagebox.showerror("Error", "Debt cannot be negative!", parent=dialog)
                    return
                
                # Confirm
                if not messagebox.askyesno("Confirm", 
                                          f"Set debt to GHS {new_debt:.2f}?\n(Current: GHS {customer['balance']:.2f})", 
                                          parent=dialog):
                    return
                
                # Update customer balance
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE customers SET balance = ? WHERE id = ?", 
                             (new_debt, customer['id']))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", f"Debt adjusted to GHS {new_debt:.2f}", parent=dialog)
                dialog.destroy()
                self.load_customers()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to adjust debt: {e}", parent=dialog)
        
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        ctk.CTkButton(btn_frame, text="Apply Adjustment", command=apply_adjustment,
                     fg_color="#f59e0b", hover_color="#d97706",
                     width=180, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy,
                     fg_color="#64748b", hover_color="#475569",
                     width=100, height=40, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        # Final update to ensure all elements are rendered properly
        dialog.update_idletasks()
        dialog.focus_set()  # Ensure dialog gets focus after all elements are added
    
    def delete_customer(self):
        """Delete a customer"""
        customer = self.get_selected_customer()
        if not customer:
            return
        
        # Warn if customer has debt
        warning = f"Delete customer '{customer['name']}'?"
        if customer['balance'] > 0:
            warning += f"\n\n⚠️ This customer has an outstanding debt of GHS {customer['balance']:.2f}!"
        
        if not messagebox.askyesno("Confirm Delete", warning, parent=self):
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id = ?", (customer['id'],))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Customer '{customer['name']}' deleted.", parent=self)
            self.load_customers()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {e}", parent=self)