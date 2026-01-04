import customtkinter as ctk
from tkinter import messagebox
from core.products import get_all_products, get_all_customers, add_customer
from core.sales import sell_product
from db.database import get_db_connection
from ui.receipt_generator import generate_receipt

class SellWindow(ctk.CTkToplevel):
    def __init__(self, parent, refresh_callback, pre_selected_product_name=None):
        super().__init__(parent)
        self.title("New Sale Transaction")
        self.geometry("700x900")
        self.configure(fg_color="#f1f5f9")
        self.refresh_callback = refresh_callback
        self.pre_selected_product = pre_selected_product_name
        
        self.customer_id = None
        self.selected_customer_name = None
        
        # Header
        ctk.CTkLabel(self, text="New Sale", 
                     font=ctk.CTkFont(size=28, weight="bold"), 
                     text_color="#0f172a").pack(pady=(30, 20))
        
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        
        # ===== PRODUCT SELECTION =====
        card1 = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card1.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card1, text="SELECT PRODUCT", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner1 = ctk.CTkFrame(card1, fg_color="transparent")
        inner1.pack(fill="x", padx=20, pady=10)
        
        self.products = get_all_products()
        product_names = [p[1] for p in self.products] if self.products else ["No Products"]
        
        ctk.CTkLabel(inner1, text="Product:", text_color="#0f172a", font=("Arial", 13)).pack(anchor="w", pady=(0, 5))
        self.product_var = ctk.StringVar(value=product_names[0] if product_names else "No Products")
        
        # Set pre-selected product if provided
        if pre_selected_product_name and pre_selected_product_name in product_names:
            self.product_var.set(pre_selected_product_name)
        
        self.product_dropdown = ctk.CTkOptionMenu(inner1, variable=self.product_var, 
                                                 values=product_names, width=600, height=50,
                                                 fg_color="#f8fafc", text_color="#1e293b", font=("Arial", 14),
                                                 dropdown_font=("Arial", 13),
                                                 command=lambda x: self.update_price_display())
        self.product_dropdown.pack(pady=5, fill="x", padx=0)
        
        # Price display
        ctk.CTkLabel(inner1, text="Unit Price (per Bag):", text_color="#0f172a", font=("Arial", 13)).pack(anchor="w", pady=(10, 5))
        self.price_lbl = ctk.CTkLabel(inner1, text="GHS 0.00", text_color="#10b981", font=("Arial", 16, "bold"))
        self.price_lbl.pack(anchor="w", pady=5)
        
        # ===== QUANTITY SELECTION =====
        card2 = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card2.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card2, text="QUANTITY", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner2 = ctk.CTkFrame(card2, fg_color="transparent")
        inner2.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(inner2, text="Quantity (Bags):", text_color="#0f172a", font=("Arial", 13)).pack(anchor="w", pady=(0, 5))
        self.qty_entry = ctk.CTkEntry(inner2, placeholder_text="Enter number of bags", width=500, height=40, font=("Arial", 13))
        self.qty_entry.pack(pady=5)
        self.qty_entry.bind("<KeyRelease>", lambda e: self.update_total_display())
        
        # Total price display
        ctk.CTkLabel(inner2, text="Total Price:", text_color="#0f172a", font=("Arial", 13)).pack(anchor="w", pady=(10, 5))
        self.total_lbl = ctk.CTkLabel(inner2, text="GHS 0.00", text_color="#10b981", font=("Arial", 16, "bold"))
        self.total_lbl.pack(anchor="w", pady=5)
        
        # ===== CUSTOMER SELECTION =====
        card3 = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card3.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card3, text="CUSTOMER", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner3 = ctk.CTkFrame(card3, fg_color="transparent")
        inner3.pack(fill="x", padx=20, pady=10)
        
        self.customer_lbl = ctk.CTkLabel(inner3, text="No customer selected", text_color="#64748b", font=("Arial", 13))
        self.customer_lbl.pack(anchor="w", pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(inner3, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(btn_frame, text="SELECT CUSTOMER", command=self.select_customer, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=240).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="CASH SALE", command=self.clear_customer, 
                     fg_color="#64748b", hover_color="#475569", height=40, width=240).pack(side="left", padx=5)
        
        # Payment section (shown only if customer selected)
        self.payment_frame = ctk.CTkFrame(inner3, fg_color="transparent")
        self.payment_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(self.payment_frame, text="Amount Paid (GHS):", text_color="#0f172a", font=("Arial", 13)).pack(anchor="w", pady=(0, 5))
        self.paid_entry = ctk.CTkEntry(self.payment_frame, placeholder_text="Amount customer paid", width=500, height=40, font=("Arial", 13))
        self.paid_entry.pack(pady=5)
        
        self.payment_frame.pack_forget()
        
        # ===== REMARKS (COLLAPSIBLE) =====
        card_remarks = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card_remarks.pack(fill="x", pady=15)
        
        # Header with toggle button
        remarks_header = ctk.CTkFrame(card_remarks, fg_color="transparent")
        remarks_header.pack(fill="x", padx=20, pady=(15, 0))
        
        ctk.CTkLabel(remarks_header, text="REMARKS (Optional)", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(side="left", anchor="w")
        
        self.remarks_expanded = False
        self.remarks_toggle_btn = ctk.CTkButton(remarks_header, text="▼", width=30, height=30,
                                               command=self.toggle_remarks, fg_color="transparent",
                                               text_color="#64748b", hover_color="#e2e8f0")
        self.remarks_toggle_btn.pack(side="right", padx=(10, 0))
        
        # Remarks content (initially hidden)
        inner_remarks = ctk.CTkFrame(card_remarks, fg_color="transparent")
        inner_remarks.pack(fill="x", padx=20, pady=(10, 15))
        
        self.remarks_text = ctk.CTkTextbox(inner_remarks, width=500, height=80, 
                                          fg_color="#f8fafc", text_color="#1e293b",
                                          border_color="#e2e8f0", border_width=1, font=("Arial", 12))
        self.remarks_text.pack(fill="x", pady=5)
        
        self.remarks_container = inner_remarks
        self.remarks_text.pack_forget()  # Hide by default
        card4 = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card4.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card4, text="TRANSACTION SUMMARY", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner4 = ctk.CTkFrame(card4, fg_color="transparent")
        inner4.pack(fill="x", padx=20, pady=10)
        
        self.summary_lbl = ctk.CTkLabel(inner4, text="Ready to process sale", text_color="#64748b", font=("Arial", 13), justify="left")
        self.summary_lbl.pack(anchor="w", pady=10)
        
        ctk.CTkButton(inner4, text="COMPLETE SALE", command=self.process_sale, 
                     fg_color="#10b981", hover_color="#059669", height=50, width=500, 
                     font=("Arial", 14, "bold")).pack(pady=(15, 20))
        
        self.update_price_display()
        self.grab_set()
    
    def update_price_display(self):
        """Update the price label when product is selected"""
        try:
            product_name = self.product_var.get()
            for p in self.products:
                if p[1] == product_name:
                    self.price_lbl.configure(text=f"GHS {p[5]:.2f}")
                    self.update_total_display()
                    break
        except:
            pass
    
    def update_total_display(self):
        """Update total price based on quantity"""
        try:
            product_name = self.product_var.get()
            qty_text = self.qty_entry.get()
            
            if not qty_text:
                self.total_lbl.configure(text="GHS 0.00")
                return
            
            qty = float(qty_text)
            
            # Get price per bag
            price_per_bag = None
            for p in self.products:
                if p[1] == product_name:
                    price_per_bag = p[5]
                    break
            
            if price_per_bag is None:
                return
            
            total = qty * price_per_bag
            self.total_lbl.configure(text=f"GHS {total:.2f}")
        except:
            pass
    
    def toggle_remarks(self):
        """Toggle remarks section visibility"""
        self.remarks_expanded = not self.remarks_expanded
        if self.remarks_expanded:
            self.remarks_text.pack(fill="x", pady=5)
            self.remarks_toggle_btn.configure(text="▲")
        else:
            self.remarks_text.pack_forget()
            self.remarks_toggle_btn.configure(text="▼")
    
    def select_customer(self):
        """Open customer selection dialog"""
        CustomerSelectWindow(self, self.set_customer)
    
    def set_customer(self, customer_id, customer_name):
        """Set the selected customer"""
        self.customer_id = customer_id
        self.selected_customer_name = customer_name
        self.customer_lbl.configure(text=f"Customer: {customer_name}", text_color="#0f172a")
        self.payment_frame.pack(fill="x", pady=(10, 0))
    
    def clear_customer(self):
        """Clear customer selection for cash sale"""
        self.customer_id = None
        self.selected_customer_name = None
        self.customer_lbl.configure(text="No customer selected (Cash Sale)", text_color="#64748b")
        self.paid_entry.delete(0, "end")
        self.payment_frame.pack_forget()
    
    def process_sale(self):
        """Process the sale"""
        try:
            product_name = self.product_var.get()
            if product_name == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            
            qty_text = self.qty_entry.get()
            if not qty_text:
                messagebox.showerror("Error", "Please enter quantity", parent=self)
                return
            
            qty = float(qty_text)
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0", parent=self)
                return
            
            # Get product ID and price
            product_id = None
            price_per_bag = None
            for p in self.products:
                if p[1] == product_name:
                    product_id = p[0]
                    price_per_bag = p[5]
                    break
            
            if not product_id:
                messagebox.showerror("Error", "Product not found", parent=self)
                return
            
            # Get amount paid
            amount_paid = 0.0
            if self.customer_id:
                paid_text = self.paid_entry.get()
                if paid_text:
                    amount_paid = float(paid_text)
            
            # Get remarks if any
            remarks = self.remarks_text.get("0.0", "end").strip() if self.remarks_expanded else ""
            
            # Process the sale
            total_price = qty * price_per_bag
            if sell_product(product_id, qty, "Bags", self.customer_id, amount_paid):
                # Show success and ask about receipt
                result = messagebox.askyesno("Success", 
                    f"Sale completed!\n\nProduct: {product_name}\nQuantity: {qty:.1f} bags\nTotal: GHS {total_price:.2f}\n\nPrint Receipt?", 
                    parent=self)
                
                # Generate receipt if user wants it
                if result:
                    try:
                        receipt_path = generate_receipt(
                            product_name=product_name,
                            quantity=qty,
                            unit_price=price_per_bag,
                            total_price=total_price,
                            customer_name=self.selected_customer_name,
                            payment_method="Credit" if self.customer_id else "Walk-in",
                            remarks=remarks,
                            parent=self  # Pass the window as parent
                        )
                        if receipt_path:
                            messagebox.showinfo("Success", f"Receipt saved:\n{receipt_path}", parent=self)
                    except Exception as e:
                        messagebox.showerror("Receipt Error", f"Could not generate receipt: {e}", parent=self)
                
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Error", "Insufficient stock or database error", parent=self)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)


class CustomerSelectWindow(ctk.CTkToplevel):
    """Window for selecting or adding a customer"""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Select Customer")
        self.geometry("500x600")
        self.configure(fg_color="#f1f5f9")
        self.callback = callback
        
        # Header
        ctk.CTkLabel(self, text="Customer Selection", 
                     font=ctk.CTkFont(size=24, weight="bold"), 
                     text_color="#0f172a").pack(pady=(30, 20))
        
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Existing customers
        card1 = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card1.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card1, text="EXISTING CUSTOMERS", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner1 = ctk.CTkFrame(card1, fg_color="transparent")
        inner1.pack(fill="x", padx=20, pady=10)
        
        customers = get_all_customers()
        customer_names = [(c[0], c[1]) for c in customers] if customers else []
        
        if customer_names:
            for cust_id, cust_name in customer_names:
                btn = ctk.CTkButton(inner1, text=cust_name, 
                                   command=lambda id=cust_id, name=cust_name: self.select_and_close(id, name),
                                   fg_color="#f8fafc", text_color="#0f172a", hover_color="#e2e8f0",
                                   height=40, width=450)
                btn.pack(pady=5)
        else:
            ctk.CTkLabel(inner1, text="No customers yet", text_color="#64748b", font=("Arial", 11)).pack(pady=10)
        
        # New customer
        card2 = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card2.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card2, text="ADD NEW CUSTOMER", 
                     font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner2 = ctk.CTkFrame(card2, fg_color="transparent")
        inner2.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(inner2, text="Customer Name:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(inner2, placeholder_text="Full name", width=450, height=40)
        self.name_entry.pack(pady=5)
        
        ctk.CTkLabel(inner2, text="Phone (Optional):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(10, 5))
        self.phone_entry = ctk.CTkEntry(inner2, placeholder_text="Phone number", width=450, height=40)
        self.phone_entry.pack(pady=5)
        
        ctk.CTkButton(inner2, text="ADD CUSTOMER", command=self.add_new_customer, 
                     fg_color="#10b981", hover_color="#059669", height=40, width=450).pack(pady=(15, 20))
        
        self.grab_set()
    
    def select_and_close(self, customer_id, customer_name):
        """Select a customer and close the window"""
        self.callback(customer_id, customer_name)
        self.destroy()
    
    def add_new_customer(self):
        """Add a new customer"""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Customer name is required", parent=self)
            return
        
        try:
            add_customer(name, phone)
            messagebox.showinfo("Success", f"Customer '{name}' added!", parent=self)
            
            # Get the newly added customer's ID
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM customers WHERE name = ? ORDER BY id DESC LIMIT 1", (name,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                self.callback(result[0], name)
                self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}", parent=self)