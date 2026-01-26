"""
تبويب إدارة المنتجات
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.product_model import ProductModel
from ui.base_tab import BaseTab


class ProductsTab(BaseTab):
    """تبويب إدارة المنتجات"""
    
    def __init__(self, parent, user, root):
        super().__init__(parent, user, root)
        self.setup_tab()
    
    def setup_tab(self):
        """إعداد تبويب المنتجات"""
        # إطار للأزرار
        buttons_frame = ttk.Frame(self.parent)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # أزرار إدارة المنتجات (للأدمن فقط)
        if self.is_admin():
            self.create_button(buttons_frame, "إضافة منتج", self.add_product).pack(side="right", padx=5)
            self.create_button(buttons_frame, "تعديل منتج", self.edit_product).pack(side="right", padx=5)
            self.create_button(buttons_frame, "حذف منتج", self.delete_product).pack(side="right", padx=5)
        
        self.create_button(buttons_frame, "تحديث", self.load_products).pack(side="left", padx=5)
        
        # إطار البحث
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(search_frame, text="بحث:").pack(side="right", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_products())
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side="right", padx=5)
        
        # إنشاء الجدول
        columns = ("name", "quantity", "price", "total_price", "sold", "profit")
        self.products_tree = ttk.Treeview(self.parent, columns=columns, show="headings", selectmode="browse")
        
        # تعيين العناوين
        self.products_tree.heading("name", text="اسم المنتج")
        self.products_tree.heading("quantity", text="العدد المتاح")
        self.products_tree.heading("price", text="سعر القطعة")
        self.products_tree.heading("total_price", text="مجموع الأسعار")
        self.products_tree.heading("sold", text="المباع")
        self.products_tree.heading("profit", text="الربح")
        
        # ضبط أحجام الأعمدة
        self.products_tree.column("name", width=200, anchor="e")
        self.products_tree.column("quantity", width=100, anchor="center")
        self.products_tree.column("price", width=100, anchor="center")
        self.products_tree.column("total_price", width=120, anchor="center")
        self.products_tree.column("sold", width=80, anchor="center")
        self.products_tree.column("profit", width=100, anchor="center")
        
        # إضافة شريط التمرير
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        # وضع العناصر
        scrollbar.pack(side="left", fill="y")
        self.products_tree.pack(side="right", fill="both", expand=True, padx=10, pady=5)
        
        # تحميل المنتجات
        self.load_products()
    
    def load_products(self):
        """تحميل المنتجات من قاعدة البيانات"""
        # مسح البيانات القديمة
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # تحميل المنتجات
        success, products = ProductModel.get_all_products()
        if success:
            for product in products:
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
        else:
            self.show_error("خطأ", "فشل في تحميل المنتجات")
    
    def filter_products(self):
        """فلترة المنتجات حسب البحث"""
        search_term = self.search_var.get().lower()
        
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        success, products = ProductModel.get_all_products()
        if success:
            for product in products:
                if search_term in product["name"].lower():
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
        """إضافة منتج جديد"""
        if not self.is_admin():
            self.show_warning("تنبيه", "ليس لديك صلاحية لإضافة منتجات")
            return
        
        add_window = tk.Toplevel(self.root)
        add_window.title("إضافة منتج جديد")
        add_window.resizable(False, False)
        add_window.configure(bg="#f5f5f5")
        self.center_window(add_window, 500, 300)
        
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
        
        def save_product():
            try:
                name = name_var.get()
                price = price_var.get()
                quantity = quantity_var.get()
                
                if not name:
                    self.show_error("خطأ", "الرجاء إدخال اسم المنتج")
                    return
                
                if price <= 0:
                    self.show_error("خطأ", "السعر يجب أن يكون أكبر من صفر")
                    return
                
                if quantity < 0:
                    self.show_error("خطأ", "الكمية لا يمكن أن تكون سالبة")
                    return
                
                success, message = ProductModel.add_product(name, price, quantity)
                if success:
                    self.show_info("نجاح", "تمت إضافة المنتج بنجاح")
                    add_window.destroy()
                    self.load_products()
                else:
                    self.show_error("خطأ", f"فشل إضافة المنتج: {message}")
            
            except ValueError:
                self.show_error("خطأ", "تأكد من إدخال قيم صحيحة للسعر والكمية")
        
        self.create_button(add_window, "حفظ", save_product).grid(row=3, column=1, padx=10, pady=20)
    
    def edit_product(self):
        """تعديل منتج"""
        if not self.is_admin():
            self.show_warning("تنبيه", "ليس لديك صلاحية لتعديل المنتجات")
            return
            
        selected = self.products_tree.selection()
        if not selected:
            self.show_warning("تحذير", "الرجاء تحديد منتج للتعديل")
            return
        
        item_tags = self.products_tree.item(selected, "tags")
        if not item_tags or len(item_tags) < 2:
            self.show_error("خطأ", "فشل في الحصول على معرف المنتج")
            return
            
        product_id = int(item_tags[1])
        success, product = ProductModel.get_product(product_id)
        
        if not success or not product:
            self.show_error("خطأ", "فشل في الحصول على بيانات المنتج")
            return
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("تعديل منتج")
        edit_window.resizable(False, False)
        edit_window.configure(bg="#f5f5f5")
        self.center_window(edit_window, 500, 300)
        
        ttk.Label(edit_window, text="اسم المنتج:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_var = tk.StringVar(value=product["name"])
        ttk.Entry(edit_window, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(edit_window, text="السعر:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        price_var = tk.DoubleVar(value=product["price"])
        ttk.Entry(edit_window, textvariable=price_var, width=30).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(edit_window, text="الكمية:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        quantity_var = tk.IntVar(value=product["quantity"])
        ttk.Entry(edit_window, textvariable=quantity_var, width=30).grid(row=2, column=1, padx=10, pady=10)
        
        def save_changes():
            try:
                name = name_var.get()
                price = price_var.get()
                quantity = quantity_var.get()
                
                if not name:
                    self.show_error("خطأ", "الرجاء إدخال اسم المنتج")
                    return
                
                if price <= 0:
                    self.show_error("خطأ", "السعر يجب أن يكون أكبر من صفر")
                    return
                
                if quantity < 0:
                    self.show_error("خطأ", "الكمية لا يمكن أن تكون سالبة")
                    return
                
                success, message = ProductModel.update_product(product_id, name, price, quantity)
                if success:
                    self.show_info("نجاح", "تم تحديث المنتج بنجاح")
                    edit_window.destroy()
                    self.load_products()
                else:
                    self.show_error("خطأ", f"فشل تحديث المنتج: {message}")
            
            except ValueError:
                self.show_error("خطأ", "تأكد من إدخال قيم صحيحة للسعر والكمية")
        
        self.create_button(edit_window, "حفظ التغييرات", save_changes).grid(row=3, column=1, padx=10, pady=20)
    
    def delete_product(self):
        """حذف منتج"""
        if not self.is_admin():
            self.show_warning("تنبيه", "ليس لديك صلاحية لحذف المنتجات")
            return
            
        selected = self.products_tree.selection()
        if not selected:
            self.show_warning("تحذير", "الرجاء تحديد منتج للحذف")
            return
        
        item_tags = self.products_tree.item(selected, "tags")
        if not item_tags or len(item_tags) < 2:
            self.show_error("خطأ", "فشل في الحصول على معرف المنتج")
            return
            
        product_id = int(item_tags[1])
        product_name = self.products_tree.item(selected, "values")[0]
        
        if self.confirm("تأكيد الحذف", f"هل أنت متأكد من حذف المنتج '{product_name}'؟"):
            success, message = ProductModel.delete_product(product_id)
            if success:
                self.show_info("نجاح", "تم حذف المنتج بنجاح")
                self.load_products()
            else:
                self.show_error("خطأ", f"فشل حذف المنتج: {message}")
