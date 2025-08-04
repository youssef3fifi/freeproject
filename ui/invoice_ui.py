import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from datetime import datetime
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvoiceUI:
    def __init__(self, root, product_model, invoice_model):
        self.root = root
        self.product_model = product_model
        self.invoice_model = invoice_model

        # Current invoice data
        self.invoice_items = []
        self.customer_name = ""
        self.discount = 0
        self.discount_type = "amount"  # 'amount' or 'percentage'

        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # Create a frame for the invoice UI
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Product selection
        left_panel = ttk.LabelFrame(self.frame, text="Products", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Product search
        ttk.Label(left_panel, text="Search Products:").pack(anchor=tk.W, pady=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_products)
        search_entry = ttk.Entry(left_panel, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=(0, 10))

        # Product list
        columns = ("id", "name", "price", "quantity")
        self.product_table = ttk.Treeview(left_panel, columns=columns, show="headings", height=10)

        # Define column headings
        self.product_table.heading("id", text="ID")
        self.product_table.heading("name", text="Name")
        self.product_table.heading("price", text="Price")
        self.product_table.heading("quantity", text="In Stock")

        # Define column widths
        self.product_table.column("id", width=50)
        self.product_table.column("name", width=150)
        self.product_table.column("price", width=80)
        self.product_table.column("quantity", width=80)

        self.product_table.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.product_table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.product_table.configure(yscrollcommand=scrollbar.set)

        # Product selection controls
        controls_frame = ttk.Frame(left_panel)
        controls_frame.pack(fill=tk.X, pady=10)

        ttk.Label(controls_frame, text="Quantity:").pack(side=tk.LEFT)
        self.quantity_var = tk.IntVar(value=1)
        quantity_spin = ttk.Spinbox(controls_frame, from_=1, to=100, textvariable=self.quantity_var, width=5)
        quantity_spin.pack(side=tk.LEFT, padx=5)

        add_button = ttk.Button(controls_frame, text="Add to Invoice", command=self.add_to_invoice,
                                style="primary.TButton")
        add_button.pack(side=tk.LEFT, padx=5)

        # Right panel - Current invoice
        right_panel = ttk.LabelFrame(self.frame, text="Current Invoice", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Customer info
        customer_frame = ttk.Frame(right_panel)
        customer_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(customer_frame, text="Customer:").pack(side=tk.LEFT)
        self.customer_var = tk.StringVar()
        customer_entry = ttk.Entry(customer_frame, textvariable=self.customer_var)
        customer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Invoice items table
        columns = ("name", "quantity", "price", "total")
        self.invoice_table = ttk.Treeview(right_panel, columns=columns, show="headings", height=8)

        # Define column headings
        self.invoice_table.heading("name", text="Product")
        self.invoice_table.heading("quantity", text="Qty")
        self.invoice_table.heading("price", text="Unit Price")
        self.invoice_table.heading("total", text="Total")

        # Define column widths
        self.invoice_table.column("name", width=150)
        self.invoice_table.column("quantity", width=50)
        self.invoice_table.column("price", width=80)
        self.invoice_table.column("total", width=80)

        self.invoice_table.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.invoice_table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.invoice_table.configure(yscrollcommand=scrollbar.set)

        # Remove item button
        remove_button = ttk.Button(right_panel, text="Remove Selected Item", command=self.remove_selected_item)
        remove_button.pack(anchor=tk.E, pady=5)

        # Discount controls
        discount_frame = ttk.Frame(right_panel)
        discount_frame.pack(fill=tk.X, pady=5)

        ttk.Label(discount_frame, text="Discount:").pack(side=tk.LEFT)
        self.discount_var = tk.DoubleVar(value=0)
        discount_entry = ttk.Entry(discount_frame, textvariable=self.discount_var, width=10)
        discount_entry.pack(side=tk.LEFT, padx=5)

        # Discount type radio buttons
        self.discount_type_var = tk.StringVar(value="amount")
        amount_radio = ttk.Radiobutton(discount_frame, text="Amount", variable=self.discount_type_var, value="amount")
        percent_radio = ttk.Radiobutton(discount_frame, text="Percentage", variable=self.discount_type_var,
                                        value="percentage")
        amount_radio.pack(side=tk.LEFT)
        percent_radio.pack(side=tk.LEFT)

        # Totals frame
        totals_frame = ttk.Frame(right_panel)
        totals_frame.pack(fill=tk.X, pady=10)

        # Subtotal
        ttk.Label(totals_frame, text="Subtotal:").grid(row=0, column=0, sticky=tk.W)
        self.subtotal_var = tk.DoubleVar(value=0)
        ttk.Label(totals_frame, textvariable=self.subtotal_var).grid(row=0, column=1, sticky=tk.E)

        # Discount amount
        ttk.Label(totals_frame, text="Discount:").grid(row=1, column=0, sticky=tk.W)
        self.discount_amount_var = tk.DoubleVar(value=0)
        ttk.Label(totals_frame, textvariable=self.discount_amount_var).grid(row=1, column=1, sticky=tk.E)

        # Total
        ttk.Label(totals_frame, text="Total:", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky=tk.W)
        self.total_var = tk.DoubleVar(value=0)
        ttk.Label(totals_frame, textvariable=self.total_var, font=("TkDefaultFont", 10, "bold")).grid(row=2, column=1,
                                                                                                      sticky=tk.E)

        # Configure grid
        totals_frame.columnconfigure(1, weight=1)

        # Finalize button
        finalize_button = ttk.Button(right_panel, text="Finalize Invoice", command=self.finalize_invoice,
                                     style="success.TButton")
        finalize_button.pack(fill=tk.X, pady=(10, 0))

        # Clear button
        clear_button = ttk.Button(right_panel, text="Clear Invoice", command=self.clear_invoice, style="danger.TButton")
        clear_button.pack(fill=tk.X, pady=(5, 0))

    def load_products(self):
        success, message, products = self.product_model.get_all_products()

        if not success:
            messagebox.showerror("Error", message)
            return

        self.all_products = products
        self.update_product_table()

    def update_product_table(self):
        # Clear the table
        for item in self.product_table.get_children():
            self.product_table.delete(item)

        # Add products to the table
        for product in self.all_products:
            # Check if a search filter is active
            if self.search_var.get().strip():
                if self.search_var.get().lower() not in product["name"].lower():
                    continue

            # Check if product has stock
            if product["quantity"] <= 0:
                continue

            self.product_table.insert("", "end", values=(
                product["id"],
                product["name"],
                f"{product['price']:.2f}",
                product["quantity"]
            ))

    def filter_products(self, *args):
        self.update_product_table()

    def add_to_invoice(self):
        selected = self.product_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product first.")
            return

        # Get product data
        product_id = self.product_table.item(selected[0])["values"][0]
        product_name = self.product_table.item(selected[0])["values"][1]
        product_price = float(self.product_table.item(selected[0])["values"][2])
        available_quantity = int(self.product_table.item(selected[0])["values"][3])

        # Get quantity
        quantity = self.quantity_var.get()

        # Check if quantity is valid
        if quantity <= 0:
            messagebox.showerror("Invalid Quantity", "Quantity must be greater than 0.")
            return

        # Check if there's enough stock
        if quantity > available_quantity:
            messagebox.showerror(
                "Insufficient Stock",
                f"Insufficient stock for '{product_name}'. Available: {available_quantity}, Requested: {quantity}"
            )
            return

        # Check if product is already in the invoice
        for i, item in enumerate(self.invoice_items):
            if item["product_id"] == product_id:
                # Check if the combined quantity exceeds stock
                if (item["quantity"] + quantity) > available_quantity:
                    messagebox.showerror(
                        "Insufficient Stock",
                        f"Insufficient stock for '{product_name}'. Available: {available_quantity}, " +
                        f"Already in cart: {item['quantity']}, Requested: {quantity}"
                    )
                    return

                # Update existing item
                self.invoice_items[i]["quantity"] += quantity
                self.update_invoice_table()
                self.update_totals()
                return

        # Add new item to invoice
        self.invoice_items.append({
            "product_id": product_id,
            "name": product_name,
            "price": product_price,
            "quantity": quantity
        })

        self.update_invoice_table()
        self.update_totals()

    def remove_selected_item(self):
        selected = self.invoice_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return

        # Get the index of the selected item
        idx = self.invoice_table.index(selected[0])

        # Remove the item
        del self.invoice_items[idx]

        self.update_invoice_table()
        self.update_totals()

    def update_invoice_table(self):
        # Clear the table
        for item in self.invoice_table.get_children():
            self.invoice_table.delete(item)

        # Add items to the table
        for item in self.invoice_items:
            self.invoice_table.insert("", "end", values=(
                item["name"],
                item["quantity"],
                f"{item['price']:.2f}",
                f"{item['price'] * item['quantity']:.2f}"
            ))

    def update_totals(self):
        # Calculate subtotal
        subtotal = sum(item["price"] * item["quantity"] for item in self.invoice_items)
        self.subtotal_var.set(f"{subtotal:.2f}")

        # Calculate discount
        discount = self.discount_var.get()

        if self.discount_type_var.get() == "percentage":
            if discount < 0 or discount > 100:
                messagebox.showerror("Invalid Discount", "Percentage discount must be between 0 and 100.")
                self.discount_var.set(0)
                discount = 0
            discount_amount = subtotal * discount / 100
        else:  # amount
            if discount < 0:
                messagebox.showerror("Invalid Discount", "Discount cannot be negative.")
                self.discount_var.set(0)
                discount = 0
            elif discount > subtotal and subtotal > 0:
                messagebox.showerror("Invalid Discount", "Discount cannot exceed the subtotal.")
                self.discount_var.set(subtotal)
                discount = subtotal
            discount_amount = discount

        self.discount_amount_var.set(f"{discount_amount:.2f}")

        # Calculate total
        total = subtotal - discount_amount
        self.total_var.set(f"{total:.2f}")

    def clear_invoice(self):
        if not self.invoice_items:
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to clear the current invoice?"):
            self.invoice_items = []
            self.customer_var.set("")
            self.discount_var.set(0)
            self.discount_type_var.set("amount")
            self.update_invoice_table()
            self.update_totals()

    def finalize_invoice(self):
        if not self.invoice_items:
            messagebox.showwarning("Empty Invoice", "Please add items to the invoice first.")
            return

        # Confirm finalization
        if not messagebox.askyesno("Confirm", "Are you sure you want to finalize this invoice?"):
            return

        # Update customer name and discount
        self.customer_name = self.customer_var.get()
        self.discount = self.discount_var.get()
        self.discount_type = self.discount_type_var.get()

        # Prepare invoice data
        invoice_data = {
            "customer_name": self.customer_name,
            "discount": self.discount,
            "discount_type": self.discount_type,
            "items": self.invoice_items
        }

        # Create invoice
        success, message, invoice_details = self.invoice_model.create_invoice(invoice_data)

        if success:
            # Show success message
            messagebox.showinfo("Success", message)

            # Ask if user wants to see invoice details
            if messagebox.askyesno("Invoice Details", "Do you want to see detailed invoice information?"):
                self.show_invoice_details(invoice_details)

            # Clear the current invoice
            self.clear_invoice()

            # Reload product data to update stock numbers
            self.load_products()
        else:
            # Show error message
            messagebox.showerror("Error", message)

    def show_invoice_details(self, invoice_details):
        # Create a new window for invoice details
        details_window = ttkb.Toplevel(self.root)
        details_window.title(f"Invoice #{invoice_details['invoice_id']} Details")
        details_window.geometry("500x600")

        # Create a frame for the invoice details
        frame = ttk.Frame(details_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Invoice header
        ttk.Label(frame, text=f"Invoice #{invoice_details['invoice_id']}", font=("TkDefaultFont", 14, "bold")).pack(
            anchor=tk.W)
        ttk.Label(frame, text=f"Date: {invoice_details['date']}").pack(anchor=tk.W)
        ttk.Label(frame, text=f"Customer: {invoice_details['customer_name']}").pack(anchor=tk.W)

        # Items table
        ttk.Label(frame, text="Items:", font=("TkDefaultFont", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))

        columns = ("name", "quantity", "price", "total")
        items_table = ttk.Treeview(frame, columns=columns, show="headings", height=8)

        # Define column headings
        items_table.heading("name", text="Product")
        items_table.heading("quantity", text="Qty")
        items_table.heading("price", text="Unit Price")
        items_table.heading("total", text="Total")

        # Define column widths
        items_table.column("name", width=200)
        items_table.column("quantity", width=50)
        items_table.column("price", width=100)
        items_table.column("total", width=100)

        items_table.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=items_table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        items_table.configure(yscrollcommand=scrollbar.set)

        # Add items to the table
        for item in invoice_details["items"]:
            total = item["price"] * item["quantity"]
            items_table.insert("", "end", values=(
                item["name"],
                item["quantity"],
                f"{item['price']:.2f}",
                f"{total:.2f}"
            ))

        # Totals frame
        totals_frame = ttk.Frame(frame)
        totals_frame.pack(fill=tk.X, pady=10)

        # Subtotal
        ttk.Label(totals_frame, text="Subtotal:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(totals_frame, text=f"{invoice_details['subtotal']:.2f}").grid(row=0, column=1, sticky=tk.E)

        # Discount
        discount_text = f"{invoice_details['discount']:.2f}"
        if invoice_details['discount_type'] == 'percentage':
            discount_text += f" ({invoice_details['discount']}%)"

        ttk.Label(totals_frame, text="Discount:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(totals_frame, text=discount_text).grid(row=1, column=1, sticky=tk.E)

        # Total
        ttk.Label(totals_frame, text="Total:", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky=tk.W)
        ttk.Label(totals_frame, text=f"{invoice_details['total']:.2f}", font=("TkDefaultFont", 10, "bold")).grid(row=2,
                                                                                                                 column=1,
                                                                                                                 sticky=tk.E)

        # Configure grid
        totals_frame.columnconfigure(1, weight=1)

        # Close button
        close_button = ttk.Button(frame, text="Close", command=details_window.destroy, style="primary.TButton")
        close_button.pack(pady=(10, 0))