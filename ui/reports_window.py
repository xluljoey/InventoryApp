import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from core.sales import get_sales_history
from core.products import get_restock_report, get_all_products
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from db.database import get_db_connection
from datetime import datetime, timedelta

class ReportsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Business Audit")
        self.geometry("1200x850")
        self.configure(fg_color="#f1f5f9")
        self.withdraw()
        
        # Get all product names for autocomplete
        self.all_products = [p[1] for p in get_all_products()]
        self.suggestion_window = None
        
        # Filter Header
        filter_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15, height=120)
        filter_card.pack(fill="x", padx=40, pady=20)
        filter_card.pack_propagate(False)

        filter_frame = ctk.CTkFrame(filter_card, fg_color="transparent")
        filter_frame.pack(fill="both", expand=True, padx=30, pady=15)
        
        # Row 1: Search and Date Range
        row1 = ctk.CTkFrame(filter_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(row1, text="Product:", font=("Arial", 11, "bold")).pack(side="left", padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(row1, placeholder_text="Search products...", 
                                         width=250, height=40, border_color="#e2e8f0")
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        ctk.CTkLabel(row1, text="From:", font=("Arial", 11, "bold")).pack(side="left", padx=(20, 5))
        self.from_date = ctk.CTkEntry(row1, placeholder_text="YYYY-MM-DD", width=120, height=40, border_color="#e2e8f0")
        self.from_date.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(row1, text="To:", font=("Arial", 11, "bold")).pack(side="left", padx=(0, 5))
        self.to_date = ctk.CTkEntry(row1, placeholder_text="YYYY-MM-DD", width=120, height=40, border_color="#e2e8f0")
        self.to_date.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(row1, text="🔍 Filter", fg_color="#10b981", hover_color="#059669", 
                     width=100, height=40, command=self.load_data).pack(side="left", padx=5)
        
        # Row 2: Total Revenue Display
        row2 = ctk.CTkFrame(filter_card, fg_color="transparent")
        row2.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(row2, text="Total Revenue:", font=("Arial", 12, "bold"), text_color="#10b981").pack(side="left", padx=(0, 10))
        self.total_label = ctk.CTkLabel(row2, text="GHS 0.00", font=("Arial", 14, "bold"), text_color="#10b981")
        self.total_label.pack(side="left")
        
        ctk.CTkButton(row2, text="📥 Export PDF", fg_color="#64748b", hover_color="#475569", 
                     width=120, height=40, command=self.export_to_pdf).pack(side="right", padx=5)
        
        ctk.CTkButton(row2, text="🖨️ Print", fg_color="#64748b", hover_color="#475569", 
                     width=100, height=40, command=self.print_records).pack(side="right", padx=5)

        # Tabs
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color="#10b981")
        self.tabview.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        self.tab_sales = self.tabview.add("Sale Records")
        self.tab_stock = self.tabview.add("Stock Audit Trail")

        self.sales_tree = self.create_tree(self.tab_sales, ("ID", "Product", "Buyer", "Qty", "Total", "Date"))
        self.stock_tree = self.create_tree(self.tab_stock, ("ID", "Product", "Before", "Added", "After", "Date"))

        self.deiconify()
        self.load_data()
        self.after(100, self.grab_set)

    def create_tree(self, parent, cols):
        container = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(container, columns=cols, show="headings")
        style = ttk.Style()
        style.configure("Treeview", rowheight=45, font=("Arial", 11), background="white")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#F1F5F9")
        
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=150)
        
        tree.pack(fill="both", expand=True, padx=15, pady=15)
        return tree

    def load_data(self):
        """Load filtered sales and stock data"""
        search_query = self.search_entry.get().strip().lower()
        from_date = self.from_date.get().strip()
        to_date = self.to_date.get().strip()
        
        # Clear tables
        for i in self.sales_tree.get_children(): 
            self.sales_tree.delete(i)
        for i in self.stock_tree.get_children(): 
            self.stock_tree.delete(i)
        
        # Load and filter sales
        total_revenue = 0
        for s in get_sales_history():
            # s = (id, product, buyer, qty, total, date)
            product_match = search_query == "" or search_query in s[1].lower()
            
            # Date filtering
            sale_date = s[5]  # date field
            date_match = True
            if from_date and to_date:
                try:
                    date_obj = datetime.strptime(sale_date, "%Y-%m-%d").date()
                    from_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                    to_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
                    date_match = from_obj <= date_obj <= to_obj
                except:
                    date_match = True
            
            if product_match and date_match:
                self.sales_tree.insert("", "end", values=s)
                total_revenue += float(s[4])
        
        # Update total revenue display
        self.total_label.configure(text=f"GHS {total_revenue:.2f}")
        
        # Load and filter stock
        for r in get_restock_report():
            self.stock_tree.insert("", "end", values=(r[0], r[1], f"{r[2]:.1f}", f"+{r[3]:.1f}", f"{r[4]:.1f}", r[5]))

    def on_search_change(self, event=None):
        """Show autocomplete suggestions as user types"""
        query = self.search_entry.get().lower()
        
        # Close previous suggestion window
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        
        if not query or len(query) < 1:
            return
        
        # Find matching products
        matches = [p for p in self.all_products if query in p.lower()]
        if not matches:
            return
        
        # Create suggestion window
        self.suggestion_window = ctk.CTkToplevel(self)
        self.suggestion_window.wm_overrideredirect(True)
        
        # Position below search entry
        entry_bbox = self.search_entry.bbox("0.0")
        if entry_bbox:
            x = self.search_entry.winfo_rootx()
            y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height() + 5
            self.suggestion_window.geometry(f"{self.search_entry.winfo_width()}x{min(len(matches) * 30 + 10, 150)}+{x}+{y}")
        
        self.suggestion_window.configure(fg_color="white")
        
        # Add suggestions
        suggestion_frame = ctk.CTkScrollableFrame(self.suggestion_window, fg_color="white", label_text="")
        suggestion_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        for product in matches[:5]:  # Show max 5 suggestions
            btn = ctk.CTkButton(
                suggestion_frame,
                text=product,
                fg_color="transparent",
                text_color="#0f172a",
                hover_color="#e2e8f0",
                anchor="w",
                height=30,
                command=lambda p=product: self.select_suggestion(p)
            )
            btn.pack(fill="x", padx=5, pady=3)
    
    def select_suggestion(self, product):
        """Handle suggestion selection"""
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, product)
        if self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        self.load_data()

    def export_to_pdf(self):
        """Export audit trail to PDF"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"Business_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        if not file_path:
            return
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=20, bottomMargin=20)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor("#10b981"),
                spaceAfter=10,
                alignment=1
            )
            story = []
            
            # Title
            story.append(Paragraph(f"Business Audit Report - {datetime.now().strftime('%B %d, %Y')}", title_style))
            story.append(Spacer(1, 12))
            
            # Sales Records Table
            story.append(Paragraph("Sale Records", styles['Heading2']))
            sales_data = [["ID", "Product", "Buyer", "Qty", "Total (GHS)", "Date"]]
            for item in self.sales_tree.get_children():
                sales_data.append(list(self.sales_tree.item(item)['values']))
            
            if len(sales_data) > 1:
                sales_table = Table(sales_data, colWidths=[50, 100, 100, 60, 80, 120])
                sales_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")])
                ]))
                story.append(sales_table)
            else:
                story.append(Paragraph("No sale records found.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Stock Audit Trail Table
            story.append(Paragraph("Stock Audit Trail", styles['Heading2']))
            stock_data = [["ID", "Product", "Before (kg)", "Added (kg)", "After (kg)", "Date"]]
            for item in self.stock_tree.get_children():
                stock_data.append(list(self.stock_tree.item(item)['values']))
            
            if len(stock_data) > 1:
                stock_table = Table(stock_data, colWidths=[50, 100, 90, 90, 90, 120])
                stock_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")])
                ]))
                story.append(stock_table)
            else:
                story.append(Paragraph("No stock records found.", styles['Normal']))
            
            doc.build(story)
            messagebox.showinfo("Success", f"PDF exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF:\n{str(e)}")

    def print_records(self):
        """Print current records (placeholder for system print dialog)"""
        messagebox.showinfo("Print", "Print functionality requires system integration.\nUse 'Export PDF' to save a copy for printing.")