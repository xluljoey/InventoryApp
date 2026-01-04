# Sales & Inventory Management System - Quick Start Guide

## First Time Setup

### Running the Application

#### Windows Users
1. Double-click `Sales & Inventory Management System.exe`
2. The app will start immediately
3. Database is created automatically on first run

#### Developers (Running from Source)
```bash
# Navigate to project folder
cd inventory_app

# Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux

# Run the app
python main.py
```

---

## Main Features

### 📊 Dashboard (Home Screen)
- Shows **TODAY'S REVENUE** in big green numbers
- Lists all products with current stock levels
- **Red text** = Low stock alert (5 bags or fewer)
- Click any product to quickly record a sale

### 💸 New Sale
- Record a product sale in seconds
- Auto-calculates total price
- Tracks customer and payment method
- Updates revenue in real-time

### 📅 Daily Sales
- View all sales from today
- See product, quantity, and price for each sale
- Track sales history

### 📊 Analytics
- View sales trends and graphs
- See top-selling products
- Analyze performance metrics

### 👥 Customers
- Add and manage customers
- Track customer balances
- View purchase history

### 📊 Reports
- Generate business audit trail
- Export to PDF for records
- Professional formatted reports

### ⚙️ Manage Stock
- Add new products to inventory
- Update product prices
- Adjust stock levels
- View all inventory details

### 🔄 Reset Daily
- Reset today's revenue counter (for next day)
- All sales records are kept for audit purposes
- Requires admin password: `SALES2025!`

---

## Common Tasks

### Recording a Sale
1. Click **💸 New Sale** button
2. Select product from dropdown
3. Enter quantity in bags
4. Select customer (or "Walk-in")
5. Click **Process Sale**
6. ✅ Revenue updates automatically

### Adding a New Product
1. Click **⚙️ Manage Stock**
2. Click **Add New Product**
3. Enter:
   - Product Name
   - Category
   - Price per bag
   - Weight per bag (kg)
4. Click **Add Product**

### Adding Stock
1. Click **⚙️ Manage Stock**
2. Find the product
3. Click the **➕ Add Stock** button
4. Enter quantity to add
5. New stock displays immediately

### Exporting Reports
1. Click **📊 Reports**
2. Click **Export Audit Trail to PDF**
3. Choose location to save
4. PDF is generated with all sales data

---

## Tips & Tricks

✨ **Pro Tips**:
- Click any product card on the dashboard to quickly open the New Sale window
- Low stock items are highlighted in RED - restock them soon!
- The reset button is in the top-right corner of the app
- All data is stored locally in `inventory.db` - back it up regularly!

---

## Troubleshooting

### "Database Error" message
- The app needs to create a database file
- Make sure the app folder is writable
- Close the app and delete `inventory.db`, then restart

### App runs slowly
- Close other applications
- If you have 1000+ sales, consider archiving old data
- Check available disk space

### Can't access Manage Stock or Reset
- You need the correct admin password
- Default password: `SALES2025!`
- Only admins can access these features

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Escape` | Close current window |
| `Tab` | Move between fields |
| `Enter` | Confirm action |

---

## Need Help?

- **Check the Deployment Guide** (`DEPLOYMENT_GUIDE.md`) for detailed information
- **Review the README** for technical details
- **Contact support** if issues persist

---

**Version**: 1.0  
**Last Updated**: December 31, 2025