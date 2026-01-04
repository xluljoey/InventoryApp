import customtkinter as ctk
from tkinter import messagebox
from core.products import get_all_products
from core.sales import get_today_revenue
from db.database import create_tables, get_db_connection, verify_admin_password
from ui.sell_window import SellWindow
from ui.password_window import PasswordSettingsWindow, PasswordResetWindow
from ui.panels import DailySalesPanel, AnalyticsPanel, CustomersPanel, ReportsPanel, ManageStockPanel, AlertsPanel
from datetime import datetime

class ThemedDialog(ctk.CTkToplevel):
    """Custom themed dialog to match UI"""
    def __init__(self, parent, title, message, dialog_type="info"):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x200")
        self.configure(fg_color="#f1f5f9")
        self.resizable(False, False)
        self.result = False
        
        # Center on parent
        self.transient(parent)
        
        # Message frame
        msg_frame = ctk.CTkFrame(self, fg_color="transparent")
        msg_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon and message
        icon_map = {"error": "❌", "success": "✅", "info": "ℹ️", "confirm": "❓"}
        icon = icon_map.get(dialog_type, "ℹ️")
        
        text_color_map = {"error": "#ef4444", "success": "#10b981", "confirm": "#f59e0b", "info": "#3b82f6"}
        text_color = text_color_map.get(dialog_type, "#0f172a")
        
        ctk.CTkLabel(msg_frame, text=f"{icon} {title}", font=("Arial", 14, "bold"), text_color=text_color).pack(pady=(0, 10))
        ctk.CTkLabel(msg_frame, text=message, font=("Arial", 12), text_color="#475569", wraplength=380, justify="left").pack(pady=10)
        
        # Button frame
        btn_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
        btn_frame.pack(pady=(20, 0), fill="x", expand=True)
        
        if dialog_type == "confirm":
            ctk.CTkButton(btn_frame, text="Yes", command=self.yes_click, fg_color="#10b981", 
                         hover_color="#059669", width=80, font=("Arial", 11, "bold")).pack(side="left", padx=5, expand=True)
            ctk.CTkButton(btn_frame, text="No", command=self.destroy, fg_color="#ef4444", 
                         hover_color="#dc2626", width=80, font=("Arial", 11, "bold")).pack(side="left", padx=5, expand=True)
        else:
            ctk.CTkButton(btn_frame, text="OK", command=self.destroy, fg_color="#3b82f6", 
                         hover_color="#2563eb", width=100, font=("Arial", 11, "bold")).pack(expand=True)
        
        # Make window modal after rendering
        self.update_idletasks()
        self.grab_set()
    
    def yes_click(self):
        self.result = True
        self.destroy()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sales & Inventory Management System")
        self.geometry("1400x800")
        self.configure(fg_color="#f1f5f9")

        # Header/Navigation Bar
        self.header = ctk.CTkFrame(self, fg_color="#1e293b", height=70, corner_radius=0)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)
        
        # Header content container
        header_content = ctk.CTkFrame(self.header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Logo/Title - Modern design with dual-color branding
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(title_frame, text="Inventory", font=("Arial", 22, "bold"), text_color="#10b981").pack()
        ctk.CTkLabel(title_frame, text="Management System", font=("Arial", 18, "bold"), text_color="white").pack()
        
        # Tab buttons in header
        self.tab_buttons = {}
        nav_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        nav_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        tabs = [
            ("🏠 Dashboard", "dashboard"),
            ("📅 Daily Sales", "daily_sales"),
            ("👥 Customers", "customers"),
            ("📊 Reports & Analytics", "reports"),
            ("⚙️ Manage Stock", "stock"),
        ]
        
        for tab_text, tab_key in tabs:
            btn = ctk.CTkButton(nav_frame, text=tab_text, command=lambda k=tab_key: self.switch_tab(k),
                               fg_color="transparent", hover_color="#334155",
                               height=40, font=("Arial", 11, "bold"))
            btn.pack(side="left", padx=5)
            self.tab_buttons[tab_key] = btn
        
        # Right side - New Sale, Options, and Alerts buttons
        right_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        right_frame.pack(side="right", padx=(20, 30))
        
        # New Sale button (opens popup - critical operation)
        ctk.CTkButton(right_frame, text="💰 New Sale", command=self.open_sell,
                     fg_color="#10b981", hover_color="#059669", 
                     height=40, width=140,
                     font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
        
        # Options button with gear icon
        ctk.CTkButton(right_frame, text="⚙️ Options", command=self.open_options_menu,
                     fg_color="#475569", hover_color="#334155", 
                     height=40, width=120,
                     font=("Arial", 11, "bold")).pack(side="left", padx=(0, 10))
        
        # Alerts button (appears after Options)
        alerts_btn = ctk.CTkButton(right_frame, text="⚠️", command=lambda: self.switch_tab("alerts"),
                     fg_color="transparent", hover_color="#334155", 
                     height=40, width=50,
                     font=("Arial", 16, "bold"))
        alerts_btn.pack(side="left", padx=(0, 0))
        self.tab_buttons["alerts"] = alerts_btn

        # Main content area (single frame that switches content)
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        
        # Current active panel
        self.current_panel = None
        self.panels = {}
        
        # Initialize panels
        self.tab_dashboard = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.setup_dashboard_tab()
        
        self.tab_daily_sales = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.daily_sales_panel = DailySalesPanel(self.tab_daily_sales, self.load_data)
        self.daily_sales_panel.pack(fill="both", expand=True)
        
        # Analytics panel moved to Reports tab - kept for backwards compatibility
        self.tab_analytics = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.analytics_panel = AnalyticsPanel(self.tab_analytics, self.load_data)
        # Don't pack it - it's merged with reports now
        
        self.tab_customers = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.customers_panel = CustomersPanel(self.tab_customers, self.load_data)
        self.customers_panel.pack(fill="both", expand=True)
        
        self.tab_reports = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.reports_panel = ReportsPanel(self.tab_reports, self.load_data)
        self.reports_panel.pack(fill="both", expand=True)
        
        # Alerts tab
        self.tab_alerts = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.alerts_panel = AlertsPanel(self.tab_alerts, self.load_data)
        self.alerts_panel.pack(fill="both", expand=True)
        
        # Manage Stock tab - create placeholder initially
        self.tab_stock = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.stock_panel = None
        self.setup_stock_placeholder()
        
        # Store panels (note: analytics is merged with reports)
        self.panels = {
            "dashboard": self.tab_dashboard,
            "alerts": self.tab_alerts,
            "daily_sales": self.tab_daily_sales,
            "customers": self.tab_customers,
            "reports": self.tab_reports,
            "stock": self.tab_stock,
        }
        
        # Load initial data
        self.load_data()
        
        # Set default tab (after load_data to ensure scroll exists)
        self.switch_tab("dashboard")
    
    def setup_dashboard_tab(self):
        """Setup the dashboard tab"""
        # Revenue Card with search functionality
        rev_card_container = ctk.CTkFrame(self.tab_dashboard, fg_color="transparent")
        rev_card_container.pack(fill="x", pady=(0, 30), padx=20)
        
        # Revenue card on the left
        self.rev_card = ctk.CTkFrame(rev_card_container, fg_color="white", corner_radius=20, height=120)
        self.rev_card.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.rev_card.pack_propagate(False)
        ctk.CTkLabel(self.rev_card, text="TODAY'S REVENUE", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(20,0))
        self.rev_lbl = ctk.CTkLabel(self.rev_card, text="GHS 0.00", font=("Arial", 38, "bold"), text_color="#10b981")
        self.rev_lbl.pack()
        
        # Search button on the right
        search_frame = ctk.CTkFrame(rev_card_container, fg_color="white", corner_radius=20, height=120, width=120)
        search_frame.pack(side="right", fill="y")
        search_frame.pack_propagate(False)
        ctk.CTkButton(search_frame, text="🔍 Search", command=self.open_search_dialog,
                     fg_color="#3b82f6", hover_color="#2563eb",
                     font=("Arial", 12, "bold"), width=100, height=50).pack(expand=True)

        self.scroll = ctk.CTkScrollableFrame(self.tab_dashboard, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def open_search_dialog(self):
        """Open search dialog for searching through stocks"""
        # Create search dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Search Stocks")
        dialog.geometry("500x400")
        dialog.configure(fg_color="#f1f5f9")
        dialog.transient(self)
        
        # Center the dialog
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        
        # Header
        ctk.CTkLabel(dialog, text="🔍 Search Stocks", 
                     font=("Arial", 18, "bold"), text_color="#0f172a").pack(pady=(20, 10))
        
        # Search input
        search_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter product name to search...", 
                                   height=40, font=("Arial", 12))
        search_entry.pack(fill="x", padx=(0, 10))
        
        # Results area
        results_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Store the after ID to cancel previous scheduled searches
        search_timer_id = None
        
        # Function to perform search
        def perform_search():
            query = search_entry.get().strip().lower()
            
            # Clear previous results
            for widget in results_frame.winfo_children():
                widget.destroy()
            
            # Get all products and filter
            all_products = get_all_products()
            if query:
                matching_products = [p for p in all_products if query in p[1].lower()]
            else:
                # If no query, show all products
                matching_products = all_products
            
            if not matching_products:
                ctk.CTkLabel(results_frame, text="No matching products found", 
                            font=("Arial", 14), text_color="#64748b").pack(pady=20)
                return
            
            # Display matching products
            for product in matching_products:
                # Calculate bags
                if len(product) >= 10:
                    bags = product[6] / product[4] if product[4] > 0 else 0
                else:
                    bags = product[6] / product[4] if product[4] > 0 else 0
                
                # Create product card
                card = ctk.CTkFrame(results_frame, fg_color="white", corner_radius=15, height=80)
                card.pack(fill="x", pady=8, padx=5)
                card.pack_propagate(False)
                
                # Left side - Product name
                left_frame = ctk.CTkFrame(card, fg_color="transparent")
                left_frame.pack(side="left", padx=20, fill="y")
                
                # Make card clickable
                product_name = product[1]
                card.bind("<Button-1>", lambda e, name=product_name: SellWindow(self, self.load_data, name))
                
                product_name_label = ctk.CTkLabel(left_frame, text=product[1], font=("Arial", 16, "bold"), 
                                                text_color="#0f172a")
                product_name_label.pack(anchor="w", pady=(10, 0))
                product_name_label.bind("<Button-1>", lambda e, name=product_name: SellWindow(self, self.load_data, name))
                
                # Right side - Stock and price
                stock_label = ctk.CTkLabel(card, text=f"{bags:.1f} Bags", font=("Arial", 16, "bold"), 
                             text_color="#0f172a")
                stock_label.pack(side="right", padx=30, pady=(15, 0))
                stock_label.bind("<Button-1>", lambda e, name=product_name: SellWindow(self, self.load_data, name))
                
                price_label = ctk.CTkLabel(card, text=f"GHS {product[5]:.2f}", font=("Arial", 14), text_color="#64748b")
                price_label.pack(side="right", padx=20, pady=(0, 15))
                price_label.bind("<Button-1>", lambda e, name=product_name: SellWindow(self, self.load_data, name))
        
        # Function to handle key release with debouncing
        def on_key_release(event):
            nonlocal search_timer_id
            # Cancel any previously scheduled search
            if search_timer_id:
                dialog.after_cancel(search_timer_id)
            # Schedule search to happen after 300ms
            search_timer_id = dialog.after(300, perform_search)
        
        # Bind key release to perform search with debouncing
        search_entry.bind("<KeyRelease>", on_key_release)
        
        # Initialize with all products
        perform_search()

    def create_btn(self, txt, cmd, parent, action=False):
        btn = ctk.CTkButton(parent, text=txt, command=cmd, height=40,
                            fg_color="#10b981" if action else "transparent",
                            hover_color="#059669" if action else "#334155",
                            font=("Arial", 12, "bold"))
        btn.pack(side="left", padx=8)

    def load_data(self):
        # Batch destroy for better performance
        children = list(self.scroll.winfo_children())
        for w in children:
            w.destroy()
        
        products = get_all_products()
        
        # Batch create widgets for better performance
        for p in products:
            # Handle both old format (7 fields) and new format (10 fields)
            if len(p) >= 10:
                bags = p[6] / p[4] if p[4] > 0 else 0
                low_threshold = p[7] if p[7] is not None else 5.0
                expiry_date = p[9]
            else:
                bags = p[6] / p[4] if p[4] > 0 else 0
                low_threshold = 5.0
                expiry_date = None
            
            card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=15, height=90)
            card.pack(fill="x", pady=8, padx=5)
            card.pack_propagate(False)
            
            # Store product name for lambda closure
            product_name = p[1]
            
            # Check for low stock
            is_low_stock = bags <= low_threshold
            
            # Check for expiring soon (within 30 days)
            is_expiring = False
            expiry_warning = ""
            if expiry_date:
                try:
                    from datetime import datetime
                    exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
                    days_until = (exp_date - datetime.now().date()).days
                    if 0 <= days_until <= 30:
                        is_expiring = True
                        expiry_warning = f" (Expires in {days_until}d)"
                except:
                    pass
            
            # Make card clickable - bind click events to all children and parent
            card.bind("<Button-1>", lambda e, name=product_name: SellWindow(self, self.load_data, name))
            
            # Left side - Product name with alerts
            left_frame = ctk.CTkFrame(card, fg_color="transparent")
            left_frame.pack(side="left", padx=25, fill="y")
            
            product_name_label = ctk.CTkLabel(left_frame, text=product_name, font=("Arial", 18, "bold"), 
                                             text_color="#ef4444" if is_low_stock or is_expiring else "#0f172a")
            product_name_label.pack(anchor="w")
            product_name_label.bind("<Button-1>", lambda e, name=product_name: SellWindow(self, self.load_data, name))
            
            # Show expiry warning if applicable
            if expiry_warning:
                expiry_label = ctk.CTkLabel(left_frame, text=f"⚠️{expiry_warning}", 
                                          font=("Arial", 10), text_color="#f59e0b")
                expiry_label.pack(anchor="w", pady=(2, 0))
            
            # Right side - Stock and price
            stock_label = ctk.CTkLabel(card, text=f"{bags:.1f} Bags", font=("Arial", 18, "bold"), 
                         text_color="#ef4444" if is_low_stock else "#0f172a")
            stock_label.pack(side="right", padx=30)
            stock_label.bind("<Button-1>", lambda e, name=product_name: SellWindow(self, self.load_data, name))
            
            price_label = ctk.CTkLabel(card, text=f"GHS {p[5]:.2f}", font=("Arial", 16), text_color="#64748b")
            price_label.pack(side="right", padx=20)
            price_label.bind("<Button-1>", lambda e, name=product_name: SellWindow(self, self.load_data, name))

        self.rev_lbl.configure(text=f"GHS {get_today_revenue():.2f}")
        
        # Update display once at the end for better performance
        self.update_idletasks()
    
    def open_options_menu(self):
        """Open options menu with settings and utilities"""
        # Create options dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Options")
        dialog.geometry("450x400")
        dialog.configure(fg_color="#f1f5f9")
        dialog.resizable(False, False)
        dialog.transient(self)
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="#1e293b", height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="⚙️ Options", 
                    font=("Arial", 18, "bold"), 
                    text_color="white").pack(pady=15)
        
        # Content
        content = ctk.CTkFrame(dialog, fg_color="white", corner_radius=15)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content, text="Settings & Utilities", 
                    font=("Arial", 14, "bold"), 
                    text_color="#0f172a").pack(pady=(20, 30))
        
        # Change Password button
        ctk.CTkButton(content, text="🔐 Change Password", 
                     command=lambda: [dialog.destroy(), self.open_password_settings()],
                     fg_color="#10b981", hover_color="#059669",
                     width=350, height=50, 
                     font=("Arial", 13, "bold")).pack(pady=10)
        
        ctk.CTkLabel(content, text="Update your admin password", 
                    font=("Arial", 10), 
                    text_color="#64748b").pack(pady=(0, 20))
        
        # Reset Daily Sales button
        ctk.CTkButton(content, text="🔄 Reset Daily Sales", 
                     command=lambda: [dialog.destroy(), self.reset_daily_revenue()],
                     fg_color="#f59e0b", hover_color="#d97706",
                     width=350, height=50, 
                     font=("Arial", 13, "bold")).pack(pady=10)
        
        ctk.CTkLabel(content, text="Reset today's revenue counter", 
                    font=("Arial", 10), 
                    text_color="#64748b").pack(pady=(0, 20))
        
        # Theme switcher
        theme_frame = ctk.CTkFrame(content, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(theme_frame, text="🌓 Theme:", 
                    font=("Arial", 13, "bold"), 
                    text_color="#0f172a").pack(side="left", padx=(0, 15))
        
        # Get current theme
        current_theme = ctk.get_appearance_mode()
        theme_text = "Dark" if current_theme == "Dark" else "Light"
        
        self.theme_switch_btn = ctk.CTkButton(theme_frame, 
                     text=f"Switch to {'Light' if current_theme == 'Dark' else 'Dark'} Mode",
                     command=lambda: self.toggle_theme(dialog),
                     fg_color="#3b82f6", hover_color="#2563eb",
                     width=200, height=40, 
                     font=("Arial", 11, "bold"))
        self.theme_switch_btn.pack(side="left")
        
        # Use after() to ensure dialog is visible before grab
        dialog.update_idletasks()
        dialog.after(50, dialog.grab_set)
    
    def toggle_theme(self, dialog):
        """Toggle between light and dark theme"""
        current_theme = ctk.get_appearance_mode()
        new_theme = "Light" if current_theme == "Dark" else "Dark"
        ctk.set_appearance_mode(new_theme)
        
        # Update button text
        self.theme_switch_btn.configure(text=f"Switch to {'Light' if new_theme == 'Dark' else 'Dark'} Mode")
        
        ThemedDialog(dialog, "Theme Changed", f"Switched to {new_theme} mode", "success")
    
    def open_password_settings(self):
        """Open password settings with options to change or reset"""
        # Create custom dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Password Options")
        dialog.geometry("400x300")
        dialog.configure(fg_color="#f1f5f9")
        dialog.resizable(False, False)
        dialog.transient(self)
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="#1e293b", height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="🔐 Password Options", 
                    font=("Arial", 18, "bold"), 
                    text_color="white").pack(pady=15)
        
        # Content
        content = ctk.CTkFrame(dialog, fg_color="white", corner_radius=15)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content, text="Choose an option:", 
                    font=("Arial", 14, "bold"), 
                    text_color="#0f172a").pack(pady=(20, 30))
        
        # Change Password button (requires current password)
        ctk.CTkButton(content, text="🔑 Change Password", 
                     command=lambda: [dialog.destroy(), self.open_change_password()],
                     fg_color="#10b981", hover_color="#059669",
                     width=300, height=50, 
                     font=("Arial", 13, "bold")).pack(pady=10)
        
        ctk.CTkLabel(content, text="(You need to know your current password)", 
                    font=("Arial", 10), 
                    text_color="#64748b").pack(pady=(0, 20))
        
        # Reset Password button (for when password is forgotten)
        ctk.CTkButton(content, text="🔓 Reset Password (Forgot Password)", 
                     command=lambda: [dialog.destroy(), PasswordResetWindow(self)],
                     fg_color="#f59e0b", hover_color="#d97706",
                     width=300, height=50, 
                     font=("Arial", 13, "bold")).pack(pady=10)
        
        ctk.CTkLabel(content, text="(Use this if you forgot your password)", 
                    font=("Arial", 10), 
                    text_color="#64748b").pack()
        
        dialog.grab_set()
    
    def open_change_password(self):
        """Open change password window (requires admin authentication)"""
        pw = ctk.CTkInputDialog(text="Enter Admin Password:", title="Verify Identity").get_input()
        if pw is None:  # User clicked cancel
            return
        
        if verify_admin_password(pw):
            PasswordSettingsWindow(self)
        else:
            ThemedDialog(self, "Access Denied", "Wrong Password", "error")
    
    def reset_daily_revenue(self):
        """Reset daily revenue display (sales records preserved for auditing)"""
        pw = ctk.CTkInputDialog(text="Admin Password:", title="Reset Daily Revenue").get_input()
        if pw is None:  # User clicked cancel
            return
        
        if not verify_admin_password(pw):
            ThemedDialog(self, "Access Denied", "Wrong Password\nOnly admins can access this feature", "error")
            return
        
        # Confirmation dialog
        confirm = ThemedDialog(self, "Confirm Reset", "Reset daily revenue display to 0?\n(Sales records are kept for audit)", "confirm")
        self.wait_window(confirm)
        if not confirm.result:
            return
        
        try:
            # Just refresh the display - don't delete records (keep for auditing)
            self.rev_lbl.configure(text="GHS 0.00")
            ThemedDialog(self, "Success", "Daily revenue reset to 0!\nAll sales records preserved for auditing.", "success")
        except Exception as e:
            ThemedDialog(self, "Error", f"Error: {e}", "error")

    def open_sell(self): 
        SellWindow(self, self.load_data)

    def setup_stock_placeholder(self):
        """Setup placeholder for stock management tab"""
        placeholder = ctk.CTkFrame(self.tab_stock, fg_color="white", corner_radius=15)
        placeholder.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(placeholder, text="⚙️ Manage Stock", 
                     font=("Arial", 24, "bold"), text_color="#10b981").pack(pady=40)
        
        ctk.CTkLabel(placeholder, text="Click the button below to access stock management", 
                     font=("Arial", 14), text_color="#64748b").pack(pady=10)
        
        ctk.CTkButton(placeholder, text="Unlock Stock Management", 
                     command=self.unlock_stock_tab,
                     fg_color="#10b981", hover_color="#059669",
                     height=50, width=300,
                     font=("Arial", 14, "bold")).pack(pady=30)
    
    def setup_stock_tab(self):
        """Setup stock management tab after password verification"""
        # Clear placeholder
        for widget in self.tab_stock.winfo_children():
            widget.destroy()
        
        # Create actual panel
        self.stock_panel = ManageStockPanel(self.tab_stock, self.load_data)
        self.stock_panel.pack(fill="both", expand=True)
    
    def unlock_stock_tab(self):
        """Unlock stock management with password"""
        pw = ctk.CTkInputDialog(text="Admin Password:", title="Dad's Lock").get_input()
        if pw is None:  # User clicked cancel
            return
        
        if verify_admin_password(pw):
            self.setup_stock_tab()
        else:
            ThemedDialog(self, "Access Denied", "Wrong Password\nOnly admins can access this feature", "error")
    
    def switch_tab(self, tab_key):
        """Switch between tabs"""
        # Hide all panels
        for panel in self.panels.values():
            panel.pack_forget()
        
        # Show selected panel
        if tab_key in self.panels:
            self.panels[tab_key].pack(fill="both", expand=True)
            self.current_panel = tab_key
        
        # Update button colors
        for key, btn in self.tab_buttons.items():
            if key == tab_key:
                btn.configure(fg_color="#10b981", hover_color="#059669")
            else:
                btn.configure(fg_color="transparent", hover_color="#334155")
        
        # Refresh panels when switching tabs
        if tab_key == "daily_sales" and hasattr(self, 'daily_sales_panel'):
            self.daily_sales_panel.refresh()
        elif tab_key == "customers" and hasattr(self, 'customers_panel'):
            self.customers_panel.refresh()
        elif tab_key == "alerts" and hasattr(self, 'alerts_panel'):
            self.alerts_panel.refresh()
        elif tab_key == "stock" and self.stock_panel:
            self.stock_panel.refresh()

if __name__ == "__main__":
    # Cross-platform performance optimizations for faster startup
    import os
    
    # Linux-specific optimization - only apply on Linux systems
    if os.name == 'posix':  # Unix-like systems (Linux, macOS)
        os.environ['QT_X11_NO_MITSHM'] = '1'
    
    # Configure CustomTkinter for better performance
    ctk.set_widget_scaling(1.0)  # Disable scaling to avoid rendering overhead
    ctk.set_window_scaling(1.0)
    
    # Use faster rendering mode (if available)
    try:
        # Disable some visual effects for better performance
        ctk.set_appearance_mode("light")  # Light mode is typically faster
    except:
        pass
    
    # Create tables early but in a separate thread to not block UI initialization
    import threading
    def init_db():
        create_tables()
    
    db_thread = threading.Thread(target=init_db, daemon=True)
    db_thread.start()
    
    # Initialize app immediately to show UI quickly
    app = App()
    
    # Wait briefly for DB initialization if needed
    if db_thread.is_alive():
        db_thread.join(timeout=1.0)  # Don't wait too long to keep startup fast
    
    # Platform-appropriate initialization
    app.update_idletasks()
    
    app.mainloop()