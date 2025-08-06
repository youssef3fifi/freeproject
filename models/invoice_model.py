import sqlite3
import os
from datetime import datetime

class InvoiceModel:
    """
    فئة نموذج الفاتورة - تتعامل مع كل عمليات الفواتير في قاعدة البيانات
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
        
        # إنشاء جدول الفواتير إذا لم يكن موجوداً
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                customer_phone TEXT,
                barcode TEXT,
                subtotal REAL NOT NULL,
                discount REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL,
                user_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # إنشاء جدول عناصر الفاتورة إذا لم يكن موجوداً
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                item_total REAL NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @classmethod
    def create_invoice(cls, user_id, customer_name, customer_phone, barcode, items, subtotal, discount, total):
        """
        إنشاء فاتورة جديدة
        
        Args:
            user_id (int): معرف المستخدم الذي أنشأ الفاتورة
            customer_name (str): اسم العميل
            customer_phone (str): رقم هاتف العميل
            barcode (str): رمز الباركود
            items (list): قائمة العناصر في الفاتورة (منتج، كمية، سعر، إجمالي)
            subtotal (float): إجمالي الفاتورة قبل الخصم
            discount (float): مقدار الخصم
            total (float): إجمالي الفاتورة بعد الخصم
            
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (int/str): معرف الفاتورة أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # تاريخ الإنشاء
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # إنشاء الفاتورة
            cursor.execute(
                """INSERT INTO invoices 
                   (customer_name, customer_phone, barcode, subtotal, discount, total, user_id, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (customer_name, customer_phone, barcode, subtotal, discount, total, user_id, created_at)
            )
            
            # الحصول على معرف الفاتورة المنشأة
            invoice_id = cursor.lastrowid
            
            # إضافة عناصر الفاتورة
            for item in items:
                cursor.execute(
                    """INSERT INTO invoice_items 
                       (invoice_id, product_id, name, price, quantity, item_total) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (invoice_id, item["product_id"], item["name"], item["price"], 
                     item["quantity"], item["total"])
                )
            
            conn.commit()
            conn.close()
            
            return True, invoice_id
            
        except Exception as e:
            return False, f"خطأ في إنشاء الفاتورة: {str(e)}"
    
    @classmethod
    def get_invoice(cls, invoice_id):
        """
        الحصول على تفاصيل فاتورة
        
        Args:
            invoice_id (int): معرف الفاتورة
            
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (dict/str): بيانات الفاتورة أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # الحصول على بيانات الفاتورة
            cursor.execute("""
                SELECT i.*, u.username as user_name
                FROM invoices i
                LEFT JOIN users u ON i.user_id = u.id
                WHERE i.id = ?
            """, (invoice_id,))
            
            invoice = cursor.fetchone()
            
            if not invoice:
                conn.close()
                return False, "الفاتورة غير موجودة"
            
            invoice_dict = dict(invoice)
            
            # الحصول على عناصر الفاتورة
            cursor.execute("""
                SELECT * FROM invoice_items
                WHERE invoice_id = ?
            """, (invoice_id,))
            
            items = [dict(row) for row in cursor.fetchall()]
            invoice_dict["items"] = items
            
            conn.close()
            return True, invoice_dict
            
        except Exception as e:
            return False, f"خطأ في استرجاع بيانات الفاتورة: {str(e)}"
    
    @classmethod
    def get_daily_sales(cls, date=None):
        """
        الحصول على المبيعات اليومية
        
        Args:
            date (str): التاريخ المطلوب بصيغة YYYY-MM-DD (اليوم الحالي إذا كانت None)
            
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (dict/str): بيانات المبيعات أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # إعداد التاريخ المطلوب
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # الحصول على المبيعات اليومية
            cursor.execute("""
                SELECT i.*, u.username as user_name
                FROM invoices i
                LEFT JOIN users u ON i.user_id = u.id
                WHERE DATE(i.created_at) = ?
                ORDER BY i.created_at DESC
            """, (date,))
            
            invoices = [dict(row) for row in cursor.fetchall()]
            
            # حساب الإجماليات
            total_sales = sum(invoice["total"] for invoice in invoices)
            total_items = 0
            
            for invoice in invoices:
                # الحصول على عناصر كل فاتورة
                cursor.execute("""
                    SELECT * FROM invoice_items
                    WHERE invoice_id = ?
                """, (invoice["id"],))
                
                items = [dict(row) for row in cursor.fetchall()]
                invoice["items"] = items
                total_items += sum(item["quantity"] for item in items)
            
            conn.close()
            
            result = {
                "date": date,
                "invoices": invoices,
                "total_sales": total_sales,
                "total_invoices": len(invoices),
                "total_items": total_items
            }
            
            return True, result
            
        except Exception as e:
            return False, f"خطأ في استرجاع المبيعات اليومية: {str(e)}"
    
    @classmethod
    def get_sales_by_date_range(cls, start_date, end_date):
        """
        الحصول على المبيعات في فترة زمنية محددة
        
        Args:
            start_date (str): تاريخ البداية بصيغة YYYY-MM-DD
            end_date (str): تاريخ النهاية بصيغة YYYY-MM-DD
            
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (dict/str): بيانات المبيعات أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # الحصول على المبيعات في الفترة الزمنية
            cursor.execute("""
                SELECT DATE(created_at) as date, 
                       COUNT(*) as invoices_count,
                       SUM(total) as total_sales
                FROM invoices
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """, (start_date, end_date))
            
            daily_sales = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            result = {
                "start_date": start_date,
                "end_date": end_date,
                "daily_sales": daily_sales,
                "total_sales": sum(day["total_sales"] for day in daily_sales),
                "total_invoices": sum(day["invoices_count"] for day in daily_sales)
            }
            
            return True, result
            
        except Exception as e:
            return False, f"خطأ في استرجاع المبيعات: {str(e)}"