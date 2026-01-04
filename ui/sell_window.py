import customtkinter as ctk
from tkinter import messagebox
from core.products import get_all_products, get_all_customers, add_customer
from core.sales import sell_product
from db.database import get_db_connection
from ui.receipt_generator import generate_receipt

class SellWindow(ctk.CTkToplevel):
    """Multi-product sale window supporting multiple items in one transaction"""
    def __init__(self, parent, refresh_callback, pre_selected_product_name=None):
        super().__init__(parent)
        self.title("New Sale Transaction (Multiple Items)")
        self.geometry("1000x750")  # Fixed size for better control
        self.configure(fg_color="#f1f5f9")
        self.resizable(True, True)
        self.minsize(900, 700)
        self.refresh_callback = refresh_callback
        self.pre_selected_product = pre_selected_product_name
        
        self.customer_id = None
        self.selected_customer_name = None
        self.cart_items = []  # List of {product_id, product_name, qty, price_per_bag, total}
        self.products = get_all_products()
        
        # Linux/Fedora display fixes
        self.lift()
        self.attributes("-topmost", True)
        self.after(50, lambda: self.attributes("-topmost", False))
        self.update_idletasks()
        
        # Use grid for better control
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#1e293b", height=55, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(header_frame, text="💰 New Sale - Multiple Items", 
                     font=("Arial", 20, "bold"),
                     text_color="white").pack(pady=12)
        
        # Main container using grid
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=8)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=2)  # Middle section expands more
        main_container.grid_rowconfigure(2, weight=0)  # Bottom section fixed
        
        # Top: Customer section (compact)
        self.setup_customer_section(main_container)
        
        # Middle: Two-column layout
        columns_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        columns_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        columns_frame.grid_columnconfigure(0, weight=0)  # Left column fixed
        columns_frame.grid_columnconfigure(1, weight=1)  # Right column expands
        columns_frame.grid_rowconfigure(0, weight=1)  # Allow rows to expand
        
        # LEFT COLUMN: Add Item Section
        left_column = ctk.CTkFrame(columns_frame, fg_color="transparent", width=400)
        left_column.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        left_column.pack_propagate(False)
        
        self.setup_add_item_section(left_column)
        
        # RIGHT COLUMN: Cart Display
        right_column = ctk.CTkFrame(columns_frame, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew")
        
        self.setup_cart_section(right_column)
        
        # Bottom: Totals, Remarks (tabbed), and Checkout (always visible)
        self.setup_bottom_section(main_container)
        
        self.grab_set()
    
    def setup_customer_section(self, parent):
        """Setup compact customer selection section"""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, height=80)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        card.pack_propagate(False)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Customer info and buttons in one row
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="y", expand=True)
        
        self.customer_lbl = ctk.CTkLabel(info_frame, text="👤 No customer selected (Cash Sale)", 
                                        text_color="#64748b", font=("Arial", 13))
        self.customer_lbl.pack(anchor="w")
        
        # Payment entry (shown only if customer selected)
        self.payment_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        self.payment_frame.pack(fill="x", pady=(5, 0))
        
        payment_row = ctk.CTkFrame(self.payment_frame, fg_color="transparent")
        payment_row.pack(fill="x")
        
        ctk.CTkLabel(payment_row, text="Amount Paid:", text_color="#0f172a", font=("Arial", 11)).pack(side="left", padx=(0, 10))
        self.paid_entry = ctk.CTkEntry(payment_row, placeholder_text="Enter amount paid", width=200, height=35, font=("Arial", 11))
        self.paid_entry.pack(side="left")
        
        self.payment_frame.pack_forget()
        
        # Buttons
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(side="right", padx=(20, 0))
        
        ctk.CTkButton(btn_frame, text="SELECT CUSTOMER", command=self.select_customer, 
                     fg_color="#10b981", hover_color="#059669", height=35, width=150,
                     font=("Arial", 11, "bold")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="CASH SALE", command=self.clear_customer, 
                     fg_color="#64748b", hover_color="#475569", height=35, width=120,
                     font=("Arial", 11, "bold")).pack(side="left", padx=5)
    
    def setup_add_item_section(self, parent):
        """Setup compact add item section"""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        card.pack(fill="both", expand=True, pady=(0, 10))
        
        ctk.CTkLabel(card, text="➕ ADD ITEM TO CART", 
                     font=("Arial", 13, "bold"), 
                     text_color="#64748b").pack(pady=(15, 15), padx=20, anchor="w")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=(0, 20))
        
        # Product dropdown
        product_names = [p[1] for p in self.products] if self.products else ["No Products"]
        
        ctk.CTkLabel(inner, text="Product:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        self.product_var = ctk.StringVar(value=product_names[0] if product_names else "No Products")
        
        if self.pre_selected_product and self.pre_selected_product in product_names:
            self.product_var.set(self.pre_selected_product)
        
        self.product_dropdown = ctk.CTkOptionMenu(inner, variable=self.product_var, 
                                                 values=product_names, width=360, height=40,
                                                 fg_color="#f8fafc", text_color="#1e293b", font=("Arial", 12),
                                                 dropdown_font=("Arial", 11),
                                                 command=lambda x: self.update_item_price())
        self.product_dropdown.pack(pady=(0, 10), fill="x")
        
        # Price and quantity in one row
        price_qty_frame = ctk.CTkFrame(inner, fg_color="transparent")
        price_qty_frame.pack(fill="x", pady=(0, 10))
        
        # Price display
        price_frame = ctk.CTkFrame(price_qty_frame, fg_color="#f8fafc", corner_radius=8)
        price_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(price_frame, text="Price:", text_color="#64748b", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(8, 0))
        self.price_lbl = ctk.CTkLabel(price_frame, text="GHS 0.00", text_color="#10b981", font=("Arial", 14, "bold"))
        self.price_lbl.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Quantity input
        qty_frame = ctk.CTkFrame(price_qty_frame, fg_color="#f8fafc", corner_radius=8)
        qty_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(qty_frame, text="Quantity (Bags):", text_color="#64748b", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(8, 0))
        self.qty_entry = ctk.CTkEntry(qty_frame, placeholder_text="Enter qty", width=180, height=35, font=("Arial", 12))
        self.qty_entry.pack(padx=10, pady=(0, 8), fill="x")
        
        # Add to cart button
        ctk.CTkButton(inner, text="➕ ADD TO CART", command=self.add_to_cart, 
                     fg_color="#10b981", hover_color="#059669", height=50, width=360,
                     font=("Arial", 13, "bold")).pack(pady=(10, 0), fill="x")
        
        self.update_item_price()
    
    def setup_cart_section(self, parent):
        """Setup large cart display section"""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        card.pack(fill="both", expand=True)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)
        
        # Header with item count
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        self.cart_label = ctk.CTkLabel(header_frame, text="🛒 ITEMS IN CART (0)", 
                     font=("Arial", 14, "bold"), 
                     text_color="#0f172a")
        self.cart_label.pack(side="left")
        
        # Scrollable cart items container - Constrained to allow bottom section visibility
        self.items_container = ctk.CTkScrollableFrame(card, fg_color="transparent", 
                                                       corner_radius=10)
        self.items_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 5))
        
        # Initial empty state
        ctk.CTkLabel(self.items_container, text="No items yet.\nAdd products from the left panel.", 
                     text_color="#64748b", font=("Arial", 12),
                     justify="center").pack(expand=True, pady=50)
    
    def setup_bottom_section(self, parent):
        """Setup bottom section with totals, remarks (tabbed), and checkout"""
        bottom_card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        bottom_card.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        bottom_card.grid_columnconfigure(0, weight=1)
        
        # Tabs for Remarks and Summary
        tab_frame = ctk.CTkFrame(bottom_card, fg_color="transparent")
        tab_frame.pack(fill="x", padx=20, pady=(10, 5))
        
        self.tabs = {}
        self.current_tab = None
        
        # Create tab buttons
        self.create_tab_button(tab_frame, "📋 Summary", "summary")
        self.create_tab_button(tab_frame, "📝 Remarks", "remarks")
        
        # Content area for tabs - fixed height to prevent expansion
        self.tab_content = ctk.CTkFrame(bottom_card, fg_color="transparent")
        self.tab_content.pack(fill="x", padx=20, pady=(0, 10))
        
        # Show summary tab by default
        self.show_tab("summary")
    
    def create_tab_button(self, parent, text, tab_key):
        """Create a tab button"""
        btn = ctk.CTkButton(parent, text=text, 
                           command=lambda: self.show_tab(tab_key),
                           fg_color="#475569", hover_color="#334155",
                           height=35, width=150,
                           font=("Arial", 11, "bold"))
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
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        
        self.current_tab = tab_key
        
        if tab_key == "summary":
            self.show_summary_tab()
        elif tab_key == "remarks":
            self.show_remarks_tab()
    
    def show_summary_tab(self):
        """Show transaction summary tab"""
        # Summary text
        self.summary_lbl = ctk.CTkLabel(self.tab_content, text="No items in cart", 
                                        text_color="#64748b", font=("Arial", 12), justify="left")
        self.summary_lbl.pack(anchor="w", pady=(0, 8))
        
        # Total - left-aligned, minimal
        total_frame = ctk.CTkFrame(self.tab_content, fg_color="#f8fafc", corner_radius=10)
        total_frame.pack(fill="x", pady=(0, 5), anchor="w")
        
        total_inner = ctk.CTkFrame(total_frame, fg_color="transparent")
        total_inner.pack(pady=5, padx=12, anchor="w")
        
        ctk.CTkLabel(total_inner, text="TOTAL:", text_color="#0f172a", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 10))
        self.total_amt_lbl = ctk.CTkLabel(total_inner, text="GHS 0.00", text_color="#10b981", font=("Arial", 20, "bold"))
        self.total_amt_lbl.pack(side="left")
        
        # Checkout buttons - compact, left-aligned
        btn_frame = ctk.CTkFrame(self.tab_content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 0))
        
        ctk.CTkButton(btn_frame, text="✓ COMPLETE SALE", command=self.process_sale, 
                     fg_color="#10b981", hover_color="#059669", height=38, width=280,
                     font=("Arial", 12, "bold")).pack(side="left", padx=3)
        
        ctk.CTkButton(btn_frame, text="✕ CANCEL", command=self.destroy, 
                     fg_color="#ef4444", hover_color="#dc2626", height=38, width=100,
                     font=("Arial", 11, "bold")).pack(side="left", padx=3)
    
    def show_remarks_tab(self):
        """Show remarks tab"""
        ctk.CTkLabel(self.tab_content, text="Additional Notes (Optional)", 
                    text_color="#64748b", font=("Arial", 11)).pack(anchor="w", pady=(0, 10))
        
        self.remarks_text = ctk.CTkTextbox(self.tab_content, width=800, height=80, 
                                          fg_color="#f8fafc", text_color="#1e293b",
                                          border_color="#e2e8f0", border_width=1, font=("Arial", 11))
        self.remarks_text.pack(fill="x", pady=(0, 10))
        
        # Back to summary button
        ctk.CTkButton(self.tab_content, text="← Back to Summary", 
                     command=lambda: self.show_tab("summary"),
                     fg_color="#64748b", hover_color="#475569", height=35, width=200,
                     font=("Arial", 11)).pack(anchor="w")
    
    def update_item_price(self):
        """Update price when product is selected"""
        try:
            product_name = self.product_var.get()
            for p in self.products:
                if p[1] == product_name:
                    self.price_lbl.configure(text=f"GHS {p[5]:.2f}")
                    break
        except:
            pass
    
    def add_to_cart(self):
        """Add selected item to cart"""
        try:
            product_name = self.product_var.get()
            if product_name == "No Products":
                messagebox.showerror("Error", "No products available", parent=self)
                return
            
            qty_text = self.qty_entry.get().strip()
            if not qty_text:
                messagebox.showerror("Error", "Please enter quantity", parent=self)
                return
            
            qty = float(qty_text)
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0", parent=self)
                return
            
            # Find product details
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
            
            # Add to cart
            item_total = qty * price_per_bag
            self.cart_items.append({
                'product_id': product_id,
                'product_name': product_name,
                'qty': qty,
                'price_per_bag': price_per_bag,
                'total': item_total
            })
            
            # Clear inputs
            self.qty_entry.delete(0, "end")
            
            # Refresh display
            self.update_cart_display()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid number", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
    
    def update_cart_display(self):
        """Update the cart items display"""
        # Clear old items
        for widget in self.items_container.winfo_children():
            widget.destroy()
        
        # Update label
        self.cart_label.configure(text=f"🛒 ITEMS IN CART ({len(self.cart_items)})")
        
        if not self.cart_items:
            ctk.CTkLabel(self.items_container, text="No items yet.\nAdd products from the left panel.", 
                         text_color="#64748b", font=("Arial", 12),
                         justify="center").pack(expand=True, pady=50)
            if hasattr(self, 'summary_lbl'):
                self.summary_lbl.configure(text="No items in cart")
            if hasattr(self, 'total_amt_lbl'):
                self.total_amt_lbl.configure(text="GHS 0.00")
            return
        
        # Display each item in a clean card format
        total = 0
        for idx, item in enumerate(self.cart_items):
            item_card = ctk.CTkFrame(self.items_container, fg_color="#f8fafc", corner_radius=12)
            item_card.pack(fill="x", pady=8, padx=5)
            
            # Item content
            content_frame = ctk.CTkFrame(item_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=12)
            
            # Top row: Product name and remove button
            top_row = ctk.CTkFrame(content_frame, fg_color="transparent")
            top_row.pack(fill="x", pady=(0, 8))
            
            ctk.CTkLabel(top_row, text=f"{item['product_name']}", 
                        font=("Arial", 14, "bold"), text_color="#0f172a").pack(side="left")
            
            ctk.CTkButton(top_row, text="✕ Remove", command=lambda i=idx: self.remove_from_cart(i),
                         fg_color="#ef4444", hover_color="#dc2626", height=28, width=90,
                         font=("Arial", 10)).pack(side="right")
            
            # Bottom row: Quantity, price, and total
            bottom_row = ctk.CTkFrame(content_frame, fg_color="transparent")
            bottom_row.pack(fill="x")
            
            ctk.CTkLabel(bottom_row, text=f"Quantity: {item['qty']:.1f} bags", 
                        font=("Arial", 11), text_color="#64748b").pack(side="left", padx=(0, 15))
            
            ctk.CTkLabel(bottom_row, text=f"@ GHS {item['price_per_bag']:.2f}", 
                        font=("Arial", 11), text_color="#64748b").pack(side="left", padx=(0, 15))
            
            ctk.CTkLabel(bottom_row, text=f"Total: GHS {item['total']:.2f}", 
                        font=("Arial", 13, "bold"), text_color="#10b981").pack(side="right")
            
            total += item['total']
        
        # Update summary if it exists
        if hasattr(self, 'summary_lbl'):
            summary_text = f"{len(self.cart_items)} item(s) in cart"
            self.summary_lbl.configure(text=summary_text)
        
        if hasattr(self, 'total_amt_lbl'):
            self.total_amt_lbl.configure(text=f"GHS {total:.2f}")
    
    def remove_from_cart(self, idx):
        """Remove item from cart"""
        if 0 <= idx < len(self.cart_items):
            removed = self.cart_items.pop(idx)
            self.update_cart_display()
    
    def select_customer(self):
        """Open customer selection dialog"""
        CustomerSelectWindow(self, self.set_customer)
    
    def set_customer(self, customer_id, customer_name):
        """Set the selected customer"""
        self.customer_id = customer_id
        self.selected_customer_name = customer_name
        self.customer_lbl.configure(text=f"👤 Customer: {customer_name}", text_color="#0f172a")
        self.payment_frame.pack(fill="x", pady=(5, 0))
    
    def clear_customer(self):
        """Clear customer selection for cash sale"""
        self.customer_id = None
        self.selected_customer_name = None
        self.customer_lbl.configure(text="👤 No customer selected (Cash Sale)", text_color="#64748b")
        self.paid_entry.delete(0, "end")
        self.payment_frame.pack_forget()
    
    def process_sale(self):
        """Process the multi-item sale"""
        try:
            if not self.cart_items:
                messagebox.showerror("Error", "Cart is empty. Add items first.", parent=self)
                return
            
            # Calculate total
            total_amount = sum(item['total'] for item in self.cart_items)
            
            # Get amount paid
            amount_paid = 0.0
            if self.customer_id:
                paid_text = self.paid_entry.get().strip()
                if paid_text:
                    amount_paid = float(paid_text)
                else:
                    # No payment entered for credit sale
                    amount_paid = 0.0
            
            # Validate payment
            if self.customer_id and amount_paid > total_amount:
                messagebox.showerror("Error", f"Payment (GHS {amount_paid:.2f}) exceeds total (GHS {total_amount:.2f})", parent=self)
                return
            
            # Get remarks
            remarks = ""
            if hasattr(self, 'remarks_text'):
                remarks = self.remarks_text.get("0.0", "end").strip()
            
            # Process each item in the sale (don't divide payment - handle debt separately)
            receipt_items = []
            for item in self.cart_items:
                # Record each sale item with NO payment (we'll handle debt once at the end)
                if sell_product(item['product_id'], item['qty'], "Bags", None, 0.0):
                    receipt_items.append(item)
                else:
                    messagebox.showerror("Error", f"Failed to sell {item['product_name']}", parent=self)
                    return
            
            # Now handle customer debt ONCE for the entire transaction
            if self.customer_id:
                from db.database import get_db_connection
                debt_to_add = total_amount - amount_paid
                if debt_to_add > 0:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE customers SET balance = balance + ? WHERE id = ?", (debt_to_add, self.customer_id))
                    conn.commit()
                    conn.close()
            
            # Show success with payment details
            items_summary = "\n".join([f"• {item['product_name']}: {item['qty']:.1f} bags - GHS {item['total']:.2f}" 
                                      for item in receipt_items])
            
            success_msg = f"Sale completed!\n\n{items_summary}\n\nTotal: GHS {total_amount:.2f}"
            
            if self.customer_id:
                debt_added = total_amount - amount_paid
                success_msg += f"\nPaid: GHS {amount_paid:.2f}"
                if debt_added > 0:
                    success_msg += f"\nDebt Added: GHS {debt_added:.2f}"
            
            success_msg += "\n\nPrint Receipt?"
            
            result = messagebox.askyesno("Success", success_msg, parent=self)
            
            # Generate receipt if requested
            if result:
                try:
                    # For receipt, use first item as primary (can be enhanced)
                    first_item = receipt_items[0]
                    receipt_path = generate_receipt(
                        product_name=f"{len(receipt_items)} items",
                        quantity=sum(item['qty'] for item in receipt_items),
                        unit_price=total_amount / sum(item['qty'] for item in receipt_items),
                        total_price=total_amount,
                        customer_name=self.selected_customer_name if self.customer_id else None,
                        payment_method="Credit" if self.customer_id else "Cash",
                        remarks=remarks,
                        parent=self
                    )
                    if receipt_path:
                        messagebox.showinfo("Success", f"Receipt saved:\n{receipt_path}", parent=self)
                except Exception as e:
                    messagebox.showerror("Receipt Error", f"Could not generate receipt: {e}", parent=self)
            
            self.refresh_callback()
            self.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please check all inputs", parent=self)
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
        
        # Linux/Fedora display fixes
        self.lift()
        self.attributes("-topmost", True)
        self.after(50, lambda: self.attributes("-topmost", False))
        self.update_idletasks()
        
        # Header
        ctk.CTkLabel(self, text="Customer Selection", 
                     font=("Arial", 24, "bold"), 
                     text_color="#0f172a").pack(pady=(30, 20))
        
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Existing customers
        card1 = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        card1.pack(fill="x", pady=15)
        
        ctk.CTkLabel(card1, text="EXISTING CUSTOMERS", 
                     font=("Arial", 12, "bold"), 
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
                     font=("Arial", 12, "bold"), 
                     text_color="#64748b").pack(pady=(15, 10), padx=20, anchor="w")
        
        inner2 = ctk.CTkFrame(card2, fg_color="transparent")
        inner2.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(inner2, text="Customer Name:", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(inner2, placeholder_text="Full name", width=450, height=40, font=("Arial", 11))
        self.name_entry.pack(pady=5)
        
        ctk.CTkLabel(inner2, text="Phone (Optional):", text_color="#0f172a", font=("Arial", 11)).pack(anchor="w", pady=(10, 5))
        self.phone_entry = ctk.CTkEntry(inner2, placeholder_text="Phone number", width=450, height=40, font=("Arial", 11))
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
