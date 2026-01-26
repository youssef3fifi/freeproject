"""
تبويب إدارة المستخدمين
"""
import tkinter as tk
from tkinter import ttk
from models.user_model import UserModel
from ui.base_tab import BaseTab


class UsersTab(BaseTab):
    """تبويب إدارة المستخدمين (للمدير فقط)"""
    
    def __init__(self, parent, user, root):
        super().__init__(parent, user, root)
        self.setup_tab()
    
    def setup_tab(self):
        """إعداد تبويب المستخدمين"""
        if not self.is_admin():
            ttk.Label(self.parent, text="لا تملك صلاحية الوصول إلى هذه الصفحة").pack(pady=20)
            return
            
        # إطار للأزرار
        buttons_frame = ttk.Frame(self.parent)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        self.create_button(buttons_frame, "إضافة مستخدم", self.add_user).pack(side="left", padx=5)
        self.create_button(buttons_frame, "تعديل مستخدم", self.edit_user).pack(side="left", padx=5)
        self.create_button(buttons_frame, "حذف مستخدم", self.delete_user).pack(side="left", padx=5)
        self.create_button(buttons_frame, "تحديث", self.load_users).pack(side="right", padx=5)
        
        # إنشاء جدول المستخدمين
        columns = ("id", "username", "role")
        self.users_tree = ttk.Treeview(self.parent, columns=columns, show="headings")
        
        self.users_tree.heading("id", text="المعرف")
        self.users_tree.heading("username", text="اسم المستخدم")
        self.users_tree.heading("role", text="الصلاحية")
        
        self.users_tree.column("id", width=50, anchor="center")
        self.users_tree.column("username", width=200, anchor="e")
        self.users_tree.column("role", width=100, anchor="center")
        
        # إضافة شريط التمرير
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="left", fill="y")
        self.users_tree.pack(side="right", fill="both", expand=True, padx=10, pady=5)
        
        # تحميل المستخدمين
        self.load_users()

    def load_users(self):
        """تحميل المستخدمين من قاعدة البيانات"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        success, users = UserModel.get_all_users()
        if success:
            for user in users:
                role_text = "مدير" if user["role"] == "admin" else "عامل"
                self.users_tree.insert("", "end", values=(
                    user["id"],
                    user["username"],
                    role_text
                ))
        else:
            self.show_error("خطأ", "فشل في تحميل المستخدمين")

    def add_user(self):
        """إضافة مستخدم جديد"""
        add_window = tk.Toplevel(self.root)
        add_window.title("إضافة مستخدم جديد")
        add_window.resizable(False, False)
        add_window.configure(bg="#f5f5f5")
        self.center_window(add_window, 450, 280)
        
        ttk.Label(add_window, text="اسم المستخدم:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        username_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=username_var, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(add_window, text="كلمة المرور:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        password_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=password_var, width=30, show="*").grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(add_window, text="الصلاحية:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        role_var = tk.StringVar(value="worker")
        role_frame = ttk.Frame(add_window)
        role_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Radiobutton(role_frame, text="مدير", variable=role_var, value="admin").pack(side="right", padx=10)
        ttk.Radiobutton(role_frame, text="عامل", variable=role_var, value="worker").pack(side="right", padx=10)
        
        def save_user():
            username = username_var.get()
            password = password_var.get()
            role = role_var.get()
            
            if not username or not password:
                self.show_error("خطأ", "الرجاء إدخال اسم المستخدم وكلمة المرور")
                return
            
            success, message = UserModel.add_user(username, password, role)
            if success:
                self.show_info("نجاح", "تمت إضافة المستخدم بنجاح")
                add_window.destroy()
                self.load_users()
            else:
                self.show_error("خطأ", f"فشل إضافة المستخدم: {message}")
        
        self.create_button(add_window, "حفظ", save_user).grid(row=3, column=1, padx=10, pady=20)

    def edit_user(self):
        """تعديل مستخدم"""
        selected = self.users_tree.selection()
        if not selected:
            self.show_warning("تحذير", "الرجاء تحديد مستخدم للتعديل")
            return
        
        user_id = int(self.users_tree.item(selected[0])["values"][0])
        success, user = UserModel.get_user(user_id)
        
        if not success or not user:
            self.show_error("خطأ", "فشل في الحصول على بيانات المستخدم")
            return
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("تعديل مستخدم")
        edit_window.resizable(False, False)
        edit_window.configure(bg="#f5f5f5")
        self.center_window(edit_window, 500, 300)
        
        ttk.Label(edit_window, text="اسم المستخدم:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        username_var = tk.StringVar(value=user["username"])
        ttk.Entry(edit_window, textvariable=username_var, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(edit_window, text="كلمة المرور جديدة:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        password_var = tk.StringVar()
        ttk.Entry(edit_window, textvariable=password_var, width=30, show="*").grid(row=1, column=1, padx=10, pady=10)
        ttk.Label(edit_window, text="(اتركها فارغة للاحتفاظ بنفس كلمة المرور)").grid(row=1, column=2, padx=10, pady=10, sticky="w")
        
        ttk.Label(edit_window, text="الصلاحية:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        role_var = tk.StringVar(value=user["role"])
        role_frame = ttk.Frame(edit_window)
        role_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Radiobutton(role_frame, text="مدير", variable=role_var, value="admin").pack(side="right", padx=10)
        ttk.Radiobutton(role_frame, text="عامل", variable=role_var, value="worker").pack(side="right", padx=10)
        
        def save_changes():
            username = username_var.get()
            password = password_var.get()
            role = role_var.get()
            
            if not username:
                self.show_error("خطأ", "الرجاء إدخال اسم المستخدم")
                return
            
            success, message = UserModel.update_user(user_id, username, password, role)
            if success:
                self.show_info("نجاح", "تم تحديث المستخدم بنجاح")
                edit_window.destroy()
                self.load_users()
            else:
                self.show_error("خطأ", f"فشل تحديث المستخدم: {message}")
        
        self.create_button(edit_window, "حفظ التغييرات", save_changes).grid(row=3, column=1, padx=10, pady=20)

    def delete_user(self):
        """حذف مستخدم"""
        selected = self.users_tree.selection()
        if not selected:
            self.show_warning("تحذير", "الرجاء تحديد مستخدم للحذف")
            return
        
        user_id = int(self.users_tree.item(selected[0])["values"][0])
        username = self.users_tree.item(selected[0])["values"][1]
        
        # التحقق من أن المستخدم ليس نفسه
        if user_id == self.user["id"]:
            self.show_warning("تحذير", "لا يمكنك حذف حسابك الحالي")
            return
        
        if self.confirm("تأكيد الحذف", f"هل أنت متأكد من حذف المستخدم '{username}'؟"):
            success, message = UserModel.delete_user(user_id)
            if success:
                self.show_info("نجاح", "تم حذف المستخدم بنجاح")
                self.load_users()
            else:
                self.show_error("خطأ", f"فشل حذف المستخدم: {message}")
