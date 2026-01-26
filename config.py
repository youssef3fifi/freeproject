"""
ملف الإعدادات والثوابت لنظام المبيعات
"""

# معلومات المتجر
STORE_NAME = "محل البركة"
STORE_ADDRESS = "شارع النصر – القاهرة"
STORE_PHONE = "0100-123-4567"

# معلومات التطبيق
APP_NAME = "نظام المبيعات"
APP_VERSION = "1.0"
APP_YEAR = "2023"

# إعدادات قاعدة البيانات
DATABASE_PATH = "data/store.db"

# إعدادات الفواتير
INVOICES_FOLDER = "invoices"

# إعدادات المخزون
LOW_STOCK_THRESHOLD = 5  # الحد الأدنى للتنبيه

# إعدادات الواجهة
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768
DEFAULT_FONT = "Arial"
DEFAULT_FONT_SIZE = 10

# الألوان
COLORS = {
    "primary": "#4CAF50",
    "primary_hover": "#45a049",
    "background": "#f0f0f0",
    "frame_bg": "#f9f9f9",
    "text": "black"
}
