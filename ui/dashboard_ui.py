import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from models.product_model import ProductModel
from models.invoice_model import InvoiceModel
from models.user_model import UserModel
from models.return_model import ReturnModel
import time
from datetime import datetime
import random
import string
import os
import re

class Dashboard:
    def __init__(self, root, user, login_window):
        self.root = root
        self.user = user
        self.login_window = login_window
        
        # ضبط عنوان النافذة الرئيسية
        self.root.title(f"نظام المبيعات - محل البركة - {user['username']} ({user['role']})")
        
        # جعل التطبيق يأخذ الشاشة كاملة
        self.root.state('zoomed')  # هذا الأمر يجعل النافذة بحجم الشاشة كاملة على Windows
        
        # بديل للأنظمة الأخرى في حالة عدم عمل الخاصية السابقة
        self.root.attributes('-fullscreen', False)  # يمكن تغييرها إلى True لملء الشاشة تماما
        
        # تحديد الحد الأدنى لحجم النافذة
        self.root.minsize(1024, 768)
        
        # تخصيص مظهر النافذة
        self.root.configure(bg="#f0f0f0")  # لون خلفية أنيق
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # محاولة تحميل أيقونة للتطبيق
        try:
            self.root.iconbitmap("assets/store_icon.ico")  # ضع ملف الأيقونة في مجلد assets
        except:
            pass
        
        # إنشاء شريط القوائم
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)
        
        # قائمة الملف
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="الملف", menu=file_menu)
        file_menu.add_command(label="تسجيل خروج", command=lambda: self.on_close())
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.login_window.destroy)
        
        # قائمة الإدارة
        manage_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="الإدارة", menu=manage_menu)
        manage_menu.add_command(label="إدارة المنتجات", command=lambda: self.notebook.select(0))
        manage_menu.add_command(label="المبيعات", command=lambda: self.notebook.select(1))
        manage_menu.add_command(label="التقارير", command=lambda: self.notebook.select(2))
        if user['role'] == 'admin':
            manage_menu.add_command(label="إدارة المستخدمين", command=lambda: self.notebook.select(3))
        
        # قائمة المساعدة
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="مساعدة", menu=help_menu)
        help_menu.add_command(label="حول البرنامج", command=self.show_about)
        
        # إنشاء إطار رئيسي
        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # إنشاء علامات التبويب
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # تبويب المنتجات
        self.products_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.products_tab, text="المنتجات")
        self.setup_products_tab()
        
        # تبويب المبيعات
        self.sales_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_tab, text="المبيعات")
        self.setup_sales_tab()
        
        # تبويب المرتجعات
        self.returns_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.returns_tab, text="المرتجعات")
        self.setup_returns_tab()
        
        # تبويب التقارير
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="التقارير")
        self.setup_reports_tab()
        
        # تبويب إدارة المستخدمين (للأدمن فقط)
        if user['role'] == 'admin':
            self.users_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.users_tab, text="إدارة المستخدمين")
            self.setup_users_tab()
        
        # شريط الحالة في الأسفل
        status_frame = ttk.Frame(root)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)
        
        # عرض معلومات المستخدم والوقت في شريط الحالة
        user_label = ttk.Label(status_frame, text=f"المستخدم: {user['username']} | الصلاحية: {'مدير' if user['role'] == 'admin' else 'موظف'}")
        user_label.pack(side="left")
        
        # إضافة عرض للتاريخ والوقت في شريط الحالة
        self.datetime_label = ttk.Label(status_frame, text="")
        self.datetime_label.pack(side="right")
        self.update_datetime(self.datetime_label)
        
        # قائمة المنتجات المضافة للفاتورة
        self.cart_items = []
        
        # تطبيق ستايل موحد لكل النوافذ
        self.apply_style()
    
    def generate_invoice_text(self, invoice_id, customer_name, customer_phone, barcode, invoice_date, cart_items, subtotal, discount, total):
        """إنشاء نص الفاتورة بتنسيق موحد"""
        invoice_text = f"""        ████████ محل البركة ████████
        العنوان: شارع النصر – القاهرة
        الهاتف: 0100-123-4567
+----------------------------------------+
| الاسم: {customer_name:<30} |
| رقم الهاتف: {customer_phone:<26} |
| رقم الفاتورة: {invoice_id:<24} |
| الباركود: {barcode:<28} |
| التاريخ: {invoice_date:<29} |
+----------------------------------------+
| الصنف              | الكمية | السعر  | الإجمالي |
+----------------------------------------+
"""
        # إضافة المنتجات
        for item in cart_items:
            # تنسيق النص مع مراعاة العرض المناسب
            product_line = f"| {item['name']:<18} | {item['quantity']:^6} | {item['price']:>6.2f} | {item['total']:>8.2f} |\n"
            invoice_text += product_line
        
        # إكمال الفاتورة مع تنسيق أفضل
        invoice_text += f"""+----------------------------------------+
| الإجمالي قبل الخصم:           {subtotal:>10.2f} |
| الخصم:                       {discount:>10.2f} |
| الإجمالي بعد الخصم:          {total:>10.2f} |
+----------------------------------------+
         شكراً لتعاملكم معنا!
      للاتصال: 0100-123-4567
"""
        return invoice_text
    
    def save_invoice_as_image(self, invoice_text, invoice_id):
        """حفظ الفاتورة كصورة باستخدام tkinter canvas"""
        # إنشاء نافذة مؤقتة لرسم الفاتورة
        temp_window = tk.Toplevel(self.root)
        temp_window.withdraw()  # إخفاء النافذة
        
        # إنشاء canvas لرسم الفاتورة
        canvas_width = 600
        canvas_height = 800
        canvas = tk.Canvas(temp_window, width=canvas_width, height=canvas_height, bg='white')
        canvas.pack()
        
        # رسم النص على canvas
        lines = invoice_text.split('\n')
        y_position = 20
        line_height = 18
        
        try:
            # استخدام خط مناسب
            font = ("Courier", 10)
            
            for line in lines:
                if line.strip():  # تجاهل الأسطر الفارغة
                    canvas.create_text(10, y_position, text=line, anchor='nw', font=font, fill='black')
                y_position += line_height
            
            # تحديث canvas
            temp_window.update()
            
            # حفظ كملف PostScript ثم تحويله
            ps_file = f"invoice_{invoice_id}.ps"
            canvas.postscript(file=ps_file)
            
            # في حالة عدم وجود مكتبات تحويل الصورة، سيتم حفظ الفاتورة كـ PostScript
            return ps_file
            
        except Exception as e:
            return None
        finally:
            temp_window.destroy()
            
    def create_invoice_canvas_widget(self, parent, invoice_id, customer_name, customer_phone, barcode, invoice_date, cart_items, subtotal, discount, total):
        """إنشاء واجهة الفاتورة الموحدة"""
        # الشعار والترويسة
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(header_frame, text="محل البركة", font=("Arial", 18, "bold")).pack(pady=5)
        ttk.Label(header_frame, text="العنوان: شارع النصر – القاهرة", font=("Arial", 10)).pack()
        ttk.Label(header_frame, text="الهاتف: 0100-123-4567", font=("Arial", 10)).pack(pady=2)
        
        ttk.Separator(parent).pack(fill="x", padx=10, pady=5)
        
        # معلومات الفاتورة
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # استخدام شبكة للمعلومات
        ttk.Label(info_frame, text="الاسم:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=customer_name).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="رقم الهاتف:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=customer_phone).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="رقم الفاتورة:", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=str(invoice_id)).grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="التاريخ:", font=("Arial", 10, "bold")).grid(row=1, column=2, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=invoice_date).grid(row=1, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="الباركود:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(info_frame, text=barcode).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Separator(parent).pack(fill="x", padx=10, pady=5)
        
        # جدول المنتجات
        items_frame = ttk.Frame(parent)
        items_frame.pack(fill="x", padx=10, pady=5)
        
        # عناوين الجدول
        ttk.Label(items_frame, text="الصنف", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(items_frame, text="الكمية", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(items_frame, text="السعر", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(items_frame, text="الإجمالي", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Separator(items_frame, orient="horizontal").grid(row=1, columnspan=4, sticky="ew", padx=5, pady=2)
        
        # إضافة المنتجات للجدول
        for i, item in enumerate(cart_items):
            ttk.Label(items_frame, text=item['name']).grid(row=i+2, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(items_frame, text=str(item['quantity'])).grid(row=i+2, column=1, padx=5, pady=2)
            ttk.Label(items_frame, text=f"{item['price']:.2f}").grid(row=i+2, column=2, padx=5, pady=2)
            ttk.Label(items_frame, text=f"{item['total']:.2f}").grid(row=i+2, column=3, padx=5, pady=2)
        
        ttk.Separator(parent).pack(fill="x", padx=10, pady=5)
        
        # الإجماليات
        totals_frame = ttk.Frame(parent)
        totals_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(totals_frame, text=f"الإجمالي قبل الخصم: {subtotal:.2f} جنيه", font=("Arial", 11, "bold")).pack(anchor="e")
        ttk.Label(totals_frame, text=f"الخصم: {discount:.2f} جنيه", font=("Arial", 11, "bold")).pack(anchor="e")
        ttk.Label(totals_frame, text=f"الإجمالي بعد الخصم: {total:.2f} جنيه", font=("Arial", 12, "bold"), foreground="red").pack(anchor="e")
        
        ttk.Separator(parent).pack(fill="x", padx=10, pady=5)
        
        # الخاتمة
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(footer_frame, text="شكراً لتعاملكم معنا!", font=("Arial", 12, "bold")).pack(pady=2)
        ttk.Label(footer_frame, text="للاتصال: 0100-123-4567", font=("Arial", 10)).pack()
    
    def apply_style(self):
        # تطبيق نمط وستايل على التطبيق
        style = ttk.Style()
        
        # استخدام السمة clam لمظهر أكثر احترافية
        style.theme_use('clam')
        
        # تخصيص ألوان الأزرار
        style.configure('TButton', background='#4CAF50', foreground='black', font=('Arial', 10))
        style.map('TButton', background=[('active', '#45a049')])
        style.configure('Hover.TButton', background='#45a049')
        
        # تخصيص علامات التبويب
        style.configure('TNotebook.Tab', font=('Arial', 11), padding=[12, 5])
        style.map('TNotebook.Tab', background=[('selected', '#e0e0e0')])
        
        # تخصيص الإطارات
        style.configure('TFrame', background='#f9f9f9')
        style.configure('TLabelframe', background='#f9f9f9')
        style.configure('TLabelframe.Label', font=('Arial', 11, 'bold'))

    def update_datetime(self, label):
        # تحديث التاريخ والوقت كل ثانية
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label.config(text=f"التاريخ: {current_time}")
        self.root.after(1000, lambda: self.update_datetime(label))

    def show_about(self):
        # عرض معلومات حول البرنامج
        about_text = """
    نظام المبيعات - محل البركة
    الإصدار 1.0
    
    تم تطويره بواسطة: يوسف
    
    © 2023 جميع الحقوق محفوظة
        """
        messagebox.showinfo("حول البرنامج", about_text)

    def create_button(self, parent, text, command, width=15):
        # إنشاء زر مع تأثيرات
        btn = ttk.Button(parent, text=text, command=command, width=width)
        
        # إضافة تأثيرات عند المرور بالماوس
        def on_enter(e):
            btn['style'] = 'Hover.TButton'
        def on_leave(e):
            btn['style'] = 'TButton'
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def setup_products_tab(self):
        # إطار للأزرار
        buttons_frame = ttk.Frame(self.products_tab)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # أزرار إدارة المنتجات (للأدمن فقط)
        if self.user['role'] == 'admin':
            self.create_button(buttons_frame, "إضافة منتج", self.add_product).pack(side="right", padx=5)
            self.create_button(buttons_frame, "تعديل منتج", self.edit_product).pack(side="right", padx=5)
            self.create_button(buttons_frame, "حذف منتج", self.delete_product).pack(side="right", padx=5)
        
        self.create_button(buttons_frame, "تحديث", self.load_products).pack(side="left", padx=5)
        
        # إطار البحث
        search_frame = ttk.Frame(self.products_tab)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(search_frame, text="بحث:").pack(side="right", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_products())
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side="right", padx=5)
        
        # إنشاء الجدول بالترتيب المطلوب (من اليمين لليسار)
        columns = ("name", "quantity", "price", "total_price", "sold", "profit")
        self.products_tree = ttk.Treeview(self.products_tab, columns=columns, show="headings", selectmode="browse")
        
        # تعيين العناوين
        self.products_tree.heading("name", text="اسم المنتج")
        self.products_tree.heading("quantity", text="العدد المتاح")
        self.products_tree.heading("price", text="سعر القطعة")
        self.products_tree.heading("total_price", text="مجموع الأسعار")
        self.products_tree.heading("sold", text="المباع")
        self.products_tree.heading("profit", text="الربح")
        
        # ضبط أحجام الأعمدة
        self.products_tree.column("name", width=200, anchor="e")  # محاذاة لليمين للعربية
        self.products_tree.column("quantity", width=100, anchor="center")
        self.products_tree.column("price", width=100, anchor="center")
        self.products_tree.column("total_price", width=120, anchor="center")
        self.products_tree.column("sold", width=80, anchor="center")
        self.products_tree.column("profit", width=100, anchor="center")
        
        # إضافة شريط التمرير
        scrollbar = ttk.Scrollbar(self.products_tab, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        # وضع العناصر
        scrollbar.pack(side="left", fill="y")
        self.products_tree.pack(side="right", fill="both", expand=True, padx=10, pady=5)
        
        # تحميل المنتجات
        self.load_products()
    
    def load_products(self):
        # مسح البيانات القديمة
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # تحميل المنتجات
        success, products = ProductModel.get_all_products()
        if success:
            for product in products:
                # حساب إجمالي السعر والربح
                total_price = product["quantity"] * product["price"]
                profit = product.get("sold", 0) * product["price"]
                
                self.products_tree.insert("", "end", values=(
                    product["name"],
                    product["quantity"],
                    f"{product['price']:.2f}",
                    f"{total_price:.2f}",
                    product.get("sold", 0),
                    f"{profit:.2f}"
                ), tags=('product', str(product["id"])))  # نضيف معرف المنتج كوسم
        else:
            messagebox.showerror("خطأ", "فشل في تحميل المنتجات")
    
    def filter_products(self):
        search_term = self.search_var.get().lower()
        
        # مسح البيانات القديمة
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # تحميل المنتجات المفلترة
        success, products = ProductModel.get_all_products()
        if success:
            for product in products:
                if search_term in product["name"].lower():
                    # حساب إجمالي السعر والربح
                    total_price = product["quantity"] * product["price"]
                    profit = product.get("sold", 0) * product["price"]
                    
                    self.products_tree.insert("", "end", values=(
                        product["name"],
                        product["quantity"],
                        f"{product['price']:.2f}",
                        f"{total_price:.2f}",
                        product.get("sold", 0),
                        f"{profit:.2f}"
                    ), tags=('product', str(product["id"])))
    
    def add_product(self):
        if self.user['role'] != 'admin':
            messagebox.showwarning("تنبيه", "ليس لديك صلاحية لإضافة منتجات")
            return
        
        # إنشاء نافذة لإضافة منتج جديد
        add_window = tk.Toplevel(self.root)
        add_window.title("إضافة منتج جديد")
        
        # حجم مناسب للنافذة
        window_width = 500
        window_height = 300
        
        # توسيط النافذة
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        add_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        add_window.resizable(False, False)
        
        # تخصيص مظهر النافذة
        add_window.configure(bg="#f5f5f5")
        
        # المدخلات
        ttk.Label(add_window, text="اسم المنتج:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(add_window, text="السعر:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        price_var = tk.DoubleVar()
        ttk.Entry(add_window, textvariable=price_var, width=30).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(add_window, text="الكمية:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        quantity_var = tk.IntVar()
        ttk.Entry(add_window, textvariable=quantity_var, width=30).grid(row=2, column=1, padx=10, pady=10)
        
        # زر الإضافة
        def save_product():
            try:
                name = name_var.get()
                price = price_var.get()
                quantity = quantity_var.get()
                
                if not name:
                    messagebox.showerror("خطأ", "الرجاء إدخال اسم المنتج")
                    return
                
                if price <= 0:
                    messagebox.showerror("خطأ", "السعر يجب أن يكون أكبر من صفر")
                    return
                
                if quantity < 0:
                    messagebox.showerror("خطأ", "الكمية لا يمكن أن تكون سالبة")
                    return
                
                success, message = ProductModel.add_product(name, price, quantity)
                if success:
                    messagebox.showinfo("نجاح", "تمت إضافة المنتج بنجاح")
                    add_window.destroy()
                    self.load_products()
                else:
                    messagebox.showerror("خطأ", f"فشل إضافة المنتج: {message}")
            
            except ValueError:
                messagebox.showerror("خطأ", "تأكد من إدخال قيم صحيحة للسعر والكمية")
        
        self.create_button(add_window, "حفظ", save_product).grid(row=3, column=1, padx=10, pady=20)
    
    def edit_product(self):
        if self.user['role'] != 'admin':
            messagebox.showwarning("تنبيه", "ليس لديك صلاحية لتعديل المنتجات")
            return
            
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "الرجاء تحديد منتج للتعديل")
            return
        
        # الحصول على معرف المنتج من الوسوم
        item_tags = self.products_tree.item(selected, "tags")
        if not item_tags or len(item_tags) < 2:
            messagebox.showerror("خطأ", "فشل في الحصول على معرف المنتج")
            return
            
        product_id = int(item_tags[1])
        
        # الحصول على بيانات المنتج
        success, product = ProductModel.get_product(product_id)
        
        if not success or not product:
            messagebox.showerror("خطأ", "فشل في الحصول على بيانات المنتج")
            return
        
        # إنشاء نافذة للتعديل
        edit_window = tk.Toplevel(self.root)
        edit_window.title("تعديل منتج")
        
        # حجم مناسب للنافذة
        window_width = 500
        window_height = 300
        
        # توسيط النافذة
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        edit_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        edit_window.resizable(False, False)
        
        # تخصيص مظهر النافذة
        edit_window.configure(bg="#f5f5f5")
        
        # المدخلات
        ttk.Label(edit_window, text="اسم المنتج:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_var = tk.StringVar(value=product["name"])
        ttk.Entry(edit_window, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(edit_window, text="السعر:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        price_var = tk.DoubleVar(value=product["price"])
        ttk.Entry(edit_window, textvariable=price_var, width=30).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(edit_window, text="الكمية:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        quantity_var = tk.IntVar(value=product["quantity"])
        ttk.Entry(edit_window, textvariable=quantity_var, width=30).grid(row=2, column=1, padx=10, pady=10)
        
        # زر الحفظ
        def save_changes():
            try:
                name = name_var.get()
                price = price_var.get()
                quantity = quantity_var.get()
                
                if not name:
                    messagebox.showerror("خطأ", "الرجاء إدخال اسم المنتج")
                    return
                
                if price <= 0:
                    messagebox.showerror("خطأ", "السعر يجب أن يكون أكبر من صفر")
                    return
                
                if quantity < 0:
                    messagebox.showerror("خطأ", "الكمية لا يمكن أن تكون سالبة")
                    return
                
                success, message = ProductModel.update_product(product_id, name, price, quantity)
                if success:
                    messagebox.showinfo("نجاح", "تم تحديث المنتج بنجاح")
                    edit_window.destroy()
                    self.load_products()
                else:
                    messagebox.showerror("خطأ", f"فشل تحديث المنتج: {message}")
            
            except ValueError:
                messagebox.showerror("خطأ", "تأكد من إدخال قيم صحيحة للسعر والكمية")
        
        self.create_button(edit_window, "حفظ التغييرات", save_changes).grid(row=3, column=1, padx=10, pady=20)
    
    def delete_product(self):
        if self.user['role'] != 'admin':
            messagebox.showwarning("تنبيه", "ليس لديك صلاحية لحذف المنتجات")
            return
            
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "الرجاء تحديد منتج للحذف")
            return
        
        # الحصول على معرف المنتج واسمه
        item_tags = self.products_tree.item(selected, "tags")
        if not item_tags or len(item_tags) < 2:
            messagebox.showerror("خطأ", "فشل في الحصول على معرف المنتج")
            return
            
        product_id = int(item_tags[1])
        product_name = self.products_tree.item(selected, "values")[0]
        
        # تأكيد الحذف
        if messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف المنتج '{product_name}'؟"):
            success, message = ProductModel.delete_product(product_id)
            if success:
                messagebox.showinfo("نجاح", "تم حذف المنتج بنجاح")
                self.load_products()
            else:
                messagebox.showerror("خطأ", f"فشل حذف المنتج: {message}")
    
    def setup_sales_tab(self):
        # قسم الصفحة إلى جزأين
        paned = ttk.PanedWindow(self.sales_tab, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # الجزء الأيمن - المنتجات
        right_frame = ttk.LabelFrame(paned, text="المنتجات المتاحة")
        paned.add(right_frame, weight=60)
        
        # إطار البحث
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="بحث:").pack(side="right", padx=5)
        self.sales_search_var = tk.StringVar()
        self.sales_search_var.trace("w", lambda name, index, mode: self.filter_sales_products())
        ttk.Entry(search_frame, textvariable=self.sales_search_var, width=25).pack(side="right", padx=5)
        
        # جدول المنتجات
        columns = ("id", "name", "price", "quantity")
        self.sales_products_tree = ttk.Treeview(right_frame, columns=columns, show="headings", selectmode="browse")
        
        self.sales_products_tree.heading("id", text="المعرف")
        self.sales_products_tree.heading("name", text="اسم المنتج")
        self.sales_products_tree.heading("price", text="السعر")
        self.sales_products_tree.heading("quantity", text="المتاح")
        
        self.sales_products_tree.column("id", width=50, anchor="center")
        self.sales_products_tree.column("name", width=150, anchor="e")  # محاذاة لليمين للعربية
        self.sales_products_tree.column("price", width=80, anchor="center")
        self.sales_products_tree.column("quantity", width=80, anchor="center")
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.sales_products_tree.yview)
        self.sales_products_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="left", fill="y")
        self.sales_products_tree.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # إطار إضافة للسلة
        add_to_cart_frame = ttk.Frame(right_frame)
        add_to_cart_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(add_to_cart_frame, text="الكمية:").pack(side="right", padx=5)
        self.quantity_var = tk.IntVar(value=1)
        ttk.Spinbox(add_to_cart_frame, from_=1, to=1000, textvariable=self.quantity_var, width=5).pack(side="right", padx=5)
        self.create_button(add_to_cart_frame, "إضافة للسلة", self.add_to_cart).pack(side="left", padx=5)
        
        # الجزء الأيسر - السلة
        left_frame = ttk.LabelFrame(paned, text="سلة المشتريات")
        paned.add(left_frame, weight=40)
        
        # جدول السلة
        columns = ("id", "name", "price", "quantity", "total")
        self.cart_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        self.cart_tree.heading("id", text="المعرف")
        self.cart_tree.heading("name", text="اسم المنتج")
        self.cart_tree.heading("price", text="السعر")
        self.cart_tree.heading("quantity", text="الكمية")
        self.cart_tree.heading("total", text="الإجمالي")
        
        self.cart_tree.column("id", width=50, anchor="center")
        self.cart_tree.column("name", width=120, anchor="e")  # محاذاة لليمين للعربية
        self.cart_tree.column("price", width=60, anchor="center")
        self.cart_tree.column("quantity", width=60, anchor="center")
        self.cart_tree.column("total", width=80, anchor="center")
        
        # شريط التمرير
        cart_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        cart_scrollbar.pack(side="left", fill="y")
        self.cart_tree.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # إطار الإجراءات والخصم والإجمالي
        actions_frame = ttk.Frame(left_frame)
        actions_frame.pack(fill="x", padx=5, pady=5)
        
        # حذف منتج من السلة
        self.create_button(actions_frame, "حذف من السلة", self.remove_from_cart).pack(side="right", padx=5)
        
        # إطار الخصم والإجمالي
        totals_frame = ttk.Frame(left_frame)
        totals_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(totals_frame, text="الخصم:").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.discount_var = tk.DoubleVar(value=0)
        discount_entry = ttk.Entry(totals_frame, textvariable=self.discount_var, width=10)
        discount_entry.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        discount_entry.bind("<KeyRelease>", lambda event: self.update_total())
        
        ttk.Label(totals_frame, text="الإجمالي:").grid(row=1, column=1, padx=5, pady=5, sticky="e")
        self.total_var = tk.StringVar(value="0.00")
        ttk.Label(totals_frame, textvariable=self.total_var, font=("Arial", 12, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        
        # زر إتمام البيع
        self.create_button(left_frame, "إتمام البيع وطباعة الفاتورة", self.complete_sale, width=30).pack(fill="x", padx=5, pady=10)
        
        # تحميل المنتجات
        self.load_sales_products()
    
    def load_sales_products(self):
        # مسح البيانات القديمة
        for item in self.sales_products_tree.get_children():
            self.sales_products_tree.delete(item)
        
        # تحميل المنتجات المتاحة فقط (الكمية > 0)
        success, products = ProductModel.get_available_products()
        if success:
            for product in products:
                self.sales_products_tree.insert("", "end", values=(
                    product["id"],
                    product["name"],
                    f"{product['price']:.2f}",
                    product["quantity"]
                ))
    
    def filter_sales_products(self):
        search_term = self.sales_search_var.get().lower()
        
        # مسح البيانات القديمة
        for item in self.sales_products_tree.get_children():
            self.sales_products_tree.delete(item)
        
        # تحميل المنتجات المفلترة
        success, products = ProductModel.get_available_products()
        if success:
            for product in products:
                if search_term in product["name"].lower():
                    self.sales_products_tree.insert("", "end", values=(
                        product["id"],
                        product["name"],
                        f"{product['price']:.2f}",
                        product["quantity"]
                    ))
    
    def add_to_cart(self):
        selected = self.sales_products_tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "الرجاء تحديد منتج للإضافة")
            return
        
        # الحصول على المنتج المحدد
        product_id = int(self.sales_products_tree.item(selected[0])["values"][0])
        product_name = self.sales_products_tree.item(selected[0])["values"][1]
        product_price = float(self.sales_products_tree.item(selected[0])["values"][2])
        available_quantity = int(self.sales_products_tree.item(selected[0])["values"][3])
        
        # التحقق من الكمية
        quantity = self.quantity_var.get()
        if quantity <= 0:
            messagebox.showerror("خطأ", "يجب أن تكون الكمية أكبر من صفر")
            return
        
        if quantity > available_quantity:
            messagebox.showerror("خطأ", f"الكمية المتاحة هي {available_quantity} فقط")
            return
        
        # التحقق إذا كان المنتج موجود بالفعل في السلة
        for item in self.cart_items:
            if item["product_id"] == product_id:
                new_quantity = item["quantity"] + quantity
                if new_quantity > available_quantity:
                    messagebox.showerror("خطأ", f"الكمية المتاحة هي {available_quantity} فقط")
                    return
                
                item["quantity"] = new_quantity
                item["total"] = round(new_quantity * item["price"], 2)  # تقريب لرقمين عشريين
                self.refresh_cart()
                self.update_total()
                return
        
        # إضافة المنتج للسلة
        item = {
            "product_id": product_id,
            "name": product_name,
            "price": product_price,
            "quantity": quantity,
            "total": round(quantity * product_price, 2)  # تقريب لرقمين عشريين
        }
        
        self.cart_items.append(item)
        self.refresh_cart()
        self.update_total()
    
    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "الرجاء تحديد منتج للحذف من السلة")
            return
        
        # الحصول على المنتج المحدد
        item_id = int(self.cart_tree.item(selected[0])["values"][0])
        
        # حذف المنتج من السلة
        self.cart_items = [item for item in self.cart_items if item["product_id"] != item_id]
        self.refresh_cart()
        self.update_total()
    
    def refresh_cart(self):
        # مسح البيانات القديمة
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # إضافة المنتجات للجدول
        for item in self.cart_items:
            self.cart_tree.insert("", "end", values=(
                item["product_id"],
                item["name"],
                f"{item['price']:.2f}",
                item["quantity"],
                f"{item['total']:.2f}"
            ))
    
    def update_total(self):
        # حساب إجمالي الفاتورة بشكل صحيح
        subtotal = sum(item["total"] for item in self.cart_items)
        
        # الحصول على قيمة الخصم
        try:
            discount = float(self.discount_var.get())
            if discount < 0:
                discount = 0
                self.discount_var.set(0)
        except:
            discount = 0
            self.discount_var.set(0)
        
        # التأكد من أن الخصم لا يتجاوز قيمة الفاتورة
        if discount > subtotal:
            discount = subtotal
            self.discount_var.set(subtotal)
        
        # حساب الإجمالي بعد الخصم
        total = subtotal - discount
        self.total_var.set(f"{total:.2f}")

    def complete_sale(self):
        if not self.cart_items:
            messagebox.showwarning("تحذير", "السلة فارغة")
            return
        
        # بدلاً من نافذة بيانات المشتري، نستخدم نمط أبسط
        customer_name = simpledialog.askstring("بيانات المشتري", "اسم المشتري:", parent=self.root)
        if customer_name is None:  # إذا قام المستخدم بالإلغاء
            return
            
        customer_phone = simpledialog.askstring("بيانات المشتري", "رقم الهاتف:", parent=self.root)
        if customer_phone is None:  # إذا قام المستخدم بالإلغاء
            return
        
        try:
            # حساب المجموع
            subtotal = sum(item["total"] for item in self.cart_items)
            discount = self.discount_var.get()
            total = subtotal - discount
            
            # إنشاء رقم فاتورة ورمز باركود
            invoice_id = int(time.time())
            barcode = "#" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            invoice_date = datetime.now().strftime("%Y-%m-%d")
            
            # إنشاء نص الفاتورة باستخدام الدالة الموحدة
            invoice_text = self.generate_invoice_text(
                invoice_id, customer_name, customer_phone, barcode, 
                invoice_date, self.cart_items, subtotal, discount, total
            )
            
            # تحديث كميات المنتجات
            for item in self.cart_items:
                try:
                    success, message = ProductModel.update_product_quantity(item["product_id"], item["quantity"])
                    if not success:
                        messagebox.showwarning("تحذير", f"فشل تحديث كمية المنتج {item['name']}: {message}")
                except Exception as e:
                    messagebox.showwarning("تحذير", f"خطأ في تحديث كمية المنتج {item['name']}: {str(e)}")
            
            # حفظ الفاتورة في ملف نصي (للنسخة الاحتياطية)
            filename = f"invoice_{invoice_id}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(invoice_text)
            
            # عرض الفاتورة في نافذة محسنة
            invoice_window = tk.Toplevel(self.root)
            invoice_window.title(f"فاتورة رقم {invoice_id}")
            
            # حجم مناسب للنافذة
            window_width = int(self.root.winfo_width() * 0.7)
            window_height = int(self.root.winfo_height() * 0.9)
            
            # توسيط النافذة
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            center_x = int(screen_width/2 - window_width/2)
            center_y = int(screen_height/2 - window_height/2)
            
            invoice_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
            invoice_window.minsize(500, 650)
            
            # تخصيص مظهر النافذة
            invoice_window.configure(bg="#f5f5f5")
            
            # إنشاء إطار للنص مع شريط تمرير
            main_frame = ttk.Frame(invoice_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # استخدام Canvas لتوفير تجربة مستخدم أفضل وأكثر استجابة
            canvas = tk.Canvas(main_frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            
            # ربط الـ Canvas بشريط التمرير
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # وضع عناصر التخطيط
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # إطار داخل الـ Canvas للمحتوى
            content_frame = ttk.Frame(canvas)
            canvas.create_window((0, 0), window=content_frame, anchor="nw")
            
            # الشعار والترويسة
            header_frame = ttk.Frame(content_frame)
            header_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(header_frame, text="محل البركة", font=("Arial", 18, "bold")).pack(pady=5)
            ttk.Label(header_frame, text="العنوان: شارع النصر – القاهرة", font=("Arial", 10)).pack()
            ttk.Label(header_frame, text="الهاتف: 0100-123-4567", font=("Arial", 10)).pack(pady=2)
            
            ttk.Separator(content_frame).pack(fill="x", padx=10, pady=5)
            
            # معلومات الفاتورة
            info_frame = ttk.Frame(content_frame)
            info_frame.pack(fill="x", padx=10, pady=5)
            
            # استخدام شبكة للمعلومات
            ttk.Label(info_frame, text="الاسم:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="e", padx=5, pady=2)
            ttk.Label(info_frame, text=customer_name).grid(row=0, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="رقم الهاتف:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="e", padx=5, pady=2)
            ttk.Label(info_frame, text=customer_phone).grid(row=1, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="رقم الفاتورة:", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="e", padx=5, pady=2)
            ttk.Label(info_frame, text=str(invoice_id)).grid(row=0, column=3, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="التاريخ:", font=("Arial", 10, "bold")).grid(row=1, column=2, sticky="e", padx=5, pady=2)
            ttk.Label(info_frame, text=invoice_date).grid(row=1, column=3, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="الباركود:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="e", padx=5, pady=2)
            ttk.Label(info_frame, text=barcode).grid(row=2, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Separator(content_frame).pack(fill="x", padx=10, pady=5)
            
            # جدول المنتجات
            items_frame = ttk.Frame(content_frame)
            items_frame.pack(fill="x", padx=10, pady=5)
            
            # عناوين الجدول
            ttk.Label(items_frame, text="الصنف", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(items_frame, text="الكمية", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=2)
            ttk.Label(items_frame, text="السعر", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=2)
            ttk.Label(items_frame, text="الإجمالي", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=2)
            
            ttk.Separator(items_frame, orient="horizontal").grid(row=1, columnspan=4, sticky="ew", padx=5, pady=2)
            
            # إضافة المنتجات للجدول
            for i, item in enumerate(self.cart_items):
                ttk.Label(items_frame, text=item['name']).grid(row=i+2, column=0, padx=5, pady=2, sticky="w")
                ttk.Label(items_frame, text=str(item['quantity'])).grid(row=i+2, column=1, padx=5, pady=2)
                ttk.Label(items_frame, text=f"{item['price']:.2f}").grid(row=i+2, column=2, padx=5, pady=2)
                ttk.Label(items_frame, text=f"{item['total']:.2f}").grid(row=i+2, column=3, padx=5, pady=2)
            
            ttk.Separator(content_frame).pack(fill="x", padx=10, pady=5)
            
            # إجماليات
            totals_frame = ttk.Frame(content_frame)
            totals_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(totals_frame, text="الإجمالي قبل الخصم:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky="e")
            ttk.Label(totals_frame, text=f"{subtotal:.2f}").grid(row=0, column=1, padx=5, pady=2, sticky="w")
            
            ttk.Label(totals_frame, text="الخصم:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=2, sticky="e")
            ttk.Label(totals_frame, text=f"{discount:.2f}").grid(row=1, column=1, padx=5, pady=2, sticky="w")
            
            ttk.Label(totals_frame, text="الإجمالي بعد الخصم:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=2, sticky="e")
            ttk.Label(totals_frame, text=f"{total:.2f}", font=("Arial", 12, "bold")).grid(row=2, column=1, padx=5, pady=2, sticky="w")
            
            ttk.Separator(content_frame).pack(fill="x", padx=10, pady=5)
            
            # تذييل
            footer_frame = ttk.Frame(content_frame)
            footer_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(footer_frame, text="شكراً لتعاملكم معنا!", font=("Arial", 12, "bold")).pack(pady=2)
            ttk.Label(footer_frame, text="للاتصال: 0100-123-4567").pack()
            
            # تحديث حجم المنطقة القابلة للتمرير
            content_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            
            # تفعيل التمرير باستخدام عجلة الماوس
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # إطار الأزرار
            button_frame = ttk.Frame(invoice_window)
            button_frame.pack(fill="x", padx=10, pady=10)
            
            # زر لحفظ الفاتورة
            def save_invoice():
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".ps",
                    initialfile=f"فاتورة_{invoice_id}.ps",
                    filetypes=[("PostScript files", "*.ps"), ("Text files", "*.txt"), ("All files", "*.*")]
                )
                if save_path:
                    try:
                        if save_path.endswith('.ps'):
                            # حفظ كصورة باستخدام postscript
                            content_frame.update()
                            canvas.postscript(file=save_path)
                            messagebox.showinfo("حفظ الفاتورة", f"تم حفظ الفاتورة كصورة في:\n{save_path}")
                        else:
                            # حفظ كنص
                            with open(save_path, "w", encoding="utf-8") as f:
                                f.write(invoice_text)
                            messagebox.showinfo("حفظ الفاتورة", f"تم حفظ الفاتورة كنص في:\n{save_path}")
                    except Exception as e:
                        messagebox.showerror("خطأ", f"فشل حفظ الفاتورة: {str(e)}")
            
            # طباعة الفاتورة (محاكاة فقط)
            def print_invoice():
                messagebox.showinfo("طباعة الفاتورة", "تم إرسال الفاتورة للطباعة")
            
            # إلغاء الربط عند إغلاق النافذة
            def on_closing():
                canvas.unbind_all("<MouseWheel>")
                invoice_window.destroy()
            
            self.create_button(button_frame, "حفظ الفاتورة", save_invoice).pack(side="left", padx=5)
            self.create_button(button_frame, "طباعة", print_invoice).pack(side="left", padx=5)
            self.create_button(button_frame, "إغلاق", on_closing).pack(side="right", padx=5)
            
            invoice_window.protocol("WM_DELETE_WINDOW", on_closing)
            
            # مسح السلة
            self.cart_items = []
            self.refresh_cart()
            self.update_total()
            self.discount_var.set(0)
            
            # تحديث المنتجات
            self.load_sales_products()
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إتمام عملية البيع: {str(e)}")

    def print_invoice(self, invoice_id):
        # الحصول على تفاصيل الفاتورة
        success, invoice = InvoiceModel.get_invoice(invoice_id)
        
        if not success:
            messagebox.showerror("خطأ", f"فشل في الحصول على تفاصيل الفاتورة: {invoice}")
            return
        
        # فقط قم بحفظ الفاتورة في ملف نصي بدون محاولة عرضها في نافذة جديدة
        filename = f"invoice_{invoice_id}_{int(time.time())}.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=" * 50 + "\n")
                f.write("نظام المبيعات - فاتورة\n")
                f.write("=" * 50 + "\n\n")
                
                # معلومات الفاتورة
                f.write(f"رقم الفاتورة: {invoice_id}\n")
                f.write(f"التاريخ: {invoice['created_at']}\n")
                f.write(f"الموظف: {self.user['username']}\n\n")
                
                # معلومات المشتري
                if invoice.get('customer_name') or invoice.get('customer_phone'):
                    f.write("معلومات المشتري:\n")
                    if invoice.get('customer_name'):
                        f.write(f"الاسم: {invoice['customer_name']}\n")
                    if invoice.get('customer_phone'):
                        f.write(f"رقم الهاتف: {invoice['customer_phone']}\n")
                    f.write("\n")
                
                # المنتجات
                f.write("المنتجات:\n")
                f.write("-" * 50 + "\n")
                f.write(f"{'اسم المنتج':<25} {'السعر':>10} {'الكمية':>10} {'الإجمالي':>10}\n")
                
                for item in invoice["items"]:
                    f.write(f"{item['name']:<25} {item['price']:>10.2f} {item['quantity']:>10} {item['item_total']:>10.2f}\n")
                
                f.write("=" * 50 + "\n")
                f.write(f"إجمالي الفاتورة: {invoice['subtotal']:.2f}\n")
                f.write(f"الخصم: {invoice['discount']:.2f}\n")
                f.write(f"المبلغ المطلوب: {invoice['total']:.2f}\n")
            
            # عرض رسالة نجاح وإظهار رقم الفاتورة فقط
            messagebox.showinfo("تمت العملية بنجاح", 
                            f"تم إنشاء الفاتورة رقم {invoice_id} بنجاح\n"
                            f"وتم حفظها في الملف: {filename}\n\n"
                            f"الإجمالي: {invoice['total']:.2f}")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حفظ الفاتورة: {str(e)}")

    def setup_returns_tab(self):
        """إعداد تبويب المرتجعات"""
        returns_frame = ttk.Frame(self.returns_tab)
        returns_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # العنوان
        ttk.Label(returns_frame, text="إدارة المرتجعات", font=("Arial", 16, "bold")).pack(pady=10)
        
        # إطار الأزرار العلوية
        top_buttons_frame = ttk.Frame(returns_frame)
        top_buttons_frame.pack(fill="x", pady=5)
        
        self.create_button(top_buttons_frame, "إرجاع منتجات", self.open_return_dialog).pack(side="right", padx=5)
        self.create_button(top_buttons_frame, "تحديث القائمة", self.load_returns).pack(side="left", padx=5)
        
        # إطار البحث
        search_frame = ttk.Frame(returns_frame)
        search_frame.pack(fill="x", pady=5)
        
        ttk.Label(search_frame, text="بحث برقم الفاتورة:").pack(side="right", padx=5)
        self.return_search_var = tk.StringVar()
        self.return_search_var.trace("w", lambda name, index, mode: self.filter_returns())
        ttk.Entry(search_frame, textvariable=self.return_search_var, width=30).pack(side="right", padx=5)
        
        # جدول المرتجعات
        columns = ("return_id", "original_invoice", "customer_name", "return_code", "amount", "date", "user")
        self.returns_tree = ttk.Treeview(returns_frame, columns=columns, show="headings", selectmode="browse")
        
        # تعيين العناوين
        self.returns_tree.heading("return_id", text="رقم الإرجاع")
        self.returns_tree.heading("original_invoice", text="رقم الفاتورة الأصلية")
        self.returns_tree.heading("customer_name", text="اسم العميل")
        self.returns_tree.heading("return_code", text="رمز الإرجاع")
        self.returns_tree.heading("amount", text="مبلغ الإرجاع")
        self.returns_tree.heading("date", text="التاريخ")
        self.returns_tree.heading("user", text="المستخدم")
        
        # تعيين عرض الأعمدة
        self.returns_tree.column("return_id", width=80, anchor="center")
        self.returns_tree.column("original_invoice", width=120, anchor="center")
        self.returns_tree.column("customer_name", width=150, anchor="e")
        self.returns_tree.column("return_code", width=100, anchor="center")
        self.returns_tree.column("amount", width=100, anchor="center")
        self.returns_tree.column("date", width=120, anchor="center")
        self.returns_tree.column("user", width=100, anchor="center")
        
        # شريط التمرير للجدول
        returns_scrollbar = ttk.Scrollbar(returns_frame, orient="vertical", command=self.returns_tree.yview)
        self.returns_tree.configure(yscrollcommand=returns_scrollbar.set)
        
        # وضع الجدول وشريط التمرير
        returns_scrollbar.pack(side="left", fill="y")
        self.returns_tree.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # ربط أحداث النقر المزدوج
        self.returns_tree.bind("<Double-1>", self.view_return_details)
        
        # تحميل البيانات
        self.load_returns()
    
    def load_returns(self):
        """تحميل قائمة المرتجعات"""
        # مسح البيانات الحالية
        for item in self.returns_tree.get_children():
            self.returns_tree.delete(item)
        
        # الحصول على المرتجعات
        success, returns = ReturnModel.get_all_returns()
        
        if success:
            for ret in returns:
                # إضافة المرتجع إلى الجدول
                self.returns_tree.insert("", "end", values=(
                    ret["id"],
                    ret["original_invoice_id"],
                    ret["customer_name"],
                    ret["return_code"],
                    f"{ret['total_return_amount']:.2f}",
                    ret["created_at"][:10],  # عرض التاريخ فقط
                    ret["username"]
                ))
        else:
            messagebox.showerror("خطأ", f"فشل في تحميل المرتجعات: {returns}")
    
    def filter_returns(self):
        """فلترة المرتجعات حسب رقم الفاتورة"""
        search_term = self.return_search_var.get().lower()
        
        # مسح البيانات الحالية
        for item in self.returns_tree.get_children():
            self.returns_tree.delete(item)
        
        # الحصول على المرتجعات
        success, returns = ReturnModel.get_all_returns()
        
        if success:
            for ret in returns:
                # التحقق من مطابقة البحث
                if (search_term == "" or 
                    search_term in str(ret["original_invoice_id"]) or
                    search_term in ret["customer_name"].lower() or
                    search_term in ret["return_code"].lower()):
                    
                    self.returns_tree.insert("", "end", values=(
                        ret["id"],
                        ret["original_invoice_id"],
                        ret["customer_name"],
                        ret["return_code"],
                        f"{ret['total_return_amount']:.2f}",
                        ret["created_at"][:10],
                        ret["username"]
                    ))
    
    def open_return_dialog(self):
        """فتح نافذة إرجاع المنتجات"""
        return_window = tk.Toplevel(self.root)
        return_window.title("إرجاع منتجات")
        return_window.geometry("800x600")
        return_window.transient(self.root)
        return_window.grab_set()
        
        # العنوان
        ttk.Label(return_window, text="إرجاع منتجات من فاتورة سابقة", font=("Arial", 14, "bold")).pack(pady=10)
        
        # إطار البحث عن الفاتورة
        search_frame = ttk.LabelFrame(return_window, text="البحث عن الفاتورة")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(search_frame, text="رقم الفاتورة:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        invoice_id_var = tk.StringVar()
        invoice_entry = ttk.Entry(search_frame, textvariable=invoice_id_var, width=20)
        invoice_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def search_invoice():
            invoice_id = invoice_id_var.get().strip()
            if not invoice_id:
                messagebox.showwarning("تحذير", "الرجاء إدخال رقم الفاتورة")
                return
            
            try:
                invoice_id = int(invoice_id)
                success, invoice = InvoiceModel.get_invoice(invoice_id)
                
                if success:
                    # عرض تفاصيل الفاتورة
                    self.display_invoice_for_return(return_window, invoice)
                else:
                    messagebox.showerror("خطأ", f"لم يتم العثور على الفاتورة: {invoice}")
            except ValueError:
                messagebox.showerror("خطأ", "رقم الفاتورة غير صحيح")
        
        ttk.Button(search_frame, text="بحث", command=search_invoice).grid(row=0, column=2, padx=5, pady=5)
        
        # التركيز على مربع النص
        invoice_entry.focus()
        return_window.bind('<Return>', lambda e: search_invoice())
    
    def display_invoice_for_return(self, parent_window, invoice):
        """عرض تفاصيل الفاتورة لاختيار المنتجات المراد إرجاعها"""
        # مسح المحتوى السابق إن وجد
        for widget in parent_window.winfo_children():
            if isinstance(widget, ttk.Frame) and widget.winfo_name() != 'search_frame':
                widget.destroy()
        
        # إطار تفاصيل الفاتورة
        details_frame = ttk.LabelFrame(parent_window, text="تفاصيل الفاتورة")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(details_frame, text=f"رقم الفاتورة: {invoice['id']}").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_frame, text=f"العميل: {invoice['customer_name']}").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(details_frame, text=f"التاريخ: {invoice['created_at'][:10]}").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_frame, text=f"الإجمالي: {invoice['total']:.2f} جنيه").grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # إطار المنتجات
        items_frame = ttk.LabelFrame(parent_window, text="المنتجات - اختر المنتجات المراد إرجاعها")
        items_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # جدول المنتجات مع checkboxes
        columns = ("select", "name", "price", "original_qty", "return_qty")
        items_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=8)
        
        items_tree.heading("select", text="اختيار")
        items_tree.heading("name", text="اسم المنتج")
        items_tree.heading("price", text="السعر")
        items_tree.heading("original_qty", text="الكمية الأصلية")
        items_tree.heading("return_qty", text="كمية الإرجاع")
        
        items_tree.column("select", width=60, anchor="center")
        items_tree.column("name", width=200, anchor="e")
        items_tree.column("price", width=100, anchor="center")
        items_tree.column("original_qty", width=100, anchor="center")
        items_tree.column("return_qty", width=120, anchor="center")
        
        # إضافة المنتجات
        return_items = []
        for item in invoice['items']:
            item_id = items_tree.insert("", "end", values=(
                "☐", item['name'], f"{item['price']:.2f}", 
                item['quantity'], "0"
            ))
            return_items.append({
                'tree_id': item_id,
                'product_id': item['product_id'],
                'name': item['name'],
                'price': item['price'],
                'original_quantity': item['quantity'],
                'return_quantity': 0,
                'selected': False
            })
        
        def on_item_click(event):
            """التعامل مع النقر على المنتج"""
            item_id = items_tree.selection()[0] if items_tree.selection() else None
            if item_id:
                # العثور على المنتج المقابل
                for i, ret_item in enumerate(return_items):
                    if ret_item['tree_id'] == item_id:
                        # تبديل حالة الاختيار
                        return_items[i]['selected'] = not return_items[i]['selected']
                        
                        # تحديث العرض
                        current_values = list(items_tree.item(item_id, 'values'))
                        current_values[0] = "☑" if return_items[i]['selected'] else "☐"
                        
                        # إذا تم اختيار المنتج، اطلب كمية الإرجاع
                        if return_items[i]['selected']:
                            qty_dialog = simpledialog.askinteger(
                                "كمية الإرجاع",
                                f"كم قطعة تريد إرجاعها من '{ret_item['name']}'؟\n"
                                f"الكمية الأصلية: {ret_item['original_quantity']}",
                                minvalue=1,
                                maxvalue=ret_item['original_quantity']
                            )
                            if qty_dialog:
                                return_items[i]['return_quantity'] = qty_dialog
                                current_values[4] = str(qty_dialog)
                            else:
                                return_items[i]['selected'] = False
                                current_values[0] = "☐"
                                current_values[4] = "0"
                        else:
                            return_items[i]['return_quantity'] = 0
                            current_values[4] = "0"
                        
                        items_tree.item(item_id, values=current_values)
                        break
        
        items_tree.bind("<Button-1>", on_item_click)
        
        # شريط تمرير للجدول
        items_scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=items_tree.yview)
        items_tree.configure(yscrollcommand=items_scrollbar.set)
        
        items_scrollbar.pack(side="left", fill="y")
        items_tree.pack(side="right", fill="both", expand=True)
        
        # إطار الأزرار
        buttons_frame = ttk.Frame(parent_window)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        def process_return():
            """معالجة عملية الإرجاع"""
            selected_items = [item for item in return_items if item['selected'] and item['return_quantity'] > 0]
            
            if not selected_items:
                messagebox.showwarning("تحذير", "الرجاء اختيار منتجات للإرجاع")
                return
            
            # حساب إجمالي مبلغ الإرجاع
            total_return = sum(item['price'] * item['return_quantity'] for item in selected_items)
            
            # إنشاء رمز الإرجاع
            return_code = "#R" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # إنشاء عملية الإرجاع
            success, result = ReturnModel.create_return(
                user_id=self.user['id'],
                original_invoice_id=invoice['id'],
                customer_name=invoice['customer_name'],
                customer_phone=invoice['customer_phone'],
                return_code=return_code,
                items=[{
                    'product_id': item['product_id'],
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': item['return_quantity'],
                    'total': item['price'] * item['return_quantity']
                } for item in selected_items],
                total_return_amount=total_return
            )
            
            if success:
                # تحديث كميات المنتجات في المخزون
                for item in selected_items:
                    # إضافة الكمية المرتجعة إلى المخزون
                    ProductModel.add_product_quantity(item['product_id'], item['return_quantity'])
                
                messagebox.showinfo("نجح الإرجاع", 
                                  f"تم إرجاع المنتجات بنجاح\n"
                                  f"رمز الإرجاع: {return_code}\n"
                                  f"مبلغ الإرجاع: {total_return:.2f} جنيه")
                
                # إغلاق النافذة وتحديث القائمة
                parent_window.destroy()
                self.load_returns()
                self.load_products()  # تحديث قائمة المنتجات
            else:
                messagebox.showerror("خطأ", f"فشل في إتمام عملية الإرجاع: {result}")
        
        ttk.Button(buttons_frame, text="تأكيد الإرجاع", command=process_return).pack(side="right", padx=5)
        ttk.Button(buttons_frame, text="إلغاء", command=parent_window.destroy).pack(side="right", padx=5)
    
    def view_return_details(self, event):
        """عرض تفاصيل عملية إرجاع"""
        selected_item = self.returns_tree.selection()
        if not selected_item:
            return
        
        return_id = self.returns_tree.item(selected_item[0], 'values')[0]
        
        success, return_data = ReturnModel.get_return(int(return_id))
        
        if success:
            # إنشاء نافذة عرض التفاصيل
            details_window = tk.Toplevel(self.root)
            details_window.title(f"تفاصيل إرجاع رقم {return_id}")
            details_window.geometry("600x500")
            details_window.transient(self.root)
            
            # إطار المحتوى
            main_frame = ttk.Frame(details_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # معلومات الإرجاع
            info_frame = ttk.LabelFrame(main_frame, text="معلومات الإرجاع")
            info_frame.pack(fill="x", pady=5)
            
            ttk.Label(info_frame, text=f"رقم الإرجاع: {return_data['id']}").grid(row=0, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(info_frame, text=f"رقم الفاتورة الأصلية: {return_data['original_invoice_id']}").grid(row=0, column=1, padx=5, pady=2, sticky="w")
            ttk.Label(info_frame, text=f"العميل: {return_data['customer_name']}").grid(row=1, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(info_frame, text=f"رمز الإرجاع: {return_data['return_code']}").grid(row=1, column=1, padx=5, pady=2, sticky="w")
            ttk.Label(info_frame, text=f"التاريخ: {return_data['created_at']}").grid(row=2, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(info_frame, text=f"المستخدم: {return_data['username']}").grid(row=2, column=1, padx=5, pady=2, sticky="w")
            
            # المنتجات المرتجعة
            items_frame = ttk.LabelFrame(main_frame, text="المنتجات المرتجعة")
            items_frame.pack(fill="both", expand=True, pady=5)
            
            columns = ("name", "price", "quantity", "total")
            items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
            
            items_tree.heading("name", text="اسم المنتج")
            items_tree.heading("price", text="السعر")
            items_tree.heading("quantity", text="الكمية")
            items_tree.heading("total", text="الإجمالي")
            
            for item in return_data['items']:
                items_tree.insert("", "end", values=(
                    item['name'],
                    f"{item['price']:.2f}",
                    item['quantity'],
                    f"{item['total']:.2f}"
                ))
            
            items_tree.pack(fill="both", expand=True, padx=5, pady=5)
            
            # الإجمالي
            total_frame = ttk.Frame(main_frame)
            total_frame.pack(fill="x", pady=5)
            
            ttk.Label(total_frame, text=f"إجمالي مبلغ الإرجاع: {return_data['total_return_amount']:.2f} جنيه", 
                     font=("Arial", 12, "bold"), foreground="red").pack(anchor="e")
            
            # زر الإغلاق
            ttk.Button(main_frame, text="إغلاق", command=details_window.destroy).pack(pady=10)
        else:
            messagebox.showerror("خطأ", f"فشل في الحصول على تفاصيل الإرجاع: {return_data}")

    def setup_reports_tab(self):
        reports_frame = ttk.Frame(self.reports_tab)
        reports_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(reports_frame, text="التقارير", font=("Arial", 16, "bold")).pack(pady=20)
        
        # إجمالي المبيعات
        buttons_frame = ttk.Frame(reports_frame)
        buttons_frame.pack(pady=30)
        
        self.create_button(buttons_frame, "تقرير المبيعات اليومي", self.show_daily_sales, width=25).pack(pady=15)
        self.create_button(buttons_frame, "تقرير المنتجات الأكثر مبيعاً", self.show_top_products, width=25).pack(pady=15)
        self.create_button(buttons_frame, "تقرير المخزون المنخفض", self.show_low_stock, width=25).pack(pady=15)
    
    def show_daily_sales(self):
        try:
            # بدلاً من الاعتماد على InvoiceModel.get_daily_sales() سنقوم بقراءة ملفات الفواتير
            import os
            import re
            from datetime import datetime
            
            # البحث عن ملفات الفواتير في المجلد الحالي
            invoice_files = [f for f in os.listdir('.') if f.startswith('invoice_') and f.endswith('.txt')]
            
            # تنظيم البيانات حسب التاريخ
            daily_sales = {}
            invoice_contents = {}  # تخزين محتويات الفاتورة
            
            for filename in invoice_files:
                try:
                    with open(filename, 'r', encoding='utf-8') as file:
                        content = file.read()
                        
                        # استخراج تاريخ الفاتورة
                        date_match = re.search(r'التاريخ: (\d{4}-\d{2}-\d{2})', content)
                        if date_match:
                            invoice_date = date_match.group(1)
                        else:
                            # محاولة استخراج التاريخ من اسم الملف
                            timestamp_match = re.search(r'invoice_(\d+)_?(\d+)?\.txt', filename)
                            if timestamp_match:
                                timestamp = int(timestamp_match.group(1))
                                invoice_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                            else:
                                continue
                        
                        # استخراج رقم الفاتورة
                        invoice_id_match = re.search(r'رقم الفاتورة: (\d+)', content)
                        if invoice_id_match:
                            invoice_id = invoice_id_match.group(1)
                        else:
                            # استخدام اسم الملف كمعرف
                            invoice_id = os.path.splitext(filename)[0].replace('invoice_', '')
                        
                        # استخراج اسم المشتري
                        customer_name_match = re.search(r'الاسم: (.*?)(?:\n|$)', content)
                        customer_name = customer_name_match.group(1) if customer_name_match else "غير محدد"
                        
                        # استخراج المبلغ الإجمالي
                        total_match = re.search(r'الإجمالي بعد الخصم:\s+(\d+\.\d+)', content)
                        if not total_match:
                            total_match = re.search(r'المبلغ المطلوب:\s+(\d+\.\d+)', content)
                        
                        if total_match:
                            invoice_total = float(total_match.group(1))
                        else:
                            invoice_total = 0
                        
                        # تخزين محتوى الفاتورة
                        invoice_contents[invoice_id] = content
                        
                        # إضافة البيانات إلى القاموس
                        if invoice_date in daily_sales:
                            daily_sales[invoice_date]["invoices"].append({
                                "id": invoice_id,
                                "customer": customer_name,
                                "total": invoice_total,
                                "filename": filename
                            })
                            daily_sales[invoice_date]["total"] += invoice_total
                        else:
                            daily_sales[invoice_date] = {
                                "date": invoice_date,
                                "invoices": [{
                                    "id": invoice_id,
                                    "customer": customer_name,
                                    "total": invoice_total,
                                    "filename": filename
                                }],
                                "total": invoice_total
                            }
                except Exception as e:
                    print(f"خطأ في قراءة الملف {filename}: {str(e)}")
            
            # تحويل القاموس إلى قائمة
            sales_list = list(daily_sales.values())
            sales_list.sort(key=lambda x: x["date"], reverse=True)
            
            # إنشاء نافذة للتقرير
            report_window = tk.Toplevel(self.root)
            report_window.title("تقرير المبيعات اليومي")
            
            # حجم كبير للنافذة
            window_width = int(self.root.winfo_width() * 0.9)
            window_height = int(self.root.winfo_height() * 0.9)
            
            # توسيط النافذة
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            center_x = int(screen_width/2 - window_width/2)
            center_y = int(screen_height/2 - window_height/2)
            
            report_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
            report_window.minsize(800, 600)
            
            # تخصيص مظهر النافذة
            report_window.configure(bg="#f5f5f5")
            
            # عرض البيانات
            ttk.Label(report_window, text="تقرير المبيعات اليومي", font=("Arial", 16, "bold")).pack(pady=10)
            
            # إنشاء إطار للجداول
            frame = ttk.Frame(report_window)
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # جدول التاريخ والمبيعات
            dates_frame = ttk.LabelFrame(frame, text="المبيعات حسب التاريخ")
            dates_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            date_columns = ("date", "invoices_count", "total")
            date_tree = ttk.Treeview(dates_frame, columns=date_columns, show="headings")
            
            date_tree.heading("date", text="التاريخ")
            date_tree.heading("invoices_count", text="عدد الفواتير")
            date_tree.heading("total", text="إجمالي المبيعات")
            
            date_tree.column("date", width=120, anchor="center")
            date_tree.column("invoices_count", width=80, anchor="center")
            date_tree.column("total", width=100, anchor="center")
            
            # إضافة البيانات
            if sales_list:
                for item in sales_list:
                    date_tree.insert("", "end", values=(
                        item["date"],
                        len(item["invoices"]),
                        f"{item['total']:.2f}"
                    ), tags=(item["date"],))
            else:
                # إذا لم تكن هناك مبيعات
                date_tree.insert("", "end", values=("لا توجد بيانات", "", ""))
            
            # شريط التمرير
            date_scrollbar = ttk.Scrollbar(dates_frame, orient="vertical", command=date_tree.yview)
            date_tree.configure(yscrollcommand=date_scrollbar.set)
            
            date_scrollbar.pack(side="right", fill="y")
            date_tree.pack(side="left", fill="both", expand=True)
            
            # جدول الفواتير
            invoices_frame = ttk.LabelFrame(frame, text="الفواتير")
            invoices_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
            
            inv_columns = ("id", "customer", "total")
            inv_tree = ttk.Treeview(invoices_frame, columns=inv_columns, show="headings")
            
            inv_tree.heading("id", text="رقم الفاتورة")
            inv_tree.heading("customer", text="اسم المشتري")
            inv_tree.heading("total", text="المبلغ")
            
            inv_tree.column("id", width=80, anchor="center")
            inv_tree.column("customer", width=150, anchor="e")
            inv_tree.column("total", width=80, anchor="center")
            
            # شريط التمرير
            inv_scrollbar = ttk.Scrollbar(invoices_frame, orient="vertical", command=inv_tree.yview)
            inv_tree.configure(yscrollcommand=inv_scrollbar.set)
            
            inv_scrollbar.pack(side="right", fill="y")
            inv_tree.pack(side="left", fill="both", expand=True)
            
            # عند تحديد تاريخ، تظهر الفواتير الخاصة به
            def on_date_select(event):
                selected = date_tree.selection()
                if not selected:
                    return
                
                # مسح الفواتير السابقة
                for item in inv_tree.get_children():
                    inv_tree.delete(item)
                
                # الحصول على التاريخ المحدد
                selected_date = date_tree.item(selected[0], "values")[0]
                
                # البحث عن الفواتير لهذا التاريخ
                for date_data in sales_list:
                    if date_data["date"] == selected_date:
                        for invoice in date_data["invoices"]:
                            inv_tree.insert("", "end", values=(
                                invoice["id"],
                                invoice["customer"],
                                f"{invoice['total']:.2f}"
                            ), tags=(invoice["id"], invoice["filename"]))
                        break
            
            # عند تحديد فاتورة، يتم عرض محتواها
            def on_invoice_select(event):
                selected = inv_tree.selection()
                if not selected:
                    return
                
                # الحصول على معرف الفاتورة وملفها
                item_tags = inv_tree.item(selected[0], "tags")
                if len(item_tags) >= 2:
                    invoice_id = item_tags[0]
                    filename = item_tags[1]
                    
                    try:
                        # فتح الملف وقراءة المحتوى
                        with open(filename, 'r', encoding='utf-8') as file:
                            content = file.read()
                        
                        # استخراج معلومات الفاتورة من المحتوى
                        customer_name = ""
                        customer_phone = ""
                        invoice_date = ""
                        barcode = ""
                        total = 0.0
                        subtotal = 0.0
                        discount = 0.0
                        
                        # استخراج معلومات الفاتورة
                        name_match = re.search(r'الاسم: (.*?)(?:\n|$)', content)
                        if name_match:
                            customer_name = name_match.group(1).strip()
                            
                        phone_match = re.search(r'رقم الهاتف: (.*?)(?:\n|$)', content)
                        if phone_match:
                            customer_phone = phone_match.group(1).strip()
                            
                        date_match = re.search(r'التاريخ: (\d{4}-\d{2}-\d{2})', content)
                        if date_match:
                            invoice_date = date_match.group(1)
                            
                        barcode_match = re.search(r'الباركود: (#[A-Z0-9]+)', content)
                        if barcode_match:
                            barcode = barcode_match.group(1)
                            
                        total_match = re.search(r'الإجمالي بعد الخصم:\s+(\d+\.\d+)', content)
                        if total_match:
                            total = float(total_match.group(1))
                            
                        subtotal_match = re.search(r'الإجمالي قبل الخصم:\s+(\d+\.\d+)', content)
                        if subtotal_match:
                            subtotal = float(subtotal_match.group(1))
                            
                        discount_match = re.search(r'الخصم:\s+(\d+\.\d+)', content)
                        if discount_match:
                            discount = float(discount_match.group(1))
                        
                        # استخراج المنتجات
                        items = []
                        # نمط استخراج المنتجات من النص
                        items_pattern = r'\| (.*?) \| (\d+) \| (\d+\.\d+) \| (\d+\.\d+) \|'
                        items_matches = re.findall(items_pattern, content)
                        
                        for match in items_matches:
                            product_name = match[0].strip()
                            quantity = int(match[1])
                            price = float(match[2])
                            item_total = float(match[3])
                            items.append({
                                'name': product_name,
                                'quantity': quantity,
                                'price': price,
                                'total': item_total
                            })
                        
                        # عرض محتوى الفاتورة في نافذة جديدة بنفس التنسيق الجميل
                        invoice_window = tk.Toplevel(report_window)
                        invoice_window.title(f"فاتورة رقم {invoice_id}")
                        
                        # حجم مناسب للنافذة
                        window_width = int(report_window.winfo_width() * 0.8)
                        window_height = int(report_window.winfo_height() * 0.9)
                        
                        # توسيط النافذة
                        screen_width = self.root.winfo_screenwidth()
                        screen_height = self.root.winfo_screenheight()
                        center_x = int(screen_width/2 - window_width/2)
                        center_y = int(screen_height/2 - window_height/2)
                        
                        invoice_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
                        invoice_window.minsize(500, 650)
                        
                        # تخصيص مظهر النافذة
                        invoice_window.configure(bg="#f5f5f5")
                        
                        # إنشاء إطار للنص مع شريط تمرير
                        main_frame = ttk.Frame(invoice_window)
                        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
                        
                        # استخدام Canvas لتوفير تجربة مستخدم أفضل وأكثر استجابة
                        canvas = tk.Canvas(main_frame, highlightthickness=0)
                        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
                        
                        # ربط الـ Canvas بشريط التمرير
                        canvas.configure(yscrollcommand=scrollbar.set)
                        
                        # وضع عناصر التخطيط
                        scrollbar.pack(side="right", fill="y")
                        canvas.pack(side="left", fill="both", expand=True)
                        
                        # إطار داخل الـ Canvas للمحتوى
                        content_frame = ttk.Frame(canvas)
                        canvas.create_window((0, 0), window=content_frame, anchor="nw")
                        
                        # استخدام الدالة الموحدة لإنشاء واجهة الفاتورة
                        self.create_invoice_canvas_widget(
                            content_frame, invoice_id, customer_name, customer_phone, 
                            barcode, invoice_date, items, subtotal, discount, total
                        )
                        
                        # تحديث حجم المنطقة القابلة للتمرير
                        content_frame.update_idletasks()
                        canvas.config(scrollregion=canvas.bbox("all"))
                        
                        # تفعيل التمرير باستخدام عجلة الماوس
                        def _on_mousewheel(event):
                            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                        
                        canvas.bind_all("<MouseWheel>", _on_mousewheel)
                        
                        # إطار الأزرار
                        button_frame = ttk.Frame(invoice_window)
                        button_frame.pack(fill="x", padx=10, pady=10)
                        
                        # زر لحفظ الفاتورة
                        def save_invoice():
                            # إنشاء نص الفاتورة باستخدام الدالة الموحدة
                            invoice_text = self.generate_invoice_text(
                                invoice_id, customer_name, customer_phone, barcode, 
                                invoice_date, items, subtotal, discount, total
                            )
                            
                            save_path = filedialog.asksaveasfilename(
                                defaultextension=".ps",
                                initialfile=f"فاتورة_{invoice_id}.ps",
                                filetypes=[("PostScript files", "*.ps"), ("Text files", "*.txt"), ("All files", "*.*")]
                            )
                            if save_path:
                                try:
                                    if save_path.endswith('.ps'):
                                        # حفظ كصورة باستخدام postscript
                                        content_frame.update()
                                        canvas.postscript(file=save_path)
                                        messagebox.showinfo("حفظ الفاتورة", f"تم حفظ الفاتورة كصورة في:\n{save_path}")
                                    else:
                                        # حفظ كنص
                                        with open(save_path, "w", encoding="utf-8") as f:
                                            f.write(invoice_text)
                                        messagebox.showinfo("حفظ الفاتورة", f"تم حفظ الفاتورة كنص في:\n{save_path}")
                                except Exception as e:
                                    messagebox.showerror("خطأ", f"فشل حفظ الفاتورة: {str(e)}")
                        
                        # طباعة الفاتورة (محاكاة فقط)
                        def print_invoice():
                            messagebox.showinfo("طباعة الفاتورة", "تم إرسال الفاتورة للطباعة")
                        
                        # إلغاء الربط عند إغلاق النافذة
                        def on_closing():
                            canvas.unbind_all("<MouseWheel>")
                            invoice_window.destroy()
                        
                        self.create_button(button_frame, "حفظ الفاتورة", save_invoice).pack(side="left", padx=5)
                        self.create_button(button_frame, "طباعة", print_invoice).pack(side="left", padx=5)
                        self.create_button(button_frame, "إغلاق", on_closing).pack(side="right", padx=5)
                        
                        invoice_window.protocol("WM_DELETE_WINDOW", on_closing)
                        
                    except Exception as e:
                        messagebox.showerror("خطأ", f"فشل في فتح الفاتورة: {str(e)}")
            
            # إضافة الأحداث
            date_tree.bind("<<TreeviewSelect>>", on_date_select)
            inv_tree.bind("<<TreeviewSelect>>", on_invoice_select)
            
            # تحديد أول عنصر تلقائيًا إذا كان موجودًا
            if date_tree.get_children():
                first_item = date_tree.get_children()[0]
                date_tree.selection_set(first_item)
                date_tree.focus(first_item)
                on_date_select(None)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في الحصول على تقرير المبيعات: {str(e)}")

    def show_top_products(self):
        success, products = ProductModel.get_top_products()
        if success:
            # إنشاء نافذة للتقرير
            report_window = tk.Toplevel(self.root)
            report_window.title("المنتجات الأكثر مبيعاً")
            
            # حجم مناسب للنافذة
            window_width = int(self.root.winfo_width() * 0.7)
            window_height = int(self.root.winfo_height() * 0.7)
            
            # توسيط النافذة
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            center_x = int(screen_width/2 - window_width/2)
            center_y = int(screen_height/2 - window_height/2)
            
            report_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
            report_window.minsize(600, 400)
            
            # تخصيص مظهر النافذة
            report_window.configure(bg="#f5f5f5")
            
            # عرض البيانات
            ttk.Label(report_window, text="المنتجات الأكثر مبيعاً", font=("Arial", 16, "bold")).pack(pady=10)
            
            # جدول البيانات
            columns = ("name", "sold", "revenue")
            tree = ttk.Treeview(report_window, columns=columns, show="headings")
            
            tree.heading("name", text="اسم المنتج")
            tree.heading("sold", text="المبيعات")
            tree.heading("revenue", text="الإيرادات")
            
            tree.column("name", width=200, anchor="e")
            tree.column("sold", width=100, anchor="center")
            tree.column("revenue", width=150, anchor="center")
            
            # إضافة البيانات
            for product in products:
                tree.insert("", "end", values=(
                    product["name"],
                    product["sold"],
                    f"{product['revenue']:.2f}"
                ))
            
            # شريط التمرير
            scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side="left", fill="y")
            tree.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        else:
            messagebox.showerror("خطأ", f"فشل في الحصول على تقرير المنتجات: {products}")

    def show_low_stock(self):
        success, products = ProductModel.get_low_stock()
        if success:
            # إنشاء نافذة للتقرير
            report_window = tk.Toplevel(self.root)
            report_window.title("تقرير المخزون المنخفض")
            
            # حجم مناسب للنافذة
            window_width = int(self.root.winfo_width() * 0.7)
            window_height = int(self.root.winfo_height() * 0.7)
            
            # توسيط النافذة
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            center_x = int(screen_width/2 - window_width/2)
            center_y = int(screen_height/2 - window_height/2)
            
            report_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
            report_window.minsize(500, 400)
            
            # تخصيص مظهر النافذة
            report_window.configure(bg="#f5f5f5")
            
            # عرض البيانات
            ttk.Label(report_window, text="المنتجات ذات المخزون المنخفض", font=("Arial", 16, "bold")).pack(pady=10)
            
            # جدول البيانات
            columns = ("name", "quantity")
            tree = ttk.Treeview(report_window, columns=columns, show="headings")
            
            tree.heading("name", text="اسم المنتج")
            tree.heading("quantity", text="الكمية المتبقية")
            
            tree.column("name", width=300, anchor="e")
            tree.column("quantity", width=150, anchor="center")
            
            # إضافة البيانات
            for product in products:
                tree.insert("", "end", values=(
                    product["name"],
                    product["quantity"]
                ))
            
            # شريط التمرير
            scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side="left", fill="y")
            tree.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        else:
            messagebox.showerror("خطأ", f"فشل في الحصول على تقرير المخزون: {products}")

    def setup_users_tab(self):
        if self.user['role'] != 'admin':
            ttk.Label(self.users_tab, text="لا تملك صلاحية الوصول إلى هذه الصفحة").pack(pady=20)
            return
            
        # إطار للأزرار
        buttons_frame = ttk.Frame(self.users_tab)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        self.create_button(buttons_frame, "إضافة مستخدم", self.add_user).pack(side="left", padx=5)
        self.create_button(buttons_frame, "تعديل مستخدم", self.edit_user).pack(side="left", padx=5)
        self.create_button(buttons_frame, "حذف مستخدم", self.delete_user).pack(side="left", padx=5)
        self.create_button(buttons_frame, "تحديث", self.load_users).pack(side="right", padx=5)
        
        # إنشاء جدول المستخدمين
        columns = ("id", "username", "role")
        self.users_tree = ttk.Treeview(self.users_tab, columns=columns, show="headings")
        
        self.users_tree.heading("id", text="المعرف")
        self.users_tree.heading("username", text="اسم المستخدم")
        self.users_tree.heading("role", text="الصلاحية")
        
        self.users_tree.column("id", width=50, anchor="center")
        self.users_tree.column("username", width=200, anchor="e")
        self.users_tree.column("role", width=100, anchor="center")
        
        # إضافة شريط التمرير
        scrollbar = ttk.Scrollbar(self.users_tab, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="left", fill="y")
        self.users_tree.pack(side="right", fill="both", expand=True, padx=10, pady=5)
        
        # تحميل المستخدمين
        self.load_users()

    def load_users(self):
        # مسح البيانات القديمة
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # تحميل المستخدمين
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
            messagebox.showerror("خطأ", "فشل في تحميل المستخدمين")

    def add_user(self):
        # إنشاء نافذة لإضافة مستخدم جديد
        add_window = tk.Toplevel(self.root)
        add_window.title("إضافة مستخدم جديد")
        
        # حجم مناسب للنافذة
        window_width = 450
        window_height = 280
        
        # توسيط النافذة
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        add_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        add_window.resizable(False, False)
        
        # تخصيص مظهر النافذة
        add_window.configure(bg="#f5f5f5")
        
        # المدخلات
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
        
        # زر الإضافة
        def save_user():
            username = username_var.get()
            password = password_var.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showerror("خطأ", "الرجاء إدخال اسم المستخدم وكلمة المرور")
                return
            
            success, message = UserModel.add_user(username, password, role)
            if success:
                messagebox.showinfo("نجاح", "تمت إضافة المستخدم بنجاح")
                add_window.destroy()
                self.load_users()
            else:
                messagebox.showerror("خطأ", f"فشل إضافة المستخدم: {message}")
        
        self.create_button(add_window, "حفظ", save_user).grid(row=3, column=1, padx=10, pady=20)

    def edit_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "الرجاء تحديد مستخدم للتعديل")
            return
        
        # الحصول على معرف المستخدم
        user_id = int(self.users_tree.item(selected[0])["values"][0])
        
        # الحصول على بيانات المستخدم
        success, user = UserModel.get_user(user_id)
        
        if not success or not user:
            messagebox.showerror("خطأ", "فشل في الحصول على بيانات المستخدم")
            return
        
        # إنشاء نافذة للتعديل
        edit_window = tk.Toplevel(self.root)
        edit_window.title("تعديل مستخدم")
        
        # حجم مناسب للنافذة
        window_width = 500
        window_height = 300
        
        # توسيط النافذة
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        edit_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        edit_window.resizable(False, False)
        
        # تخصيص مظهر النافذة
        edit_window.configure(bg="#f5f5f5")
        
        # المدخلات
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
        
        # زر الحفظ
        def save_changes():
            username = username_var.get()
            password = password_var.get()  # قد تكون فارغة
            role = role_var.get()
            
            if not username:
                messagebox.showerror("خطأ", "الرجاء إدخال اسم المستخدم")
                return
            
            success, message = UserModel.update_user(user_id, username, password, role)
            if success:
                messagebox.showinfo("نجاح", "تم تحديث المستخدم بنجاح")
                edit_window.destroy()
                self.load_users()
            else:
                messagebox.showerror("خطأ", f"فشل تحديث المستخدم: {message}")
        
        self.create_button(edit_window, "حفظ التغييرات", save_changes).grid(row=3, column=1, padx=10, pady=20)

    def delete_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "الرجاء تحديد مستخدم للحذف")
            return
        
        # الحصول على معرف المستخدم واسمه
        user_id = int(self.users_tree.item(selected[0])["values"][0])
        username = self.users_tree.item(selected[0])["values"][1]
        
        # التحقق من أن المستخدم ليس نفسه
        if user_id == self.user["id"]:
            messagebox.showwarning("تحذير", "لا يمكنك حذف حسابك الحالي")
            return
        
        # تأكيد الحذف
        if messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف المستخدم '{username}'؟"):
            success, message = UserModel.delete_user(user_id)
            if success:
                messagebox.showinfo("نجاح", "تم حذف المستخدم بنجاح")
                self.load_users()
            else:
                messagebox.showerror("خطأ", f"فشل حذف المستخدم: {message}")

    def on_close(self):
        if messagebox.askyesno("تأكيد الخروج", "هل تريد تسجيل الخروج وإغلاق البرنامج؟"):
            self.login_window.destroy()