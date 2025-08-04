import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from datetime import datetime
from models.product_model import ProductModel
from models.invoice_model import InvoiceModel
from ui.product_ui import ProductUI
from ui.invoice_ui import InvoiceUI


def open_dashboard(root, db_config, current_user):
    # Close current window
    root.destroy()

    # Create a new window
    new_root = ttkb.Window(themename="superhero")
    new_root.title("Point of Sale System - Dashboard")
    new_root.geometry("1200x700")
    new_root.minsize(width=800, height=600)

    # Create tabs
    tab_control = ttk.Notebook(new_root)

    # Dashboard tab
    dashboard_tab = ttk.Frame(tab_control)
    tab_control.add(dashboard_tab, text="Dashboard")

    # Products tab
    products_tab = ttk.Frame(tab_control)
    tab_control.add(products_tab, text="Products")

    # Invoices tab
    invoices_tab = ttk.Frame(tab_control)
    tab_control.add(invoices_tab, text="Invoices")

    tab_control.pack(expand=1, fill="both")

    # Initialize models
    product_model = ProductModel(db_config)
    invoice_model = InvoiceModel(db_config)

    # Create simple dashboard
    create_simple_dashboard(dashboard_tab, product_model, invoice_model, current_user)

    # Initialize UI modules for other tabs
    product_ui = ProductUI(products_tab, product_model)
    invoice_ui = InvoiceUI(invoices_tab, product_model, invoice_model)

    # Set focus to dashboard tab
    tab_control.select(0)

    # Run the window
    new_root.mainloop()


def create_simple_dashboard(parent, product_model, invoice_model, current_user):
    # Create main frame
    frame = ttk.Frame(parent, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill=tk.X, pady=(0, 20))

    ttk.Label(header_frame, text="Dashboard", font=("TkDefaultFont", 16, "bold")).pack(side=tk.LEFT)

    # User info and date
    user_frame = ttk.Frame(header_frame)
    user_frame.pack(side=tk.RIGHT)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")

    ttk.Label(user_frame, text=f"Welcome, {current_user}").pack(anchor=tk.E)
    ttk.Label(user_frame, text=f"Date: {date_str}").pack(anchor=tk.E)

    # Create stats cards
    stats_frame = ttk.Frame(frame)
    stats_frame.pack(fill=tk.X, pady=(0, 20))

    # Configure grid
    stats_frame.columnconfigure(0, weight=1)
    stats_frame.columnconfigure(1, weight=1)
    stats_frame.columnconfigure(2, weight=1)

    # Load data for stats
    try:
        # Get product stats
        success, message, products = product_model.get_all_products()
        if success:
            total_products = len(products)
            low_stock = sum(1 for p in products if p["quantity"] <= 5)
        else:
            total_products = 0
            low_stock = 0

        # Get sales stats
        success, message, invoice_data = invoice_model.get_all_invoices()
        if success:
            invoices = invoice_data.get('invoices', [])
            total_sales = sum(invoice["total"] for invoice in invoices)
        else:
            total_sales = 0

    except Exception as e:
        total_products = 0
        low_stock = 0
        total_sales = 0
        print(f"Error loading dashboard data: {str(e)}")

    # Create stat cards
    create_stat_card(stats_frame, 0, "Total Products", str(total_products), "info")
    create_stat_card(stats_frame, 1, "Low Stock Items", str(low_stock), "warning")
    create_stat_card(stats_frame, 2, "Total Sales", f"${total_sales:.2f}", "success")

    # Add some additional content
    content_frame = ttk.Frame(frame)
    content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    ttk.Label(
        content_frame,
        text="Welcome to the Point of Sale System",
        font=("TkDefaultFont", 14, "bold")
    ).pack(pady=20)

    ttk.Label(
        content_frame,
        text="Use the tabs above to manage products and create invoices.",
        wraplength=600
    ).pack()

    ttk.Label(
        content_frame,
        text="The invoice system has been updated to provide better stock validation.",
        wraplength=600
    ).pack(pady=10)

    ttk.Separator(content_frame).pack(fill=tk.X, pady=20)

    ttk.Label(
        content_frame,
        text="© 2025 POS System by youssef3fifi",
        font=("TkDefaultFont", 8)
    ).pack(side=tk.BOTTOM, pady=10)


def create_stat_card(parent, column, title, value, color):
    card = ttk.Frame(parent, style=f"{color}.TFrame", padding=10)
    card.grid(row=0, column=column, sticky="nsew", padx=5)

    ttk.Label(card, text=title).pack(anchor=tk.W)
    ttk.Label(
        card,
        text=value,
        font=("TkDefaultFont", 20, "bold")
    ).pack(anchor=tk.W)