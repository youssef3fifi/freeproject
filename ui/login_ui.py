import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from database.db_connection import connect
from ui.new_windo import open_dashboard
from models.user_model import verify_user

class LoginUI:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
    
    def setup_ui(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo or app title
        ttk.Label(
            self.main_frame, 
            text="Point of Sale System", 
            font=("TkDefaultFont", 24, "bold")
        ).pack(pady=(0, 20))
        
        # Login frame
        login_frame = ttk.Frame(self.main_frame, padding=20)
        login_frame.pack(pady=20)
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(login_frame, textvariable=self.username_var, width=30)
        username_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=30)
        password_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Login button
        login_button = ttk.Button(login_frame, text="Login", command=self.login, style="success.TButton")
        login_button.grid(row=2, column=1, sticky=tk.E, pady=(20, 0))
        
        # Add event bindings
        username_entry.bind("<Return>", lambda event: password_entry.focus())
        password_entry.bind("<Return>", lambda event: self.login())
        
        # Set focus on username field
        username_entry.focus()
    
    def login(self):
        # Get the entered credentials
        username = self.username_var.get()
        password = self.password_var.get()
        
        # Validate credentials are not empty
        if not username:
            messagebox.showerror("Login Error", "Please enter your username.")
            return
        
        if not password:
            messagebox.showerror("Login Error", "Please enter your password.")
            return
        
        # Attempt to verify the user
        success, user_data = verify_user(username, password)
        
        if success:
            # Get database configuration
            db_config = connect()
            
            # Show success message
            messagebox.showinfo("Login Successful", f"Welcome, {user_data['username']}!")
            
            # Open the dashboard
            open_dashboard(self.root, db_config, user_data['username'])
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")