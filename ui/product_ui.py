import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *


class ProductUI:
    def __init__(self, parent, product_model):
        self.parent = parent
        self.product_model = product_model
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # Main frame
        self.frame = ttk.Frame(self.parent, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Header frame
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(header_frame, text="Products Management", font=("TkDefaultFont", 16, "bold")).pack(side=tk.LEFT)

        # Buttons frame
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)

        self.add_button = ttk.Button(buttons_frame, text="Add Product", command=self.show_add_product,
                                     style="success.TButton")
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.refresh_button = ttk.Button(buttons_frame, text="Refresh", command=self.load_products)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        # Products table
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "price", "quantity", "sold", "action")
        self.products_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Define column headings
        self.products_table.heading("id", text="ID")
        self.products_table.heading("name", text="Product Name")
        self.products_table.heading("price", text="Price")
        self.products_table.heading("quantity", text="In Stock")
        self.products_table.heading("sold", text="Sold")
        self.products_table.heading("action", text="Actions")

        # Define column widths
        self.products_table.column("id", width=50, anchor=tk.CENTER)
        self.products_table.column("name", width=200)
        self.products_table.column("price", width=100, anchor=tk.CENTER)
        self.products_table.column("quantity", width=100, anchor=tk.CENTER)
        self.products_table.column("sold", width=100, anchor=tk.CENTER)
        self.products_table.column("action", width=100, anchor=tk.CENTER)

        self.products_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.products_table.configure(yscrollcommand=scrollbar.set)

        # Bind click events
        self.products_table.bind("<Double-1>", self.on_item_double_click)
        self.products_table.bind("<Button-1>", self.on_item_click)

    def load_products(self):
        # Clear the table
        for item in self.products_table.get_children():
            self.products_table.delete(item)

        # Get products from model
        success, message, products = self.product_model.get_all_products()

        if not success:
            messagebox.showerror("Error", message)
            return

        # Add products to the table
        for product in products:
            self.products_table.insert("", "end", values=(
                product["id"],
                product["name"],
                f"{product['price']:.2f}",
                product["quantity"],
                product["sold"],
                "Edit/Delete"
            ))

    def show_add_product(self):
        # Create a new window for adding a product
        add_window = ttkb.Toplevel(self.parent)
        add_window.title("Add New Product")
        add_window.geometry("400x300")

        # Create a frame for the form
        form_frame = ttk.Frame(add_window, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Product name
        ttk.Label(form_frame, text="Product Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Price
        ttk.Label(form_frame, text="Price:").grid(row=1, column=0, sticky=tk.W, pady=5)
        price_var = tk.DoubleVar(value=0.00)
        price_entry = ttk.Entry(form_frame, textvariable=price_var, width=30)
        price_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=2, column=0, sticky=tk.W, pady=5)
        quantity_var = tk.IntVar(value=0)
        quantity_entry = ttk.Entry(form_frame, textvariable=quantity_var, width=30)
        quantity_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Submit button
        submit_button = ttk.Button(form_frame, text="Add Product", style="success.TButton",
                                   command=lambda: self.add_product(name_var.get(), price_var.get(), quantity_var.get(),
                                                                    add_window))
        submit_button.grid(row=3, column=1, sticky=tk.E, pady=20)

        # Cancel button
        cancel_button = ttk.Button(form_frame, text="Cancel", command=add_window.destroy)
        cancel_button.grid(row=3, column=0, sticky=tk.W, pady=20)

    def add_product(self, name, price, quantity, window):
        # Validate inputs
        if not name:
            messagebox.showerror("Error", "Product name is required")
            return

        if price <= 0:
            messagebox.showerror("Error", "Price must be greater than 0")
            return

        if quantity < 0:
            messagebox.showerror("Error", "Quantity cannot be negative")
            return

        # Create product
        product_data = {
            "name": name,
            "price": price,
            "quantity": quantity
        }

        success, message = self.product_model.add_product(product_data)

        if success:
            messagebox.showinfo("Success", "Product added successfully")
            window.destroy()
            self.load_products()
        else:
            messagebox.showerror("Error", message)

    def on_item_click(self, event):
        # Check if clicked on "action" column
        region = self.products_table.identify("region", event.x, event.y)
        if region == "cell":
            column = self.products_table.identify_column(event.x)
            if column == "#6":  # Action column
                row_id = self.products_table.identify_row(event.y)
                if row_id:
                    item = self.products_table.item(row_id)
                    product_id = item["values"][0]
                    self.show_edit_menu(event.x_root, event.y_root, product_id)

    def on_item_double_click(self, event):
        item = self.products_table.focus()
        if item:
            product_id = self.products_table.item(item)["values"][0]
            self.show_edit_product(product_id)

    def show_edit_menu(self, x, y, product_id):
        # Create context menu
        menu = tk.Menu(self.parent, tearoff=0)
        menu.add_command(label="Edit", command=lambda: self.show_edit_product(product_id))
        menu.add_command(label="Delete", command=lambda: self.confirm_delete_product(product_id))
        menu.tk_popup(x, y)

    def show_edit_product(self, product_id):
        # Get product details
        success, message, product = self.product_model.get_product(product_id)

        if not success:
            messagebox.showerror("Error", message)
            return

        # Create a new window for editing the product
        edit_window = ttkb.Toplevel(self.parent)
        edit_window.title(f"Edit Product: {product['name']}")
        edit_window.geometry("400x300")

        # Create a frame for the form
        form_frame = ttk.Frame(edit_window, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Product name
        ttk.Label(form_frame, text="Product Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=product["name"])
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Price
        ttk.Label(form_frame, text="Price:").grid(row=1, column=0, sticky=tk.W, pady=5)
        price_var = tk.DoubleVar(value=product["price"])
        price_entry = ttk.Entry(form_frame, textvariable=price_var, width=30)
        price_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=2, column=0, sticky=tk.W, pady=5)
        quantity_var = tk.IntVar(value=product["quantity"])
        quantity_entry = ttk.Entry(form_frame, textvariable=quantity_var, width=30)
        quantity_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Submit button
        submit_button = ttk.Button(form_frame, text="Update Product", style="success.TButton",
                                   command=lambda: self.update_product(product_id, name_var.get(), price_var.get(),
                                                                       quantity_var.get(), edit_window))
        submit_button.grid(row=3, column=1, sticky=tk.E, pady=20)

        # Cancel button
        cancel_button = ttk.Button(form_frame, text="Cancel", command=edit_window.destroy)
        cancel_button.grid(row=3, column=0, sticky=tk.W, pady=20)

    def update_product(self, product_id, name, price, quantity, window):
        # Validate inputs
        if not name:
            messagebox.showerror("Error", "Product name is required")
            return

        if price <= 0:
            messagebox.showerror("Error", "Price must be greater than 0")
            return

        if quantity < 0:
            messagebox.showerror("Error", "Quantity cannot be negative")
            return

        # Update product
        product_data = {
            "id": product_id,
            "name": name,
            "price": price,
            "quantity": quantity
        }

        success, message = self.product_model.update_product(product_data)

        if success:
            messagebox.showinfo("Success", "Product updated successfully")
            window.destroy()
            self.load_products()
        else:
            messagebox.showerror("Error", message)

    def confirm_delete_product(self, product_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            self.delete_product(product_id)

    def delete_product(self, product_id):
        success, message = self.product_model.delete_product(product_id)

        if success:
            messagebox.showinfo("Success", "Product deleted successfully")
            self.load_products()
        else:
            messagebox.showerror("Error", message)