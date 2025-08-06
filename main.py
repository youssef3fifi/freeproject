import tkinter as tk
from ui.login_ui import Login
import os

def main():
    # إنشاء المجلدات الضرورية إذا لم تكن موجودة
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # إنشاء النافذة الرئيسية
    root = tk.Tk()
    
    # ضبط نوع الخط للدعم العربي
    try:
        root.option_add("*Font", "Arial 10")
    except:
        pass
    
    # بدء تطبيق تسجيل الدخول
    app = Login(root)
    
    # تشغيل حلقة الأحداث
    root.mainloop()

if __name__ == "__main__":
    main()