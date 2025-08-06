import sqlite3
import os

class ProductModel:
    """
    فئة نموذج المنتج - تتعامل مع كل عمليات المنتجات في قاعدة البيانات
    """
    
    # مسار قاعدة البيانات
    db_path = "data/store.db"
    
    @classmethod
    def _ensure_db_exists(cls):
        """التأكد من وجود قاعدة البيانات وإنشاء الجداول إذا لم تكن موجودة"""
        # التأكد من وجود مجلد البيانات
        os.makedirs(os.path.dirname(cls.db_path), exist_ok=True)
        
        # إنشاء الاتصال بقاعدة البيانات
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        
        # إنشاء جدول المنتجات إذا لم يكن موجوداً
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                sold INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @classmethod
    def get_all_products(cls):
        """
        الحصول على جميع المنتجات
        
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (list/str): قائمة المنتجات أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # الحصول على جميع المنتجات
            cursor.execute("SELECT * FROM products")
            products = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return True, products
            
        except Exception as e:
            return False, f"خطأ في استرجاع المنتجات: {str(e)}"
    
    @classmethod
    def get_available_products(cls):
        """
        الحصول على المنتجات المتاحة فقط (الكمية > 0)
        
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (list/str): قائمة المنتجات أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # الحصول على المنتجات المتاحة
            cursor.execute("SELECT * FROM products WHERE quantity > 0")
            products = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return True, products
            
        except Exception as e:
            return False, f"خطأ في استرجاع المنتجات المتاحة: {str(e)}"
    
    @classmethod
    def get_product(cls, product_id):
        """
        الحصول على منتج محدد حسب المعرف
        
        Args:
            product_id (int): معرف المنتج
            
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (dict/str): بيانات المنتج أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # البحث عن المنتج بواسطة المعرف
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            conn.close()
            
            if product:
                return True, dict(product)
            else:
                return False, "المنتج غير موجود"
                
        except Exception as e:
            return False, f"خطأ في استرجاع المنتج: {str(e)}"
    
    @classmethod
    def add_product(cls, name, price, quantity):
        """
        إضافة منتج جديد
        
        Args:
            name (str): اسم المنتج
            price (float): سعر المنتج
            quantity (int): الكمية المتاحة
            
        Returns:
            tuple: (success, message)
                - success (bool): نجاح العملية
                - message (str): رسالة النجاح أو الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # التحقق من صحة البيانات
            if not name:
                return False, "اسم المنتج مطلوب"
                
            if price <= 0:
                return False, "السعر يجب أن يكون أكبر من صفر"
                
            if quantity < 0:
                return False, "الكمية لا يمكن أن تكون سالبة"
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # إضافة المنتج
            try:
                cursor.execute(
                    "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                    (name, price, quantity)
                )
                conn.commit()
                conn.close()
                return True, "تمت إضافة المنتج بنجاح"
            except sqlite3.IntegrityError:
                return False, "اسم المنتج موجود بالفعل"
                
        except Exception as e:
            return False, f"خطأ في إضافة المنتج: {str(e)}"
    
    @classmethod
    def update_product(cls, product_id, name, price, quantity):
        """
        تحديث بيانات منتج
        
        Args:
            product_id (int): معرف المنتج
            name (str): اسم المنتج الجديد
            price (float): سعر المنتج الجديد
            quantity (int): الكمية المتاحة الجديدة
            
        Returns:
            tuple: (success, message)
                - success (bool): نجاح العملية
                - message (str): رسالة النجاح أو الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # التحقق من صحة البيانات
            if not name:
                return False, "اسم المنتج مطلوب"
                
            if price <= 0:
                return False, "السعر يجب أن يكون أكبر من صفر"
                
            if quantity < 0:
                return False, "الكمية لا يمكن أن تكون سالبة"
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # التحقق من وجود المنتج
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                conn.close()
                return False, "المنتج غير موجود"
            
            # تحديث بيانات المنتج
            try:
                cursor.execute(
                    "UPDATE products SET name = ?, price = ?, quantity = ? WHERE id = ?",
                    (name, price, quantity, product_id)
                )
                conn.commit()
                conn.close()
                return True, "تم تحديث بيانات المنتج بنجاح"
            except sqlite3.IntegrityError:
                return False, "اسم المنتج موجود بالفعل"
                
        except Exception as e:
            return False, f"خطأ في تحديث المنتج: {str(e)}"
    
    @classmethod
    def update_product_quantity(cls, product_id, sold_quantity):
        """
        تحديث كمية المنتج بعد البيع
        
        Args:
            product_id (int): معرف المنتج
            sold_quantity (int): الكمية المباعة
            
        Returns:
            tuple: (success, message)
                - success (bool): نجاح العملية
                - message (str): رسالة النجاح أو الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # التحقق من صحة البيانات
            if sold_quantity <= 0:
                return False, "الكمية المباعة يجب أن تكون أكبر من صفر"
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # التحقق من وجود المنتج وكمية كافية
            cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                conn.close()
                return False, "المنتج غير موجود"
            
            if product[0] < sold_quantity:
                conn.close()
                return False, "الكمية المتاحة غير كافية"
            
            # تحديث كمية المنتج وزيادة عدد المبيعات
            cursor.execute(
                "UPDATE products SET quantity = quantity - ?, sold = sold + ? WHERE id = ?",
                (sold_quantity, sold_quantity, product_id)
            )
            conn.commit()
            conn.close()
            return True, "تم تحديث كمية المنتج بنجاح"
                
        except Exception as e:
            return False, f"خطأ في تحديث كمية المنتج: {str(e)}"
    
    @classmethod
    def delete_product(cls, product_id):
        """
        حذف منتج
        
        Args:
            product_id (int): معرف المنتج
            
        Returns:
            tuple: (success, message)
                - success (bool): نجاح العملية
                - message (str): رسالة النجاح أو الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # التحقق من وجود المنتج
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                conn.close()
                return False, "المنتج غير موجود"
            
            # حذف المنتج
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            
            return True, "تم حذف المنتج بنجاح"
                
        except Exception as e:
            return False, f"خطأ في حذف المنتج: {str(e)}"
    
    @classmethod
    def get_top_products(cls, limit=10):
        """
        الحصول على أكثر المنتجات مبيعاً
        
        Args:
            limit (int): عدد المنتجات المراد استرجاعها
            
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (list/str): قائمة المنتجات أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # الحصول على أكثر المنتجات مبيعاً
            cursor.execute("""
                SELECT id, name, price, quantity, sold, (sold * price) as revenue
                FROM products
                WHERE sold > 0
                ORDER BY sold DESC
                LIMIT ?
            """, (limit,))
            
            products = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return True, products
            
        except Exception as e:
            return False, f"خطأ في استرجاع أكثر المنتجات مبيعاً: {str(e)}"
    
    @classmethod
    def get_low_stock(cls, threshold=5):
        """
        الحصول على المنتجات ذات المخزون المنخفض
        
        Args:
            threshold (int): الحد الأدنى للمخزون
            
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (list/str): قائمة المنتجات أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # الحصول على المنتجات ذات المخزون المنخفض
            cursor.execute("""
                SELECT * FROM products
                WHERE quantity <= ?
                ORDER BY quantity ASC
            """, (threshold,))
            
            products = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return True, products
            
        except Exception as e:
            return False, f"خطأ في استرجاع المنتجات ذات المخزون المنخفض: {str(e)}"