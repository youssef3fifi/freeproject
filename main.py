# main.py
import tkinter as tk
from ui.login_ui import LoginUI

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginUI(root)
    root.mainloop()
