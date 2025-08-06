import sqlite3
import os
import hashlib

class UserModel:
    """
    فئة نموذج المستخدم - تتعامل مع كل عمليات المستخدمين في قاعدة البيانات
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
        
        # إنشاء جدول المستخدمين إذا لم يكن موجوداً
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # إضافة مستخدم مدير افتراضي إذا كانت قاعدة البيانات فارغة
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # إنشاء مستخدم افتراضي (admin / admin)
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", "admin", "admin")
            )
            
            # إضافة مستخدم عادي (user / user)
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("user", "user", "worker")
            )
        
        conn.commit()
        conn.close()
    
    @classmethod
    def authenticate(cls, username, password):
        """
        التحقق من بيانات تسجيل الدخول للمستخدم
        
        Args:
            username (str): اسم المستخدم
            password (str): كلمة المرور
            
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (dict/str): بيانات المستخدم أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # تحويل كلمة المرور إلى هاش
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # محاولة الدخول باستخدام كلمة المرور الأصلية
            cursor.execute(
                "SELECT id, username, role, password FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()
            
            if user:
                # فحص إذا كانت كلمة المرور تطابق النص الأصلي أو الهاش
                if user['password'] == password:
                    # تحديث كلمة المرور إلى النسخة المشفرة تلقائياً
                    cursor.execute(
                        "UPDATE users SET password = ? WHERE id = ?",
                        (hashed_password, user['id'])
                    )
                    conn.commit()
                    
                    # تحويل نتيجة قاعدة البيانات إلى قاموس
                    result = dict(user)
                    del result['password']  # حذف كلمة المرور من النتيجة للأمان
                    conn.close()
                    return True, result
                elif user['password'] == hashed_password:
                    # كلمة المرور مشفرة بالفعل وتطابق المدخل
                    result = dict(user)
                    del result['password']  # حذف كلمة المرور من النتيجة للأمان
                    conn.close()
                    return True, result
            
            conn.close()
            return False, "اسم المستخدم أو كلمة المرور غير صحيحة"
                
        except Exception as e:
            return False, f"خطأ في المصادقة: {str(e)}"
    
    @classmethod
    def get_all_users(cls):
        """
        الحصول على جميع المستخدمين
        
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (list/str): قائمة المستخدمين أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # الحصول على جميع المستخدمين
            cursor.execute("SELECT id, username, role FROM users")
            users = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return True, users
            
        except Exception as e:
            return False, f"خطأ في استرجاع المستخدمين: {str(e)}"
    
    @classmethod
    def get_user(cls, user_id):
        """
        الحصول على مستخدم محدد حسب المعرف
        
        Args:
            user_id (int): معرف المستخدم
            
        Returns:
            tuple: (success, result)
                - success (bool): نجاح العملية
                - result (dict/str): بيانات المستخدم أو رسالة الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
            cursor = conn.cursor()
            
            # البحث عن المستخدم بواسطة المعرف
            cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return True, dict(user)
            else:
                return False, "المستخدم غير موجود"
                
        except Exception as e:
            return False, f"خطأ في استرجاع المستخدم: {str(e)}"
    
    @classmethod
    def add_user(cls, username, password, role):
        """
        إضافة مستخدم جديد
        
        Args:
            username (str): اسم المستخدم
            password (str): كلمة المرور
            role (str): دور المستخدم (admin أو worker)
            
        Returns:
            tuple: (success, message)
                - success (bool): نجاح العملية
                - message (str): رسالة النجاح أو الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # التحقق من صحة البيانات
            if not username or not password:
                return False, "اسم المستخدم وكلمة المرور مطلوبان"
                
            if role not in ["admin", "worker"]:
                return False, "دور المستخدم يجب أن يكون 'admin' أو 'worker'"
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # إضافة المستخدم
            try:
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, password, role)  # نستخدم كلمة المرور كما هي (بدون تشفير) للسهولة في البداية
                )
                conn.commit()
                conn.close()
                return True, "تمت إضافة المستخدم بنجاح"
            except sqlite3.IntegrityError:
                return False, "اسم المستخدم موجود بالفعل"
                
        except Exception as e:
            return False, f"خطأ في إضافة المستخدم: {str(e)}"
    
    @classmethod
    def update_user(cls, user_id, username, password, role):
        """
        تحديث بيانات مستخدم
        
        Args:
            user_id (int): معرف المستخدم
            username (str): اسم المستخدم الجديد
            password (str): كلمة المرور الجديدة (فارغة للاحتفاظ بالقديمة)
            role (str): دور المستخدم الجديد
            
        Returns:
            tuple: (success, message)
                - success (bool): نجاح العملية
                - message (str): رسالة النجاح أو الخطأ
        """
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # التحقق من صحة البيانات
            if not username:
                return False, "اسم المستخدم مطلوب"
                
            if role not in ["admin", "worker"]:
                return False, "دور المستخدم يجب أن يكون 'admin' أو 'worker'"
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # التحقق من وجود المستخدم
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "المستخدم غير موجود"
            
            # تحديث بيانات المستخدم
            try:
                if password:
                    # استخدام كلمة المرور كما هي بدون تشفير
                    cursor.execute(
                        "UPDATE users SET username = ?, password = ?, role = ? WHERE id = ?",
                        (username, password, role, user_id)
                    )
                else:
                    # الحفاظ على كلمة المرور القديمة
                    cursor.execute(
                        "UPDATE users SET username = ?, role = ? WHERE id = ?",
                        (username, role, user_id)
                    )
                
                conn.commit()
                conn.close()
                return True, "تم تحديث بيانات المستخدم بنجاح"
            except sqlite3.IntegrityError:
                return False, "اسم المستخدم موجود بالفعل"
                
        except Exception as e:
            return False, f"خطأ في تحديث المستخدم: {str(e)}"
    
    @classmethod
    def delete_user(cls, user_id):
        """
        حذف مستخدم
        
        Args:
            user_id (int): معرف المستخدم
            
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
            
            # التحقق من وجود المستخدم
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "المستخدم غير موجود"
            
            # التأكد من وجود مستخدم مدير واحد على الأقل بعد الحذف
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND id != ?", (user_id,))
            admin_count = cursor.fetchone()[0]
            
            if user[3] == 'admin' and admin_count == 0:
                conn.close()
                return False, "لا يمكن حذف المستخدم المدير الوحيد"
            
            # حذف المستخدم
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            return True, "تم حذف المستخدم بنجاح"
                
        except Exception as e:
            return False, f"خطأ في حذف المستخدم: {str(e)}"
            
    @classmethod
    def reset_default_users(cls):
        """إعادة تعيين المستخدمين الافتراضيين"""
        try:
            # التأكد من وجود قاعدة البيانات
            cls._ensure_db_exists()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(cls.db_path)
            cursor = conn.cursor()
            
            # حذف المستخدمين الموجودين
            cursor.execute("DELETE FROM users WHERE username IN ('admin', 'user')")
            
            # إضافة المستخدمين الافتراضيين
            cursor.execute(
                "INSERT OR REPLACE INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", "admin", "admin")
            )
            
            cursor.execute(
                "INSERT OR REPLACE INTO users (username, password, role) VALUES (?, ?, ?)",
                ("user", "user", "worker")
            )
            
            conn.commit()
            conn.close()
            
            return True, "تمت إعادة تعيين المستخدمين الافتراضيين بنجاح"
        except Exception as e:
            return False, f"خطأ في إعادة تعيين المستخدمين: {str(e)}"