# ui/invoice_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.product_model import get_all_products
from models.invoice_model import InvoiceModel
from datetime import datetime
import os

class InvoiceUI:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.invoice_items = []
        self.create_invoice_window()
    
    def create_invoice_window(self):
        """Create the main invoice window with tab interface"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Invoice Management System")
        self.window.geometry("1000x700")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_invoice_tab = ttk.Frame(self.notebook)
        self.invoice_history_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.create_invoice_tab, text="Create Invoice")
        self.notebook.add(self.invoice_history_tab, text="Invoice History")
        
        # Setup tabs
        self.setup_create_invoice_tab()
        self.setup_invoice_history_tab()
    
    def setup_create_invoice_tab(self):
        """Setup the create invoice tab"""
        tab = self.create_invoice_tab
        
        # Customer Information Section
        customer_frame = ttk.LabelFrame(tab, text="Customer Information", padding="10")
        customer_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(customer_frame, text="Customer Name:").grid(row=0, column=0, sticky="w", padx=5)
        self.customer_name_entry = ttk.Entry(customer_frame, width=30)
        self.customer_name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(customer_frame, text="Phone Number:").grid(row=0, column=2, sticky="w", padx=5)
        self.customer_phone_entry = ttk.Entry(customer_frame, width=20)
        self.customer_phone_entry.grid(row=0, column=3, padx=5, pady=2)
        
        # Product Selection Section
        product_frame = ttk.LabelFrame(tab, text="Product Selection", padding="10")
        product_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Product list with improved display
        columns = ("id", "name", "available_qty", "price", "total_value")
        self.product_tree = ttk.Treeview(product_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("name", text="Product Name")
        self.product_tree.heading("available_qty", text="Available Qty")
        self.product_tree.heading("price", text="Unit Price")
        self.product_tree.heading("total_value", text="Total Value")
        
        # Set column widths
        self.product_tree.column("id", width=50)
        self.product_tree.column("name", width=200)
        self.product_tree.column("available_qty", width=100)
        self.product_tree.column("price", width=100)
        self.product_tree.column("total_value", width=100)
        
        self.product_tree.pack(fill="both", expand=True)
        
        # Product selection controls
        selection_frame = ttk.Frame(product_frame)
        selection_frame.pack(fill="x", pady=5)
        
        ttk.Label(selection_frame, text="Quantity:").pack(side="left", padx=5)
        self.quantity_entry = ttk.Entry(selection_frame, width=10)
        self.quantity_entry.pack(side="left", padx=5)
        self.quantity_entry.insert(0, "1")
        
        ttk.Button(selection_frame, text="Add to Invoice", command=self.add_to_invoice).pack(side="left", padx=10)
        ttk.Button(selection_frame, text="Refresh Products", command=self.load_products).pack(side="left", padx=5)
        
        # Invoice Items Section
        invoice_frame = ttk.LabelFrame(tab, text="Invoice Items", padding="10")
        invoice_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Invoice items list
        invoice_columns = ("product_name", "quantity", "unit_price", "total_price")
        self.invoice_tree = ttk.Treeview(invoice_frame, columns=invoice_columns, show="headings", height=6)
        
        self.invoice_tree.heading("product_name", text="Product")
        self.invoice_tree.heading("quantity", text="Quantity")
        self.invoice_tree.heading("unit_price", text="Unit Price")
        self.invoice_tree.heading("total_price", text="Total Price")
        
        self.invoice_tree.column("product_name", width=200)
        self.invoice_tree.column("quantity", width=100)
        self.invoice_tree.column("unit_price", width=100)
        self.invoice_tree.column("total_price", width=100)
        
        self.invoice_tree.pack(fill="both", expand=True)
        
        # Invoice items controls
        items_control_frame = ttk.Frame(invoice_frame)
        items_control_frame.pack(fill="x", pady=5)
        
        ttk.Button(items_control_frame, text="Remove Selected", command=self.remove_selected_item).pack(side="left", padx=5)
        ttk.Button(items_control_frame, text="Clear All", command=self.clear_invoice).pack(side="left", padx=5)
        
        # Discount and Total Section
        total_frame = ttk.LabelFrame(tab, text="Discount & Total", padding="10")
        total_frame.pack(fill="x", padx=10, pady=5)
        
        # Discount controls
        discount_control_frame = ttk.Frame(total_frame)
        discount_control_frame.pack(fill="x", pady=5)
        
        ttk.Label(discount_control_frame, text="Discount:").pack(side="left", padx=5)
        self.discount_entry = ttk.Entry(discount_control_frame, width=10)
        self.discount_entry.pack(side="left", padx=5)
        self.discount_entry.insert(0, "0")
        self.discount_entry.bind('<KeyRelease>', self.calculate_totals)
        
        self.discount_type_var = tk.StringVar(value="fixed")
        ttk.Radiobutton(discount_control_frame, text="Fixed Amount", variable=self.discount_type_var, 
                       value="fixed", command=self.calculate_totals).pack(side="left", padx=10)
        ttk.Radiobutton(discount_control_frame, text="Percentage", variable=self.discount_type_var, 
                       value="percentage", command=self.calculate_totals).pack(side="left", padx=5)
        
        # Totals display
        totals_display_frame = ttk.Frame(total_frame)
        totals_display_frame.pack(fill="x", pady=10)
        
        self.subtotal_label = ttk.Label(totals_display_frame, text="Subtotal: $0.00", font=("Arial", 12))
        self.subtotal_label.pack(anchor="e")
        
        self.discount_label = ttk.Label(totals_display_frame, text="Discount: $0.00", font=("Arial", 12))
        self.discount_label.pack(anchor="e")
        
        self.total_label = ttk.Label(totals_display_frame, text="Total: $0.00", font=("Arial", 14, "bold"))
        self.total_label.pack(anchor="e")
        
        # Action buttons
        action_frame = ttk.Frame(tab)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(action_frame, text="Create Invoice", command=self.create_invoice).pack(side="right", padx=5)
        ttk.Button(action_frame, text="Print Receipt", command=self.print_receipt).pack(side="right", padx=5)
        
        # Load initial data
        self.load_products()
    
    def setup_invoice_history_tab(self):
        """Setup the invoice history tab"""
        tab = self.invoice_history_tab
        
        # Search and filter section
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        
        ttk.Button(search_frame, text="Search", command=self.search_invoices).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Refresh", command=self.load_invoice_history).pack(side="left", padx=5)
        
        # Invoice history list
        history_columns = ("id", "customer_name", "customer_phone", "subtotal", "discount", "total", "created_at")
        self.history_tree = ttk.Treeview(tab, columns=history_columns, show="headings")
        
        # Configure history columns
        for col in history_columns:
            self.history_tree.heading(col, text=col.replace("_", " ").title())
            if col == "id":
                self.history_tree.column(col, width=50)
            elif col in ["customer_name", "customer_phone"]:
                self.history_tree.column(col, width=150)
            elif col == "created_at":
                self.history_tree.column(col, width=150)
            else:
                self.history_tree.column(col, width=100)
        
        self.history_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # History actions
        history_action_frame = ttk.Frame(tab)
        history_action_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(history_action_frame, text="View Details", command=self.view_invoice_details).pack(side="left", padx=5)
        ttk.Button(history_action_frame, text="Print Receipt", command=self.print_selected_receipt).pack(side="left", padx=5)
        
        # Load invoice history
        self.load_invoice_history()
    
    def load_products(self):
        """Load products into the product tree"""
        self.product_tree.delete(*self.product_tree.get_children())
        try:
            products = get_all_products()
            for product in products:
                total_value = product["quantity"] * product["price"]
                self.product_tree.insert("", "end", values=(
                    product["id"], product["name"], product["quantity"], 
                    f"${product['price']:.2f}", f"${total_value:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")
    
    def add_to_invoice(self):
        """Add selected product to invoice"""
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product")
            return
        
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
            return
        
        for item in selected:
            values = self.product_tree.item(item)["values"]
            product_id, name, available_qty, price_str = values[0], values[1], values[2], values[3]
            price = float(price_str.replace("$", ""))
            
            if quantity > available_qty:
                messagebox.showwarning("Warning", f"Not enough quantity for {name}. Available: {available_qty}")
                continue
            
            # Check if product already in invoice
            existing_item = None
            for i, invoice_item in enumerate(self.invoice_items):
                if invoice_item["product_id"] == int(product_id):
                    existing_item = i
                    break
            
            if existing_item is not None:
                # Update existing item
                self.invoice_items[existing_item]["quantity"] += quantity
            else:
                # Add new item
                self.invoice_items.append({
                    "product_id": int(product_id),
                    "name": name,
                    "quantity": quantity,
                    "price": price
                })
        
        self.refresh_invoice_display()
        self.calculate_totals()
    
    def refresh_invoice_display(self):
        """Refresh the invoice items display"""
        self.invoice_tree.delete(*self.invoice_tree.get_children())
        for item in self.invoice_items:
            total_price = item["quantity"] * item["price"]
            self.invoice_tree.insert("", "end", values=(
                item["name"], item["quantity"], f"${item['price']:.2f}", f"${total_price:.2f}"
            ))
    
    def remove_selected_item(self):
        """Remove selected item from invoice"""
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        for item in selected:
            index = self.invoice_tree.index(item)
            del self.invoice_items[index]
        
        self.refresh_invoice_display()
        self.calculate_totals()
    
    def clear_invoice(self):
        """Clear all items from invoice"""
        if messagebox.askyesno("Confirm", "Clear all items from invoice?"):
            self.invoice_items.clear()
            self.refresh_invoice_display()
            self.calculate_totals()
    
    def calculate_totals(self, event=None):
        """Calculate and update totals display"""
        if not self.invoice_items:
            self.subtotal_label.config(text="Subtotal: $0.00")
            self.discount_label.config(text="Discount: $0.00")
            self.total_label.config(text="Total: $0.00")
            return
        
        # Calculate subtotal
        subtotal = sum(item["quantity"] * item["price"] for item in self.invoice_items)
        
        # Calculate discount
        try:
            discount_value = float(self.discount_entry.get() or 0)
        except ValueError:
            discount_value = 0
        
        discount_type = self.discount_type_var.get()
        if discount_type == "percentage":
            discount_amount = subtotal * (discount_value / 100)
        else:
            discount_amount = discount_value
        
        total = subtotal - discount_amount
        
        # Update labels
        self.subtotal_label.config(text=f"Subtotal: ${subtotal:.2f}")
        self.discount_label.config(text=f"Discount: ${discount_amount:.2f}")
        self.total_label.config(text=f"Total: ${total:.2f}")
    
    def create_invoice(self):
        """Create the invoice"""
        if not self.invoice_items:
            messagebox.showwarning("Warning", "No items in invoice")
            return
        
        try:
            customer_name = self.customer_name_entry.get().strip()
            customer_phone = self.customer_phone_entry.get().strip()
            discount_value = float(self.discount_entry.get() or 0)
            discount_type = self.discount_type_var.get()
            
            result = InvoiceModel.create_invoice_with_items(
                self.invoice_items, discount_value, discount_type, customer_name, customer_phone
            )
            
            messagebox.showinfo("Success", 
                f"Invoice #{result['invoice_id']} created successfully!\n"
                f"Total: ${result['total']:.2f}")
            
            # Clear the form
            self.clear_invoice()
            self.customer_name_entry.delete(0, tk.END)
            self.customer_phone_entry.delete(0, tk.END)
            self.discount_entry.delete(0, tk.END)
            self.discount_entry.insert(0, "0")
            
            # Refresh products and history
            self.load_products()
            self.load_invoice_history()
            
            # Store last invoice for printing
            self.last_invoice_result = result
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create invoice: {str(e)}")
    
    def print_receipt(self):
        """Print receipt for the current invoice"""
        if not hasattr(self, 'last_invoice_result'):
            messagebox.showwarning("Warning", "No invoice to print. Create an invoice first.")
            return
        
        self.generate_receipt(self.last_invoice_result)
    
    def generate_receipt(self, invoice_data):
        """Generate and save receipt as text file"""
        try:
            receipt_content = self.format_receipt(invoice_data)
            
            # Create receipts directory if it doesn't exist
            if not os.path.exists("receipts"):
                os.makedirs("receipts")
            
            filename = f"receipts/receipt_{invoice_data['invoice_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(receipt_content)
            
            messagebox.showinfo("Receipt Generated", f"Receipt saved as: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate receipt: {str(e)}")
    
    def format_receipt(self, invoice_data):
        """Format receipt content"""
        content = f"""
========================================
           INVOICE RECEIPT
========================================
Invoice ID: {invoice_data['invoice_id']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Customer Information:
Name: {invoice_data.get('customer_name', 'N/A')}
Phone: {invoice_data.get('customer_phone', 'N/A')}

========================================
                ITEMS
========================================
"""
        
        for item in self.invoice_items:
            total_price = item['quantity'] * item['price']
            content += f"{item['name']:<20} x{item['quantity']:<3} @ ${item['price']:<8.2f} = ${total_price:>8.2f}\n"
        
        content += f"""
========================================
Subtotal:                    ${invoice_data['subtotal']:>8.2f}
Discount ({invoice_data['discount_type']}):           ${invoice_data['discount_amount']:>8.2f}
----------------------------------------
TOTAL:                       ${invoice_data['total']:>8.2f}
========================================

Thank you for your business!
"""
        return content
    
    def load_invoice_history(self):
        """Load invoice history"""
        try:
            self.history_tree.delete(*self.history_tree.get_children())
            invoices = InvoiceModel.get_all_invoices()
            
            for invoice in invoices:
                # Handle both enhanced and basic invoice formats
                values = []
                values.append(invoice['id'])
                values.append(invoice.get('customer_name', 'N/A'))
                values.append(invoice.get('customer_phone', 'N/A'))
                values.append(f"${invoice.get('subtotal', invoice.get('total_price', 0)):.2f}")
                values.append(f"${invoice.get('discount', 0):.2f}")
                values.append(f"${invoice['total_price']:.2f}")
                values.append(invoice['created_at'].strftime('%Y-%m-%d %H:%M') if invoice['created_at'] else 'N/A')
                
                self.history_tree.insert("", "end", values=values)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load invoice history: {str(e)}")
    
    def search_invoices(self):
        """Search invoices by customer name or phone"""
        # This is a placeholder for search functionality
        messagebox.showinfo("Info", "Search functionality will filter invoices by customer name or phone")
    
    def view_invoice_details(self):
        """View details of selected invoice"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an invoice")
            return
        
        # Get invoice ID from selected row
        invoice_id = self.history_tree.item(selected[0])["values"][0]
        
        try:
            invoice_details = InvoiceModel.get_invoice_details(invoice_id)
            if invoice_details:
                self.show_invoice_details_window(invoice_details)
            else:
                messagebox.showerror("Error", "Invoice not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load invoice details: {str(e)}")
    
    def show_invoice_details_window(self, invoice_details):
        """Show invoice details in a new window"""
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Invoice #{invoice_details['id']} Details")
        details_window.geometry("600x500")
        
        # Invoice header info
        header_frame = ttk.LabelFrame(details_window, text="Invoice Information", padding="10")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(header_frame, text=f"Invoice ID: {invoice_details['id']}").pack(anchor="w")
        ttk.Label(header_frame, text=f"Date: {invoice_details['created_at']}").pack(anchor="w")
        ttk.Label(header_frame, text=f"Customer: {invoice_details.get('customer_name', 'N/A')}").pack(anchor="w")
        ttk.Label(header_frame, text=f"Phone: {invoice_details.get('customer_phone', 'N/A')}").pack(anchor="w")
        
        # Invoice items
        items_frame = ttk.LabelFrame(details_window, text="Items", padding="10")
        items_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("product_name", "quantity", "unit_price", "total_price")
        items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        
        for col in columns:
            items_tree.heading(col, text=col.replace("_", " ").title())
        
        for item in invoice_details.get('items', []):
            items_tree.insert("", "end", values=(
                item['product_name'], item['quantity'], 
                f"${item['unit_price']:.2f}", f"${item['total_price']:.2f}"
            ))
        
        items_tree.pack(fill="both", expand=True)
        
        # Totals
        totals_frame = ttk.Frame(details_window)
        totals_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(totals_frame, text=f"Discount: ${invoice_details['discount']:.2f}").pack(anchor="e")
        ttk.Label(totals_frame, text=f"Total: ${invoice_details['total_price']:.2f}", 
                 font=("Arial", 12, "bold")).pack(anchor="e")
    
    def print_selected_receipt(self):
        """Print receipt for selected invoice from history"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an invoice")
            return
        
        invoice_id = self.history_tree.item(selected[0])["values"][0]
        
        try:
            invoice_details = InvoiceModel.get_invoice_details(invoice_id)
            if invoice_details:
                # Format for receipt generation
                receipt_data = {
                    'invoice_id': invoice_details['id'],
                    'subtotal': invoice_details.get('subtotal', invoice_details['total_price']),
                    'discount_amount': invoice_details['discount'],
                    'discount_type': invoice_details.get('discount_type', 'fixed'),
                    'total': invoice_details['total_price'],
                    'customer_name': invoice_details.get('customer_name', 'N/A'),
                    'customer_phone': invoice_details.get('customer_phone', 'N/A')
                }
                
                # Set invoice items for receipt formatting
                self.invoice_items = []
                for item in invoice_details.get('items', []):
                    self.invoice_items.append({
                        'name': item['product_name'],
                        'quantity': item['quantity'],
                        'price': item['unit_price']
                    })
                
                self.generate_receipt(receipt_data)
            else:
                messagebox.showerror("Error", "Invoice not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print receipt: {str(e)}")

def open_invoice_ui(parent, user):
    """Function to open the invoice UI"""
    return InvoiceUI(parent, user)