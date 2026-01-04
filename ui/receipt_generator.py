"""Receipt Generator - Creates PDF receipts for sales transactions"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os
from tkinter import filedialog
import tkinter as tk

def generate_receipt(product_name, quantity, unit_price, total_price, customer_name=None, payment_method="Cash", remarks=None, parent=None):
    """
    Generate a PDF receipt for a sale transaction
    
    Args:
        product_name: Name of the product sold
        quantity: Quantity sold (in bags)
        unit_price: Price per unit
        total_price: Total sale amount
        customer_name: Name of customer (optional)
        payment_method: Payment method (Cash/Credit)
        parent: Parent window for dialog (optional)
    
    Returns:
        Path to the generated PDF or None if cancelled
    """
    
    # Ask user where to save the receipt
    # Create a temporary root if parent is not provided
    if parent is None:
        temp_root = tk.Tk()
        temp_root.withdraw()
        master = temp_root
    else:
        master = parent
    
    file_path = filedialog.asksaveasfilename(
        parent=master,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        initialfile=f"Receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    
    # Destroy temp root if we created one
    if parent is None and 'temp_root' in locals():
        temp_root.destroy()
    
    if not file_path:
        return None
    
    try:
        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#10b981'),
            spaceAfter=6,
            alignment=1  # Center
        )
        
        company_style = ParagraphStyle(
            'Company',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=2,
            alignment=1  # Center
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#475569'),
            spaceAfter=10,
            alignment=1  # Center
        )
        
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#475569'),
            spaceAfter=2
        )
        
        # Header
        story.append(Paragraph("SALES & INVENTORY MANAGEMENT SYSTEM", title_style))
        story.append(Paragraph("Receipt", company_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Receipt details
        receipt_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Date: {receipt_date}", label_style))
        
        # Customer info
        if customer_name:
            story.append(Paragraph(f"Customer: {customer_name}", label_style))
        story.append(Paragraph(f"Payment Method: {payment_method}", label_style))
        
        # Remarks section
        if remarks and remarks.strip():
            story.append(Spacer(1, 0.15*inch))
            story.append(Paragraph("REMARKS:", label_style))
            remarks_style = ParagraphStyle(
                'Remarks',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#64748b'),
                spaceAfter=5,
                alignment=0  # Left align
            )
            story.append(Paragraph(remarks, remarks_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Sales details table
        data = [
            ['Product', 'Qty (Bags)', 'Price/Bag', 'Total'],
            [product_name, f'{quantity:.1f}', f'GHS {unit_price:.2f}', f'GHS {total_price:.2f}']
        ]
        
        table = Table(data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Total amount
        total_style = ParagraphStyle(
            'Total',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#10b981'),
            spaceAfter=10,
            alignment=2  # Right
        )
        story.append(Paragraph(f"<b>Total Amount: GHS {total_price:.2f}</b>", total_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#94a3b8'),
            alignment=1  # Center
        )
        story.append(Paragraph("Thank you for your purchase!", footer_style))
        story.append(Paragraph("Sales & Inventory Management System", footer_style))
        
        # Build PDF
        doc.build(story)
        return file_path
        
    except Exception as e:
        print(f"Error generating receipt: {e}")
        return None