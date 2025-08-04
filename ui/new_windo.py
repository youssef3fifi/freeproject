#new_windo.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.product_model import get_all_products, update_product_quantity
from models.invoice_model import create_invoice_with_items  


def open_dashboard(user):
    dashboard = tk.Toplevel()
    dashboard.title("Inventory Management Dashboard")
    dashboard.geometry("800x700")

    # Header with user info and navigation
    header_frame = tk.Frame(dashboard)
    header_frame.pack(fill="x", padx=10, pady=5)
    
    label = tk.Label(header_frame, text=f"Welcome {user['username']} - Role: {user['role']}", font=("Arial", 14))
    label.pack(side="left")
    
    # Navigation buttons
    nav_frame = tk.Frame(header_frame)
    nav_frame.pack(side="right")
    
    def open_invoice_system():
        try:
            from ui.invoice_ui import open_invoice_ui
            open_invoice_ui(dashboard, user)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open invoice system: {str(e)}")
    
    ttk.Button(nav_frame, text="📄 Invoice System", command=open_invoice_system).pack(side="left", padx=5)
    ttk.Button(nav_frame, text="🔄 Refresh", command=lambda: load_products()).pack(side="left", padx=5)

    # Create notebook for organized interface
    notebook = ttk.Notebook(dashboard)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Inventory tab
    inventory_tab = ttk.Frame(notebook)
    notebook.add(inventory_tab, text="📦 Inventory Overview")
    
    # Quick Sale tab (legacy system)
    quick_sale_tab = ttk.Frame(notebook)
    notebook.add(quick_sale_tab, text="💳 Quick Sale (Legacy)")
    
    # Setup inventory overview tab
    setup_inventory_tab(inventory_tab, user)
    
    # Setup quick sale tab (existing functionality)
    setup_quick_sale_tab(quick_sale_tab, user)

def setup_inventory_tab(tab, user):
    """Setup the inventory overview tab"""
    
    # Product overview section
    products_frame = ttk.LabelFrame(tab, text="Product Inventory", padding="10")
    products_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    columns = ("id", "name", "quantity", "price", "total_value", "sold", "profit")
    tree = ttk.Treeview(products_frame, columns=columns, show="headings", selectmode="extended")
    
    # Configure columns
    tree.heading("id", text="ID")
    tree.heading("name", text="Product Name")
    tree.heading("quantity", text="Stock Qty")
    tree.heading("price", text="Unit Price")
    tree.heading("total_value", text="Total Value")
    tree.heading("sold", text="Sold")
    tree.heading("profit", text="Revenue")
    
    # Set column widths
    tree.column("id", width=50)
    tree.column("name", width=200)
    tree.column("quantity", width=80)
    tree.column("price", width=100)
    tree.column("total_value", width=100)
    tree.column("sold", width=80)
    tree.column("profit", width=100)
    
    tree.pack(fill="both", expand=True)

    def load_products():
        tree.delete(*tree.get_children())
        try:
            for product in get_all_products():
                total_value = product["quantity"] * product["price"]
                profit = product["sold"] * product["price"]
                tree.insert("", "end", values=(
                    product["id"], product["name"], product["quantity"], 
                    f"${product['price']:.2f}", f"${total_value:.2f}", 
                    product["sold"], f"${profit:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    # Statistics section
    stats_frame = ttk.LabelFrame(tab, text="Statistics", padding="10")
    stats_frame.pack(fill="x", padx=10, pady=5)
    
    def update_statistics():
        try:
            products = get_all_products()
            total_products = len(products)
            total_stock_value = sum(p["quantity"] * p["price"] for p in products)
            total_revenue = sum(p["sold"] * p["price"] for p in products)
            low_stock_items = len([p for p in products if p["quantity"] < 5])
            
            stats_text = f"Total Products: {total_products} | Stock Value: ${total_stock_value:.2f} | Revenue: ${total_revenue:.2f} | Low Stock: {low_stock_items}"
            stats_label.config(text=stats_text)
        except Exception as e:
            stats_label.config(text="Error loading statistics")
    
    stats_label = tk.Label(stats_frame, text="Loading statistics...", font=("Arial", 10))
    stats_label.pack()
    
    # Load initial data
    load_products()
    update_statistics()
    
    # Admin product management
    if user["role"] == "admin":
        admin_frame = ttk.LabelFrame(tab, text="Product Management (Admin)", padding="10")
        admin_frame.pack(fill="x", padx=10, pady=5)

        # Product form
        form_frame = ttk.Frame(admin_frame)
        form_frame.pack(fill="x", pady=5)
        
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5)
        name_entry = ttk.Entry(form_frame, width=20)
        name_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Quantity:").grid(row=0, column=2, sticky="w", padx=5)
        quantity_entry_add = ttk.Entry(form_frame, width=10)
        quantity_entry_add.grid(row=0, column=3, padx=5)
        
        ttk.Label(form_frame, text="Price:").grid(row=0, column=4, sticky="w", padx=5)
        price_entry = ttk.Entry(form_frame, width=10)
        price_entry.grid(row=0, column=5, padx=5)

        def add_product_handler():
            name = name_entry.get().strip()
            try:
                quantity = int(quantity_entry_add.get())
                price = float(price_entry.get())
                if quantity < 0 or price < 0:
                    raise ValueError("Values must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid quantity and price")
                return

            if not name:
                messagebox.showerror("Error", "Enter product name")
                return

            try:
                from models.product_model import add_product
                add_product(name, quantity, price)
                messagebox.showinfo("Success", "Product added successfully")
                
                # Clear form
                name_entry.delete(0, tk.END)
                quantity_entry_add.delete(0, tk.END)
                price_entry.delete(0, tk.END)
                
                load_products()
                update_statistics()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {str(e)}")

        ttk.Button(form_frame, text="Add Product", command=add_product_handler).grid(row=0, column=6, padx=10)

def setup_quick_sale_tab(tab, user):
    """Setup the quick sale tab (legacy functionality)"""
    
    # Info label
    info_frame = ttk.Frame(tab)
    info_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Label(info_frame, text="⚠️ Legacy Quick Sale - Use the new Invoice System for enhanced features", 
             font=("Arial", 10, "italic")).pack()
    
    # Product selection
    products_frame = ttk.LabelFrame(tab, text="Select Products", padding="10")
    products_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    columns = ("id", "name", "quantity", "price")
    tree = ttk.Treeview(products_frame, columns=columns, show="headings", selectmode="extended")
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
    tree.pack(fill="both", expand=True)

    def load_products():
        tree.delete(*tree.get_children())
        try:
            for product in get_all_products():
                tree.insert("", "end", values=(
                    product["id"], product["name"], product["quantity"], product["price"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    # Sale controls
    controls_frame = ttk.Frame(tab)
    controls_frame.pack(fill="x", padx=10, pady=5)
    
    # Quantity and add controls
    quantity_frame = ttk.Frame(controls_frame)
    quantity_frame.pack(fill="x", pady=5)
    
    ttk.Label(quantity_frame, text="Quantity:").pack(side="left", padx=5)
    quantity_entry = ttk.Entry(quantity_frame, width=10)
    quantity_entry.pack(side="left", padx=5)
    quantity_entry.insert(0, "1")

    # ===== Quick sale functionality (existing logic) =====
    invoice_items = []

    def add_to_invoice():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product")
            return
        try:
            quantity = int(quantity_entry.get())
            if quantity <= 0:
                raise ValueError()
        except:
            messagebox.showerror("Error", "Enter valid quantity")
            return

        for item in selected:
            values = tree.item(item)["values"]
            product_id, name, available_qty, price = values[0], values[1], values[2], values[3]
            if quantity > available_qty:
                messagebox.showwarning("Warning", f"Not enough quantity for {name}")
                continue
            invoice_items.append({"product_id": int(product_id),
                                  "name": name,
                                  "quantity": int(quantity),
                                  "price": float(price)
            })
        refresh_invoice_preview()

    def refresh_invoice_preview():
        invoice_preview.delete(0, tk.END)
        for item in invoice_items:
            invoice_preview.insert(tk.END, f"{item['name']} x {item['quantity']} @ ${item['price']:.2f}")

    def remove_selected_item(event):
        selected = invoice_preview.curselection()
        if selected:
            index = selected[0]
            del invoice_items[index]
            refresh_invoice_preview()

    def finalize_invoice():
        try:
            discount = float(discount_entry.get()) if discount_entry.get() else 0.0
        except:
            messagebox.showerror("Error", "Invalid discount value")
            return

        if not invoice_items:
            messagebox.showwarning("Warning", "No items added to invoice")
            return

        try:
            invoice_id = create_invoice_with_items(invoice_items, discount)
            for item in invoice_items:
                update_product_quantity(item["product_id"], item["quantity"])
            messagebox.showinfo("Success", f"Invoice #{invoice_id} completed successfully")
            invoice_items.clear()
            refresh_invoice_preview()
            load_products()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete invoice.\n{str(e)}")

    ttk.Button(quantity_frame, text="Add to Sale", command=add_to_invoice).pack(side="left", padx=10)

    # Invoice preview
    preview_frame = ttk.LabelFrame(tab, text="Sale Items", padding="10")
    preview_frame.pack(fill="x", padx=10, pady=5)
    
    invoice_preview = tk.Listbox(preview_frame, height=4)
    invoice_preview.pack(fill="x", pady=5)
    invoice_preview.bind("<Double-Button-1>", remove_selected_item)

    # Discount and finalize
    final_frame = ttk.Frame(tab)
    final_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Label(final_frame, text="Fixed Discount:").pack(side="left", padx=5)
    discount_entry = ttk.Entry(final_frame, width=10)
    discount_entry.pack(side="left", padx=5)
    discount_entry.insert(0, "0")

    ttk.Button(final_frame, text="Complete Sale", command=finalize_invoice).pack(side="right", padx=5)
    ttk.Button(final_frame, text="Clear Items", command=lambda: (invoice_items.clear(), refresh_invoice_preview())).pack(side="right", padx=5)

    load_products()
