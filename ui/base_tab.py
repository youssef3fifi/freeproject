"""
الفئة الأساسية للتابات - تحتوي على الدوال المشتركة
"""
import tkinter as tk
from tkinter import ttk, messagebox


class BaseTab:
    """الفئة الأساسية لجميع التابات"""
    
    def __init__(self, parent, user, root):
        """
        تهيئة التاب الأساسي
        
        Args:
            parent: الـ frame الأب (notebook tab)
            user: بيانات المستخدم الحالي
            root: النافذة الرئيسية
        """
        self.parent = parent
        self.user = user
        self.root = root
    
    def create_button(self, parent, text, command, width=15):
        """
        إنشاء زر مع تأثيرات hover
        
        Args:
            parent: الـ widget الأب
            text: نص الزر
            command: الدالة المرتبطة بالزر
            width: عرض الزر
            
        Returns:
            ttk.Button: الزر المنشأ
        """
        btn = ttk.Button(parent, text=text, command=command, width=width)
        
        # إضافة تأثيرات عند المرور بالماوس
        def on_enter(e):
            btn['style'] = 'Hover.TButton'
        def on_leave(e):
            btn['style'] = 'TButton'
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def is_admin(self):
        """التحقق إذا كان المستخدم مدير"""
        return self.user['role'] == 'admin'
    
    def show_error(self, title, message):
        """عرض رسالة خطأ"""
        messagebox.showerror(title, message)
    
    def show_info(self, title, message):
        """عرض رسالة معلومات"""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title, message):
        """عرض رسالة تحذير"""
        messagebox.showwarning(title, message)
    
    def confirm(self, title, message):
        """عرض رسالة تأكيد وإرجاع True/False"""
        return messagebox.askyesno(title, message)
    
    def center_window(self, window, width, height):
        """توسيط نافذة على الشاشة"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - width/2)
        center_y = int(screen_height/2 - height/2)
        window.geometry(f"{width}x{height}+{center_x}+{center_y}")
