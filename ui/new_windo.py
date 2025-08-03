#new_windo.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.product_model import get_all_products, update_product_quantity
from models.invoice_model import create_invoice_with_items  


def open_dashboard(user):
    dashboard = tk.Toplevel()
    dashboard.title("Dashboard")
    dashboard.geometry("700x650")

    label = tk.Label(dashboard, text=f"Welcome {user['username']} - Role: {user['role']}", font=("Arial", 14))
    label.pack(pady=10)

    columns = ("id", "name", "quantity", "price", "total_price", "sold", "profit")
    tree = ttk.Treeview(dashboard, columns=columns, show="headings", selectmode="extended")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    def load_products():
        tree.delete(*tree.get_children())
        for product in get_all_products():
            total_price = product["quantity"] * product["price"]
            profit = product["sold"] * product["price"]
            tree.insert("", "end", values=(
                product["id"], product["name"], product["quantity"], product["price"],
                total_price, product["sold"], profit
            ))

    # ===== بيع أكثر من منتج =====
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
            invoice_preview.insert(tk.END, f"{item['name']} x {item['quantity']} @ {item['price']}")

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

    # إدخال الكمية وزر الإضافة
    quantity_entry = tk.Entry(dashboard)
    quantity_entry.pack(pady=5)
    quantity_entry.insert(0, "1")

    add_button = tk.Button(dashboard, text="Add to Invoice", command=add_to_invoice)
    add_button.pack(pady=5)

    # معاينة محتوى الفاتورة
    invoice_preview = tk.Listbox(dashboard, height=6)
    invoice_preview.pack(pady=5, fill="x")
    invoice_preview.bind("<Double-Button-1>", remove_selected_item)

    # إدخال الخصم وزر إنهاء الفاتورة
    discount_entry = tk.Entry(dashboard)
    discount_entry.pack(pady=5)
    discount_entry.insert(0, "0")

    finalize_button = tk.Button(dashboard, text="Finalize Invoice", command=finalize_invoice)
    finalize_button.pack(pady=5)

    load_products()

    # ===== Add New Product (Admin only) =====
    if user["role"] == "admin":
        separator = ttk.Separator(dashboard, orient='horizontal')
        separator.pack(fill='x', pady=10)

        add_label = tk.Label(dashboard, text="Add New Product", font=("Arial", 12, "bold"))
        add_label.pack(pady=5)

        name_entry = tk.Entry(dashboard)
        name_entry.pack()
        name_entry.insert(0, "Product Name")

        quantity_entry_add = tk.Entry(dashboard)
        quantity_entry_add.pack()
        quantity_entry_add.insert(0, "Quantity")

        price_entry = tk.Entry(dashboard)
        price_entry.pack()
        price_entry.insert(0, "Price")

        def add_product_handler():
            name = name_entry.get()
            try:
                quantity = int(quantity_entry_add.get())
                price = float(price_entry.get())
            except:
                messagebox.showerror("Error", "Please enter valid quantity and price")
                return

            if not name:
                messagebox.showerror("Error", "Enter product name")
                return

            from models.product_model import add_product
            add_product(name, quantity, price)
            messagebox.showinfo("Success", "Product added successfully")
            load_products()

        add_button = tk.Button(dashboard, text="Add Product", command=add_product_handler)
        add_button.pack(pady=5)

    dashboard.mainloop()
