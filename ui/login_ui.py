import tkinter as tk
from tkinter import ttk, messagebox
from models.user_model import UserModel
from ui.dashboard_ui import Dashboard

class Login:
    def __init__(self, root):
        self.root = root
        
        # ضبط عنوان النافذة
        self.root.title("نظام المبيعات - محل البركة - تسجيل الدخول")
        
        # ضبط حجم النافذة وجعلها في وسط الشاشة
        window_width = 500
        window_height = 350
        
        # الحصول على دقة الشاشة
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # حساب موضع مركز النافذة
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # ضبط حجم وموضع النافذة
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # جعل النافذة ثابتة الحجم
        self.root.resizable(False, False)
        
        # تخصيص مظهر النافذة
        self.root.configure(bg="#f0f0f0")
        
        # محاولة تحميل أيقونة للتطبيق
        try:
            self.root.iconbitmap("assets/store_icon.ico")
        except:
            pass
            
        # تطبيق النمط
        self.apply_style()
        
        # إنشاء واجهة تسجيل الدخول
        self.setup_login_ui()
    
    def apply_style(self):
        # تطبيق نمط وستايل على التطبيق
        style = ttk.Style()
        
        # استخدام السمة clam لمظهر أكثر احترافية
        style.theme_use('clam')
        
        # تخصيص ألوان الأزرار
        style.configure('TButton', background='#4CAF50', foreground='black', font=('Arial', 10))
        style.map('TButton', background=[('active', '#45a049')])
        style.configure('Hover.TButton', background='#45a049')
        
        # تخصيص الإطارات
        style.configure('TFrame', background='#f9f9f9')
        style.configure('TLabel', background='#f9f9f9', font=('Arial', 10))
        style.configure('TEntry', font=('Arial', 10))
        
        # تخصيص العنوان
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        

    
    def setup_login_ui(self):
        # إنشاء إطار رئيسي
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=250)
        
        # شعار المتجر (أو عنوان)
        ttk.Label(main_frame, text="محل البركة", style='Title.TLabel').pack(pady=20)
        
        # إطار المدخلات
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10)
        
        # مدخلات اسم المستخدم وكلمة المرور
        ttk.Label(input_frame, text="اسم المستخدم:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.username_var, width=25).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(input_frame, text="كلمة المرور:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.password_var, show="*", width=25).grid(row=1, column=1, padx=10, pady=10)
        
        # زر تسجيل الدخول
        login_button = ttk.Button(main_frame, text="تسجيل الدخول", command=self.login)
        login_button.pack(pady=15)
        
        # تخصيص زر التسجيل
        def on_enter(e):
            login_button['style'] = 'Hover.TButton'
        def on_leave(e):
            login_button['style'] = 'TButton'
        
        login_button.bind('<Enter>', on_enter)
        login_button.bind('<Leave>', on_leave)
        

        
        # تسجيل حدث الضغط على Enter للقيام بتسجيل الدخول
        self.root.bind('<Return>', lambda event: self.login())
        
        # حقوق النشر أو معلومات الإصدار
        ttk.Label(self.root, text="© 2023 نظام المبيعات - الإصدار 1.0", 
                 font=("Arial", 8)).place(relx=0.5, rely=0.95, anchor=tk.CENTER)
    
    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("خطأ", "الرجاء إدخال اسم المستخدم وكلمة المرور")
            return
        
        success, result = UserModel.authenticate(username, password)
        
        if success:
            self.root.withdraw()  # إخفاء نافذة تسجيل الدخول
            
            # إنشاء نافذة جديدة للوحة التحكم
            dashboard_window = tk.Toplevel()
            dashboard = Dashboard(dashboard_window, result, self.root)
            
            # ضبط عنوان النافذة
            dashboard_window.title(f"نظام المبيعات - محل البركة - {result['username']}")
            
            # إظهار النافذة في كامل الشاشة
            dashboard_window.state('zoomed')
            
            # تعيين حدث الإغلاق
            dashboard_window.protocol("WM_DELETE_WINDOW", lambda: self.on_dashboard_close(dashboard_window))
            
            # محاولة تحميل أيقونة للتطبيق
            try:
                dashboard_window.iconbitmap("assets/store_icon.ico")
            except:
                pass
        else:
            messagebox.showerror("خطأ في تسجيل الدخول", result)
    

    
    def on_dashboard_close(self, dashboard_window):
        dashboard_window.destroy()
        self.root.destroy()