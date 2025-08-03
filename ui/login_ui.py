#login_ui.py
import tkinter as tk
from tkinter import messagebox
from models.user_model import UserModel
from ui.new_windo import open_dashboard

class LoginUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("400x400")

        self.label_username = tk.Label(root, text="Username")
        self.label_username.pack()

        self.entry_username = tk.Entry(root)
        self.entry_username.pack()

        self.label_password = tk.Label(root, text="Password")
        self.label_password.pack()

        self.entry_password = tk.Entry(root, show="*")
        self.entry_password.pack()

        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        user = UserModel.login(username, password)

        if user:
            messagebox.showinfo("Login", f"Login successful! Role: {user['role']}")
            open_dashboard(user)
            self.root.destroy()  # ✅
        else:
            messagebox.showerror("Login", "Invalid username or password.")
