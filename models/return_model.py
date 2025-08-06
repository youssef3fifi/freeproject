import sqlite3
import os
from datetime import datetime

class ReturnModel:
    """
    فئة نموذج المرتجعات - تتعامل مع كل عمليات المرتجعات في قاعدة البيانات
    """
    
    # مسار قاعدة البيانات
    db_path = "data/store.db"
    
    @classmethod
    def _ensure_db_exists(cls):
        """التأكد من وجود قاعدة البيانات وإنشاء جداول المرتجعات إذا لم تكن موجودة"""
        # التأكد من وجود مجلد البيانات
        os.makedirs(os.path.dirname(cls.db_path), exist_ok=True)
        
        # إنشاء الاتصال بقاعدة البيانات
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        
        # إنشاء جدول المرتجعات إذا لم يكن موجوداً
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_invoice_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT,
                return_code TEXT NOT NULL,
                total_return_amount REAL NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (original_invoice_id) REFERENCES invoices(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # إنشاء جدول عناصر المرتجعات إذا لم يكن موجوداً
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS return_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                item_total REAL NOT NULL,
                FOREIGN KEY (return_id) REFERENCES returns(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @classmethod
    def create_return(cls, user_id, original_invoice_id, customer_name, customer_phone, return_code, items, total_return_amount):
        """
        إنشاء عملية إرجاع جديدة
        
        Args:
            user_id (int): معرف المستخدم الذي أجرى الإرجاع
            original_invoice_id (int): معرف الفاتورة الأصلية
            customer_name (str): اسم العميل
            customer_phone (str): رقم هاتف العميل
            return_code (str): رمز الإرجاع
            items (list): قائمة العناصر المرتجعة
            total_return_amount (float): إجمالي مبلغ الإرجاع
            
        Returns:
            tuple: (success, result)
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # تاريخ الإنشاء
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # إنشاء عملية الإرجاع
            cursor.execute(
                """INSERT INTO returns 
                   (original_invoice_id, customer_name, customer_phone, return_code, total_return_amount, user_id, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (original_invoice_id, customer_name, customer_phone, return_code, total_return_amount, user_id, created_at)
            )
            
            # الحصول على معرف عملية الإرجاع المنشأة
            return_id = cursor.lastrowid
            
            # إضافة عناصر الإرجاع
            for item in items:
                cursor.execute(
                    """INSERT INTO return_items 
                       (return_id, product_id, name, price, quantity, item_total) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (return_id, item["product_id"], item["name"], item["price"], item["quantity"], item["total"])
                )
            
            conn.commit()
            conn.close()
            
            return True, return_id
            
        except Exception as e:
            return False, f"فشل في إنشاء عملية الإرجاع: {str(e)}"
    
    @classmethod
    def get_return(cls, return_id):
        """
        الحصول على تفاصيل عملية إرجاع محددة
        
        Args:
            return_id (int): معرف عملية الإرجاع
            
        Returns:
            tuple: (success, result)
        """
        try:
            cls._ensure_db_exists()
            
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # الحصول على بيانات عملية الإرجاع
            cursor.execute(
                """SELECT r.*, u.username
                   FROM returns r
                   LEFT JOIN users u ON r.user_id = u.id
                   WHERE r.id = ?""",
                (return_id,)
            )
            
            return_data = cursor.fetchone()
            
            if not return_data:
                conn.close()
                return False, "عملية الإرجاع غير موجودة"
            
            # الحصول على عناصر الإرجاع
            cursor.execute(
                """SELECT * FROM return_items WHERE return_id = ?""",
                (return_id,)
            )
            
            items = cursor.fetchall()
            
            conn.close()
            
            # تنسيق البيانات
            return_info = {
                'id': return_data[0],
                'original_invoice_id': return_data[1],
                'customer_name': return_data[2],
                'customer_phone': return_data[3],
                'return_code': return_data[4],
                'total_return_amount': return_data[5],
                'user_id': return_data[6],
                'created_at': return_data[7],
                'username': return_data[8] if return_data[8] else "مجهول",
                'items': [
                    {
                        'id': item[0],
                        'product_id': item[2],
                        'name': item[3],
                        'price': item[4],
                        'quantity': item[5],
                        'total': item[6]
                    }
                    for item in items
                ]
            }
            
            return True, return_info
            
        except Exception as e:
            return False, f"فشل في الحصول على بيانات عملية الإرجاع: {str(e)}"
    
    @classmethod
    def get_all_returns(cls):
        """
        الحصول على جميع عمليات الإرجاع
        
        Returns:
            tuple: (success, result)
        """
        try:
            cls._ensure_db_exists()
            
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT r.*, u.username
                   FROM returns r
                   LEFT JOIN users u ON r.user_id = u.id
                   ORDER BY r.created_at DESC"""
            )
            
            returns = cursor.fetchall()
            conn.close()
            
            return_list = [
                {
                    'id': ret[0],
                    'original_invoice_id': ret[1],
                    'customer_name': ret[2],
                    'customer_phone': ret[3],
                    'return_code': ret[4],
                    'total_return_amount': ret[5],
                    'user_id': ret[6],
                    'created_at': ret[7],
                    'username': ret[8] if ret[8] else "مجهول"
                }
                for ret in returns
            ]
            
            return True, return_list
            
        except Exception as e:
            return False, f"فشل في الحصول على قائمة المرتجعات: {str(e)}"
    
    @classmethod
    def get_returns_by_date(cls, date):
        """
        الحصول على عمليات الإرجاع في تاريخ محدد
        
        Args:
            date (str): التاريخ بصيغة YYYY-MM-DD
            
        Returns:
            tuple: (success, result)
        """
        try:
            cls._ensure_db_exists()
            
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT r.*, u.username
                   FROM returns r
                   LEFT JOIN users u ON r.user_id = u.id
                   WHERE DATE(r.created_at) = ?
                   ORDER BY r.created_at DESC""",
                (date,)
            )
            
            returns = cursor.fetchall()
            conn.close()
            
            return_list = [
                {
                    'id': ret[0],
                    'original_invoice_id': ret[1],
                    'customer_name': ret[2],
                    'customer_phone': ret[3],
                    'return_code': ret[4],
                    'total_return_amount': ret[5],
                    'user_id': ret[6],
                    'created_at': ret[7],
                    'username': ret[8] if ret[8] else "مجهول"
                }
                for ret in returns
            ]
            
            return True, return_list
            
        except Exception as e:
            return False, f"فشل في الحصول على قائمة المرتجعات: {str(e)}"